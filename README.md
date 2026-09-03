# IPHS 400: Frontiers in AI

**Kenyon College — Integrated Program for Humane Studies (IPHS) — Fall 2026**

Course website for IPHS 400, a hands-on study of AI software engineering (AI-SWE):
configuring, extending, and orchestrating AI coding agents through a professional
software development lifecycle. This repository contains the site's source, its
build tooling, and its test suite; course submissions, quizzes, and grades are
handled separately on Moodle.

- **Instructor:** Jon Chun
- **Schedule:** Tu/Th, 2:40–4:00 PM · Timberlake #5 (Evans Conference Room)

> This is a Mini-Project #1 revision of the course site. See
> [`docs/design-brief.md`](docs/design-brief.md) for the argument behind the
> changes and [What changed](#what-changed-in-this-revision) below for the summary.

## Repository Structure

```
.
├── index.html               # Home page (carries the generated "Where we are" panel)
├── 404.html
├── core/                    # Syllabus, schedule, assignments, policies, about
├── weeks/                   # week-01.html … week-15.html, plus Markdown sources
│   ├── week-01.md           #   a week with a .md source is generated from it
│   └── week-01.html         #   a week without one keeps its hand-written HTML
├── data/
│   └── schedule.json        # SINGLE SOURCE OF TRUTH: weeks, dates, units, deadlines
├── tools/
│   ├── build_site.py        # generates all 22 pages, robots.txt, sitemap.xml
│   ├── build_css.py         # assembles css/style.css
│   └── requirements.txt     # build-time only (markdown)
├── css/
│   ├── vendor/              # pre-compiled just-the-docs (light + dark), unmodified
│   ├── custom.css           # ← site-specific rules go here
│   ├── custom-dark.css      # ← dark-scheme overrides for those rules
│   ├── style.css            # GENERATED — do not edit
│   └── style-dark.css       # GENERATED — do not edit
├── js/theme.js              # colour-scheme toggle (progressive enhancement only)
├── images/favicon.svg
├── licenses/                # MIT texts for vendored work
└── tests/                   # pytest suite (45 tests)
```

The site remains **static HTML/CSS with no build step for visitors** and no deploy
pipeline. The build tools are for authors; the published artifact is plain files
that any static file server can serve.

## Local Development

No install is required to *view* the site:

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

To *rebuild* it after editing `data/schedule.json`, a `weeks/*.md` file, or
`css/custom.css`:

```bash
uv venv --python=3.12 && source .venv/bin/activate
uv pip install -r tests/requirements.txt -r tools/requirements.txt
python tools/build_css.py
python tools/build_site.py
pytest tests/ -q
```

`tools/build_site.py --date 2026-10-15` renders the site as if it were that
date, which is how the "Where we are" panel is tested.

## How the site is generated

Three things are now derived rather than typed by hand:

| What | Derived from |
|---|---|
| Week session dates, unit grouping, assignment deadlines | `data/schedule.json` |
| Week page bodies | `weeks/week-NN.md`, when that file exists |
| The whole-semester table on the home page | `data/schedule.json` |
| Page chrome, meta tags, `robots.txt`, `sitemap.xml` | `tools/build_site.py` |

**Adding a week's content:** write `weeks/week-07.md` and run
`python tools/build_site.py`. The heading, session dates, unit label, previous/next
pager, and any deadlines falling in that week are generated around it.

**Changing a date:** edit `data/schedule.json` and rebuild. The home page, schedule
page, and every affected week page update together. They cannot disagree.

Weeks with no `.md` source keep their existing hand-written HTML untouched, so the
Markdown workflow can be adopted one week at a time.

## Running the Tests

```bash
pytest tests/ -q
```

- `test_unit_html_structure.py` — DOCTYPE, title suffix, stylesheet link, header,
  footer, hero `<h1>`, no placeholder or stub content
- `test_integration_links.py` — every internal link resolves; navigation is
  identical across pages; the schedule links to all 15 week pages
- `test_e2e_site.py` — required files/directories; exact page count; every page
  reachable from `index.html`
- `test_unit_seo_a11y.py` — meta descriptions, favicon, Open Graph tags, skip
  links, `aria-current`, table header `scope`, `robots.txt`/`sitemap.xml`
- `test_unit_html_validity.py` — duplicate ids, parse errors, `<html lang>`,
  image `alt` text
- `test_unit_schedule.py` — session dates fall on class days inside the term and
  never during a break; every week and every deadline appears on the home page;
  rows within each week are in chronological order

## What changed in this revision

**Design foundation.** The site adopts the [just-the-docs](https://github.com/just-the-docs/just-the-docs)
design system, following the course-site conventions of
[just-the-class](https://github.com/kevinlin1/just-the-class). Both are MIT
licensed and both are **vendored as pre-compiled CSS rather than installed as
Jekyll themes** — installing them would have added a Ruby build pipeline,
contradicting the standalone-static-site requirement, and would have broken most
of the existing test suite, which asserts against source HTML files on disk.

Adopting a mature design system was a deliberate choice over generating a
stylesheet: it encodes years of human decisions about type scale, spacing,
tables, focus states, and print behaviour that a freshly generated stylesheet
does not have behind it.

One conflict had to be resolved against the theme. just-the-docs hides its
sidebar navigation behind a JavaScript hamburger at narrow widths. This site is
required to work with no JavaScript, so the sidebar is laid out as a single
column at every width instead, and stacks above the content on small screens.
The theme also widens the sidebar past 1064px to swallow the left gutter, which
leaves a large band of empty chrome on a wide display; it is pinned to 16.5rem.

**Colour scheme.** Both of the theme's compiled schemes are vendored. The dark
one is linked as `media="(prefers-color-scheme: dark)"`, so the right scheme is
applied with no JavaScript at all. `js/theme.js` adds a manual override, stored
per reader; the toggle button ships hidden and is revealed by that script, so a
reader without JavaScript never sees a control that does nothing. No content is
gated behind script.

**Information architecture.** The site is now schedule-first, following the
pattern established by [just-the-class](https://github.com/kevinlin1/just-the-class)
and course sites built on it. The home page leads with a "Where we are" panel
resolved against the current date, then the entire semester as one table per
week — every session and every deadline, in order, with the current week marked.
`data/schedule.json` holds that data; week pages are generated from Markdown
where a source exists.

The motivation was in the repository already: `weeks/week-template.md` and
Markdown sources for two of fifteen weeks existed, with the HTML being produced
by hand — and the commit history shows one of those conversions being reverted
with `git restore`. Doing that fourteen more times, then again whenever a reading
changes, is how a course site goes stale. The Markdown is now the source and the
HTML is a build artifact.

**Tech-spec tasks.** All 16 tasks in
[`docs/tech-spec_website-revision_v1_20260901.md`](docs/tech-spec_website-revision_v1_20260901.md)
are implemented, with two documented deviations:

- *Task 12 (print stylesheet)* and *Task 5 (skip link)* arrived partly with the
  vendored theme, which already ships both; site-specific print rules were added
  on top.
- *Task 15 (HTML validation)* uses `lxml`-based structural checks rather than
  `html5validator`, which requires a Java runtime — a heavy dependency for a repo
  whose only other requirement is pytest. The check covers the same class of bug.

**Content.** No course content was written, reworded, or deleted by this revision.
Page text was extracted verbatim from the existing pages and re-emitted. The one
exception is documented above: week pages generated from Markdown take their
heading, dates, unit, and deadline block from `data/schedule.json` instead of from
hand-written HTML.

**Removed.** `notes/subscription-zai-glm-coder.md` (unrelated to the site, per
tech-spec task 9) and the 218-line generic Python `.gitignore`, replaced with 10
lines matching what this repo actually produces.

### Known content discrepancy

The syllabus, `core/assignments.html`, and `core/schedule.html` all describe
Mini-Project 1 as *"Development Environment Configuration,"* due Friday, September 4.
The Mini-Project #1 manual distributed on 2026-09-01 describes it as *"Redesigning a
Website."* These have not been reconciled here because the correct resolution is the
instructor's to make. The deadline now lives in one place (`data/schedule.json`), so
changing it is a one-line edit.

## Generative AI Use Statement

Required by the course AI policy. This project is *about* directing AI coding
agents, so the tools were used throughout; what follows is what each did and where
the human judgment sat.

**Tools used**

- **Claude Code CLI (Sonnet 5)**, run in the repository, for the Mini-Project #1
  manual's scripted steps: stripping the Netlify/GitHub Actions configuration
  (H.0) and producing the codebase critique
  ([`docs/report_web-revision_v2_20260903.md`](docs/report_web-revision_v2_20260903.md)).
- **Claude Code (Opus 5)**, in the desktop app, for the design brief, the
  build tooling (`tools/build_site.py`, `tools/build_css.py`), the CSS custom
  layer, and the added test suites.

**What the AI did.** Wrote essentially all of the code and prose drafts: the build
scripts, the CSS custom layer, the new pytest files, and the first draft of this
README and of `docs/design-brief.md`. It also diagnosed the layout bugs described
above and verified the results in a browser.

**What I decided.** The choices the code follows were mine and are recorded in
`docs/design-brief.md`, written *before* any critique or implementation prompt was
run — deliberately, so the AI's analysis was evaluated against my criteria rather
than generic web best practices:

- To adopt an existing human-made design system rather than generate a stylesheet,
  because generated CSS converges on a recognisable house style.
- To use just-the-docs/just-the-class specifically, and to **reject** the initial
  recommendation to merely take stylistic inspiration from them.
- To vendor rather than install them, once the Jekyll route was shown to break the
  test suite and contradict Step 0.
- The schedule-first direction, over a documentation-style or editorial layout.
- To resolve the theme's JavaScript-hamburger conflict in favour of the no-JS
  constraint rather than relaxing the constraint.
- To leave the MP1 naming/deadline discrepancy for the instructor rather than
  silently "fixing" course content.

**Verification.** Every change was checked against the pytest suite (45 tests,
green at each commit) and viewed in a browser. Test failures during development
were treated as findings, not obstacles: two tests written for this revision
initially failed and revealed real defects. Pages whose first paragraph was too
short to serve as a search snippet. Week pages whose active navigation link lives
in the week nav rather than the section nav. Schedule rows sorted by their markup
rather than by date, which put "Fri, Sep 4" above "Thu, Sep 3". And — the one
that mattered most — the Final Project deadline, 20% of the course grade, was
silently absent from the schedule because it falls in the exam period, after the
last class session, so no week window covered it. Each of those now has a
regression test.

## Attribution and Licenses

- [just-the-docs](https://github.com/just-the-docs/just-the-docs) — © 2016 Patrick
  Marsceill, MIT. Vendored, unmodified, at `css/vendor/just-the-docs.css`.
  Full text: [`licenses/just-the-docs-LICENSE.txt`](licenses/just-the-docs-LICENSE.txt).
- [just-the-class](https://github.com/kevinlin1/just-the-class) — © 2020 Kevin Lin,
  MIT. Structural conventions for course sites.
  Full text: [`licenses/just-the-class-LICENSE.txt`](licenses/just-the-class-LICENSE.txt).

## Content Source and Provenance

All course content (syllabus text, schedule, assignments, policies) is sourced from
the official Fall 2026 syllabus.

## License

See [LICENSE](LICENSE).
