#!/usr/bin/env python3
"""
Fetch publication metadata and generate Jekyll markdown file.

Usage:
    python scripts/fetch_publication.py 10.1145/3307334.3326090          # DOI (recommended)
    python scripts/fetch_publication.py "Paper Title Here"               # Title search
    python scripts/fetch_publication.py 10.1145/xxx -o myfile            # Custom output filename
    python scripts/fetch_publication.py 10.1145/xxx --dry-run            # Preview without saving

DOI lookups are more reliable. Title searches may hit API rate limits.
For heavy use, get a free API key from https://www.semanticscholar.org/product/api
and set: export S2_API_KEY=your_key
"""

import argparse
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import json
from pathlib import Path
from datetime import datetime

# Path configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PUBLICATIONS_DIR = PROJECT_ROOT / "_publications"
MEMBERS_FILE = PROJECT_ROOT / "_data" / "members.yml"

# Semantic Scholar API
S2_API_BASE = "https://api.semanticscholar.org/graph/v1"


def load_members():
    """Load members.yml and create name -> id mapping."""
    members = {}
    if not MEMBERS_FILE.exists():
        return members

    content = MEMBERS_FILE.read_text()
    # Simple YAML parsing for our specific format
    current_id = None
    current_name = None

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- id:'):
            current_id = line.split(':', 1)[1].strip()
        elif line.startswith('name:'):
            current_name = line.split(':', 1)[1].strip()
            if current_id and current_name:
                # Normalize name for matching
                normalized = current_name.lower().replace('.', '').strip()
                members[normalized] = current_id
                # Also add last name only for partial matching
                parts = current_name.split()
                if len(parts) > 1:
                    members[parts[-1].lower()] = current_id
                current_id = None
                current_name = None

    return members


def normalize_name(name):
    """Normalize author name for comparison."""
    return name.lower().replace('.', '').strip()


def match_author(author_name, members):
    """Try to match an author name to a member ID."""
    normalized = normalize_name(author_name)

    # Direct match
    if normalized in members:
        return members[normalized]

    # Try last name only
    parts = author_name.split()
    if len(parts) > 1:
        last_name = parts[-1].lower()
        if last_name in members:
            return members[last_name]

    # No match - return quoted full name
    return None


def fetch_from_semantic_scholar(query, is_doi=False, max_retries=4):
    """Fetch paper metadata from Semantic Scholar API with retry logic."""
    fields = "title,authors,venue,year,abstract,externalIds,publicationDate"

    if is_doi:
        # Direct lookup by DOI
        url = f"{S2_API_BASE}/paper/DOI:{query}?fields={fields}"
    else:
        # Search by title
        encoded_query = urllib.parse.quote(query)
        url = f"{S2_API_BASE}/paper/search?query={encoded_query}&fields={fields}&limit=1"

    # Check for API key (helps with rate limits)
    api_key = os.environ.get("S2_API_KEY")
    headers = {"User-Agent": "PublicationFetcher/1.0"}
    if api_key:
        headers["x-api-key"] = api_key

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

                if is_doi:
                    return data
                else:
                    # Search returns a list
                    if data.get("data") and len(data["data"]) > 0:
                        return data["data"][0]
                    return None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Rate limited - wait and retry with exponential backoff
                wait_time = (2 ** attempt) * 5  # 5, 10, 20, 40 seconds
                print(f"Rate limited, waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            print(f"Error fetching from Semantic Scholar: {e.code} {e.reason}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    print("Error: Max retries exceeded. Try using a DOI instead of title,")
    print("or get an API key from https://www.semanticscholar.org/product/api")
    return None


def fetch_bibtex(doi):
    """Fetch BibTeX from doi.org."""
    if not doi:
        return None

    url = f"https://doi.org/{doi}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/x-bibtex",
                "User-Agent": "PublicationFetcher/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode()
    except Exception as e:
        print(f"Could not fetch BibTeX: {e}")
        return None


def generate_filename(title):
    """Generate a filename from the title."""
    # Extract first significant word (skip articles)
    words = title.lower().split()
    skip_words = {'a', 'an', 'the', 'on', 'in', 'at', 'to', 'for', 'of', 'with'}

    for word in words:
        # Clean the word
        clean = re.sub(r'[^a-z0-9]', '', word)
        if clean and clean not in skip_words:
            return clean

    # Fallback
    return re.sub(r'[^a-z0-9]', '', words[0]) if words else "paper"


def format_authors(authors, members):
    """Format authors list, mapping to member IDs where possible."""
    formatted = []
    for author in authors:
        name = author.get("name", "")
        member_id = match_author(name, members)
        if member_id:
            formatted.append(member_id)
        else:
            formatted.append(f"'{name}'")
    return formatted


def escape_yaml_string(s):
    """Escape a string for YAML."""
    if not s:
        return "''"
    # If it contains special chars, quote it
    if any(c in s for c in [':', '#', "'", '"', '\n', '[', ']', '{', '}']):
        # Use single quotes and escape internal single quotes
        escaped = s.replace("'", "''")
        return f"'{escaped}'"
    return s


def generate_markdown(paper, members):
    """Generate Jekyll markdown content."""
    title = paper.get("title", "Untitled")
    authors = paper.get("authors", [])
    venue = paper.get("venue", "")
    year = paper.get("year", datetime.now().year)
    abstract = paper.get("abstract", "")
    pub_date = paper.get("publicationDate")
    external_ids = paper.get("externalIds", {})
    doi = external_ids.get("DOI")

    # Format date
    if pub_date:
        date_str = pub_date
    else:
        date_str = f"{year}-01-01"

    # Format authors
    formatted_authors = format_authors(authors, members)
    authors_str = "[" + ", ".join(formatted_authors) + "]"

    # Format conference/venue with year
    if venue:
        conference = f"{venue}, {year}"
    else:
        conference = str(year)

    # Fetch BibTeX
    bibtex = fetch_bibtex(doi) if doi else None

    # Build markdown
    lines = ["---"]
    lines.append(f"title: '{title}'")
    lines.append(f"authors: {authors_str}")
    lines.append(f"conference: '{conference}'")
    lines.append(f"date: {date_str}")

    if abstract:
        lines.append("abstract: |")
        # Wrap abstract text
        for para in abstract.split('\n'):
            lines.append(f"  {para}")

    if bibtex:
        lines.append("bibtex: |")
        for bib_line in bibtex.strip().split('\n'):
            lines.append(f"  {bib_line}")

    # Placeholder fields (commented out)
    lines.append("#pdf: /pdfs/filename.pdf")
    lines.append("#thumbnail: /images/pubs/filename_thumb.png")
    lines.append("#video: https://youtube.com/...")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def is_doi(query):
    """Check if query looks like a DOI."""
    doi_pattern = r'^10\.\d{4,}/'
    return bool(re.match(doi_pattern, query))


def main():
    parser = argparse.ArgumentParser(
        description="Fetch publication metadata and generate Jekyll markdown"
    )
    parser.add_argument(
        "query",
        help="Paper title or DOI (e.g., '10.1145/3307334.3326090')"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output filename (without .md extension)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print markdown to stdout instead of writing file"
    )

    args = parser.parse_args()

    # Load member mapping
    print("Loading member data...")
    members = load_members()
    print(f"Loaded {len(members)} member name mappings")

    # Detect if query is a DOI
    query_is_doi = is_doi(args.query)
    print(f"Searching for {'DOI' if query_is_doi else 'title'}: {args.query}")

    # Fetch paper data
    paper = fetch_from_semantic_scholar(args.query, is_doi=query_is_doi)

    if not paper:
        print("Error: Could not find paper")
        sys.exit(1)

    print(f"Found: {paper.get('title', 'Unknown')}")
    print(f"Authors: {', '.join(a.get('name', '') for a in paper.get('authors', []))}")
    print(f"Venue: {paper.get('venue', 'Unknown')}")
    print(f"Year: {paper.get('year', 'Unknown')}")

    # Generate markdown
    markdown = generate_markdown(paper, members)

    if args.dry_run:
        print("\n--- Generated Markdown ---")
        print(markdown)
        return

    # Determine output filename
    if args.output:
        filename = args.output
    else:
        filename = generate_filename(paper.get("title", "paper"))

    output_path = PUBLICATIONS_DIR / f"{filename}.md"

    # Check if file exists
    if output_path.exists():
        print(f"Warning: {output_path} already exists")
        response = input("Overwrite? [y/N] ")
        if response.lower() != 'y':
            print("Aborted")
            sys.exit(0)

    # Write file
    output_path.write_text(markdown)
    print(f"\nCreated: {output_path}")


if __name__ == "__main__":
    main()
