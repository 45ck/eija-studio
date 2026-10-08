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
    assert "pack: () => packInfo" in play and 'new CustomEvent("playide:select"' in play


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
