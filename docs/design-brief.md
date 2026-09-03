# Design Brief — IPHS 400 Course Site Revision

**Author:** Calvin Deka
**Date:** 2026-09-03
**Status:** Written *before* running any AI critique or implementation prompt.

This document exists so that the critique, tech-spec, and implementation for this
project are evaluated against *this course's actual needs*, rather than against
generic web best practices. It is the input to every subsequent prompt.

---

## 1. Who actually uses this site

Roughly 15 students in an upper-division seminar that meets Tu/Th 2:40–4:00 in
Timberlake #5, plus the instructor. That is the entire audience.

It is **not** a recruiting site. Nobody arriving here needs to be persuaded the
course is interesting — they are already enrolled. Every pixel spent on
persuasion is a pixel not spent on information.

## 2. The three jobs this site is hired to do

In rough order of frequency:

1. **"What do I have to do before the next class?"** — readings, assignment
   deadlines, quiz topics.
2. **"Where is the spec for the thing I'm building?"** — mini-project
   requirements, rubrics, submission mechanics.
3. **"What are the rules?"** — grading weights, attendance, late work, AI-use
   policy.

Job 1 dominates and is *time-sensitive*: the answer changes every week. The
current site answers it worst, because the schedule is a flat table with no
indication of where in the semester you are.

## 3. Non-goals

- Marketing copy, hero imagery, or anything that persuades rather than informs.
- Public SEO reach as a primary aim. (SEO tasks in the tech-spec are still worth
  doing — they are cheap and correct — but they are hygiene, not the point.)
- Visual novelty for its own sake.

## 4. Constraints (chosen, not inherited)

| Constraint | Rationale |
|---|---|
| **No build step.** Static HTML + CSS, served by `python3 -m http.server`. | Required by Mini-Project #1 Step 0. Also means any classmate or the instructor can run it with zero toolchain setup. |
| **The existing pytest suite stays green at every commit.** | Required by the manual's implementation loop. It is also the only automated definition of "not broken" this repo has. |
| **No JavaScript required to read any page.** | Content must work if JS fails. JS may *enhance* (search, nav toggle) but never gate content. |
| **Readable on a phone in a hallway five minutes before class.** | This is the realistic worst-case usage context for Job 1. |
| **Prints correctly.** | The syllabus is a document people print for advising and financial aid. |

## 5. Visual foundation: just-the-docs, via just-the-class conventions

The site adopts the **just-the-docs** design system (MIT) as its visual base,
following the structural conventions of **just-the-class** (MIT) — a Jekyll
template built specifically for university course websites. Both are vendored as
pre-compiled CSS and re-implemented as static HTML, not installed as Jekyll themes.

**Why adopt an existing system rather than design one:**
A mature, widely-used design system encodes years of human decisions about type
scale, spacing rhythm, table styling, focus states, and print behavior. Generating
a stylesheet from scratch with an AI agent produces something that *looks*
designed but has no reasoning behind it, and converges on a recognizable generic
house style. Standing on a human-designed foundation is both more honest and
better-looking.

**Why just-the-class specifically:** it is the established convention for course
sites. Its structure — `_modules/` for weeks, `_schedules/` for the recurring
timetable, labels for due dates — is a course-site information architecture that
many universities already run on. Notably, it ships *no meaningful CSS of its own*:
its live demo loads the identical `just-the-docs-default.css` this project
vendors. What it contributes is architecture, not appearance.

**Why vendored, not installed:**
Consuming either as a Jekyll theme introduces a Ruby build pipeline — directly
contradicting Step 0's "no deploy pipeline, standalone static site" requirement —
and breaks most of the existing pytest suite, which asserts against source HTML
files on disk. Using the published compiled CSS keeps the site static, keeps the
tests meaningful, and keeps runtime dependencies at zero.

**Obligations:** the MIT license notices for both projects ship with the vendored
assets and are credited in the README. Attribution is a requirement, not a courtesy.

## 6. The differentiator: generate the week pages from their Markdown sources

The single highest-value change this project can make is not visual.

The repository currently contains `weeks/week-template.md`, `weeks/week-01.md`, and
`weeks/week-02.md` — Markdown sources for two of fifteen week pages. The recent
commit history shows those pages being converted to HTML by hand, one at a time
("rebuild page body from week-02.md outline"), including one revision that had to
be reverted with `git restore`.

In other words: the instructor has already chosen a source-of-truth pattern and is
currently executing it manually, at a cost of one error-prone edit per week for
fourteen weeks.

**So the deliverable is the tool that does it.** A small Python generator that
renders `weeks/week-NN.md` into `weeks/week-NN.html` against a single shared
template, plus the same treatment for the schedule data that the home page,
schedule page, and week pages all currently duplicate by hand.

This is the right bet for four reasons:

1. **It solves a problem the maintainer demonstrably has right now**, rather than
   one inferred from best-practice checklists.
2. **It removes an entire class of bug.** Today the home page, schedule page, and
   week pages can silently disagree. After this, they cannot.
3. **It keeps every existing test meaningful.** The generator writes the same 22
   HTML files on disk that the pytest suite already asserts against — nothing in
   the test contract changes.
4. **It is written in Python**, matching the repository's existing test toolchain
   (`uv` + pytest). No new runtime, no new language, nothing extra to install.

Layered on top, the site is restructured schedule-first: the schedule becomes the
front door rather than a page you navigate to, and the current week is computed
from the date rather than hardcoded — so the answer to "what do I need to do
before Thursday" requires no scanning and no date arithmetic.

**Why this wins the stated criterion:** the instructor has said the strongest
version of this project may become the real course site. The deciding question is
therefore not "which looks best in a screenshot" but *"which would I actually run
my course on for fourteen weeks?"* The syllabus itself warns that readings and
tools will be revised continuously. A site whose weeks regenerate from Markdown is
one that survives that. Fifteen hand-maintained HTML pages is one that goes stale
by Week 5 — and the commit history suggests that pressure has already started.

## 7. How this will be evaluated

Before/after evidence, not description:

- **Lighthouse** scores (performance, accessibility, best practices, SEO)
  captured on the original site and on the revision.
- **All 16 tech-spec tasks** implemented — these are the floor, not the ceiling.
- **Full pytest suite green**, with new tests added for new invariants.
- **Manual pass** on every page in Chrome, plus keyboard-only navigation and
  print preview.

## 8. Anti-slop checklist (run before submitting)

Delete on sight:

- Gradient hero sections; decorative purple/indigo; glassmorphism
- Emoji used as interface icons
- Three-card "feature" grids
- A dark-mode toggle that serves no stated purpose
- Testimonials, calls-to-action, or any section that persuades rather than informs
- Copy containing: "empower", "seamless", "dive into", "unlock", "in today's
  rapidly evolving landscape", or a subheading that restates its heading
- Any block on any page that conveys no information a student needs

**Governing rule:** every block on every page must carry information a student
needs. Filler that merely *looks* like structure is the primary tell of
machine-generated work, and it is the first thing to cut.

---

## Note on Kenyon purple

Kenyon's institutional color is purple, which is also the single most common tell
of AI-generated design. Using purple here is defensible *only* if it is Kenyon's
actual brand value, sampled from official College materials, and documented as an
institutional choice. Sampled and cited, it is an argument. Invented, it is a tell.
