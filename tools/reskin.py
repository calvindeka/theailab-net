#!/usr/bin/env python3
"""Rewrap every page of the course site in the vendored just-the-docs shell.

This changes page *chrome* only. The contents of each page's `.page-content`
block are extracted verbatim from the existing file and re-emitted unmodified,
so no course content is created, deleted, or reworded here.

Run from the repo root:  python tools/reskin.py
"""
from __future__ import annotations

import os
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent

SITE_TITLE = "IPHS 400: Frontiers in AI"
SITE_TAGLINE = "Kenyon College — Fall 2026"
FOOTER_TEXT = "IPHS 400: Frontiers in AI · Kenyon College"

# canonical repo-root-relative targets; labels must match tests' EXPECTED_NAV_LABELS
MAIN_NAV = [
    ("Home", "index.html"),
    ("Syllabus", "core/syllabus.html"),
    ("Schedule", "core/schedule.html"),
    ("Assignments", "core/assignments.html"),
    ("Policies", "core/policies.html"),
    ("About", "core/about.html"),
]
WEEKS = [(f"Week {n}", f"weeks/week-{n:02d}.html") for n in range(1, 16)]


def pages() -> list[Path]:
    found = [ROOT / "index.html", ROOT / "404.html"]
    found += sorted((ROOT / "core").glob("*.html"))
    found += sorted((ROOT / "weeks").glob("*.html"))
    return [p for p in found if p.exists()]


def relative(from_page: Path, target: str) -> str:
    """Shortest correct relative href from a page to a repo-root-relative target."""
    return os.path.relpath(ROOT / target, from_page.parent).replace(os.sep, "/")


def nav_items(page: Path, items, extra_class: str = "") -> str:
    here = page.relative_to(ROOT).as_posix()
    out = []
    for label, target in items:
        href = relative(page, target)
        current = target == here
        aria = ' aria-current="page"' if current else ""
        active = " active" if current else ""
        out.append(
            f'<li class="nav-list-item{active}">'
            f'<a href="{href}" class="nav-list-link{extra_class}"{aria}>{label}</a></li>'
        )
    return "\n".join(out)


def render(page: Path, title: str, heading: str, content_html: str) -> str:
    css = relative(page, "css/style.css")
    home = relative(page, "index.html")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
<a class="skip-to-main" href="#main-content">Skip to main content</a>
<div class="side-bar">
<header class="site-header">
<a href="{home}" class="site-title lh-tight">{SITE_TITLE}</a>
<span class="site-description">{SITE_TAGLINE}</span>
</header>
<nav class="main-nav" aria-label="Main">
<ul class="nav-list">
{nav_items(page, MAIN_NAV)}
</ul>
</nav>
<nav class="week-nav" aria-label="Weekly schedule">
<p class="nav-category">Weeks</p>
<ul class="nav-list">
{nav_items(page, WEEKS)}
</ul>
</nav>
</div>
<div class="main" id="top">
<div class="main-content-wrap">
<main id="main-content" class="main-content">
<section class="hero"><h1>{heading}</h1></section>
<div class="page-content">
{content_html}
</div>
</main>
<footer class="site-footer">
<p>{FOOTER_TEXT}</p>
</footer>
</div>
</div>
</body>
</html>
"""


def main() -> None:
    changed = 0
    for page in pages():
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "lxml")

        title = soup.title.string.strip() if soup.title and soup.title.string else SITE_TITLE
        hero_h1 = soup.select_one("section.hero h1")
        heading = hero_h1.get_text(strip=True) if hero_h1 else title.split("–")[0].strip()

        block = soup.select_one(".page-content") or soup.select_one("main")
        if block is None:
            print(f"  !! no content block found in {page.name}, skipped")
            continue
        content_html = "".join(str(c) for c in block.contents).strip()

        page.write_text(render(page, title, heading, content_html), encoding="utf-8")
        changed += 1
    print(f"reskinned {changed} pages")


if __name__ == "__main__":
    main()
