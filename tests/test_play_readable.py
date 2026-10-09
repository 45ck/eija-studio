"""PlayIDE on a laptop screen, in a real browser: with the side bar and the chat open, the state machine is drawn large
enough to read rather than shrunk to fit one long row, and a previewed change ("Unsaved changes" in the status bar)
never makes the page wider than the window, which would scroll it sideways.

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
            # The chat's example, previewed: the status bar says "Unsaved changes", and the page still fits the window.
            page.fill("#chat-input", page.text_content("#chat-example"))
            page.click("#chat-send")
            preview = page.get_by_role("button", name="Preview on the diagram").first
            preview.wait_for(timeout=30_000)
            preview.click()
            page.wait_for_selector("#plan-banner:not([hidden])")
            page.wait_for_selector("#system-saved[data-dirty=true]", state="attached")
            assert page.evaluate("() => document.documentElement.scrollWidth - innerWidth") <= 0
            assert errors == []
        finally:
            chrome.close()
