"""PlayIDE roles (ADR-0215): every role is an actor you can choose, see the app as and run the built app as.

The assets are served after play.js, the role layer asks the kernel (`/api/play/access`) rather than reading the page,
the page learns each role's description, and the generated app opens acting as `#actor=<id>`, puts the acting role's
screens first and never labels a button with a word a workflow may use as an action. The browser test is marked
`browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise) and never downloads a browser.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces.http import create_app, pack_summary
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "src/eija_studio/resources/web"
APP = ROOT / "src/eija_studio/resources/appgen/web"
SESSION = "synthetic-play-roles-test"
ORIGIN = "http://127.0.0.1:8765"


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace"), SESSION)
    yield TestClient(app, base_url=ORIGIN)
    app.state.play.stop()


def test_the_play_page_loads_the_role_layer_after_play_js(client):
    page = client.get("/play").text
    assert page.index("/assets/play.js") < page.index("/assets/play-roles.js")
    assert 'id="role-lens"' in page and 'id="role-app"' in page
    for name in ("play-roles.js", "play-roles.css"):
        assert client.get(f"/assets/{name}").status_code == 200


def test_what_a_role_may_do_is_the_kernels_answer_not_a_reading_of_the_page():
    source = (WEB / "play-roles.js").read_text(encoding="utf-8")
    assert "fetch(" not in source
    assert set(re.findall(r'"(/api/[^"]+)"', source)) == {"/api/play/access"}  # the permissions matrix (ADR-0171)
    play = (WEB / "play.js").read_text(encoding="utf-8")
    assert "runAs, openScreen" in play and "for (const f of hooks.screens)" in play


def test_the_page_learns_each_roles_description():
    pack = load_pack(PACKS_ROOT / "library-loan")
    notes = pack_summary(pack)["role_notes"]
    assert notes == {r.id: r.description for r in pack.roles}
    assert notes["Clerk"] == "Flags overdue loans; never takes a return."


def test_the_generated_app_acts_as_the_linked_actor_and_folds_away_other_roles():
    page = (APP / "app.js.tmpl").read_text(encoding="utf-8")
    assert 'get("actor")' in page and "hashchange" in page  # PlayIDE's "Run as" opens #actor=<id>
    assert "o.role === role" in page and '"details"' in page  # the acting role's screens first, the rest folded
    assert '"Cancel"' not in page  # library-loan has an action named Cancel; the screen's own button says Close
    assert 'id="actor-role"' in (APP / "index.html.tmpl").read_text(encoding="utf-8")


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


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_see_the_app_as_a_role_and_inspect_an_actor_in_a_real_browser():
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

            page.click("#tab-screens")
            page.click(".lens-role[data-role=Clerk]")
            page.wait_for_selector("#role-app:not([hidden])")
            assert "A Clerk sees 2 of 6 screens." in page.inner_text("#role-app")
            assert page.locator("#screen-list li.not-theirs").count() == 4  # Create and MarkOverdue stay
            page.click("#role-app .role-flow li:nth-child(2) button")
            assert page.inner_text("#screen-card .role-note") == "A Clerk sees this screen."
            page.click("#screen-list li:nth-child(2) button")  # Cancel, a Member's
            assert "only a Member may take Cancel" in page.inner_text("#screen-card .role-note")
            assert page.get_attribute("#role-app .run-as.primary", "data-actor") == "clerk"

            page.click('.outline button[data-id="role:Librarian"]')
            page.wait_for_selector("#inspector .role-cases")
            assert [b.inner_text() for b in page.query_selector_all("#inspector .role-cases button")] == ["CheckOut", "Return", "ReturnLate"]
            assert "assigned only" in page.inner_text("#inspector .role-cases")
            assert "Checks loans out" in page.inner_text("#inspector")
            assert not page.query_selector("#inspector button:has-text('breakpoint')")
            assert errors == []
        finally:
            chrome.close()


def test_run_as_reuses_a_build_only_while_its_app_still_runs():
    play = (WEB / "play.js").read_text(encoding="utf-8")
    assert '!$("run").hidden && $("run-frame").src.startsWith(lastBuild.url)' in play  # Stop blanks the frame: build again


def test_the_generated_app_knows_which_actors_are_not_people():
    assert '"kinds": {r.id: r.kind for r in PACK.roles}' in (ROOT / "src/eija_studio/resources/appgen/server.py.tmpl").read_text(encoding="utf-8")
    assert "you stand in for its API calls" in (APP / "app.js.tmpl").read_text(encoding="utf-8")


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_an_ai_agent_has_no_screens_only_calls_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/refund-desk") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click("#tab-screens")
            page.click(".lens-role[data-role=SupportAgent]")
            page.wait_for_selector("#role-app .role-calls")
            assert "An AI agent (SupportAgent) has no screens." in page.inner_text("#role-app")
            calls = page.inner_text("#role-app .role-calls")
            assert '"action":"AssessRequest","actor":"support-bot"' in calls and '"action":"ProposeRefund"' in calls
            assert "ApproveRefund" not in calls  # only a person approves (ADR-0210)
            assert page.locator("#screen-list li").count() == page.locator("#screen-list li.not-theirs").count()
            assert page.inner_text("#role-app .run-as.primary") == "▶ Stand in for support-bot"
            page.click('.outline button[data-id="role:SlaTimer"]')
            page.wait_for_selector("#inspector .role-calls")
            assert "«timer»" in page.inner_text("#inspector") and "EscalateStale" in page.inner_text("#inspector .role-calls")
            assert errors == []
        finally:
            chrome.close()
