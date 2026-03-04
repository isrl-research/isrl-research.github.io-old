# Contributing to iSRL

Thank you for your interest in contributing. iSRL is a small, fully remote lab — contributions are async by default and reviewed as capacity allows.

All outputs are released under [CC BY 4.0 International](https://creativecommons.org/licenses/by/4.0/). By contributing you agree your work may be published under the same license.

---

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
│   ├── *.html                # Raw LaTeXML output (pre-format.py)
│   └── *.css                 # LaTeXML stylesheets (ltx-article.css, etc.)
├── ifid/
│   └── ency/                 # Encyclopedia HTML pages (ingredient entries)
├── index.html                # Homepage
├── about.html                # Lab culture, rhythm, values
├── ifid.html                 # IFID project page
├── funding.html              # Full artifact list + funding tiers
├── join-us.html              # How to join
└── research-101.html         # Introductory research guide
```

The site is a **Jekyll static site** deployed on GitHub Pages. The `_site/` directory is the built output — do not edit files there directly.

---

## Branding Guidelines

**The following must not be changed without explicit notice from the PI:**

- **Color palette** — `--bg: #f7f6f2`, `--ink: #111110`, `--navy: #2c346b`, `--red: #c0392b`
- **Typefaces** — Libre Baskerville (titles), Source Serif 4 (body), DM Mono (monospace)
- **Logo** — `isrl-logo-square.*` and `isrl-logo-landscape.*`; shape, color, and proportions are fixed

Comprehensive branding guidelines will be published in **April 2026**. Until then, keep visual changes minimal and scoped to the task at hand.

---

## Main Contribution Area: HTML Syncing

The primary ongoing task is keeping the site's HTML versions in sync with published records in the iSRL Zenodo community:

**https://zenodo.org/communities/isrl/records**

### What to check for

| Situation | Action |
|---|---|
| A new release appears on Zenodo that has no HTML on the site | Open an issue: `[new record] <title>` |
| An existing record has been updated (new version) | Open an issue: `[version update] <title> — vN → vN+1` |
| An existing HTML page on the site has broken links, rendering issues, or missing sections | Open an issue: `[html bug] <slug> — <short description>` |

Please include the Zenodo DOI in any issue you open. A minimal issue is better than no issue — you do not need to fix it yourself to report it.

### If you want to help with HTML conversion

If you are comfortable with HTML and CSS and want to help convert a new record to an HTML page, we use the following pipeline:

**1. LaTeX → HTML via LaTeXML**

```bash
latexml --dest=paper.xml paper.tex
latexmlpost --dest=paper.html --format=html5 paper.xml
```

The raw output is a minimal HTML file with `ltx_*` CSS classes throughout.

**2. Processing via `format.py`**

```bash
cd logs/
python3 format.py path/to/paper.html
```

This interactive script:
- Auto-detects title, authors, abstract, and section headings from the LaTeXML output
- Prompts you for the Zenodo DOI, publication date, document type, and tags
- Asks which listing pages the log should appear on (`show_home`, `show_ifid`, `show_funding`)
- Writes `_logs/<slug>.html` — a Jekyll collection entry with YAML front matter + raw body

**3. Custom tweaking**

After `format.py` runs, manual cleanup is often needed:
- Fix table rendering, math display, or figure alignment
- Confirm section `id` attributes are correct for the ToC
- Check that `render_with_liquid: false` is present in front matter (required for any file containing `{{ }}` — e.g., LaTeX expressions)

**4. Source TeX**

The `.tex` source files for all new records are available in the `/source-tex` repository in the iSRL GitHub org. The older files will be made available around April 2025. Until then, Please reach out via the specific issue if a source file is needed.

---

## How to Contribute

1. **Open an issue first** for anything beyond a typo fix. This avoids duplicate effort.
2. **Fork and branch** — use a descriptive branch name, e.g. `html-sync/emf-v2` or `fix/funding-broken-link`.
3. **PR against `main`** — keep PRs scoped; one record or one bug per PR is preferred.
4. **Do not modify `_site/`** — this is auto-generated by Jekyll and should not be committed manually.

---

## Questions

Open a GitHub issue or email [lalithaar.research@gmail.com](mailto:lalithaar.research@gmail.com).
