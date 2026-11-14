"""A second, deeper inspection of diagram drawing and editing (2026-11-14), each defect checked in a real browser.

- Every diagram canvas took the height of its drawing, not of the stage: on every pack the Components tab was 1,163
  pixels tall at 1280 x 800, so the workbench scrolled the help line and the foot of the diagram off the screen, and
  a model at the kernel's limits made the state machine's canvas 3,669 pixels tall.
- Lines crossed shapes they do not connect: dependencies through components, actors' lines through other actors and
  workflow links through workflows on the System lens, and, once an actor has many use cases, its lines through the
  use cases between. Two workflow links in opposite directions lay on top of each other and hid each other's label.
- An association's multiplicities and role name, placed at a fixed fraction of the line, sat on the class box when the
  line was short or steep.
- Switching tabs, resizing the window or opening a side region threw away the zoom and pan the person had chosen.
- Escape did not let go of a selection, and a state machine larger than the canvas opened with its initial state out
  of view.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

browser = pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")

# What a diagram gets wrong where it is drawn: a line through a shape it does not connect, a label on a shape, or two
# labels on each other. Boxes are screen boxes of the current view; containers (the system boundary, packages,
# composites, frames, nodes) hold what they contain, so only crossing their edge would count.
CROSSINGS = r"""(key) => { const g = window.PlayIDE.diagram(key);
  if (!g || !g.container.offsetParent) return null;
  const m = g.getDataModel(), v = g.view, root = g.getDefaultParent();
  const box = (s) => [s.x, s.y, s.width, s.height];
  const hit = (a, b, pad) => a[0] + pad < b[0] + b[2] && b[0] + pad < a[0] + a[2] && a[1] + pad < b[1] + b[3] && b[1] + pad < a[1] + a[3];
  const inside = (P, Q) => P[0] <= Q[0] && P[1] <= Q[1] && P[0] + P[2] >= Q[0] + Q[2] && P[1] + P[3] >= Q[1] + Q[3];
  const holder = (c) => /^(system|composite:|pkg:|frame|deploy:device|deploy:node)/.test(c.id);
  const cells = Object.values(m.cells).filter((c) => c.id && v.getState(c));
  const shapes = cells.filter((c) => c.isVertex() && c.parent === root && c.geometry && c.geometry.width > 0 && !holder(c)
    && !(c.style && c.style.fillColor === "none" && c.style.strokeColor === "none"));
  const text = (c) => { const s = v.getState(c); return s && s.text && s.text.value && s.text.boundingBox ? box(s.text.boundingBox) : null; };
  const labels = cells.filter((c) => c.isEdge() || (c.isVertex() && c.parent && c.parent.isEdge && c.parent.isEdge()))
    .map((c) => [c, text(c)]).filter(([, t]) => t);
  const found = [];
  for (const [c, t] of labels) for (const s of shapes) { const S = box(v.getState(s)); if (hit(t, S, 2) && !inside(S, t)) found.push(["label on shape", c.id, s.id]); }
  for (let i = 0; i < labels.length; i++) for (let j = i + 1; j < labels.length; j++)
    if (hit(labels[i][1], labels[j][1], 2)) found.push(["label on label", labels[i][0].id, labels[j][0].id]);
  const through = (p, q, r) => { const [x, y, w, h] = [r[0] + 3, r[1] + 3, r[2] - 6, r[3] - 6];
    for (let k = 0; k <= 40; k++) { const px = p.x + (q.x - p.x) * k / 40, py = p.y + (q.y - p.y) * k / 40; if (px > x && px < x + w && py > y && py < y + h) return true; }
    return false; };
  for (const e of cells.filter((c) => c.isEdge())) {
    const st = v.getState(e), mine = new Set();
    for (const end of [e.source, e.target]) for (let c = end; c; c = c.parent) mine.add(c);
    const points = (st && st.absolutePoints || []).filter(Boolean);
    for (const s of shapes) {
      if (mine.has(s)) continue;
      const S = box(v.getState(s));
      for (let k = 0; k + 1 < points.length; k++) if (through(points[k], points[k + 1], S)) { found.push(["line through shape", e.id, s.id]); break; }
    }
  }
  return found; }"""
TALL = """(id) => { const c = document.getElementById(id), wb = document.querySelector(".workbench");
    return [c.clientHeight, wb.scrollHeight - wb.clientHeight]; }"""
VIEW = "(key) => { const v = window.PlayIDE.diagram(key).view; return [v.scale, v.translate.x, v.translate.y]; }"
SELECTED = "(key) => window.PlayIDE.diagram(key).getSelectionCells().map((c) => c.id)"


def _launch(api, playwright):
    executable = os.environ.get("EIJA_CHROMIUM")
    try:
        return (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                else playwright.chromium.launch(channel="chrome", headless=True))
    except api.Error as exc:
        pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")


def _open(chrome, server, errors, width=1280):
    page = chrome.new_page(viewport={"width": width, "height": 800})
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{server.base_url}/play#{server.token}")
    page.wait_for_selector("body[data-ready=true]", timeout=60_000)
    return page


def _settle(page, script, arg, attempts=60):
    """The value of `script` once two readings 200 ms apart agree (a lens fetches before it draws)."""
    was = None
    for _ in range(attempts):
        now = page.evaluate(script, arg)
        if now == was and now is not None:
            return now
        was = now
        page.wait_for_timeout(200)
    return was


def _lens(page, lens):
    page.click(f"#component-lens [data-lens={lens}]")
    page.wait_for_timeout(300)


def _limits_pack(tmp_path: Path) -> Path:
    """library-loan stretched to the kernel's limits: 32 states and 64 transitions, most of them by one role."""
    pack = tmp_path / "limits"
    shutil.copytree(ROOT / "packs/library-loan", pack)
    doc = json.loads((pack / "pack.json").read_text(encoding="utf-8"))
    model = doc["model"]
    back = next(t for t in model["transitions"] if t["action"] == "Return")
    cancel = next(t for t in model["transitions"] if t["action"] == "Cancel")
    renew = next(a for a in doc["actions"] if a["id"] == "Renew")
    phases = [f"Phase{i}" for i in range(1, 28)]
    model["states"] += phases
    for n, (a, b) in enumerate(zip(["OnLoan", *phases], phases, strict=False)):
        model["transitions"].append({**copy.deepcopy(back), "id": f"TR-X{n}", "action": f"Advance{n}", "from_state": a, "to_state": b,
                                     "required_effects": ["Audit:LoanRenewed"]})
        doc["actions"].append({**copy.deepcopy(renew), "id": f"Advance{n}"})
    for template in (back, cancel):
        for n, state in enumerate(phases):
            if len(model["transitions"]) < 64:
                model["transitions"].append({**copy.deepcopy(template), "id": f"TR-{template['action'].upper()}-{n}", "from_state": state})
    assert (len(model["states"]), len(model["transitions"])) == (32, 64)
    (pack / "pack.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return pack


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_lines_and_labels_stay_off_the_shapes_they_do_not_belong_to():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            # specialist-referral has short, steep associations; library-loan has a link each way between two workflows.
            for name in ("specialist-referral", "library-loan"):
                with ephemeral_eija_server(pack=ROOT / "packs" / name) as server:
                    errors: list[str] = []
                    page = _open(chrome, server, errors)
                    page.click("#tab-classes")
                    assert _settle(page, CROSSINGS, "classes") == [], name
                    # Dragging a class to the other side of the one it is associated with turns the line: its end
                    # labels follow, rather than keep an offset that now points into the class.
                    page.evaluate("""() => { const g = window.PlayIDE.diagram("classes"), m = g.getDataModel();
                        const a = m.getCell("assoc:0"), s = a.source.geometry, t = a.target.geometry;
                        g.moveCells([a.target], 2 * (s.x - t.x) - t.width - 200, 2 * (s.y - t.y)); }""")
                    moved = [f for f in _settle(page, CROSSINGS, "classes") if f[0] == "label on shape"]
                    assert moved == [], (name, moved)
                    page.click("#tab-components")
                    assert _settle(page, CROSSINGS, "components") == [], name
                    _lens(page, "system")
                    assert _settle(page, CROSSINGS, "components") == [], name
                    assert not errors
                    page.close()
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_every_canvas_takes_the_stage_height_and_keeps_the_view_the_person_chose():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/building-permit") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            errors: list[str] = []
            page = _open(chrome, server, errors)
            heights = {}
            for tab, canvas in (("states", "canvas"), ("sequences", "sequence-canvas"), ("classes", "class-canvas"),
                                ("usecases", "usecase-canvas"), ("components", "component-canvas")):
                page.click(f"#tab-{tab}")
                heights[tab] = _settle(page, TALL, canvas)
            # Nothing pushes the workbench into scrolling: the help line and the foot of each diagram stay on screen.
            assert all(scroll == 0 for _, scroll in heights.values()), heights
            assert all(height < 700 for height, _ in heights.values()), heights

            # A zoom the person chose survives another tab, a window resize and a side region opening.
            page.click("#tab-classes")
            page.click("#zoom-in")
            page.click("#zoom-in")
            chosen = page.evaluate(VIEW, "classes")
            page.click("#tab-states")
            page.click("#tab-classes")
            assert page.evaluate(VIEW, "classes") == chosen
            page.set_viewport_size({"width": 1270, "height": 800})
            page.wait_for_timeout(400)
            assert page.evaluate(VIEW, "classes") == chosen
            page.click("#toggle-left")
            page.wait_for_timeout(400)
            assert page.evaluate(VIEW, "classes") == chosen
            # Fit still fits.
            page.click("#fit")
            assert page.evaluate(VIEW, "classes") != chosen

            # Escape lets go of the selection.
            page.click("#toggle-left")
            page.click("#tab-states")
            page.click("#outline-states button[data-id^='state:']")
            assert page.evaluate(SELECTED, "states")
            page.focus("#canvas")
            page.keyboard.press("Escape")
            assert page.evaluate(SELECTED, "states") == []
            assert page.text_content("#status-selection") == ""
            assert not errors
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_a_model_at_the_kernel_limits_opens_readably(tmp_path):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=_limits_pack(tmp_path)) as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            errors: list[str] = []
            page = _open(chrome, server, errors)
            # The state machine's canvas is the stage's, and it opens where records start.
            height, scroll = page.evaluate(TALL, "canvas")
            assert scroll == 0 and height < 700, (height, scroll)
            x, y, w, h = page.evaluate("""() => { const g = window.PlayIDE.diagram("states"), s = g.view.getState(g.getDataModel().getCell("initial"));
                return [s.x, s.y, g.container.clientWidth, g.container.clientHeight]; }""")
            assert 0 <= x <= w and 0 <= y <= h, (x, y, w, h)
            # One actor with dozens of use cases: each line reaches its use case without crossing the others.
            page.click("#tab-usecases")
            assert _settle(page, CROSSINGS, "usecases") == []
            assert page.evaluate(TALL, "usecase-canvas")[1] == 0
            assert not errors
        finally:
            chrome.close()
