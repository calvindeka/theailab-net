# theailab-net Website Critique v2 — Evaluated Against the Design Brief

**Date:** 2026-09-03
**Scope:** Full repository, evaluated against `docs/design-brief.md` (2026-09-03) — the three
jobs in §2, the constraints in §4, and the maintenance problem in §6 — not against generic
web best practices.
**Relationship to prior docs:** `report_web-revision_v1_20260901.md` and
`tech-spec_website-revision_v1_20260901.md` were produced by a generic "critique this codebase"
pass, before the brief existed. This document re-evaluates the same codebase against the brief's
actual stated criteria, and closes with a task-by-task read of what the v1 tech-spec's 16 tasks
mean once the brief's architecture is adopted.

---

## 1. Summary

The v1 critique was accurate about what it looked at — missing meta tags, no skip link, an
inconsistent `.gitignore` — but it evaluated the site the way a generic SEO/accessibility audit
tool would: 22 independent HTML files, each missing the same handful of things. The brief
reframes the actual problem: this is *one template, copy-pasted by hand into 22 files*, and the
real defect isn't any individual missing attribute — it's that there is no template. Fixing
`aria-current` across 22 files by hand is treating a symptom the same way the missing attribute
itself is a symptom.

Judged against the brief's three jobs, the site's worst failure is Job 1 ("what do I have to do
before the next class?"), and it's an information-architecture failure, not a metadata gap — no
tech-spec task touches it. Judged against the brief's constraints, the site currently *passes*
four of five outright (no build step, tests green, no JS anywhere, responsive CSS) and *fails*
the fifth (print) in a way the tech-spec under-prioritizes relative to what the brief says that
constraint is for. Judged against the maintenance problem in §6, the evidence for it is already
sitting in the repo and in the commit log — this section confirms it directly rather than taking
the brief's word for it.

---

## 2. Against the three jobs (§2)

### Job 1 — "What do I have to do before the next class?" (dominant, time-sensitive)

This is the job the site currently answers worst, and inspecting the actual pages confirms the
brief's claim rather than just repeating it.

- `core/schedule.html` is not a flat table — it's a set of `<h2>`-grouped `<ul>` link lists, one
  group per mini-project (Weeks 1–2, 3–5, 6–9, 10–13, ...). That's better than a flat table, but
  it still has **zero indication of where "now" is** in the semester. Nothing distinguishes a
  week that already happened from the current week from a week three months out. A student
  checking this page in class on any given Tuesday has to already know it's Week 6 before the
  page becomes useful.
- The actual answer to "what do I have to do before Thursday" — readings, deadlines, quiz
  topics — lives on the individual `weeks/week-NN.html` page, one click deeper, and the schedule
  page gives no hint about which of those 15 pages is relevant right now.
- `index.html`, the front door, doesn't mention the schedule or the current week at all — its
  "Quick Links" section is five links to the core pages in a fixed, non-time-aware order (see
  `index.html:34-41`). A returning student gets no orientation cue from the page they're most
  likely to land on.
- Confirmed duplication that makes this worse, not just inconvenient: `core/schedule.html:29`
  states "Week 1 has a single session (Thursday) ... Week 7 has a single session (Tuesday)
  because of October Break" as prose, and `weeks/week-01.html:29` restates the same fact about
  Week 1 independently, in different words. These are two hand-written descriptions of the same
  calendar fact. Nothing enforces that they agree, and nothing would catch it if a future edit to
  one left the other stale.

None of the 16 tech-spec tasks touch this. It is entirely orthogonal to the v1 tech-spec's
metadata/accessibility/hygiene scope — which is itself evidence that a "generic best practices"
audit is structurally incapable of surfacing this class of problem, because it inspects each page
independently rather than asking what the page is *for*.

### Job 2 — "Where is the spec for the thing I'm building?"

`core/assignments.html` exists and is reachable from every page's nav. This job is served
adequately by the current site; it's a lookup problem and the site is a flat enough hierarchy
(one click from anywhere) that it doesn't need restructuring. The brief doesn't ask for anything
here, and nothing in this review found a gap worth flagging under this job specifically — the
weaknesses that do exist (missing `scope` on rubric tables, no last-updated stamp) are covered
under Job 1/3 and the constraints below rather than being specific to spec-lookup.

### Job 3 — "What are the rules?"

`core/policies.html` covers grading weights, attendance, late work, and AI-use policy in one
place, one click from nav — also adequately served. The only friction specific to this job is
the same one affecting Job 1 and 2: no visible "last updated" signal (tech-spec Task 11), which
matters most here because policy pages are exactly the kind of content a student needs to trust is
current before relying on it (e.g., a late-work grace period that changed mid-semester).

**Net read on §2:** the site is one job away from doing its job. Jobs 2 and 3 are single-page
lookups the current flat structure already handles. Job 1 is the one that's time-sensitive,
dominant, and structurally unserved — which is exactly what §6's differentiator (schedule-first
restructuring, computed current week) targets. The brief's prioritization is correct on the
evidence.

---

## 3. Against the constraints (§4)

| Constraint | Status today | Evidence |
|---|---|---|
| No build step | **Pass** | Site is already plain HTML/CSS served by `python3 -m http.server`; no bundler, no framework, confirmed by `README.md` and repo contents. |
| pytest suite stays green | **Pass** | 25/25 tests passing per the v1 review; not independently re-run here, but nothing in this critique proposes a change that would touch test-covered behavior. |
| No JS required to read any page | **Pass, trivially** | There is no JavaScript anywhere in the repository — not "JS that degrades gracefully," but a total absence. This isn't a designed enhancement layer that fails safe; it's zero JS, full stop. Worth naming explicitly since the brief phrases it as "JS may enhance... but never gate," implying JS exists in some enhancing role — it currently doesn't. |
| Readable on a phone in a hallway | **Likely pass, unverified here** | v1 review noted "responsive breakpoints are sensible"; this critique did not re-test at mobile viewport widths. Flagging as the one constraint in this table not independently re-checked. |
| Prints correctly | **Fail** | No `@media print` block exists anywhere in `css/style.css`. Printing `core/syllabus.html` today includes the full header, 5-link nav, and the decorative `.hero h1::before` underline — all irrelevant on paper. |

The print failure is the one item in this table that deserves a different priority than the v1
tech-spec gives it. Tech-spec Task 12 ("Add print stylesheet") is ranked **Low**, grouped with
footer links and JSON-LD structured data. But the brief lists "prints correctly" in §4 as a
**constraint** — same tier as "no build step" and "no JS required" — with a specific, load-bearing
justification: *"The syllabus is a document people print for advising and financial aid."* That's
not a nice-to-have; a student who can't get a clean printout of the syllabus for a financial-aid
office has a real problem the site caused. Under the brief's own criteria, Task 12 belongs in the
High tier, not Low — this is a criticality mismatch the v1 tech-spec should not carry forward as-is.

---

## 4. Against the maintenance problem (§6)

The brief's central claim is checkable, not just assertable, and it checks out:

- `weeks/week-template.md`, `weeks/week-01.md`, and `weeks/week-02.md` exist in the repo right
  now, alongside all 15 `.html` week pages — confirmed by directory listing. Markdown sources
  exist for 2 of 15 weeks; the other 13 have no source-of-truth file, only hand-authored HTML.
- The commit log corroborates the brief's account of this being executed manually and imperfectly:
  `e293e85 content(week-02): rebuild page body from week-02.md outline`, immediately preceded by
  `d03fa7f Restore ./weeks/week-01.html to 4184aa181` — a revert. That sequence is a hand-edit
  that went wrong, restored, and redone — precisely the "error-prone, one at a time" pattern §6
  describes, not a hypothetical risk.
- The schedule-data duplication the brief cites is real and demonstrated above under Job 1: the
  same calendar fact (Week 1's single-session Thursday start) is independently prose-authored in
  both `core/schedule.html` and `weeks/week-01.html`. Fourteen more weeks of this pattern, hand-
  maintained, is the failure mode §6 predicts.

This critique's addition to §6, rather than just confirming it: **the differentiator as written
only explicitly commits to generating the 15 week pages and single-sourcing schedule data.** It
does not commit to bringing `core/*.html` (syllabus, schedule, assignments, policies, about),
`index.html`, or `404.html` under the same generated-template discipline — 7 of the 22 pages.
Section 5's adoption of just-the-docs/just-the-class as a shared visual and structural
convention implies a common header/nav/footer partial across *all* pages, but §6's concrete
deliverable ("a small Python generator that renders `weeks/week-NN.md` into
`weeks/week-NN.html`... plus the same treatment for the schedule data") only names weeks and
schedule data. If the shared chrome (nav, skip link, footer) for the other 7 pages isn't also
driven from one template file — generated or literally shared via include — those 7 pages keep
exactly the duplication risk §6 diagnoses, just with a nicer stylesheet on top. This is worth
resolving explicitly before implementation starts, not discovering after: does "shared template"
mean *all 22 pages render through one chrome-generating function*, or only the 15 week pages?
The redundancy analysis below assumes the narrower reading (weeks-only) is what gets built unless
the brief is amended, and flags each task's status accordingly.

---

## 5. Tech-spec task disposition under the brief's approach

Read against the brief's actual architecture (Python generator for `weeks/*.html` + single-
sourced schedule data + just-the-docs/class chrome, scope as discussed in §4 above), the v1
tech-spec's 16 tasks split three ways: tasks whose *mechanism* the generator absorbs (they stop
being 22-file edits and become one template edit, for the 15 week pages at minimum), tasks that
are genuinely superseded by a better version of themselves, and tasks with no relationship to the
generator at all.

| # | Task | Disposition | Why |
|---|---|---|---|
| 1 | Meta descriptions | **Untouched** | Content, not mechanism — each page's description still has to be individually written regardless of how the HTML gets assembled. Insertion point becomes a template slot (or an md frontmatter field) for week pages, but the task itself survives. |
| 2 | Favicon | **Untouched** | Fully orthogonal to the generator; one asset + one template line. |
| 3 | `robots.txt` / `sitemap.xml` | **Untouched, mildly synergistic** | Still a required standalone task, but a generator that knows the full page list can emit `sitemap.xml` as a build output instead of a hand-maintained file — worth doing that way once the generator exists, but the task doesn't disappear. |
| 4 | `aria-current="page"` on nav | **Redundant as a 22-page task, for weeks/ (15 pages) at minimum** | Once week pages render through one template function, this is a single conditional in the template, not a per-file edit. Whether it also collapses for the other 7 pages depends on the scope question raised in §4 above. |
| 5 | Skip-link + `id="main-content"` | **Same as Task 4** | Template-level for weeks/; scope-dependent for the other 7. |
| 6 | Normalize `core/` internal link style | **Not resolved by the brief as written** | This task is specifically about `core/*.html` (syllabus, schedule vs. assignments, policies, about) — the 7 pages the brief's §6 deliverable does not explicitly commit to generating. Unless the scope question in §4 is answered in favor of the wider reading, this inconsistency survives the brief's implementation untouched and still needs its own fix. |
| 7 | `scope` on table headers | **Split** | The schedule table (if driven by the single-sourced schedule data) inherits correct `scope` from wherever that data gets rendered. The ~12 other `<th>` elements in `syllabus.html`'s hand-written rubric/grading tables are untouched — same scope-dependency as Task 6. |
| 8 | Trim `.gitignore` | **Untouched, slightly less misleading than v1 found it** | v1 flagged the generic Python `.gitignore` as misleading because "the only Python in the repo is `tests/`." Once the brief's generator ships, there genuinely will be a Python build script — the file should still be trimmed to match actual usage, but the specific "misleading" framing in the v1 finding weakens. |
| 9 | Relocate stray `notes/` dir | **Untouched** | Pure housekeeping, unrelated to page architecture. |
| 10 | OG/Twitter Card metadata | **Untouched as a requirement, same mechanism note as Task 1** | Reuses Task 1's descriptions either way; insertion point templated for weeks/, manual for the other 7 pending the scope question. |
| 11 | "Last updated" indicator | **Superseded, not just absorbed** | This is the clearest case in the list. Tech-spec Task 11 explicitly punts on automation ("no automation is required for this task") and asks for a manually-typed date — which is itself exactly the kind of hand-maintained fact §6 warns will drift, on the very feature meant to signal drift. Once a generator exists, this should be derived automatically (file mtime, or a frontmatter field the generator validates against the file's own last edit) rather than implemented as originally specified. Don't implement Task 11 as written; implement its goal as a generator feature. |
| 12 | Print stylesheet | **Untouched as a task, mis-ranked in v1** | Not affected by the generator either way (it's pure CSS), but see §3 above — this should move to High criticality, not stay Low, because the brief names it a hard constraint with a concrete real-world consequence (financial aid / advising paperwork), not a polish item. |
| 13 | Footer links | **Same pattern as Task 4/5** | Template-level for weeks/, scope-dependent for the other 7. |
| 14 | Bare-`<code>` GitHub URL → link | **Untouched** | This is inline prose inside `syllabus.html` and `about.html` — both `core/` pages outside the generator's committed scope, and even if they were templated, this is content authoring, not chrome. No architecture change removes the need to just fix these two links. |
| 15 | HTML5 validator test | **Untouched, more valuable, not less** | If anything this task's justification gets stronger: a generator emitting 15 files from one template is exactly the kind of change where a loop bug silently produces a duplicate `id` or malformed tag across every output file at once. This should stay in the High/near-High tier and specifically run against the generator's output, not just the pre-existing hand-written files. |
| 16 | JSON-LD structured data | **Untouched** | Independent of architecture, and the brief's own §3 already calls SEO work "hygiene, not the point" — this task's low ranking is correct and doesn't move. |

**Net count:** of 16 tasks, **2 are fully absorbed/redundant as standalone tasks for at least the
15 week pages** (4, 5), **2 more follow the same pattern but only if the core/-pages scope
question is resolved toward the wider reading** (13, and half of 7), **1 is superseded by a
better version of itself and should not be implemented as literally specified** (11), and
**11 are genuinely untouched by the brief's architecture** (1, 2, 3, 6, 8, 9, 10, 12, 14, 15, 16)
— several of which (6, part of 7, 14) are untouched specifically *because* they live in the 7
pages the brief's differentiator doesn't commit to generating, which is itself the report's main
finding under §6.

---

## 6. What this changes about priority order, relative to v1

1. Resolve the scope question raised in §4 first: does the shared-template treatment cover all
   22 pages or only the 15 week pages? This single decision determines the disposition of Tasks
   4, 5, 6, 7, 10, and 13 above and should be settled before task-by-task implementation starts,
   not discovered mid-implementation.
2. Build the week-page generator and single-sourced schedule data (§6) before doing any of the
   16 tasks that touch weeks/ pages individually — implementing Task 4 by hand across 15 files
   and then replacing those files with generator output a week later is wasted work.
3. Re-rank Task 12 (print stylesheet) into the High tier per §3's constraint reading.
4. Implement the goal of Task 11 (last-updated signal) as a generator feature, not as originally
   specified — skip the "decide whether to automate" step in the original task; the brief already
   answers it.
5. Everything else in the tech-spec proceeds as originally ranked; the brief doesn't give reason
   to change Tasks 1, 2, 3, 8, 9, 14, 15, or 16.
