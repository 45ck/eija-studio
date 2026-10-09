"""Adding without dragging (ADR-0174): in a real browser, a palette item is picked and then placed with a click, the
diagram opens a small editor where you click or double-click, Enter adds the step to the plan and Escape drops it. The
keyboard still gets the full form, dragging still works, and the review view opens no editor at all.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The centre of a cell on the state machine, in page pixels, or null when it is not drawn.
CENTRE = """(id) => { const g = window.PlayIDE.diagram("states"), cell = g.getDataModel().getCell(id);
    const s = cell && g.view.getState(cell), r = document.getElementById("canvas").getBoundingClientRect();
    return s ? [r.left + s.getCenterX(), r.top + s.getCenterY()] : null; }"""
# A point on the canvas with no element under it, in page pixels.
EMPTY = """() => { const g = window.PlayIDE.diagram("states"), box = document.getElementById("canvas"), r = box.getBoundingClientRect();
    for (const [fx, fy] of [[0.9, 0.85], [0.1, 0.85], [0.9, 0.15], [0.5, 0.92]]) {
      const x = box.clientWidth * fx, y = box.clientHeight * fy;
      if (!g.getCellAt(x, y)) return [r.left + x, r.top + y];
    }
    return null; }"""
GEOMETRY = """([key, id]) => { const c = window.PlayIDE.diagram(key).getDataModel().getCell(id); return [c.geometry.x, c.geometry.y]; }"""
STEPS = "document.querySelectorAll('.msg .plan-steps > li').length"


def _launch(api, playwright):
    executable = os.environ.get("EIJA_CHROMIUM")
    try:
        return (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                else playwright.chromium.launch(channel="chrome", headless=True))
    except api.Error as exc:
        pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")


def _steps(page, n: int) -> None:
    for _ in range(100):  # the page's CSP rules out wait_for_function with a string
        if page.evaluate(STEPS) == n:
            return
        page.wait_for_timeout(100)
    assert page.evaluate(STEPS) == n


def _at(page, script: str, arg=None) -> tuple[float, float]:
    for _ in range(50):  # the preview redraws after each step
        point = page.evaluate(script, arg) if arg is not None else page.evaluate(script)
        if point:
            return point
        page.wait_for_timeout(100)
    raise AssertionError(f"nothing to click for {arg or 'an empty point'}")


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_pick_then_click_double_click_and_edit_inline_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            state = '#draw-palette [data-kind="state"]'

            # Picking a palette item arms it; Escape (or picking it again) puts it down.
            page.click(state)
            assert page.get_attribute(state, "aria-pressed") == "true"
            assert "placing" in page.get_attribute("#canvas", "class")
            assert "Click the diagram" in page.inner_text("#canvas-help")
            page.keyboard.press("Escape")
            assert page.get_attribute(state, "aria-pressed") == "false"
            page.click(state)
            page.click(state)
            assert page.get_attribute(state, "aria-pressed") == "false"

            # Pick State, click empty space: a name editor opens there; Enter adds the step and the preview shows it.
            page.click(state)
            page.mouse.click(*_at(page, EMPTY))
            page.wait_for_selector(".inline-edit input:focus")
            assert page.get_attribute(state, "aria-pressed") == "false"  # one placement, then the tool is put down
            page.keyboard.type("Lost")
            page.dblclick(".inline-edit input")  # selecting the word keeps the editor and what was typed
            page.dblclick(".inline-edit .inline-title")
            page.click(".inline-edit input")
            assert page.locator(".inline-edit").count() == 1 and page.input_value(".inline-edit input") == "Lost"
            page.keyboard.press("End")
            page.keyboard.press("Enter")
            page.wait_for_selector(".inline-edit", state="detached")
            _steps(page, 1)
            _at(page, CENTRE, "state:Lost")

            # Double-click a state: rename it in place. Escape leaves the plan as it was.
            page.mouse.dblclick(*_at(page, CENTRE, "state:Overdue"))
            page.wait_for_selector(".inline-edit input:focus")
            assert page.input_value(".inline-edit input") == "Overdue"
            page.keyboard.press("Escape")
            page.wait_for_selector(".inline-edit", state="detached")
            page.mouse.dblclick(*_at(page, CENTRE, "state:Overdue"))
            page.fill(".inline-edit input", "Late")
            page.keyboard.press("Enter")
            _steps(page, 2)
            _at(page, CENTRE, "state:Late")

            # Pick Transition, click where it leaves and where it goes: only the action and the role are asked for.
            page.click('#draw-palette [data-kind="transition"]')
            page.mouse.click(*_at(page, CENTRE, "state:Late"))
            assert "now click the state it goes to" in page.inner_text("#canvas-help")
            page.mouse.click(*_at(page, CENTRE, "state:Lost"))
            page.wait_for_selector(".inline-edit select:focus")
            assert [t.splitlines()[0] for t in page.locator(".inline-edit label").all_inner_texts()] == ["Action", "Who may take it"]
            assert "Late → Lost" in page.inner_text(".inline-edit")
            page.keyboard.press("Enter")
            _steps(page, 3)

            # Double-click empty space opens a new state editor; clicking away while it is empty drops it.
            page.mouse.dblclick(*_at(page, EMPTY))
            page.wait_for_selector(".inline-edit input:focus")
            page.click("#outline-states button >> nth=0")
            page.wait_for_selector(".inline-edit", state="detached")

            # The keyboard needs no pointing: Enter on a palette item opens the full form in the inspector.
            page.focus(state)
            page.keyboard.press("Enter")
            page.wait_for_selector("#inspector .draft-form input:focus")
            assert [t.splitlines()[0] for t in page.locator("#inspector .draft-form label").all_inner_texts()] == ["Name", "Place after"]

            # Dragging still works, and drops into the same editor.
            page.drag_and_drop(state, "#canvas", target_position={"x": 40, "y": 40})
            page.wait_for_selector(".inline-edit input:focus")
            page.keyboard.press("Escape")
            _steps(page, 3)

            # The review view changes nothing: no tool, no editor.
            page.goto(f"{server.base_url}/play?view=review#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.mouse.dblclick(*_at(page, EMPTY))
            page.mouse.dblclick(*_at(page, CENTRE, "state:Overdue"))
            page.wait_for_timeout(300)
            assert page.locator(".inline-edit").count() == 0
            assert errors == []
        finally:
            chrome.close()


def _near(page, cell: str, point, tolerance: float = 3.0) -> None:
    for _ in range(50):  # the preview redraws after each step
        centre = page.evaluate(CENTRE, cell)
        if centre and abs(centre[0] - point[0]) <= tolerance and abs(centre[1] - point[1]) <= tolerance:
            return
        page.wait_for_timeout(100)
    raise AssertionError(f"{cell} is at {page.evaluate(CENTRE, cell)}, not {point}")


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_a_state_lands_where_you_put_it_and_stays_there_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            state = '#draw-palette [data-kind="state"]'
            page.click("#zoom-in")  # not at the fitted scale
            page.wait_for_timeout(300)
            requested = _at(page, CENTRE, "state:Requested")

            # Before the click, an outline shows where the state will land; after it, the state is centred there and
            # nothing else on the diagram has moved.
            page.click(state)
            spot = _at(page, EMPTY)
            page.mouse.move(*spot)
            ghost = page.evaluate("""() => { const r = document.querySelector('.place-preview .ghost-state').getBoundingClientRect();
                return [r.left + r.width / 2, r.top + r.height / 2]; }""")
            assert abs(ghost[0] - spot[0]) <= 1 and abs(ghost[1] - spot[1]) <= 1
            page.mouse.click(*spot)
            page.keyboard.type("Lost")
            page.keyboard.press("Enter")
            _steps(page, 1)
            _near(page, "state:Lost", spot)
            _near(page, "state:Requested", requested)

            # Drag a state to move it: it stays where you let go, through the next redraw too.
            overdue = _at(page, CENTRE, "state:Overdue")
            target = _at(page, EMPTY)
            page.mouse.move(*overdue)
            page.mouse.down()
            page.mouse.move((overdue[0] + target[0]) / 2, (overdue[1] + target[1]) / 2, steps=5)
            page.mouse.move(*target, steps=5)
            page.mouse.up()
            _near(page, "state:Overdue", target, tolerance=12)  # maxGraph snaps a move to its 10px grid
            moved = page.evaluate(CENTRE, "state:Overdue")
            assert page.is_visible("#tidy")
            page.mouse.dblclick(*_at(page, CENTRE, "state:Lost"))
            page.fill(".inline-edit input", "Missing")
            page.keyboard.press("Enter")
            _steps(page, 2)
            _near(page, "state:Missing", spot)
            _near(page, "state:Overdue", moved)

            # A drag from the palette, zoomed out, drops the state exactly where it is let go.
            page.click("#zoom-out")
            page.click("#zoom-out")
            page.wait_for_timeout(300)
            drop = _at(page, EMPTY)
            box = page.locator("#canvas").bounding_box()
            page.drag_and_drop(state, "#canvas", target_position={"x": drop[0] - box["x"], "y": drop[1] - box["y"]})
            page.wait_for_selector(".inline-edit input:focus")
            page.keyboard.type("Found")
            page.keyboard.press("Enter")
            _steps(page, 3)
            _near(page, "state:Found", drop)

            # Tidy forgets the positions and lays the diagram out again.
            page.click("#tidy")
            page.wait_for_selector("#tidy", state="hidden")
            _at(page, CENTRE, "state:Found")
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_a_shape_moved_on_the_other_diagrams_stays_there_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    centre = """([key, id]) => { const g = window.PlayIDE.diagram(key), cell = g.getDataModel().getCell(id);
        const s = cell && g.view.getState(cell), r = g.container.getBoundingClientRect();
        return s ? [r.left + s.getCenterX(), r.top + s.getCenterY()] : null; }"""
    first = """(key) => { const g = window.PlayIDE.diagram(key);
        const c = Object.values(g.getDataModel().cells).find((x) => x.isVertex() && x.id && x.parent === g.getDefaultParent() && x.style.movable !== false);
        return c ? c.id : null; }"""
    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            kept = {}
            for key, tab in (("classes", "#tab-classes"), ("usecases", "#tab-usecases"), ("components", "#tab-components")):
                page.click(tab)
                page.wait_for_timeout(400)
                cell = page.evaluate(first, key)
                start = page.evaluate(centre, [key, cell])
                page.mouse.move(*start)
                page.mouse.down()
                page.mouse.move(start[0] + 30, start[1] + 40, steps=4)
                page.mouse.move(start[0] + 60, start[1] + 80, steps=4)
                page.mouse.up()
                after = page.evaluate(centre, [key, cell])
                assert abs(after[1] - start[1]) > 40, (key, start, after)
                assert page.is_visible("#tidy")
                kept[key] = (cell, page.evaluate(GEOMETRY, [key, cell]))
            # A plan preview redraws every diagram: what was moved stays where it was put.
            page.click("#tab-states")
            page.click('#draw-palette [data-kind="state"]')
            page.mouse.click(*_at(page, EMPTY))
            page.keyboard.type("Lost")
            page.keyboard.press("Enter")
            _steps(page, 1)
            for key, tab in (("classes", "#tab-classes"), ("usecases", "#tab-usecases"), ("components", "#tab-components")):
                page.click(tab)
                page.wait_for_timeout(300)
                cell, where = kept[key]
                assert page.evaluate(GEOMETRY, [key, cell]) == where, key
            assert errors == []
        finally:
            chrome.close()
