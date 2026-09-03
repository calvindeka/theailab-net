#!/usr/bin/env python3
"""Assemble css/style.css from the vendored theme plus this site's own layer.

    css/vendor/just-the-docs.css   pre-compiled upstream distribution, unmodified
    css/custom.css                 rules written for this site
    -> css/style.css               the single stylesheet every page links to

Keeping the two sources separate means upstream can be re-vendored by replacing
one file, without hand-merging site rules back in. `css/style.css` is generated;
edit `css/custom.css` instead.

Run from the repo root:  python tools/build_css.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "css"

HEADER = """/*! ============================================================================
 *  IPHS 400: Frontiers in AI — course site stylesheet
 *  GENERATED FILE — do not edit. Edit css/custom.css, then run:
 *      python tools/build_css.py
 *  ---------------------------------------------------------------------------
 *  Visual foundation: just-the-docs (compiled distribution, vendored)
 *      https://github.com/just-the-docs/just-the-docs
 *      Copyright (c) 2016 Patrick Marsceill — MIT License
 *
 *  Course-site structural conventions: just-the-class
 *      https://github.com/kevinlin1/just-the-class
 *      Copyright (c) 2020 Kevin Lin — MIT License
 *
 *  Both are consumed as pre-compiled CSS rather than installed as Jekyll
 *  themes, so this site stays a standalone static site with no build step for
 *  visitors (see docs/design-brief.md section 5). Full license texts: licenses/
 *  ========================================================================= */

"""


def main() -> None:
    """Builds two stylesheets.

    style.css       light scheme + this site's layer; always loaded.
    style-dark.css  the theme's dark scheme + dark colour overrides; loaded
                    only under `media="(prefers-color-scheme: dark)"`, so a
                    reader with no JavaScript still gets whichever scheme their
                    operating system asks for.
    """
    read = lambda *parts: (CSS.joinpath(*parts)).read_text(encoding="utf-8")
    custom = read("custom.css")

    (CSS / "style.css").write_text(
        HEADER + read("vendor", "just-the-docs.css") + "\n" + custom, encoding="utf-8")
    (CSS / "style-dark.css").write_text(
        HEADER + read("vendor", "just-the-docs-dark.css") + "\n" + custom
        + "\n" + read("custom-dark.css"), encoding="utf-8")

    for name in ("style.css", "style-dark.css"):
        print(f"built css/{name} ({(CSS / name).stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
