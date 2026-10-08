"""PlayIDE undo, redo and autosave (ADR-0190): every edit is one undoable step, and the work survives a reload.

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
SESSION = "synthetic-play-history-test"
ORIGIN = "http://127.0.0.1:8765"


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace"), SESSION)
    yield TestClient(app, base_url=ORIGIN)
    app.state.play.stop()


def test_the_page_has_undo_and_redo_hidden_from_the_review_view(client):
    page = client.get("/play").text
    for id_ in ("undo", "redo", "status-saved"):
        assert page.count(f'id="{id_}"') == 1, id_
    toolbar = page[page.index('id="history"') - 60:page.index('id="runbar"')]
    assert "edit-tools" in toolbar  # hidden in ?view=review (ADR-0172)
    script = client.get("/assets/play.js").text
    assert 'addEventListener("keydown", historyKeys)' in script and "localStorage" in script


browser = pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1",
                             reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")


def _launch(api, playwright):
    try:
        executable = os.environ.get("EIJA_CHROMIUM")
        if executable:
            return playwright.chromium.launch(headless=True, executable_path=executable)
        return playwright.chromium.launch(channel="chrome", headless=True)
    except api.Error as exc:
        pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_undo_redo_and_recovery_after_a_reload_in_a_real_browser():
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
            assert page.is_disabled("#undo") and page.is_disabled("#redo")
            # The palette places a state (pick it, click empty space, name it): a step of your own, previewed.
            page.click('#draw-palette [data-kind="state"]')
            box = page.locator("#canvas").bounding_box()
            page.mouse.click(box["x"] + 12, box["y"] + 12)
            page.wait_for_selector(".inline-edit input:focus")
            page.keyboard.type("Archived")
            page.keyboard.press("Enter")
            page.wait_for_selector("#plan-banner:not([hidden])")
            assert page.get_attribute("#undo", "title") == "Undo add state Archived (Ctrl+Z)"
            # Ctrl+Z on the diagram: the drawn plan is gone and the model is back.
            page.click("#canvas")
            page.keyboard.press("Control+KeyZ")
            page.wait_for_selector("#plan-banner", state="hidden")
            assert page.locator("#chat-log .plan").count() == 0 and page.is_disabled("#undo") and page.is_enabled("#redo")
            assert "Undid: add state Archived" in page.text_content("#toast")
            # Ctrl+Shift+Z brings it back, checked by the server again and previewed.
            page.keyboard.press("Control+Shift+KeyZ")
            page.wait_for_selector("#plan-banner:not([hidden])")
            page.wait_for_selector("#chat-log .plan .plan-verdict.ok")
            # A second edit (a role change from the inspector), then rejecting the first step: three snapshots.
            page.click('.outline button[data-id="transition:TR-MARKOVERDUE"]')
            page.click('#inspector .edit-tools button:text-is("Let Librarian take it")')
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(2).applies")
            assert page.get_attribute("#undo", "title") == "Undo let Librarian take MarkOverdue (Ctrl+Z)"
            page.uncheck("#chat-log .plan .plan-steps > li:nth-child(1) input")
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(1).rejected")
            assert page.get_attribute("#undo", "title").startswith("Undo reject step 1")
            assert page.text_content("#status-saved") == "Saved in this browser"
            # A screen edit is undoable too.
            page.click("#tab-screens")
            page.wait_for_selector("#screen-card .screen-title")
            page.fill("#screen-card .screen-title", "Borrow a book")
            page.press("#screen-card .screen-title", "Enter")
            page.click("#tab-states")
            page.click("#undo")
            page.click("#tab-screens")
            assert page.input_value("#screen-card .screen-title") != "Borrow a book"
            page.click("#redo")
            assert page.input_value("#screen-card .screen-title") == "Borrow a book"
            # A reload (or a crash) loses nothing: the plan, its ticks and the screens come back, with their history.
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.wait_for_selector("#chat-log .recovered")
            assert "2 plan steps and screen edits" in page.text_content("#chat-log .recovered")
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(1).rejected")
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(2).applies")
            assert page.is_checked("#chat-log .plan .plan-steps > li:nth-child(2) input")
            page.click("#tab-screens")
            assert page.input_value("#screen-card .screen-title") == "Borrow a book"
            page.click("#tab-states")
            page.click("#undo")  # the screen edit
            page.click("#undo")  # rejecting step 1
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(1).applies")
            # An AI plan is one edit: undoing it sets its card aside in the chat; redo brings it back.
            page.click('#chat-log .recovered button:text-is("Discard it")')
            page.wait_for_selector("#chat-log .plan", state="detached")
            page.fill("#chat-input", "add state Archived after Returned")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .msg.ai .plan .plan-verdict")
            page.click("#canvas")
            page.keyboard.press("Control+KeyZ")
            page.wait_for_selector("#chat-log .msg.ai .plan >> text=Undone.")
            assert page.is_disabled("#chat-log .msg.ai .plan .plan-tools .primary")
            page.keyboard.press("Control+KeyY")
            page.wait_for_selector("#chat-log .msg.ai .plan >> text=Undone.", state="detached")
            assert page.is_enabled("#chat-log .msg.ai .plan .plan-steps input")
            # Typing in the chat keeps the browser's own text undo.
            page.fill("#chat-input", "hello")
            page.press("#chat-input", "Control+KeyZ")
            assert page.locator("#chat-log .msg.ai .plan >> text=Undone.").count() == 0
            # The review view neither restores nor offers to undo.
            page.goto(f"{server.base_url}/play?view=review#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.is_hidden("#undo") and page.locator("#chat-log .recovered").count() == 0
            assert errors == []
        finally:
            chrome.close()
