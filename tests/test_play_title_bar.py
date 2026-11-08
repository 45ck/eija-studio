"""PlayIDE's title bar says the source state in words, never as the machine code. On a local checkout the kernel source
is not the shipped fixture, so the badge is "Source review required"; the code SOURCE_REVIEW_REQUIRED stays in the
problems list, not on the badge.

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
@pytest.mark.skipif(
    os.environ.get("EIJA_BROWSER_TESTS") != "1",
    reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1",
)
def test_the_title_bar_says_source_review_required_in_words_not_as_a_code():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with (
        ephemeral_eija_server(pack=ROOT / "packs" / "library-loan") as server,
        api.sync_playwright() as playwright,
    ):
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1280, "height": 800})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            badge = page.text_content("#source-status").strip()
            assert badge == "Source review required", badge
            assert "SOURCE_REVIEW_REQUIRED" not in page.inner_text("#source-status")
            assert not errors, errors
        finally:
            chrome.close()
