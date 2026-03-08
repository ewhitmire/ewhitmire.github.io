# ericwhitmire.com

Personal website for Eric Whitmire. Built with Jekyll, deployed via GitHub Pages.

## Local Development

```bash
# Install dependencies
bundle install

# Run local server
bundle exec jekyll serve

# Visit http://localhost:4000
```

## Updating Content

### Adding a New Publication

1. Create a new markdown file in `_publications/` (e.g., `_publications/my-paper.md`)

2. Use this frontmatter template:

```yaml
---
title: 'Paper Title Here'
authors: [whitmire, coauthor_id, another_id]
conference: Venue Name (e.g., CHI), Year
date: YYYY-MM-DD
pdf: /pdfs/filename.pdf
video: https://youtube.com/watch?v=xxx  # optional
award: Best Paper Award  # optional
---
```

3. For author names:
   - Use IDs from `_data/members.yml` for known collaborators
   - Use full names as strings for one-off coauthors (e.g., `"Jane Smith"`)

4. Add the PDF to the `pdfs/` directory

5. Rebuild the site to see changes

### Adding a New Collaborator

Edit `_data/members.yml`:

```yaml
- id: newperson
  name: Full Name
  website: https://their-website.com  # optional
  status: alumni
```

### Updating Bio/Copy

- **Hero section**: Edit lines 6-15 in `index.html`
- **About section**: Edit lines 93-101 in `index.html`
- **Contact info**: Edit `_config.yml` for email, GitHub, LinkedIn, Scholar URL

### Updating CV

Replace the file at `pdfs/whitmire_cv_web.pdf`

## File Structure

```
├── index.html           # Main single-page site
├── _config.yml          # Site configuration
├── _publications/       # Publication markdown files
├── _data/members.yml    # Author name database
├── _includes/           # Reusable HTML components
├── _layouts/            # Page templates
├── _sass/               # SCSS stylesheets
├── css/main.scss        # Main stylesheet (imports partials)
├── images/              # Images (portrait, etc.)
└── pdfs/                # PDF files (CV, papers)
```

## Design Notes

- Typography-first design with system fonts
- Minimal dependencies (no Bootstrap, no jQuery)
- Publications grouped by year, older years collapsed
- Mobile-responsive, optimized for desktop reading
