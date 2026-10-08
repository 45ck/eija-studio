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


def test_the_page_loads_the_changes_view_after_play_js_and_it_only_asks_for_the_diff(client):
    page = client.get("/play").text
    assert page.index("/assets/play.js") < page.index("/assets/play-diff.js") and "/assets/play-diff.css" in page
    for name in ("play-diff.js", "play-diff.css"):
        assert client.get(f"/assets/{name}").status_code == 200
    source = (WEB / "play-diff.js").read_text(encoding="utf-8")
    assert "fetch(" not in source and set(__import__("re").findall(r'"(/api/[^"]+)"', source)) == {"/api/play/diff"}


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
            page.focus(".diff-canvas")
            page.keyboard.press("]")
            assert page.inner_text("#diff-pos") == "Change 1 of 4" and "Adds state Lost" in page.inner_text("#inspector")
            page.keyboard.press("b")  # Before hides what the change adds, and drops the marks
            lost = page.evaluate("() => window.PlayIDE.hooks.diffGraph().getDataModel().getCell('state:Lost').visible")
            assert lost is False and page.get_attribute(".lens button[data-lens=before]", "aria-checked") == "true"
            page.keyboard.press("a")
            assert page.evaluate("() => window.PlayIDE.hooks.diffGraph().getDataModel().getCell('was:TR-CANCEL').visible") is False
            page.click("#tab-classes")  # another tab closes the view and gives the state machine back
            page.click("#tab-states")
            assert page.is_visible("#canvas") and page.is_hidden("#diff-view")
            assert errors == []
        finally:
            chrome.close()
