"""Tests for the view-time schedule enhancements (js/site.js).

The "where we are" panel is built with today's date baked in, then recomputed
in the browser from data embedded in index.html. These tests check that the
embedded data matches data/schedule.json, that every page loads the script, and
-- the one that matters -- that the browser's logic gives the same answer as the
Python build for every date across the term.
"""
import datetime as dt
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

SITE_ROOT = Path(__file__).parent.parent
DATA = json.loads((SITE_ROOT / "data" / "schedule.json").read_text(encoding="utf-8"))


def _index():
    return BeautifulSoup((SITE_ROOT / "index.html").read_text(encoding="utf-8"), "lxml")


def _build_module():
    spec = importlib.util.spec_from_file_location("build_site", SITE_ROOT / "tools" / "build_site.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestEmbeddedData:
    def test_home_page_embeds_the_schedule(self):
        node = _index().find("script", id="schedule-data")
        assert node, "index.html has no script#schedule-data"
        embedded = json.loads(node.string)
        assert [w["sessions"] for w in embedded["weeks"]] == [w["sessions"] for w in DATA["weeks"]]
        assert [a["due"] for a in embedded["assignments"]] == [a["due"] for a in DATA["assignments"]]

    def test_schedule_rows_and_headings_carry_hooks(self):
        soup = _index()
        dated = {tr["data-date"] for tr in soup.select("tr[data-date]")}
        every_session = {s for w in DATA["weeks"] for s in w["sessions"]}
        assert dated == every_session, "every session row needs a data-date"
        assert len(soup.select("h3[data-week]")) == len(DATA["weeks"])
        assert len(soup.select(".this-week-tag")) == 1

    def test_every_page_loads_the_enhancement_script(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            tags = [s for s in soup.find_all("script", src=True) if s["src"].endswith("js/site.js")]
            if not tags or not (path.parent / tags[0]["src"]).resolve().exists():
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"pages missing a resolvable js/site.js: {failures[:10]}"

    def test_week_list_is_a_disclosure_that_starts_open(self, parsed_pages):
        """Open in the markup, so the list is visible without JavaScript."""
        failures = []
        for path, _, soup in parsed_pages:
            group = soup.select_one("nav.week-nav details.week-nav-group")
            if not group or group.get("open") is None or not group.find("summary"):
                failures.append(str(path.relative_to(SITE_ROOT)))
        assert not failures, f"week nav not an open <details>: {failures[:10]}"


NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="node not installed")
class TestBrowserMatchesBuild:
    def test_where_we_are_agrees_with_python_for_every_date(self):
        mod = _build_module()
        start, end = dt.date(2026, 8, 20), dt.date(2026, 12, 25)
        dates = [(start + dt.timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]

        script = (
            "const s=require(process.argv[1]);"
            "const data=JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));"
            "const dates=JSON.parse(process.argv[3]);"
            "console.log(JSON.stringify(dates.map(d=>{const r=s.whereWeAre(data,d);"
            "return [r.week.number,r.nextSession,r.deadline?r.deadline.id:null,"
            "r.deadline?s.daysBetween(d,r.deadline.due):null];})));"
        )
        out = subprocess.run(
            [NODE, "-e", script, str(SITE_ROOT / "js" / "site.js"),
             str(SITE_ROOT / "data" / "schedule.json"), json.dumps(dates)],
            capture_output=True, text=True, check=True,
        ).stdout
        js = json.loads(out)

        mismatches = []
        for iso, got in zip(dates, js):
            day = dt.date.fromisoformat(iso)
            w = mod.current_week(day)
            nxt = next((s for s in w["sessions"] if s >= iso), None)
            dl = mod.next_deadline(day)
            want = [w["number"], nxt, dl[0]["id"] if dl else None,
                    (dl[1] - day).days if dl else None]
            if got != want:
                mismatches.append(f"{iso}: js={got} py={want}")
        assert not mismatches, f"browser and build disagree on {len(mismatches)} dates: {mismatches[:5]}"
