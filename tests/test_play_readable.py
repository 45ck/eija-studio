"""PlayIDE on a laptop screen, in a real browser: with the side bar and the chat open, the state machine is drawn large
enough to read rather than shrunk to fit one long row, a previewed change ("Unsaved changes" in the title bar)
never makes the page wider than the window, which would scroll it sideways, every diagram tab in the strip is shown
whole whichever tab is open, and a screen's fields show their whole label.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from test_play_place import _launch

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
@pytest.mark.parametrize("pack", ["library-loan", "excursion", "eija-review-slice"])
def test_the_state_machine_reads_on_a_laptop_and_the_page_never_scrolls_sideways(pack):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs" / pack) as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1280, "height": 800})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            # 0.6 keeps a 14 px state name at 8 px or more; laid out in one long row Library loan was drawn at 0.33.
            assert page.evaluate("() => window.PlayIDE.diagram('states').view.scale") >= 0.6
            # The chat's example, previewed: the title bar gains "Unsaved changes", and the page still fits the window.
            page.fill("#chat-input", page.text_content("#chat-example"))
            page.click("#chat-send")
            preview = page.get_by_role("button", name="Preview on the diagram").first
            preview.wait_for(timeout=30_000)
            preview.click()
            page.wait_for_selector("#plan-banner:not([hidden])")
            page.wait_for_selector("#system-saved[data-dirty=true]")
            assert page.evaluate("() => document.documentElement.scrollWidth - innerWidth") <= 0
            assert errors == []
        finally:
            chrome.close()


WHOLE_TABS = """() => { const s = document.querySelector('.stage-tools .tabs').getBoundingClientRect();
    return [...document.querySelectorAll('.stage-tools .tabs [role=tab]')].filter((t) => t.offsetParent && getComputedStyle(t).opacity !== '0')
        .filter((t) => { const r = t.getBoundingClientRect();  // partly in view: scrolled wholly out of it is fine
            return r.right > s.left + 0.5 && r.left < s.right - 0.5 && (r.left < s.left - 0.5 || r.right > s.right + 0.5); })
        .map((t) => t.textContent.trim()); }"""


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_tabs_are_whole_and_screen_fields_show_their_labels_on_a_laptop():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1280, "height": 800})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            # A tab cut off mid-word ("Use") reads as another tab: each one is shown whole or not at all.
            assert page.evaluate(WHOLE_TABS) == []
            for tab in ("Screens", "Review"):
                if page.is_visible(f".stage-tools .tabs [role=tab]:has-text('{tab}')"):
                    page.click(f".stage-tools .tabs [role=tab]:has-text('{tab}')")
                else:
                    page.click("#tabs-more")
                    page.click(f"#tabs-menu button:has-text('{tab}')")
                page.wait_for_selector(f".stage-tools .tabs [role=tab][aria-selected=true]:has-text('{tab}')")
                assert page.is_visible(f".stage-tools .tabs [role=tab][aria-selected=true]:has-text('{tab}')")
                assert page.evaluate(WHOLE_TABS) == [], tab
                if tab == "Screens":
                    # Each field's label fits its box ("Member card", not "Member c"), and its type takes two lines at most.
                    page.wait_for_selector("#screen-card .screen-field")
                    rows = page.evaluate("""() => [...document.querySelectorAll('#screen-card .screen-field')].map((r) => {
                        const i = r.querySelector('input'), m = r.querySelector('.field-meta');
                        return [i.value, i.scrollWidth <= i.clientWidth,
                                m.getBoundingClientRect().height / (1.2 * parseFloat(getComputedStyle(m).fontSize))]; })""")
                    assert rows and all(fits for _, fits, _ in rows), rows
                    assert all(lines < 2.5 for _, _, lines in rows), rows
            assert errors == []
        finally:
            chrome.close()
