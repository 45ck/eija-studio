"""Transition labels on the state machine never overlap (issue #153).

A back-and-forth pair (RequestRefund / RejectRefund, FailPayout / RetryPayout) used to draw both labels on top of
each other: dagre left a fixed 120 pixels of room for each label, to the right of its edge, and maxGraph put the label
halfway along the line anyway. Now each label is laid out at its real size, centred, and placed where the layout left
room for it, on the state machine and in the Changes view. The browser test is marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise) and
never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKS = ["card-payment", "refund-desk", "building-permit", "specialist-referral", "saas-subscription", "parcel-delivery", "library-loan"]
CENTRE = """(id) => { const g = window.PlayIDE.diagram("states"), s = g.view.getState(g.getDataModel().getCell(id));
    const r = document.getElementById("canvas").getBoundingClientRect(); return [r.left + s.getCenterX(), r.top + s.getCenterY()]; }"""
OVERLAPS = """(changes) => { const P = window.PlayIDE, g = changes ? P.hooks.diffGraph() : P.diagram("states"), boxes = [];
  const isTransition = (c) => (changes ? c.isEdge() && c.value && c.id !== "initial-edge" && !c.id.startsWith("was:") : c.id.startsWith("transition:"));
  for (const c of Object.values(g.getDataModel().cells)) {
    if (!c.id || !isTransition(c)) continue;
    const s = g.view.getState(c), b = s && s.text && s.text.boundingBox;
    if (b) boxes.push([c.id, b.x, b.y, b.width, b.height]);
  }
  const hits = [];
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const [p, q] = [boxes[i], boxes[j]];
    const x = Math.min(p[1] + p[3], q[1] + q[3]) - Math.max(p[1], q[1]), y = Math.min(p[2] + p[4], q[2] + q[4]) - Math.max(p[2], q[2]);
    if (x > 1 && y > 1) hits.push(`${p[0]} and ${q[0]}`);
  }
  return [boxes.length, hits]; }"""


def test_labels_are_laid_out_at_their_size_and_placed_in_their_room():
    source = (ROOT / "src/eija_studio/resources/web/play.js").read_text(encoding="utf-8")
    assert 'labelpos: "c"' in source and "textWidth(label(t))" in source
    assert "liftLabels(graph);" in source
    changes = (ROOT / "src/eija_studio/resources/web/play-diff.js").read_text(encoding="utf-8")
    assert "ide().textWidth" in changes and "ide().liftLabels(graph" in changes  # the Changes view lays labels out the same way


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
@pytest.mark.parametrize("pack", PACKS)
def test_no_two_transition_labels_overlap_in_a_real_browser(pack):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs" / pack) as server, api.sync_playwright() as playwright:
        executable = os.environ.get("EIJA_CHROMIUM")
        try:
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            for size in ({"width": 1280, "height": 800}, {"width": 2400, "height": 700}):  # top to bottom, and left to right
                page = chrome.new_page(viewport=size)
                page.goto(f"{server.base_url}/play#{server.token}")
                page.wait_for_selector("body[data-ready=true]", timeout=60_000)
                count, hits = page.evaluate(OVERLAPS, False)
                assert count > 0
                assert hits == [], f"{pack} at {size['width']}px: {hits}"
                if pack == "refund-desk" and size["width"] == 1280:  # and in the Changes view of a plan
                    page.mouse.dblclick(*page.evaluate(CENTRE, "state:Assessed"))  # rename a state: a change to show
                    page.fill(".inline-edit input", "Triaged")
                    page.keyboard.press("Enter")
                    page.wait_for_selector("#show-changes:not([hidden])")
                    page.click("#show-changes")
                    page.wait_for_selector("#diff-view:not([hidden]) .diff-canvas")
                    count, hits = page.evaluate(OVERLAPS, True)
                    assert count > 0 and hits == [], f"{pack} Changes view: {hits}"
                page.close()
        finally:
            chrome.close()
