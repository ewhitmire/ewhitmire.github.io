# Changelog

## 2026-01-11 - Complete Site Redesign

### Structure
- Consolidated from multi-page to **single scrolling page** with anchor navigation
- New section order: Hero, Publications, About, Contact
- Removed separate publications page, blog functionality, and RSS feed

### Design
- Complete visual redesign with typography-forward, minimal aesthetic
- Removed Bootstrap framework (was Bootstrap 5.3.3)
- Custom SCSS architecture with modular partials
- System font stack for performance
- Generous whitespace and restrained color palette
- Mobile-responsive, desktop-first reading experience

### Publications
- Changed from card grid with thumbnails to clean text-based list
- Publications now grouped by year (reverse chronological)
- Older publications (6+ years) collapsed by default with toggle
- Removed: thumbnails, modals for BibTeX/citations, press mentions display
- Awards still displayed inline with venue

### Content
- Updated hero with new positioning statement per spec
- Updated About section with current bio
- Updated email to ewhitmire@meta.com
- Added Google Scholar link
- CV link retained in navigation and contact section

### Files Removed
- `publications.html` - merged into index.html
- `_layouts/page.html`, `_layouts/post.html` - no longer needed
- `_posts/` directory - blog functionality removed
- `feed.xml` - RSS removed
- `_sass/_pubs.scss`, `_sass/_home.scss`, `_sass/_svg-icons.scss` - old styles
- `_includes/pub_badge.html` - replaced by `publication_item.html`
- `_includes/icon-*.html`, `_includes/icon-*.svg` - social icons now inline SVG

### Files Added
- `_sass/_nav.scss` - navigation styles
- `_sass/_hero.scss` - hero section styles
- `_sass/_publications.scss` - publication list styles
- `_sass/_about.scss` - about section styles
- `_sass/_contact.scss` - contact section and footer styles
- `_includes/publication_item.html` - new publication display component

### Files Modified
- `index.html` - complete rewrite as single-page layout
- `_config.yml` - updated email, description, removed unused collections
- `_includes/header.html` - anchor-based navigation
- `_includes/footer.html` - simplified
- `_includes/head.html` - removed Bootstrap, updated meta tags
- `_includes/author_list.html` - removed name bolding
- `_sass/_variables.scss` - new design tokens
- `_sass/_base.scss` - new base styles
- `_sass/_layout.scss` - simplified layout utilities
- `css/main.scss` - updated imports
