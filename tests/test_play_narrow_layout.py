"""PlayIDE does not scroll sideways at the laptop widths below 1000px: the toolbar wraps its checks pill rather than
pushing the page wider than the window. Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(
    os.environ.get("EIJA_BROWSER_TESTS") != "1",
    reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1",
)
@pytest.mark.parametrize("width", [900, 768])
def test_playide_does_not_scroll_sideways_on_narrow_laptop_widths(width):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with (
        ephemeral_eija_server(pack=ROOT / "packs" / "library-loan") as server,
        api.sync_playwright() as playwright,
    ):
        try:
            executable = os.environ.get("EIJA_CHROMIUM")
            chrome = (
                playwright.chromium.launch(headless=True, executable_path=executable)
                if executable
                else playwright.chromium.launch(channel="chrome", headless=True)
            )
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": width, "height": 800})
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            for tab in ("tab-states", "tab-tests", "tab-review"):
                page.click(f"#{tab}")
                scroll_width, client_width = page.evaluate(
                    "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"
                )
                assert scroll_width <= client_width, (
                    f"{tab} at {width}px scrolls sideways: {scroll_width} > {client_width}"
                )
        finally:
            chrome.close()
