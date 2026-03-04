#!/usr/bin/env python3
"""
format.py — iSRL Research Log Publisher (Jekyll mode)
======================================================
Takes a raw LaTeXML-converted HTML file and writes a Jekyll collection
entry to ../_logs/<slug>.html — YAML front matter + raw body content.

Usage:
    python3 format.py path/to/paper.html

What it does:
  1. Reads the raw LaTeXML HTML (minimal head, bare body)
  2. Extracts title, authors, date, abstract from ltx_* classes
  3. Extracts section headings for ToC
  4. Prompts for: Zenodo DOI, publication date, document type, tags,
     and display flags (show_home, show_ifid, show_funding)
  5. Builds a YAML front matter block with:
       layout: log
       title, date_iso, date_display, doc_type, authors, doi, doi_url,
       platform, description, tags, show_home, show_ifid, show_funding,
       permalink, render_with_liquid: false, toc: [...]
  6. Writes front matter + raw body to ../_logs/<slug>.html
     (Jekyll builds the full iSRL shell via _layouts/log.html)

Requirements: Python 3.8+, no third-party libraries.
"""

import sys
import re
from datetime import datetime
from pathlib import Path


# ─── ANSI colour helpers ───────────────────────────────────────
R    = "\033[0;31m"
G    = "\033[0;32m"
Y    = "\033[0;33m"
B    = "\033[0;34m"
W    = "\033[0m"
BOLD = "\033[1m"


# ─── CLI helpers ──────────────────────────────────────────────
def ask(label: str, default: str = "", required: bool = True) -> str:
    hint = f" [{default}]" if default else ""
    while True:
        val = input(f"  {BOLD}{label}{W}{hint}: ").strip()
        if val:
            return val
        if default:
            return default
        if not required:
            return ""
        print(f"  {R}This field is required.{W}")


def ask_yn(label: str, default: bool = True) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    val = input(f"  {BOLD}{label}{W} {hint}: ").strip().lower()
    if not val:
        return default
    return val.startswith("y")


def pick(label: str, options: list) -> str:
    print(f"\n  {BOLD}{label}{W}")
    for i, opt in enumerate(options, 1):
        print(f"    {Y}{i}.{W} {opt}")
    while True:
        raw = input("  Enter number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  {R}Enter a number 1–{len(options)}.{W}")


def pick_tags(label: str) -> list:
    """Multi-select from a predefined tag list."""
    options = ["ifid", "a11y", "tool", "ai"]
    print(f"\n  {BOLD}{label}{W}")
    print(f"  Options: {', '.join(f'{Y}{i+1}.{W} {t}' for i, t in enumerate(options))}")
    raw = input("  Enter numbers separated by spaces (e.g. 1 3): ").strip()
    selected = []
    for tok in raw.split():
        if tok.isdigit() and 1 <= int(tok) <= len(options):
            t = options[int(tok) - 1]
            if t not in selected:
                selected.append(t)
    if not selected:
        print(f"  {Y}No tags selected — defaulting to [ifid].{W}")
        return ["ifid"]
    return selected


# ─── HTML extraction helpers ──────────────────────────────────
def strip_tags(html: str) -> str:
    """Remove all HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def extract_title(html: str) -> str:
    """Extract document title from ltx_title_document h1."""
    m = re.search(
        r'<h1[^>]*class="[^"]*ltx_title_document[^"]*"[^>]*>(.*?)</h1>',
        html, re.DOTALL | re.IGNORECASE
    )
    if m:
        return strip_tags(m.group(1))
    m2 = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    return strip_tags(m2.group(1)) if m2 else "iSRL Research Log"


def extract_abstract(html: str) -> str:
    """Extract plain-text abstract for meta description (max 300 chars)."""
    m = re.search(r'<div[^>]*class="[^"]*ltx_abstract[^"]*"[^>]*>(.*?)</div>',
                  html, re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    para = re.search(r'<p[^>]*class="[^"]*ltx_p[^"]*"[^>]*>(.*?)</p>',
                     m.group(1), re.DOTALL | re.IGNORECASE)
    raw = strip_tags(para.group(1)) if para else strip_tags(m.group(1))
    return raw[:297] + "…" if len(raw) > 300 else raw


def extract_authors(html: str) -> list:
    """Extract author names from ltx_personname spans."""
    spans = re.findall(
        r'<span[^>]*class="[^"]*ltx_personname[^"]*"[^>]*>(.*?)</span>',
        html, re.DOTALL | re.IGNORECASE
    )
    authors = []
    for s in spans:
        clean = re.sub(r"<br[^>]*>.*", "", s, flags=re.DOTALL)
        name  = strip_tags(clean)
        if name:
            authors.append(name)
    return authors


def extract_date_str(html: str) -> str:
    """Extract date from ltx_dates div."""
    m = re.search(r'<div[^>]*class="[^"]*ltx_dates[^"]*"[^>]*>\(?(.*?)\)?<',
                  html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_sections(html: str) -> list:
    """
    Extract all h2 and h3 headings that have a nearby section/div id.
    Returns list of dicts: {id, text, level}
    """
    section_ids = {}
    for m in re.finditer(r'<(?:section|div)[^>]*\bid="([^"]+)"[^>]*>', html, re.IGNORECASE):
        section_ids[m.start()] = m.group(1)

    results = []
    heading_re = re.compile(
        r'<(h[23])[^>]*class="[^"]*ltx_title[^"]*"[^>]*>(.*?)</\1>',
        re.DOTALL | re.IGNORECASE
    )
    for hm in heading_re.finditer(html):
        tag   = hm.group(1).lower()
        level = 2 if tag == "h2" else 3
        inner = hm.group(2)
        text  = strip_tags(inner)
        text  = re.sub(r"^\d+(\.\d+)*\s+", "", text)
        if not text:
            continue

        pos     = hm.start()
        nearest = ""
        best    = -1
        for spos, sid in section_ids.items():
            if spos <= pos and spos > best:
                best    = spos
                nearest = sid

        if nearest:
            results.append({"id": nearest, "text": text, "level": level})

    seen = set()
    deduped = []
    for r in results:
        key = r["id"]
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    return deduped


# ─── Date helpers ──────────────────────────────────────────────
def normalise_date(raw: str) -> str:
    """Return an ISO date string; fallback to raw input."""
    for fmt in ("%B %d, %Y", "%B %Y", "%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime(
                "%Y-%m-%d" if "%d" in fmt else "%Y-%m"
            )
        except ValueError:
            continue
    return raw.strip()


def make_date_display(pub_date: str, pub_iso: str) -> str:
    """
    Return a human-readable date string like 'February 2026'.
    Uses pub_date if it looks like 'Month YYYY', else derives from pub_iso.
    """
    # Try to parse pub_date as "Month YYYY" directly
    try:
        dt = datetime.strptime(pub_date.strip(), "%B %Y")
        return dt.strftime("%B %Y")
    except ValueError:
        pass
    # Try "Month DD, YYYY"
    try:
        dt = datetime.strptime(pub_date.strip(), "%B %d, %Y")
        return dt.strftime("%B %Y")
    except ValueError:
        pass
    # Fall back to parsing pub_iso
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            dt = datetime.strptime(pub_iso.strip()[:7], "%Y-%m")
            return dt.strftime("%B %Y")
        except ValueError:
            pass
    return pub_date.strip()


# ─── YAML helpers ─────────────────────────────────────────────
def yaml_str(s: str) -> str:
    """Wrap a string in double-quotes, escaping internal quotes."""
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def build_front_matter(
    title: str,
    description: str,
    authors: list,
    doi: str,
    pub_iso: str,
    date_display: str,
    doc_type: str,
    tags: list,
    show_home: bool,
    show_ifid: bool,
    show_funding: bool,
    slug: str,
    sections: list,
) -> str:
    """Build the Jekyll YAML front matter block."""
    doi_url    = f"https://doi.org/{doi}"
    permalink  = f"/logs/{slug}.html"

    # Authors as YAML list
    author_lines = "\n".join(f'  - {yaml_str(a)}' for a in (authors or ["Lalitha A R"]))

    # Tags as YAML inline list  e.g. ["ifid"]
    tags_yaml = "[" + ", ".join(f'"{t}"' for t in tags) + "]"

    # ToC as YAML sequence of inline mappings
    toc_lines = []
    for s in sections:
        text_escaped = s["text"].replace('"', '\\"')
        toc_lines.append(f'  - {{id: "{s["id"]}", text: "{text_escaped}", level: {s["level"]}}}')
    toc_yaml = "\n".join(toc_lines) if toc_lines else "  []"

    return f"""---
layout: log
title: {yaml_str(title)}
date_iso: "{pub_iso}"
date_display: "{date_display}"
doc_type: {doc_type}
authors:
{author_lines}
doi: "{doi}"
doi_url: "{doi_url}"
platform: Zenodo
description: {yaml_str(description)}
tags: {tags_yaml}
show_home: {"true" if show_home else "false"}
show_ifid: {"true" if show_ifid else "false"}
show_funding: {"true" if show_funding else "false"}
permalink: {permalink}
render_with_liquid: false
toc:
{toc_yaml}
---"""


# ─── Main ──────────────────────────────────────────────────────
def main():
    print(f"\n{BOLD}iSRL Research Log Publisher — Jekyll mode{W}")
    print("─" * 46)

    if len(sys.argv) < 2:
        print(f"{R}Usage: python3 format.py path/to/paper.html{W}\n")
        sys.exit(1)

    source = Path(sys.argv[1])
    if not source.exists():
        print(f"{R}File not found: {source}{W}\n")
        sys.exit(1)

    html = source.read_text(encoding="utf-8")
    print(f"{G}✓ Loaded:{W} {source.name}  ({len(html):,} chars)")

    # ── Extract metadata from LaTeXML output ──
    title    = extract_title(html)
    abstract = extract_abstract(html)
    authors  = extract_authors(html)
    raw_date = extract_date_str(html)
    sections = extract_sections(html)

    print(f"\n{B}Auto-detected:{W}")
    print(f"  Title:    {title[:72]}{'…' if len(title) > 72 else ''}")
    print(f"  Authors:  {', '.join(authors) if authors else '(none)'}")
    print(f"  Date:     {raw_date or '(none)'}")
    print(f"  Sections: {len(sections)} heading(s) found for ToC")

    # ── Prompt for publication metadata ──
    print(f"\n{B}Publication metadata:{W}")
    doi      = ask("Zenodo DOI  (e.g. 10.5281/zenodo.12345678)")
    pub_date = ask(
        "Publication date  (e.g. 'February 2026' or '2026-02-19')",
        default=raw_date or datetime.today().strftime("%Y-%m-%d")
    )
    pub_iso      = normalise_date(pub_date)
    date_display = make_date_display(pub_date, pub_iso)
    doc_type     = pick("Document type", ["report", "paper", "audit"])
    tags         = pick_tags("Tags (select all that apply)")

    print(f"\n{B}Listing flags:{W}")
    show_home    = ask_yn("Show on homepage (show_home)?", default=True)
    show_ifid    = ask_yn("Show on IFID page (show_ifid)?", default=True)
    show_funding = ask_yn("Show on Funding page (show_funding)?", default=True)

    # ── Determine output path ──
    slug     = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-")
    logs_dir = Path(__file__).resolve().parent.parent / "_logs"
    logs_dir.mkdir(exist_ok=True)
    out_path = logs_dir / f"{slug}.html"

    # ── Extract raw body content ──
    body_open_m = re.search(r"<body[^>]*>", html, re.IGNORECASE)
    if not body_open_m:
        print(f"{R}No <body> tag found in source file.{W}")
        sys.exit(1)
    content_start  = body_open_m.end()
    body_close_idx = html.lower().rfind("</body>")
    if body_close_idx == -1:
        raw_body = html[content_start:].strip()
    else:
        raw_body = html[content_start:body_close_idx].strip()

    # ── Build and write output ──
    print(f"\n{B}Building…{W}")
    front_matter = build_front_matter(
        title        = title,
        description  = abstract,
        authors      = authors,
        doi          = doi,
        pub_iso      = pub_iso,
        date_display = date_display,
        doc_type     = doc_type,
        tags         = tags,
        show_home    = show_home,
        show_ifid    = show_ifid,
        show_funding = show_funding,
        slug         = slug,
        sections     = sections,
    )

    output = front_matter + "\n" + raw_body + "\n"
    out_path.write_text(output, encoding="utf-8")

    print(f"\n{G}{'─' * 46}")
    print(f"✓ Written:    {out_path}")
    print(f"  Slug:       {slug}")
    print(f"  DOI:        {doi}")
    print(f"  Type:       {doc_type}")
    print(f"  Date:       {pub_date}  →  ISO: {pub_iso}  /  Display: {date_display}")
    print(f"  Tags:       {', '.join(tags)}")
    print(f"  ToC:        {len(sections)} section(s)")
    print(f"  Flags:      home={show_home}, ifid={show_ifid}, funding={show_funding}")
    print(f"  Output:     {len(output):,} chars")
    print(f"{'─' * 46}{W}")
    print(f"\n  {Y}Next step:{W} commit _logs/{slug}.html — GitHub Pages rebuilds automatically.")
    print(f"  The log will appear in all Liquid loops that match its flags/tags.\n")


if __name__ == "__main__":
    main()
