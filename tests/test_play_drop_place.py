"""A state lands where you put it: in a real browser, a state clicked or dragged onto empty space is drawn centred on the
pointer, zoomed in and panned too, and nothing else on the diagram moves when it is added, when a transition is drawn
to it, or on undo and redo. A state dragged to rearrange the diagram stays where it was dropped.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from test_play_place import CENTRE, EMPTY, _at, _launch, _steps

ROOT = Path(__file__).resolve().parents[1]
NEAR = 4  # pixels


ORIGIN = "() => [-scrollX, -scrollY]"


def _rel(page, point):
    """A viewport point as a point on the page, so the check holds even if the page itself scrolls (a layout matter, not placing)."""
    left, top = page.evaluate(ORIGIN)
    return [point[0] - left, point[1] - top]


def _near(page, cell: str, point) -> None:
    for _ in range(30):  # the preview redraws after each step
        now = page.evaluate(CENTRE, cell)
        now = now and _rel(page, now)
        if now and abs(now[0] - point[0]) <= NEAR and abs(now[1] - point[1]) <= NEAR:
            return
        page.wait_for_timeout(100)
    raise AssertionError(f"{cell} is at {now}, not at {point}")


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_a_state_lands_under_the_pointer_and_nothing_else_moves():
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
            # Zoomed in and panned, as you would be while working on one part of a diagram.
            page.click("#zoom-in")
            page.click("#zoom-in")
            box = page.locator("#canvas").bounding_box()
            page.mouse.move(box["x"] + box["width"] * 0.5, box["y"] + box["height"] * 0.95)
            page.mouse.down()
            page.mouse.move(box["x"] + box["width"] * 0.3, box["y"] + box["height"] * 0.75, steps=8)
            page.mouse.up()
            overdue = _rel(page, _at(page, CENTRE, "state:Overdue"))

            # Pick State and click empty space: the state is drawn there, and Overdue stays where it was.
            spot = _at(page, EMPTY)
            page.click('#draw-palette [data-kind="state"]')
            page.mouse.click(*spot)
            spot = _rel(page, spot)
            page.wait_for_selector(".inline-edit input:focus")
            page.keyboard.type("Lost")
            page.keyboard.press("Enter")
            _steps(page, 1)
            _near(page, "state:Lost", spot)
            _near(page, "state:Overdue", overdue)

            # A transition drawn to it moves neither end.
            page.click('#draw-palette [data-kind="transition"]')
            page.mouse.click(*_at(page, CENTRE, "state:Overdue"))
            page.mouse.click(*_at(page, CENTRE, "state:Lost"))
            page.wait_for_selector(".inline-edit select:focus")
            page.keyboard.press("Enter")
            _steps(page, 2)
            _near(page, "state:Lost", spot)
            _near(page, "state:Overdue", overdue)

            # Undo and redo keep the view: Lost goes and comes back in the same place.
            page.click("#undo")
            page.click("#undo")
            _steps(page, 0)
            _near(page, "state:Overdue", overdue)
            page.click("#redo")
            _steps(page, 1)
            _near(page, "state:Lost", spot)
            _near(page, "state:Overdue", overdue)

            # A state dragged to rearrange the diagram stays where it was dropped when the next edit redraws.
            start = _at(page, CENTRE, "state:Overdue")
            page.mouse.move(*start)
            page.mouse.down()
            page.mouse.move(start[0] - 60, start[1] + 40, steps=8)
            page.mouse.up()
            page.wait_for_timeout(300)
            overdue = _rel(page, page.evaluate(CENTRE, "state:Overdue"))  # where the grid snapped it
            assert abs(overdue[0] - _rel(page, start)[0]) > 30

            # Dragged from the palette, it lands where it is dropped.
            box = page.locator("#canvas").bounding_box()
            drop = _at(page, EMPTY)
            page.drag_and_drop('#draw-palette [data-kind="state"]', "#canvas",
                               target_position={"x": drop[0] - box["x"], "y": drop[1] - box["y"]})
            drop = _rel(page, drop)
            page.wait_for_selector(".inline-edit input:focus")
            page.keyboard.type("Found")
            page.keyboard.press("Enter")
            _steps(page, 2)
            _near(page, "state:Found", drop)
            _near(page, "state:Lost", spot)
            _near(page, "state:Overdue", overdue)
            assert errors == []
        finally:
            chrome.close()
