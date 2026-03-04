# iSRL Website

Source for the [Interdisciplinary Systems Research Lab](https://isrl-research.github.io/) website — a Jekyll static site deployed on GitHub Pages.

## About the Lab

iSRL is an independent, fully remote research lab founded in 2025 and led by Lead Researcher Lalitha A R. The lab builds neutral, open-source systems designed to meet the reality of human complexity. All outputs are released under [CC BY 4.0 International](https://creativecommons.org/licenses/by/4.0/).

Current focus: **IFID (Indian Food Informatics Data)** — a coordination layer for India's food systems that maps thousands of regional ingredient expressions to stable machine-readable identifiers without erasing regional identity.

## Repository Structure

```
isrl/
├── _config.yml               # Jekyll config; defines the `logs` collection
├── _layouts/
│   ├── default.html          # Shell for all main pages
│   └── log.html              # Shell for research log pages (ToC, right sidebar)
├── _includes/
│   ├── head.html             # <head>: GA tag, meta, fonts, main.css
│   ├── sidebar.html          # Left sidebar (nav + ToC); reads page.toc_items
│   ├── mobile-nav.html       # Hamburger header
│   └── mobile-nav-js.html    # Hamburger JS
├── assets/
│   ├── css/main.css          # All site CSS (~760 lines)
│   ├── js/logs-filter.js     # Filter button JS for logs/index.html
│   └── isrl-logo-square.*    # Logo assets (PNG, SVG, HTML)
├── _logs/                    # Jekyll collection; one file per published log
│   └── <slug>.html           # Front matter + raw LaTeXML body
├── logs/                     # Source/tooling directory (excluded from Jekyll build)
│   ├── format.py             # Publisher script: LaTeXML HTML → _logs/<slug>.html
│   ├── *.tex                 # LaTeX source files
│   └── *.html                # Raw LaTeXML output (pre-format.py)
├── ifid/
│   └── ency/                 # Encyclopedia HTML pages (ingredient entries)
├── index.html                # Homepage
├── about.html                # Lab culture, rhythm, values
├── ifid.html                 # IFID project page
├── funding.html              # Full artifact list + funding tiers
├── join-us.html              # How to join
└── research-101.html         # Introductory research guide
```

The `_site/` directory is the built output — do not edit files there directly.

## Running Locally

```bash
gem install bundler jekyll
bundle install
bundle exec jekyll serve
```

The site will be available at `http://localhost:4000`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide. The primary ongoing task is keeping the site's HTML in sync with published records in the [iSRL Zenodo community](https://zenodo.org/communities/isrl/records).

Quick summary:
- Open an issue before starting any work beyond a typo fix
- Fork and branch with a descriptive name (e.g. `html-sync/emf-v2`, `fix/funding-broken-link`)
- PR against `main`; keep PRs scoped to one record or one bug
- Do not commit changes to `_site/`

## License

All content CC BY 4.0 International. See individual Zenodo records for artifact-level licensing details.

## Contact

[lalithaar.research@gmail.com](mailto:lalithaar.research@gmail.com)
