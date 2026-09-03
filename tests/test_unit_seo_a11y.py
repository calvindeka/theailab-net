"""Unit tests for the SEO and accessibility invariants added during the MP1
revision (tech-spec tasks 1-5, 7, 10).

These assert properties of the *generated* site, so they fail loudly if
tools/build_site.py regresses or if a page is hand-edited out of band.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

SITE_ROOT = Path(__file__).parent.parent


def _rel(p):
    return str(p.relative_to(SITE_ROOT))


class TestMetadata:
    def test_every_page_has_a_meaningful_meta_description(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            tag = soup.find("meta", attrs={"name": "description"})
            content = (tag.get("content") or "").strip() if tag else ""
            if len(content) < 50:
                failures.append(f"{_rel(path)}: {len(content)} chars")
        assert not failures, f"Weak or missing meta descriptions: {failures[:15]}"

    def test_every_page_has_a_favicon_link(self, parsed_pages):
        failures = [
            _rel(p) for p, _, s in parsed_pages
            if not s.find("link", attrs={"rel": lambda v: v and "icon" in v})
        ]
        assert not failures, f"Pages without a favicon link: {failures[:15]}"

    def test_favicon_file_exists(self):
        assert (SITE_ROOT / "images" / "favicon.svg").exists()

    def test_every_page_has_open_graph_tags(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            for prop in ("og:title", "og:description", "og:type"):
                if not soup.find("meta", attrs={"property": prop}):
                    failures.append(f"{_rel(path)}: missing {prop}")
        assert not failures, f"Missing Open Graph tags: {failures[:15]}"


class TestAccessibility:
    def test_every_page_has_a_skip_link_targeting_main(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            link = soup.select_one('a.skip-to-main[href="#main-content"]')
            target = soup.select_one("main#main-content")
            if not link or not target:
                failures.append(_rel(path))
        assert not failures, f"Pages without a working skip link: {failures[:15]}"

    def test_active_nav_link_is_marked_aria_current(self, parsed_pages):
        """Exactly one sidebar link per page carries aria-current="page".

        Week pages are reached from the week nav rather than the section nav,
        so the assertion spans the whole sidebar. 404.html is excluded: it has
        no corresponding nav entry anywhere.
        """
        failures = []
        for path, _, soup in parsed_pages:
            if path.name == "404.html":
                continue
            sidebar = soup.select_one(".side-bar")
            marked = sidebar.select('a[aria-current="page"]') if sidebar else []
            if len(marked) != 1:
                failures.append(f"{_rel(path)}: {len(marked)} marked")
        assert not failures, f"Pages without exactly one aria-current nav link: {failures[:15]}"

    def test_every_table_header_has_a_scope(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            for th in soup.find_all("th"):
                if th.get("scope") not in ("col", "row"):
                    failures.append(f"{_rel(path)}: <th>{th.get_text(strip=True)[:25]}")
        assert not failures, f"Table headers without scope: {failures[:15]}"


class TestCrawlFiles:
    def test_robots_txt_exists_and_points_at_the_sitemap(self):
        robots = (SITE_ROOT / "robots.txt")
        assert robots.exists(), "robots.txt missing"
        assert "Sitemap:" in robots.read_text(encoding="utf-8")

    def test_sitemap_is_well_formed_and_lists_every_real_page(self, all_html_files):
        path = SITE_ROOT / "sitemap.xml"
        assert path.exists(), "sitemap.xml missing"
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        locs = [u.find(f"{ns}loc").text for u in root.findall(f"{ns}url")]
        expected = len([f for f in all_html_files if f.name != "404.html"])
        assert len(locs) == expected, f"sitemap lists {len(locs)}, site has {expected} indexable pages"
