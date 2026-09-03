"""Structural validity checks (tech-spec task 15).

The spec suggested `html5validator`, which wraps the Nu HTML Checker and
therefore needs a Java runtime. That is a heavy dependency for a course repo
whose only other requirement is pytest, so this covers the same class of bug --
duplicate ids, unclosed or mis-nested elements, missing required attributes --
using the lxml parser already in tests/requirements.txt.
"""
from collections import Counter
from pathlib import Path

from lxml import etree

SITE_ROOT = Path(__file__).parent.parent


def _rel(p):
    return str(p.relative_to(SITE_ROOT))


class TestValidity:
    def test_no_duplicate_ids(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            ids = [t["id"] for t in soup.find_all(attrs={"id": True})]
            dupes = [i for i, n in Counter(ids).items() if n > 1]
            if dupes:
                failures.append(f"{_rel(path)}: {dupes}")
        assert not failures, f"Duplicate id attributes: {failures[:15]}"

    def test_html_parses_without_recoverable_errors(self, parsed_pages):
        """lxml records a recovery log for mis-nested or unclosed tags."""
        failures = []
        for path, text, _ in parsed_pages:
            parser = etree.HTMLParser(recover=True)
            etree.fromstring(text, parser)
            serious = [
                e for e in parser.error_log
                # htmlParseEntityRef / unknown-entity noise is not a nesting bug
                if "htmlParseEntityRef" not in e.message
            ]
            if serious:
                failures.append(f"{_rel(path)}: {serious[0].message}")
        assert not failures, f"HTML parse errors: {failures[:10]}"

    def test_every_page_declares_a_language(self, parsed_pages):
        failures = [
            _rel(p) for p, _, s in parsed_pages
            if not (s.find("html") and s.find("html").get("lang"))
        ]
        assert not failures, f"Pages without <html lang>: {failures[:15]}"

    def test_images_have_alt_text(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            for img in soup.find_all("img"):
                if img.get("alt") is None:
                    failures.append(f"{_rel(path)}: {img.get('src', '?')}")
        assert not failures, f"Images without alt attributes: {failures[:15]}"
