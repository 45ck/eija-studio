"""Simulate keeps the state machine readable (#139): in a real browser at 1280x800, opening the Simulation panel leaves the
diagram at a size whose labels and heat counts can be read (at least 0.8 scale, about 10px text) with the initial state in
view, instead of shrinking it to fit the shorter canvas. The Fit button still shows all of it, however small.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from test_play_place import CENTRE, _launch

ROOT = Path(__file__).resolve().parents[1]
SCALE = "() => window.PlayIDE.diagram('states').view.scale"
INSIDE = """(p) => { const r = document.getElementById('canvas').getBoundingClientRect();
    return p[0] >= r.left && p[0] <= r.right && p[1] >= r.top && p[1] <= r.bottom; }"""


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
@pytest.mark.parametrize("pack", ["library-loan", "excursion"])
def test_the_state_machine_stays_readable_while_simulate_is_open(pack):
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
            page.click("#simulate")
            page.wait_for_selector('body[data-dock="open"]', timeout=30_000)
            page.wait_for_selector("#sim-summary:not(:empty)", timeout=60_000)
            page.wait_for_timeout(400)  # the panel opening refits the diagram on the next frame
            assert page.evaluate(SCALE) >= 0.8
            initial = page.evaluate(CENTRE, "initial")
            assert initial and page.evaluate(INSIDE, initial)
            # Fit, pressed on purpose, shows the whole diagram even if that is smaller.
            page.click("#fit")
            page.wait_for_timeout(200)
            assert page.evaluate(SCALE) <= 1.4
            assert errors == []
        finally:
            chrome.close()
