#!/usr/bin/env python3
"""Build the IPHS 400 course site from its sources.

Sources of truth
----------------
  data/schedule.json    week numbers, titles, unit grouping, session dates
  weeks/week-NN.md      prose body for a week (optional, per week)
  css/custom.css        site-specific styles (see tools/build_css.py)

What this generates
-------------------
  * Shared page chrome (sidebar, nav, footer) for all 22 pages.
  * The week list on core/schedule.html, from data/schedule.json.
  * The "this week" panel on index.html, resolved against today's date.
  * weeks/week-NN.html for any week that has a Markdown source. Weeks with no
    .md file keep their existing hand-written content untouched.

Why this exists
---------------
The repository already contained weeks/week-template.md and Markdown sources
for two of fifteen weeks, with the HTML being produced by hand (see the commit
history around week-01/week-02). Doing that by hand fifteen times, then again
whenever a reading changes, is where course sites go stale. This makes the
Markdown the source and the HTML a build artifact.

Usage:  python tools/build_site.py [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "schedule.json").read_text(encoding="utf-8"))

SITE_TITLE = "IPHS 400: Frontiers in AI"
SITE_TAGLINE = "Kenyon College — Fall 2026"
FOOTER_TEXT = "IPHS 400: Frontiers in AI · Kenyon College"

MAIN_NAV = [
    ("Home", "index.html"),
    ("Syllabus", "core/syllabus.html"),
    ("Schedule", "core/schedule.html"),
    ("Assignments", "core/assignments.html"),
    ("Policies", "core/policies.html"),
    ("About", "core/about.html"),
]
WEEK_NAV = [(f"Week {w['number']}", w["page"]) for w in DATA["weeks"]]

MD_EXT = ["tables", "attr_list", "fenced_code", "sane_lists", "toc"]


# ---------------------------------------------------------------- helpers ---
def rel(from_page: Path, target: str) -> str:
    return os.path.relpath(ROOT / target, from_page.parent).replace(os.sep, "/")


def all_pages() -> list[Path]:
    found = [ROOT / "index.html", ROOT / "404.html"]
    found += sorted((ROOT / "core").glob("*.html"))
    found += sorted((ROOT / "weeks").glob("*.html"))
    return [p for p in found if p.exists()]


def fmt_sessions(iso_dates: list[str]) -> str:
    """'Tuesday & Thursday, September 1 & 3' / 'Thursday, August 27'."""
    ds = [dt.date.fromisoformat(s) for s in iso_dates]
    if not ds:
        return ""
    if len(ds) == 1:
        return ds[0].strftime("%A, %B ") + str(ds[0].day)
    a, b = ds[0], ds[-1]
    if a.month == b.month:
        return f"{a:%A} & {b:%A}, {a:%B} {a.day} & {b.day}"
    return f"{a:%A}, {a:%B} {a.day} & {b:%A}, {b:%B} {b.day}"


def nav_items(page: Path, items) -> str:
    here = page.relative_to(ROOT).as_posix()
    out = []
    for label, target in items:
        cur = target == here
        out.append(
            f'<li class="nav-list-item{" active" if cur else ""}">'
            f'<a href="{rel(page, target)}" class="nav-list-link"'
            f'{" aria-current=\"page\"" if cur else ""}>{label}</a></li>'
        )
    return "\n".join(out)


def add_table_scopes(html: str) -> str:
    """Give every <th> a scope. WCAG 1.3.1: without it a screen reader cannot
    reliably say which header a cell belongs to. Row-header tables (the
    two-column 'Course Details' style used across this site) need scope="row";
    header-only rows need scope="col"."""
    if "<th" not in html:
        return html
    soup = BeautifulSoup(html, "lxml")
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [c for c in tr.find_all(["th", "td"], recursive=False)]
            ths = [c for c in cells if c.name == "th"]
            if not ths:
                continue
            header_row = len(ths) == len(cells)
            for c in ths:
                c["scope"] = "col" if header_row else "row"
    body = soup.body if soup.body else soup
    return "".join(str(c) for c in body.contents)


def describe(html: str, fallback: str) -> str:
    """One-sentence page description for <meta> and Open Graph tags."""
    soup = BeautifulSoup(html, "lxml")
    for p_ in soup.find_all("p"):
        text = " ".join(p_.get_text(" ", strip=True).split())
        if len(text) >= 60:   # shorter paragraphs make poor search snippets
            if len(text) > 155:
                text = text[:155].rsplit(" ", 1)[0] + "…"
            return text.replace('"', "&quot;")
    return fallback.replace('"', "&quot;")


def aux_nav(page: Path) -> str:
    """Quick links to external course resources, from data/schedule.json."""
    links = DATA["course"].get("links", [])
    if not links:
        return ""
    items = "".join(
        f'<li><a href="{l["url"]}" class="aux-nav-link">{l["label"]}</a></li>' for l in links)
    return (f'<nav class="aux-nav" aria-label="External resources">'
            f'<ul class="aux-nav-list">{items}</ul></nav>')


def shell(page: Path, title: str, heading: str, body: str, extra_head: str = "") -> str:
    body = add_table_scopes(body)
    desc = describe(body, f"{heading} — {SITE_TITLE}, {SITE_TAGLINE}.")
    og_title = title.replace(f" – {SITE_TITLE}", "")
    repo = DATA["course"]["repo"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta name="twitter:card" content="summary">
<title>{title}</title>
<link rel="icon" href="{rel(page, 'images/favicon.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{rel(page, 'css/style.css')}">
<link rel="stylesheet" href="{rel(page, 'css/style-dark.css')}" id="dark-scheme" media="(prefers-color-scheme: dark)">{extra_head}
</head>
<body>
<a class="skip-to-main" href="#main-content">Skip to main content</a>
<div class="side-bar">
<header class="site-header">
<a href="{rel(page, 'index.html')}" class="site-title lh-tight"><span class="brand-block">{DATA["course"]["code"]}</span><span class="brand-title">{DATA["course"]["title"]}</span></a>
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
{nav_items(page, WEEK_NAV)}
</ul>
</nav>
<div class="theme-toggle-wrap">
<button type="button" class="theme-toggle" id="theme-toggle" aria-pressed="false" hidden>Dark mode</button>
</div>
</div>
<div class="main" id="top">
<div class="main-content-wrap">
{aux_nav(page)}
<main id="main-content" class="main-content">
<section class="hero"><h1>{heading}</h1></section>
<div class="page-content">
{body}
</div>
</main>
<footer class="site-footer">
<p>{FOOTER_TEXT}</p>
<p class="footer-links">Built by <a href="{DATA["course"]["author"]["github"]}">{DATA["course"]["author"]["name"]}</a> · <a href="{repo}">Source repository</a> · <span>Built {dt.date.today().isoformat()}</span></p>
</footer>
<script src="{rel(page, 'js/theme.js')}" defer></script>
</div>
</div>
</body>
</html>
"""


# ------------------------------------------------------------- generators ---
def current_week(today: dt.date):
    """The week in session today, else the next upcoming week, else the last."""
    weeks = DATA["weeks"]
    for w in weeks:
        last = dt.date.fromisoformat(w["sessions"][-1])
        if today <= last:
            return w
    return weeks[-1]


def this_week_panel(page: Path, today: dt.date) -> str:
    w = current_week(today)
    upcoming = [dt.date.fromisoformat(s) for s in w["sessions"] if dt.date.fromisoformat(s) >= today]
    if upcoming:
        nxt = upcoming[0]
        when = "Today" if nxt == today else f"{nxt:%A, %B} {nxt.day}"
        line = f"Next session: <strong>{when}</strong> · {DATA['course']['meets'].split(', ',1)[1]} · {DATA['course']['location']}"
    else:
        line = f"Sessions: {fmt_sessions(w['sessions'])}"
    nd = ""
    dl = next_deadline(today)
    if dl:
        a, d = dl
        days = (d - today).days
        when = "today" if days == 0 else ("tomorrow" if days == 1 else f"in {days} days")
        nd = (f'<p class="this-week-due">Next deadline: '
              f'<a href="{rel(page, a["page"])}">{a["name"]}</a> — '
              f'<strong>{d:%A, %B} {d.day}</strong> ({when})</p>\n')
    return (
        '<div class="this-week">\n'
        '<p class="this-week-label">Where we are</p>\n'
        f'<h2><a href="{rel(page, w["page"])}">Week {w["number"]}: {w["title"]}</a></h2>\n'
        f"<p>{line}</p>\n"
        f'<p class="this-week-unit">{w["unit"]}</p>\n'
        + nd
        + "</div>"
    )


def deadlines_in_week(w) -> list:
    """Assignments due during this week (Mon-Sun around its sessions)."""
    first = dt.date.fromisoformat(w["sessions"][0])
    monday = first - dt.timedelta(days=first.weekday())
    sunday = monday + dt.timedelta(days=6)
    out = []
    for a in DATA.get("assignments", []):
        d = dt.date.fromisoformat(a["due"])
        if monday <= d <= sunday:
            out.append((a, d))
    return out


def next_deadline(today: dt.date):
    upcoming = [(a, dt.date.fromisoformat(a["due"])) for a in DATA.get("assignments", [])
                if dt.date.fromisoformat(a["due"]) >= today]
    return min(upcoming, key=lambda x: x[1]) if upcoming else None


def semester_schedule(page: Path, today: dt.date) -> str:
    """The whole semester as one table per week: every session date and every
    deadline, in order. This is the site's front door -- the question a student
    opens it to answer is 'what is happening, and when'."""
    cur = current_week(today)
    out = ['<h2 id="semester-schedule">Semester Schedule</h2>']
    for w in DATA["weeks"]:
        # (date, html) so rows sort chronologically -- sorting the markup itself
        # orders them by weekday name, which puts Fri Sep 4 above Thu Sep 3.
        rows = []
        for s in w["sessions"]:
            d = dt.date.fromisoformat(s)
            today_cls = ' class="is-today"' if d == today else ""
            rows.append((d,
                f'<tr{today_cls}><th scope="row">{d:%a, %b} {d.day}</th>'
                f'<td><span class="label label-blue">CLASS</span> '
                f'<a href="{rel(page, w["page"])}">{w["title"]}</a></td></tr>'))
        for a, d in deadlines_in_week(w):
            rows.append((d,
                f'<tr class="is-due"><th scope="row">{d:%a, %b} {d.day}</th>'
                f'<td><span class="label label-red">DUE</span> '
                f'<a href="{rel(page, a["page"])}">{a["name"]}</a> '
                f'<span class="due-meta">{a["weight"]} · {a["grading"]}</span></td></tr>'))
        rows.sort(key=lambda pair: pair[0])
        rows = [html for _, html in rows]
        here = ' <span class="label label-purple">THIS WEEK</span>' if w is cur else ""
        out.append(
            f'<h3 class="week-heading" id="week-{w["number"]:02d}">'
            f'<a href="{rel(page, w["page"])}">Week {w["number"]}</a>'
            f'<span class="week-heading-title">{w["title"]}</span>{here}</h3>')
        out.append(f'<table class="semester-table"><tbody>{"".join(rows)}</tbody></table>')

    # Deadlines that fall outside every week window -- the final project sits in
    # the exam period, after the last class session, so nothing above would show
    # it. Losing the 20% deliverable off the schedule is the worst thing this
    # page could do, hence the explicit tail section.
    covered = {a["id"] for w in DATA["weeks"] for a, _ in deadlines_in_week(w)}
    leftover = sorted(
        ((a, dt.date.fromisoformat(a["due"])) for a in DATA.get("assignments", [])
         if a["id"] not in covered),
        key=lambda pair: pair[1])
    if leftover:
        rows = "".join(
            f'<tr class="is-due"><th scope="row">{d:%a, %b} {d.day}</th>'
            f'<td><span class="label label-red">DUE</span> '
            f'<a href="{rel(page, a["page"])}">{a["name"]}</a> '
            f'<span class="due-meta">{a["weight"]} · {a["grading"]}</span></td></tr>'
            for a, d in leftover)
        out.append('<h3 class="week-heading" id="after-classes">'
                   '<span class="week-heading-title">After classes end</span></h3>')
        out.append(f'<table class="semester-table"><tbody>{rows}</tbody></table>')
    return "\n".join(out)


def week_meta(page: Path, w) -> str:
    n = w["number"]
    prev_ = next((x for x in DATA["weeks"] if x["number"] == n - 1), None)
    next_ = next((x for x in DATA["weeks"] if x["number"] == n + 1), None)
    due = deadlines_in_week(w)
    due_html = ""
    if due:
        items = "".join(
            f'<li><a href="{rel(page, a["page"])}">{a["name"]}</a> due '
            f'<strong>{d:%A, %B} {d.day}</strong></li>' for a, d in due)
        due_html = f'<ul class="week-due">{items}</ul>\n'
    bits = [f'<a href="{rel(page, "core/schedule.html")}">← Schedule</a>']
    if prev_:
        bits.append(f'<a href="{rel(page, prev_["page"])}">« Week {prev_["number"]}</a>')
    if next_:
        bits.append(f'<a href="{rel(page, next_["page"])}">Week {next_["number"]} »</a>')
    return (
        '<div class="week-meta">\n'
        f'<p class="week-dates">{fmt_sessions(w["sessions"])}</p>\n'
        f'<p class="week-unit">Part of {w["unit"]}</p>\n'
        f'<nav class="week-pager" aria-label="Week navigation">{" · ".join(bits)}</nav>\n'
        + due_html
        + "</div>"
    )


def existing_body(page: Path) -> tuple[str, str, str]:
    """(title, heading, inner html of .page-content) from a page as it stands."""
    soup = BeautifulSoup(page.read_text(encoding="utf-8"), "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else SITE_TITLE
    h1 = soup.select_one("section.hero h1")
    heading = h1.get_text(strip=True) if h1 else title.split("–")[0].strip()
    block = soup.select_one(".page-content") or soup.select_one("main")
    body = "".join(str(c) for c in block.contents).strip() if block else ""
    return title, heading, body


def build_schedule(page: Path) -> str:
    """Intro prose is preserved; the week listing is regenerated from data."""
    _, _, body = existing_body(page)
    soup = BeautifulSoup(body, "lxml")
    root = soup.body if soup.body else soup

    # Keep the intro prose, drop every existing week section. The original
    # markup wraps each <h2> in <div class="section">, so the first heading is
    # not a top-level node -- find it anywhere, then cut at its top-level
    # ancestor. Scanning only top-level nodes silently kept the old sections
    # and appended new ones, doubling the list on every build.
    first_h2 = soup.find("h2")
    cut = None
    if first_h2 is not None:
        cut = first_h2
        while cut.parent is not None and cut.parent is not root:
            cut = cut.parent

    keep = []
    for el in root.contents:
        if cut is not None and el is cut:
            break
        keep.append(str(el))
    out = ["".join(keep).strip()]
    seen = []
    for w in DATA["weeks"]:
        if w["unit"] not in seen:
            seen.append(w["unit"])
    for unit in seen:
        members = [w for w in DATA["weeks"] if w["unit"] == unit]
        span = f"Weeks {members[0]['number']}-{members[-1]['number']}" if len(members) > 1 else f"Week {members[0]['number']}"
        out.append(f"<h2>{span}: {unit}</h2>")
        lis = "\n".join(
            f'<li><a href="{rel(page, w["page"])}">Week {w["number"]}: {w["title"]}</a>'
            f' <span class="week-dates-inline">{fmt_sessions(w["sessions"])}</span></li>'
            for w in members
        )
        out.append(f'<ul class="item-list">\n{lis}\n</ul>')
    return "\n".join(out)


def write_robots_and_sitemap() -> None:
    """robots.txt and sitemap.xml, listing exactly the pages that exist.

    The site is served locally (no deploy pipeline), so absolute URLs are built
    from course.site_url in data/schedule.json -- update that one value if the
    site is ever hosted."""
    base = DATA["course"]["site_url"].rstrip("/")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    urls = "\n".join(
        f"  <url><loc>{base}/{p.relative_to(ROOT).as_posix()}</loc></url>"
        for p in all_pages() if p.name != "404.html")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n", encoding="utf-8")


# -------------------------------------------------------------------- main ---
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="treat this ISO date as today (for testing)")
    args = ap.parse_args()
    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()

    by_page = {w["page"]: w for w in DATA["weeks"]}
    generated_weeks = 0

    for page in all_pages():
        key = page.relative_to(ROOT).as_posix()
        title, heading, body = existing_body(page)

        if key == "index.html":
            soup = BeautifulSoup(body, "lxml")
            for old in soup.select(".this-week"):
                old.decompose()
            for old in soup.select("#semester-schedule, .semester-table, .week-heading"):
                old.decompose()
            rest = [c for c in (soup.body.contents if soup.body else soup.contents)]
            # keep the welcome paragraph first, then lead with the schedule
            lead, tail, seen_p = [], [], False
            for c in rest:
                if not seen_p and getattr(c, "name", None) == "p":
                    lead.append(str(c)); seen_p = True
                else:
                    tail.append(str(c))
            body = "\n".join([
                this_week_panel(page, today),
                "".join(lead).strip(),
                semester_schedule(page, today),
                "".join(tail).strip(),
            ])

        elif key == "core/schedule.html":
            body = build_schedule(page)

        elif key in by_page:
            w = by_page[key]
            md_file = ROOT / "weeks" / f"week-{w['number']:02d}.md"
            heading = f"Week {w['number']}: {w['title']}"
            if md_file.exists() and md_file.read_text(encoding="utf-8").strip():
                html = markdown.markdown(md_file.read_text(encoding="utf-8"), extensions=MD_EXT)
                body = week_meta(page, w) + "\n" + html
                generated_weeks += 1

        extra = ""
        if key == "index.html":
            c = DATA["course"]
            ld = {
                "@context": "https://schema.org", "@type": "Course",
                "name": f'{c["code"]}: {c["title"]}',
                "courseCode": c["code"],
                "description": "Hands-on study of AI software engineering: coordinating "
                               "autonomous coding agents through a professional SDLC.",
                "provider": {"@type": "CollegeOrUniversity", "name": c["institution"]},
                "instructor": {"@type": "Person", "name": "Jon Chun"},
            }
            extra = ('\n<script type="application/ld+json">'
                     + json.dumps(ld, indent=1) + "</script>")
        page.write_text(shell(page, title, heading, body, extra), encoding="utf-8")

    write_robots_and_sitemap()

    print(f"built {len(all_pages())} pages "
          f"({generated_weeks} week pages generated from Markdown, "
          f"current week = {current_week(today)['number']})")


if __name__ == "__main__":
    main()
