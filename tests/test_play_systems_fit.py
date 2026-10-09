"""PlayIDE's New system dialog on a 1080p screen and on a laptop, in a real browser: with every sector template listed,
the kernel's verdict and Create and open stay in view and clickable while the list scrolls, whichever option is chosen.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from test_play_place import _launch

ROOT = Path(__file__).resolve().parents[1]

IN_VIEW = """() => { const b = document.getElementById('systems-create').getBoundingClientRect(),
    d = document.getElementById('systems-dialog').getBoundingClientRect(), x = b.left + b.width / 2, y = b.top + b.height / 2;
    return { inside: b.top >= d.top && b.bottom <= d.bottom && b.bottom <= innerHeight && b.right <= innerWidth,
             onTop: document.elementFromPoint(x, y)?.closest('#systems-create') !== null }; }"""


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
@pytest.mark.parametrize("size", [(1920, 1080), (1280, 800)])
def test_create_and_open_stays_in_view_with_every_template_listed(size):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs" / "library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": size[0], "height": size[1]})
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click("#system-menu")
            page.click("#systems-tab-new")
            assert page.locator("#systems-templates .template").count() >= 8  # blank, a UML file and the sector templates
            for choice in ("blank", "refund-desk", "uml"):
                page.locator(f"#systems-templates input[value={choice}]").check()
                assert page.evaluate(IN_VIEW) == {"inside": True, "onTop": True}, choice
            assert page.evaluate("() => { const s = document.getElementById('systems-new-pane'); return s.scrollWidth - s.clientWidth; }") <= 0
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_create_and_open_survives_reopening_after_a_uml_file():
    """Choosing "From a UML file" moves the verdict and Create and open under it; reopening the dialog must keep them."""
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs" / "library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click("#system-menu")
            page.click("#systems-tab-new")
            page.check("#systems-templates input[value=uml]")
            page.click("#systems-close")
            page.click("#system-menu")
            page.click("#systems-tab-new")
            page.check("#systems-templates input[value=refund-desk]")
            page.wait_for_selector("#systems-create:not([disabled])", timeout=30_000)
            assert page.locator("#systems-form #systems-create").is_visible()
        finally:
            chrome.close()
