"""PlayIDE Changes (ADR-0176): the server draws nothing and saves nothing; it returns the union of the model in force
and the change shown, and the page only styles it. In a real browser the Changes view shows both models on one layout,
flips between Before, Changes and After without moving a state, and steps through the changes.

The browser test is marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed
Chrome, or the Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "src/eija_studio/resources/web"
SESSION = "synthetic-play-diff-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}
LOAN = ROOT / "packs" / "library-loan"


@pytest.fixture
def studio(tmp_path):
    return harness_studio(tmp_path / "workspace", pack=LOAN)


@pytest.fixture
def client(studio):
    app = create_app(studio, SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"])
    app.state.play.stop()


def test_the_diff_of_a_plan_is_drawn_against_the_model_in_force_and_saves_nothing(client, studio):
    with studio.store.transaction() as u:
        before = u.active()["model"]
    plan = [{"kind": "add_state", "state": "Lost", "after": "Overdue"}, {"kind": "remove_transition", "transition": "TR-CANCEL"}]
    ghost = client.post("/api/play/diff", json={"plan": plan}, headers=HEADERS).json()
    assert ghost.get("code") is None, ghost
    assert ghost["format"] == "eija.ghost-diff.v1" and ghost["before"] == studio.pack.model.semantic_hash
    assert [c["text"] for c in ghost["changes"]] == ["Adds state Lost", "Removes Cancel [Member]: Requested → Cancelled"]
    nothing = client.post("/api/play/diff", json={}, headers=HEADERS).json()
    assert nothing["changes"] == [] and nothing["before"] == nothing["after"]
    with studio.store.transaction() as u:
        assert u.active()["model"] == before


def test_the_diff_refuses_a_model_the_page_no_longer_shows_and_a_plan_the_policy_refuses(client, studio):
    stale = studio.pack.model.model_copy(update={"initial_state": "OnLoan"}).model_dump(mode="json")
    assert client.post("/api/play/diff", json={"model": stale}, headers=HEADERS).json()["code"] == "MODEL_CHANGED"
    refused = client.post("/api/play/diff", json={"plan": [{"kind": "set_role", "transition": "TR-RETURN", "role": "Clerk"}]}, headers=HEADERS)
    assert refused.status_code >= 400 and refused.json()["code"] == "POLICY_BLOCKED"


def test_the_page_loads_the_changes_view_after_play_js_and_it_only_asks_for_the_diff_and_the_laws(client):
    page = client.get("/play").text
    assert page.index("/assets/play.js") < page.index("/assets/play-diff.js") and "/assets/play-diff.css" in page
    for name in ("play-diff.js", "play-diff.css"):
        assert client.get(f"/assets/{name}").status_code == 200
    source = (WEB / "play-diff.js").read_text(encoding="utf-8")
    assert "fetch(" not in source and set(__import__("re").findall(r'"(/api/[^"]+)"', source)) == {"/api/play/diff", "/api/play/laws"}


def test_the_state_machine_keeps_every_state_in_place_between_preview_and_the_model():
    play = (WEB / "play.js").read_text(encoding="utf-8")
    # One layout for both sides while a plan can be previewed, in a fixed order (baseModel first), whichever is drawn.
    assert "const models = plan && plan.result && plan.result.legal ? [baseModel, plan.result.candidate] : [workflow];" in play
    assert "shape = basis(workflow)" in play


browser = pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1",
                             reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")


def _launch(api, playwright):
    executable = os.environ.get("EIJA_CHROMIUM")
    try:
        if executable:
            return playwright.chromium.launch(headless=True, executable_path=executable)
        return playwright.chromium.launch(channel="chrome", headless=True)
    except api.Error as exc:
        pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")


def _places(page) -> dict[str, list[float]]:
    return page.evaluate("""() => { const g = window.PlayIDE.graph(), out = {};
        for (const c of Object.values(g.getDataModel().cells)) if (c.id && c.id.startsWith('state:')) out[c.id] = [c.geometry.x, c.geometry.y];
        return out; }""")


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_the_changes_view_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=LOAN) as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.is_hidden("#show-changes")  # nothing to show yet
            page.fill("#chat-input", "add state Lost after Overdue then add Renew from Overdue to Lost for Librarian "
                                     "then move ReturnLate target to Lost then remove Cancel")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .plan .plan-verdict.ok", timeout=30_000)
            page.wait_for_selector("#show-changes:not([hidden]) .badge:text('4')", timeout=30_000)

            page.click("#chat-log .plan .plan-tools .primary")  # preview the plan, then go back: no state moves
            page.wait_for_selector("#plan-banner:not([hidden])")
            after = _places(page)
            page.click("#plan-back")
            before = _places(page)
            assert {k: v for k, v in after.items() if k in before} == {k: v for k, v in before.items() if k in after}

            page.click("#show-changes")
            page.wait_for_selector(".diff-item")
            assert page.is_hidden("#canvas") and page.get_attribute("#show-changes", "aria-pressed") == "true"
            ghost = page.evaluate("() => window.PlayIDE.hooks.diffGraph().getDataModel().getCell('was:TR-CANCEL').style")
            assert ghost["dashed"] and ghost["opacity"] < 100  # the removed arrow is a ghost, not gone
            tip = page.evaluate("""() => { const g = window.PlayIDE.hooks.diffGraph(), t = g.getTooltipForCell(g.getDataModel().getCell('t:TR-RENEW'));
                return [t instanceof HTMLElement, t.children.length, t.textContent]; }""")
            assert tip[:2] == [True, 0] and "Renew" in tip[2]  # a text node: model names are never parsed as HTML
            # Calm by default: one summary line and stepping; the lenses and slider wait behind Compare, the list is in the inspector.
            assert page.inner_text(".diff-summary") == "4 changes: 2 added, 1 moved, 1 removed"
            assert page.is_hidden("#diff-compare-tools") and page.locator("#inspector .diff-item").count() == 4
            page.focus(".diff-canvas")
            page.keyboard.press("]")
            assert page.inner_text("#diff-pos") == "Change 1 of 4" and page.locator(".diff-detail").count() == 0  # nothing to tabulate
            page.click("#inspector .diff-item.moved")
            assert "Overdue → Returned" in page.inner_text(".diff-detail")  # the moved arrow opens its route before and after
            page.click("#diff-compare")
            assert page.is_visible(".lens button[data-lens=after]")
            page.focus(".diff-canvas")
            page.keyboard.press("b")  # Before hides what the change adds, and drops the marks
            lost = page.evaluate("() => window.PlayIDE.hooks.diffGraph().getDataModel().getCell('state:Lost').visible")
            assert lost is False and page.get_attribute(".lens button[data-lens=before]", "aria-checked") == "true"
            page.keyboard.press("a")
            assert page.evaluate("() => window.PlayIDE.hooks.diffGraph().getDataModel().getCell('was:TR-CANCEL').visible") is False
            # Changes stays on across the diagrams: the class diagram and the use cases show the same change.
            page.click("#tab-classes")
            lost = page.evaluate("() => window.PlayIDE.diagram('classes').getDataModel().getCell('literal:Lost').value")
            assert lost == "+ Lost" and page.locator("#inspector .diff-item").count() == 4
            page.click("#tab-usecases")
            cells = page.evaluate("""() => { const m = window.PlayIDE.diagram('usecases').getDataModel();
                return ['uc:TR-CANCEL', 'uc:TR-RENEW', 'role:Clerk'].map((id) => { const c = m.getCell(id); return c && [c.value, !!c.style.dashed]; }); }""")
            assert cells == [["\u2212 Cancel", True], ["+ Renew", False], ["Clerk", False]]  # Clerk keeps MarkOverdue in this plan
            page.click("#inspector .diff-item.removed")
            assert page.evaluate("() => window.PlayIDE.diagram('usecases').getSelectionCell().id") == "uc:TR-CANCEL"
            page.click("#show-changes")  # off: every diagram is the model again
            plain = page.evaluate("() => window.PlayIDE.diagram('usecases').getDataModel().getCell('uc:TR-CANCEL').value")
            assert plain == "Cancel" and page.get_attribute("#show-changes", "aria-pressed") == "false"
            page.click("#tab-states")
            assert page.is_visible("#canvas") and page.is_hidden("#diff-view") and page.locator("#inspector .diff-item").count() == 0
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_your_own_change_and_the_ais_read_the_same_way_with_what_to_consider():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=LOAN) as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.fill("#chat-input", "add Renew from Overdue to OnLoan for Librarian then remove Cancel")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .plan .plan-verdict.ok", timeout=30_000)
            box = page.locator("#canvas").bounding_box()
            spot = {"x": box["width"] * 0.5, "y": box["height"] * 0.85}
            page.drag_and_drop("#draw-palette button[data-kind=state]", "#canvas", target_position=spot)
            page.wait_for_selector(".inline-edit input")
            page.keyboard.type("Lost")
            page.keyboard.press("Enter")
            page.wait_for_selector("#show-changes:not([hidden]) .badge:text('3')", timeout=30_000)
            # The state you drew is where you dropped it, not wherever the layout would put it.
            lost = page.evaluate("""() => { const g = window.PlayIDE.graph(), c = g.getDataModel().getCell('state:Lost'), s = g.view.getState(c);
                return [s.getCenterX(), s.getCenterY()]; }""")
            assert abs(lost[0] - spot["x"]) < 60 and abs(lost[1] - spot["y"]) < 60, (lost, spot)

            page.click("#show-changes")
            page.wait_for_selector("#diff-consider li.ok, #diff-consider li.bad", timeout=30_000)
            tags = page.eval_on_selector_all("#inspector .diff-item", "items => items.map((b) => [b.querySelector('.who') && b.querySelector('.who').textContent, b.textContent])")
            assert [t[0] for t in tags] == ["You", "AI", "AI"] and "Adds state Lost" in tags[0][1]
            consider = page.inner_text("#diff-consider")
            assert "problem" in consider and "No law is broken" in consider and "Also changes: " in consider
            assert page.get_attribute("#diff-flags", "open") is None  # the details wait behind one line of counts
            page.click("#diff-flags summary")
            assert "No record can ever reach Lost" in page.inner_text("#diff-flags")
            page.click("#diff-consider button.link >> text=Use cases")
            assert page.get_attribute("#tab-usecases", "aria-selected") == "true"
            assert errors == []
        finally:
            chrome.close()
