Run `~/.pixi/bin/pixi run discover-pubs` to find new papers from the ORCID profile not yet in `_publications/`. The script prints the JSON output path on stdout; read that file.

For each paper in `new_papers`, work through them one at a time interactively:

1. **Show a summary**: title, authors (raw from S2), venue, date, pdf_url.

2. **PDF handling**:
   - If `pdf_url` is set and points to an open-access URL (e.g. arXiv), note it will be used as-is.
   - If `pdf_url` is null or a paywalled URL: ask the user to provide a local PDF path. When they do, copy it to `pdfs/{filename}.pdf` (where `filename` is the suggested slug) and set `pdf: /pdfs/{filename}.pdf` in the markdown.

3. **Thumbnail selection**:
   - If `rendered_pages` is non-empty: read the image files and identify which page has the best teaser figure — a system photo, diagram, or visual result (not a text-heavy page). Tell the user which page you picked and why.
   - If `rendered_pages` is empty but a local PDF was just provided: render the pages yourself using PyMuPDF via `~/.pixi/bin/pixi run python3 -c "import fitz, pathlib; ..."` to `/tmp/{filename}_pages/`, then read and evaluate them.
   - Show the chosen page to the user and ask for confirmation or an alternate page number.

4. **Show the proposed markdown** that would be written to `_publications/{filename}.md`. Generate it using the helpers in `scripts/fetch_publication.py` (import `load_members`, `format_authors`, `generate_markdown`, `fetch_bibtex`). Include the resolved `pdf` and `thumbnail` fields.

5. **Ask the user**: Accept, skip, try a different page, or edit any field? Wait for their response.

6. **On accept**:
   - If a local PDF was provided: copy it to `pdfs/{filename}.pdf`
   - Copy the selected rendered page PNG to `images/pubs/{filename}_thumb.png`
   - Write the markdown to `_publications/{filename}.md`
   - Confirm what was written with the relative paths

7. After all papers, summarize what was added and what was skipped.
