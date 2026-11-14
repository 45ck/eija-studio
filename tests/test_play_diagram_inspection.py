"""Defects found by a Fagan inspection of diagram drawing and editing (2026-11-13), each checked in a real browser.

- A redraw (any plan step, a preview, Tidy) cleared the inspector but kept the selection, so Delete removed a state
  nothing showed as selected, and the status bar still named it. Now a selection that is still drawn stays selected
  on the diagram, and one that is gone is dropped.
- Choosing in the outline let go of the class diagram's selection only: the use case diagram kept a stale handle.
- A composite state's tooltip said "Initial state", and double-clicking the empty inside of one did nothing.
- The class diagram drew the target end's role name in the middle of the association, where UML puts the
  association's own name; it now sits at the target end, under the multiplicity.
- At 1280 pixels wide the use case diagram cut off its right-hand actor at the readable scale.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

STEPS = "[...document.querySelectorAll('.msg .plan-steps > li')].length"
SELECTED = "(key) => window.PlayIDE.diagram(key).getSelectionCells().map((c) => c.id)"
# The right edge of the drawing and the canvas width, in screen pixels.
WIDTH = """(key) => { const g = window.PlayIDE.diagram(key), b = g.getGraphBounds();
    return [b.x + b.width, g.container.clientWidth, g.view.scale]; }"""

browser = pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")


def _launch(api, playwright):
    executable = os.environ.get("EIJA_CHROMIUM")
    try:
        return (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                else playwright.chromium.launch(channel="chrome", headless=True))
    except api.Error as exc:
        pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")


def _wait(page, script: str, expected, arg=None):
    for _ in range(100):  # the page's CSP rules out wait_for_function with a string
        got = page.evaluate(script, arg) if arg is not None else page.evaluate(script)
        if got == expected:
            return
        page.wait_for_timeout(100)
    assert got == expected


def _open(chrome, server, errors):
    page = chrome.new_page(viewport={"width": 1280, "height": 800})
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{server.base_url}/play#{server.token}")
    page.wait_for_selector("body[data-ready=true]", timeout=60_000)
    return page


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_delete_acts_only_on_a_selection_the_diagram_shows():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            errors: list[str] = []
            page = _open(chrome, server, errors)
            # Select a use case, then a state in the outline: the use case diagram lets go of what it had.
            page.click("#tab-usecases")
            page.evaluate("""() => { const g = window.PlayIDE.diagram("usecases");
                g.setSelectionCell(g.getDataModel().getCell("uc:create")); }""")
            page.click("#outline-states button[data-id='state:OnLoan']")
            assert page.evaluate(SELECTED, "states") == ["state:OnLoan"]
            page.click("#tab-usecases")
            assert page.evaluate(SELECTED, "usecases") == []
            page.click("#tab-states")

            # A step elsewhere redraws the diagram: OnLoan is still drawn, so it is still selected, and says so.
            page.focus('#draw-palette [data-kind="state"]')
            page.keyboard.press("Enter")
            page.fill("#inspector .draft-form input", "Archived")
            page.keyboard.press("Enter")
            _wait(page, STEPS, 1)
            _wait(page, SELECTED, ["state:OnLoan"], "states")
            assert page.inner_text("#inspector h3").lower() == "state onloan"
            assert page.text_content("#status-selection").startswith("state OnLoan")

            # Delete removes what is shown; once it is gone nothing is selected, and Delete again does nothing.
            page.click("#outline-states button[data-id='state:Archived']")
            page.focus("#canvas")
            page.keyboard.press("Delete")
            _wait(page, STEPS, 2)
            _wait(page, SELECTED, [], "states")
            assert page.text_content("#status-selection") == ""
            assert "Select a state or transition" in page.inner_text("#inspector")
            page.focus("#canvas")
            page.keyboard.press("Delete")
            page.wait_for_timeout(800)
            assert page.evaluate(STEPS) == 2
            assert not errors
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_composites_role_names_and_the_use_case_width_read_right_at_1280():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/refund-desk") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            errors: list[str] = []
            page = _open(chrome, server, errors)

            # A composite state is named as one, and the empty space inside it takes a new state like any other.
            tip, point = page.evaluate("""() => { const g = window.PlayIDE.diagram("states"), m = g.getDataModel();
                const box = Object.values(m.cells).find((c) => c.id && c.id.startsWith("composite:")), v = g.view;
                v.setTranslate(v.translate.x, v.translate.y - (v.getState(box).y - 40) / v.scale); // bring its top into view
                const s = v.getState(box);
                const r = document.getElementById("canvas").getBoundingClientRect();
                for (let fy = 0.1; fy < 1; fy += 0.05) for (let fx = 0.05; fx < 1; fx += 0.05) {
                  const x = s.x + s.width * fx, y = s.y + s.height * fy, hit = g.getCellAt(x, y);
                  const page = document.elementFromPoint(r.left + x, r.top + y);
                  if (hit === box && page && page.closest("#canvas") && y > 0 && y < g.container.clientHeight) return [g.getTooltipForCell(box), [r.left + x, r.top + y]];
                }
                return [g.getTooltipForCell(box), null]; }""")
            assert tip.startswith("Composite state ")
            assert point, "no empty point inside a composite state is on screen"
            page.mouse.dblclick(*point)
            page.wait_for_selector(".inline-edit input:focus")
            page.keyboard.press("Escape")

            # The role name of an association sits at its target end, not in the middle where its name would go.
            page.click("#tab-classes")
            ends = page.evaluate("""() => { const g = window.PlayIDE.diagram("classes"), m = g.getDataModel();
                return Object.values(m.cells).filter((c) => c.id && c.id.startsWith("assoc:")).map((e) => {
                  const role = m.getCell("role-end:" + e.id.slice(6));
                  return [e.value, role && role.value, role && role.geometry.x]; }); }""")
            assert ["", "payouts", 1] in ends
            assert all(value == "" for value, _, _ in ends)

            # The whole width of the use case diagram is on screen at 1280 pixels, at the readable scale.
            page.click("#tab-usecases")
            right, width, scale = page.evaluate(WIDTH, "usecases")
            assert scale >= 0.8
            assert right <= width, f"the use case diagram runs {right - width:.0f} px past the canvas"
            assert not errors
        finally:
            chrome.close()
