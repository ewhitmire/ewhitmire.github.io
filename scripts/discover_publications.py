#!/usr/bin/env python3
"""
Discover new publications from ORCID and prepare them for review.

Fetches your ORCID works, diffs against _publications/, downloads PDFs,
renders pages as images, and writes a JSON summary for the review workflow.

Usage:
    python scripts/discover_publications.py
    python scripts/discover_publications.py --output /tmp/new_papers.json

Output JSON format:
    {
      "new_papers": [
        {
          "title": "...",
          "filename": "...",        # suggested _publications/{filename}.md
          "pdf_url": "...",
          "metadata": { ...s2 fields... },
          "rendered_pages": [       # paths to rendered PNG files (may be empty)
            "/tmp/pubupdate_xxx/page_0.png",
            ...
          ]
        }
      ]
    }
"""

import json
import re
import sys
import tempfile
import time
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_publication import (
    load_members,
    generate_filename,
    fetch_from_semantic_scholar,
)

PROJECT_ROOT = Path(__file__).parent.parent
PUBLICATIONS_DIR = PROJECT_ROOT / "_publications"

ORCID_ID = "0000-0001-7715-7557"
ORCID_API = "https://pub.orcid.org/v3.0"


# ── ORCID ─────────────────────────────────────────────────────────────────────

def fetch_orcid_papers():
    url = f"{ORCID_API}/{ORCID_ID}/works"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "PublicationUpdater/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    papers = []
    for group in data.get("group", []):
        for summary in group.get("work-summary", []):
            title = ((summary.get("title") or {}).get("title") or {}).get("value", "").strip()
            doi = arxiv_id = None
            for eid in (summary.get("external-ids") or {}).get("external-id", []):
                t = eid.get("external-id-type", "").lower()
                v = (eid.get("external-id-value") or "").strip()
                if t == "doi" and not doi:
                    doi = v
                elif t == "arxiv" and not arxiv_id:
                    arxiv_id = v.replace("arxiv:", "").strip()
            if title:
                papers.append({"title": title, "doi": doi, "arxiv_id": arxiv_id})

    return papers


def normalize_title(title):
    """Lowercase, strip punctuation/numbers-only tokens for fuzzy comparison."""
    t = title.lower()
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def is_new_paper(orcid_title, existing_titles, threshold=0.80):
    """Return True if this ORCID title doesn't match any existing publication."""
    na = normalize_title(orcid_title)
    words_a = set(na.split())
    for existing in existing_titles:
        nb = normalize_title(existing)
        # Prefix match: handles ORCID appending paper IDs (e.g. "MHCI006")
        shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
        if longer.startswith(shorter) and len(shorter) / len(longer) >= threshold:
            return False
        # Word overlap: handles minor subtitle differences
        words_b = set(nb.split())
        if words_a and words_b:
            overlap = len(words_a & words_b) / max(len(words_a), len(words_b))
            if overlap >= threshold:
                return False
    return True


def get_existing_titles():
    """Return list of titles already in _publications/."""
    existing = []
    for md_file in PUBLICATIONS_DIR.glob("*.md"):
        for line in md_file.read_text().split("\n"):
            line = line.strip()
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip("'\"")
                existing.append(title)
                break
    return existing


# ── PDF ───────────────────────────────────────────────────────────────────────

def find_pdf_url(doi, arxiv_id, s2_metadata=None):
    """Find an open-access PDF URL. Checks arXiv, S2 external IDs, then Unpaywall."""
    # Prefer arXiv (always open access)
    if not arxiv_id and s2_metadata:
        arxiv_id = (s2_metadata.get("externalIds") or {}).get("ArXiv")
    if arxiv_id:
        return f"https://arxiv.org/pdf/{arxiv_id}"

    if doi:
        try:
            url = f"https://api.unpaywall.org/v2/{doi}?email=scripts@ewhitmire.github.io"
            req = urllib.request.Request(url, headers={"User-Agent": "PublicationUpdater/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            loc = data.get("best_oa_location") or {}
            pdf = loc.get("url_for_pdf")
            # Only return if it looks like an actual PDF endpoint, not a DOI redirect
            if pdf and not pdf.startswith("https://doi.org"):
                return pdf
        except Exception:
            pass

    return None


def download_pdf(url, dest_dir):
    if not url:
        return None
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/pdf"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        path = dest_dir / "paper.pdf"
        path.write_bytes(data)
        return path
    except Exception as e:
        print(f"    Could not download PDF: {e}", file=sys.stderr)
        return None


def render_pages(pdf_path, dest_dir, max_pages=6):
    try:
        import fitz
    except ImportError:
        print("    pymupdf not available (run `pixi install`)", file=sys.stderr)
        return []

    doc = fitz.open(str(pdf_path))
    paths = []
    for i in range(min(max_pages, len(doc))):
        pix = doc[i].get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        out = dest_dir / f"page_{i}.png"
        pix.save(str(out))
        paths.append(str(out))
    doc.close()
    return paths


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/tmp/new_papers.json")
    args = parser.parse_args()

    print(f"Fetching ORCID papers for {ORCID_ID}...", file=sys.stderr)
    orcid_papers = fetch_orcid_papers()
    print(f"Found {len(orcid_papers)} works", file=sys.stderr)

    existing = get_existing_titles()
    print(f"Found {len(existing)} existing publications", file=sys.stderr)

    new_papers = [p for p in orcid_papers if is_new_paper(p["title"], existing)]
    print(f"{len(new_papers)} new paper(s)", file=sys.stderr)

    if not new_papers:
        result = {"new_papers": []}
        Path(args.output).write_text(json.dumps(result, indent=2))
        print(args.output)
        return

    results = []
    for paper in new_papers:
        title = paper["title"]
        doi = paper.get("doi")
        arxiv_id = paper.get("arxiv_id")
        filename = generate_filename(title)

        print(f"\n  Processing: {title[:70]}", file=sys.stderr)

        # Fetch S2 metadata
        metadata = None
        if doi:
            print(f"    Looking up DOI {doi}...", file=sys.stderr)
            metadata = fetch_from_semantic_scholar(doi, is_doi=True)
        if not metadata:
            print(f"    Searching by title...", file=sys.stderr)
            metadata = fetch_from_semantic_scholar(title, is_doi=False)
        if not metadata:
            print(f"    Could not fetch metadata, skipping", file=sys.stderr)
            continue

        # Download PDF and render
        pdf_url = find_pdf_url(doi, arxiv_id, s2_metadata=metadata)
        rendered_pages = []

        if pdf_url:
            dest_dir = Path(tempfile.mkdtemp(prefix="pubupdate_"))
            print(f"    Downloading PDF...", file=sys.stderr)
            pdf_path = download_pdf(pdf_url, dest_dir)
            if pdf_path:
                print(f"    Rendering pages...", file=sys.stderr)
                rendered_pages = render_pages(pdf_path, dest_dir)
                print(f"    Rendered {len(rendered_pages)} pages", file=sys.stderr)

        results.append({
            "title": title,
            "filename": filename,
            "pdf_url": pdf_url,
            "metadata": metadata,
            "rendered_pages": rendered_pages,
        })

    result = {"new_papers": results}
    Path(args.output).write_text(json.dumps(result, indent=2))
    print(f"\n{args.output}", file=sys.stderr)

    # Print the output path to stdout for the skill to capture
    print(args.output)


if __name__ == "__main__":
    main()
