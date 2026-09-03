"""Tests for the generated schedule: data/schedule.json is the single source of
truth, so these lock in that what is rendered actually matches it."""
import datetime as dt
import json
from pathlib import Path

from bs4 import BeautifulSoup

SITE_ROOT = Path(__file__).parent.parent
DATA = json.loads((SITE_ROOT / "data" / "schedule.json").read_text(encoding="utf-8"))


def _index():
    return BeautifulSoup((SITE_ROOT / "index.html").read_text(encoding="utf-8"), "lxml")


class TestScheduleData:
    def test_every_week_points_at_a_page_that_exists(self):
        missing = [w["page"] for w in DATA["weeks"] if not (SITE_ROOT / w["page"]).exists()]
        assert not missing, f"schedule.json references missing pages: {missing}"

    def test_sessions_fall_on_class_days_within_the_term(self):
        first = dt.date.fromisoformat(DATA["calendar"]["first_class"])
        last = dt.date.fromisoformat(DATA["calendar"]["last_class"])
        bad = []
        for w in DATA["weeks"]:
            for s in w["sessions"]:
                d = dt.date.fromisoformat(s)
                if not (first <= d <= last):
                    bad.append(f"week {w['number']}: {s} outside term")
                if d.weekday() not in (1, 3):          # course meets Tu/Th
                    bad.append(f"week {w['number']}: {s} is a {d:%A}")
        assert not bad, f"Bad session dates: {bad}"

    def test_no_session_falls_during_a_break(self):
        breaks = set()
        for a, b in (DATA["calendar"]["october_break"],
                     DATA["calendar"]["thanksgiving_recess"]):
            start, end = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
            while start <= end:
                breaks.add(start); start += dt.timedelta(days=1)
        hits = [s for w in DATA["weeks"] for s in w["sessions"]
                if dt.date.fromisoformat(s) in breaks]
        assert not hits, f"Sessions scheduled during a break: {hits}"


class TestRenderedSchedule:
    def test_home_page_lists_every_week(self):
        soup = _index()
        for w in DATA["weeks"]:
            assert soup.find(id=f"week-{w['number']:02d}"), f"week {w['number']} missing from home page"

    def test_rows_within_each_week_are_in_chronological_order(self):
        """Regression: rows were once sorted by their markup, which ordered them
        by weekday name and put 'Fri, Sep 4' above 'Thu, Sep 3'."""
        soup = _index()
        failures = []
        for w in DATA["weeks"]:
            table = soup.find(id=f"week-{w['number']:02d}").find_next("table")
            labels = [tr.th.get_text(strip=True) for tr in table.find_all("tr")]
            year = dt.date.fromisoformat(w["sessions"][0]).year
            dates = [dt.datetime.strptime(f"{l}, {year}", "%a, %b %d, %Y").date() for l in labels]
            if dates != sorted(dates):
                failures.append(f"week {w['number']}: {labels}")
        assert not failures, f"Schedule rows out of order: {failures}"

    def test_every_assignment_deadline_appears_on_the_home_page(self):
        text = (SITE_ROOT / "index.html").read_text(encoding="utf-8")
        missing = [a["name"] for a in DATA["assignments"] if a["name"] not in text]
        assert not missing, f"Deadlines missing from the schedule: {missing}"

    def test_home_page_has_a_current_week_panel(self):
        soup = _index()
        assert soup.select_one(".this-week"), "home page is missing the 'where we are' panel"
        assert soup.select_one(".this-week h2 a"), "panel does not link to the current week"
