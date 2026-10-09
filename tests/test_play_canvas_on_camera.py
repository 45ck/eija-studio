"""The state machine stays on screen as the canvas changes size (round 11 of the demo dry run, ADR-0174 note).

In a real browser: on first load at 1280x800 nothing of the state machine is clipped; after a state is dropped and the
plan banner pushes the canvas down, the whole diagram (its initial state at the top, the new state at the foot) stays
inside the canvas; and a Run paused with the dock open keeps the paused state inside the shorter canvas.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from test_play_place import _launch

ROOT = Path(__file__).resolve().parents[1]
# The diagram's top and foot, and the canvas's, in page pixels.
SPAN = """() => { const g = window.PlayIDE.diagram('states'), c = document.getElementById('canvas'), r = c.getBoundingClientRect(),
    b = g.getGraphBounds(); return [r.top, r.top + c.clientHeight, r.top + b.y, r.top + b.y + b.height]; }"""
# The paused state (marked as the current step) against the canvas height, in canvas pixels.
CURRENT = """() => { const g = window.PlayIDE.diagram('states'), c = document.getElementById('canvas');
    for (const cell of Object.values(g.getDataModel().cells)) if (cell.id && cell.id.startsWith('state:') && cell.style.fillColor === '#fff6d6') {
      const s = g.view.getState(cell); return [s.y, s.y + s.height, c.clientHeight]; } return null; }"""

pytestmark = [
    pytest.mark.browser,
    pytest.mark.slow,
    pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1"),
]


def _open(api, playwright, server, width: int, height: int):
    chrome = _launch(api, playwright)
    page = chrome.new_page(viewport={"width": width, "height": height})
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{server.base_url}/play#{server.token}")
    page.wait_for_selector("body[data-ready=true]", timeout=60_000)
    page.wait_for_timeout(400)  # the canvas settles to its final height, and the diagram is fitted to it
    return chrome, page, errors


def _inside(span) -> bool:
    top, foot, graph_top, graph_foot = span
    return graph_top >= top - 0.5 and graph_foot <= foot + 0.5


@pytest.mark.parametrize("width,height", [(1280, 800), (1920, 1080)])
def test_first_load_and_the_plan_banner_keep_the_whole_state_machine_on_screen(width, height):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs" / "library-loan") as server, api.sync_playwright() as playwright:
        chrome, page, errors = _open(api, playwright, server, width, height)
        try:
            assert _inside(page.evaluate(SPAN)), page.evaluate(SPAN)
            box = page.locator("#canvas").bounding_box()
            page.drag_and_drop('#draw-palette [data-kind="state"]', "#canvas",
                               target_position={"x": box["width"] * 0.82, "y": box["height"] * 0.82})
            page.fill(".inline-edit input", "Lost")
            page.click('.inline-edit button[type="submit"]')
            page.wait_for_selector("#plan-banner:not([hidden])", timeout=30_000)
            page.wait_for_timeout(600)
            span = page.evaluate(SPAN)
            assert _inside(span), span  # the initial dot is not under the banner, and Lost is not off the foot
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.parametrize("width,height", [(1280, 800), (1440, 900)])
def test_a_paused_run_keeps_the_current_state_on_screen_with_the_dock_open(width, height):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs" / "library-loan") as server, api.sync_playwright() as playwright:
        chrome, page, errors = _open(api, playwright, server, width, height)
        try:
            page.click("#outline-states button:has-text('Overdue')")
            page.click("#inspector button:has-text('Add breakpoint')")
            page.select_option("#run-speed", "40")
            page.click("#run-play")
            page.wait_for_selector("#run-status:has-text('Paused')", timeout=60_000)
            page.wait_for_timeout(300)
            assert page.evaluate("() => window.PlayIDE.diagram('states').view.scale") >= 0.8  # readable, not shrunk
            top, foot, high = page.evaluate(CURRENT)
            assert top >= 0 and foot <= high, (top, foot, high)
            assert errors == []
        finally:
            chrome.close()


def test_replaying_a_simulation_keeps_the_replayed_step_on_screen():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    replayed = """() => { const g = window.PlayIDE.diagram('states'), c = document.getElementById('canvas'), out = [];
        for (const cell of Object.values(g.getDataModel().cells)) if (cell.id && ['#3157d5', '#a12f2f'].includes(cell.style.strokeColor) && cell.style.strokeWidth === (cell.isEdge() ? 6 : 4)) {
          const s = g.view.getState(cell), b = s.text && cell.isEdge() ? s.text.boundingBox || s : s;
          out.push([cell.id, b.y, b.y + b.height, c.clientHeight]); } return out; }"""
    with ephemeral_eija_server(pack=ROOT / "packs" / "library-loan") as server, api.sync_playwright() as playwright:
        chrome, page, errors = _open(api, playwright, server, 1280, 800)
        try:
            page.click("#simulate")
            page.wait_for_selector("#sim-summary:not(:empty)", timeout=60_000)
            page.click("#sim-replay")
            seen = []
            for _ in range(60):
                page.wait_for_timeout(100)
                seen += page.evaluate(replayed)
            states = [s for s in seen if s[0].startswith("state:")]  # the line taken shows too when both fit
            assert states, "the replay marked no state"
            assert {"state:Returned", "state:Cancelled"} & {s[0] for s in states}  # it reached the foot of the diagram
            off = [s for s in states if not (s[1] >= 0 and s[2] <= s[3])]
            assert off == []
            assert errors == []
        finally:
            chrome.close()
