"""PlayIDE assist (ADR-0170): the assets are served, and in a real browser the page asks about the selection, completes
exact names, holds a request with an unfilled blank, opens the command palette and reviews a plan from the keyboard.

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
SESSION = "synthetic-play-assist-test"
ORIGIN = "http://127.0.0.1:8765"
OPEN, CLOSE = "\u2039", "\u203a"  # the blank markers the page writes, e.g. \u2039role\u203a


def blank(kind: str) -> str:
    return f"{OPEN}{kind}{CLOSE}"


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace"), SESSION)
    yield TestClient(app, base_url=ORIGIN)
    app.state.play.stop()


def test_the_play_page_loads_the_assist_layer_after_play_js(client):
    page = client.get("/play").text
    assert page.index("/assets/play.js") < page.index("/assets/play-assist.js")
    assert "/assets/play-assist.css" in page
    for name in ("play-assist.js", "play-assist.css"):
        assert client.get(f"/assets/{name}").status_code == 200


def test_the_assist_layer_only_reads_the_page_view_and_never_calls_the_api():
    source = (ROOT / "src/eija_studio/resources/web/play-assist.js").read_text(encoding="utf-8")
    assert "fetch(" not in source and "/api/" not in source  # it presses the page's controls; the server decides
    play = (ROOT / "src/eija_studio/resources/web/play.js").read_text(encoding="utf-8")
    assert "base: () => baseModel" in play and 'new CustomEvent("playide:select"' in play


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
def test_ask_complete_palette_and_keyboard_review_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-assist=ready]", timeout=60_000)
            assert "Owner approves and applies" in page.inner_text("#authority")

            page.click('.outline button[data-id="state:Overdue"]')
            assert "About Overdue" in page.text_content("#chat-suggest")
            page.click('#chat-suggest button:has-text("Add a state after")')
            page.keyboard.type("Lost")
            page.click('#chat-suggest button:has-text("Add a transition from here")')
            assert page.input_value("#chat-input") == f"add state Lost after Overdue then add {blank('action')} from Overdue to {blank('state')} for {blank('role')}"
            page.keyboard.type("Ren")
            page.keyboard.press("Enter")  # completes the action and selects the next blank
            assert "Lost" in page.inner_text("#chat-complete")  # a state the request itself adds is offered
            page.keyboard.type("Lost")
            page.keyboard.press("Tab")
            page.keyboard.press("Control+Enter")
            assert page.inner_text("#chat-hint") == f"Fill in {blank('role')} first."
            assert not page.query_selector("#chat-log .plan")  # held, not sent
            page.keyboard.type("C")  # typed over the role blank: only roles are offered, not CheckOut or Cancel
            assert page.inner_text("#chat-complete").split() == ["Clerk", "ROLE"]
            page.keyboard.press("Backspace")
            page.keyboard.type("Librarian")
            page.keyboard.press("Control+Enter")
            page.wait_for_selector("#chat-log .plan .plan-verdict.ok", timeout=30_000)

            page.keyboard.press("Control+k")
            page.keyboard.type("review")
            page.keyboard.press("Enter")
            assert page.evaluate("document.activeElement.id").endswith("-0")
            page.keyboard.press("s")
            page.keyboard.press("j")
            page.keyboard.press("s")
            assert "Looked at AI step 2" in page.inner_text("#earned")
            page.keyboard.press("Space")  # the checkbox's own toggle rejects step 2
            page.wait_for_selector("#chat-log .plan .plan-verdict:has-text('1 of 2 steps accepted')", timeout=30_000)

            page.keyboard.press("Control+k")
            page.keyboard.type("ask cancelled")
            page.keyboard.press("Enter")
            assert page.evaluate("document.activeElement.id") == "chat-input"
            assert "About Cancelled" in page.text_content("#chat-suggest")
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_the_review_view_keeps_diagrams_and_simulate_and_hides_every_editing_tool():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with (
        ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server,
        api.sync_playwright() as playwright,
    ):
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play?view=review#{server.token}")
            page.wait_for_selector("body[data-assist=ready]", timeout=60_000)
            assert "Review view" in page.inner_text("#review-badge")
            for hidden in ("#draw-palette", ".side .chat"):
                assert not page.is_visible(hidden)
            page.click('.outline button[data-id="state:Overdue"]')
            assert page.locator("#inspector .edit-tools").count() == 1 and not page.is_visible("#inspector .edit-tools")
            page.keyboard.press("Delete")  # would add a removal to a plan in the editing view
            assert page.locator("#chat-log .plan").count() == 0
            page.click("#tab-screens")
            assert page.evaluate("document.getElementById('screen-card').inert") and not page.is_visible("#screens .palette")
            page.click("#tab-states")
            page.click("#simulate")
            page.wait_for_selector("#sim-summary:has-text('refused by the kernel')", timeout=60_000)
            page.keyboard.press("Control+k")
            page.keyboard.type("ai")
            assert "Ask the AI" not in page.inner_text("#palette-list")
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_a_failed_request_can_be_edited_without_losing_the_plan_or_newer_composer_text():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser fixture

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.fill("#chat-input", "add state Archived after Returned")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .plan .plan-verdict.ok", timeout=30_000)
            previous = page.evaluate("PlayIDE.draft()")
            pending = []

            def hold_request(route):
                pending.append(route)  # Playwright attaches metadata, so its handler must be a Python function.

            page.route("**/api/play/plan", hold_request)
            request = "add Renew from Overdue to OnLoan for Librarian"
            page.fill("#chat-input", request)
            # Programmatic duplicate submit bypasses the disabled button, exercising the in-flight guard.
            with page.expect_request("**/api/play/plan"):
                page.evaluate("""() => {
                    document.getElementById('chat-form').dispatchEvent(new Event('submit', {cancelable: true}));
                    document.getElementById('chat-input').value = 'newer request';
                    document.getElementById('chat-form').dispatchEvent(new Event('submit', {cancelable: true}));
                }""")
            assert page.is_disabled("#chat-send") and len(pending) == 1
            page.fill("#chat-input", "keep this newer idea")
            pending[0].fulfill(status=503, json={"code": "PROVIDER_UNAVAILABLE", "message": "Try again later."})
            failure = page.locator(".request-failure").last
            failure.get_by_role("button", name="Edit request", exact=True).wait_for()
            assert page.evaluate("PlayIDE.draft()") == previous
            assert page.is_enabled("#chat-send")
            failure.get_by_role("button", name="Edit request", exact=True).click()
            assert page.input_value("#chat-input") == "keep this newer idea"
            assert len(pending) == 1
            failure.get_by_role("button", name="Keep newer text", exact=True).click()
            assert page.input_value("#chat-input") == "keep this newer idea"
            failure.get_by_role("button", name="Edit request", exact=True).click()
            failure.get_by_role("button", name="Replace composer with this request", exact=True).click()
            assert page.input_value("#chat-input") == request
            assert page.evaluate("document.activeElement.id") == "chat-input"
            assert len(pending) == 1  # editing never submits automatically
            with page.expect_request("**/api/play/plan"):
                page.click("#chat-send")
            assert len(pending) == 2
            pending[1].fulfill(status=503, json={"code": "PROVIDER_UNAVAILABLE", "message": "Still unavailable."})
            page.locator(".request-failure").nth(1).wait_for()
            page.locator(".request-failure").nth(1).get_by_role("button", name="Edit request", exact=True).click()
            assert page.input_value("#chat-input") == request
            assert len(pending) == 2 and page.evaluate("PlayIDE.draft()") == previous
        finally:
            chrome.close()
