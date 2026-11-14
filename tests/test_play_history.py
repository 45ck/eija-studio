"""PlayIDE undo, redo and autosave (ADR-0198): every edit is one undoable step, and the work survives a reload.

The browser test is marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed
Chrome, or the Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import json
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
            assert page.text_content("#status-saved").endswith("Edits kept in this browser")
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


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_a_saved_draft_opens_as_an_undoable_edit_and_newer_kept_work_wins_in_a_real_browser():
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
            page.fill("#chat-input", "add state Archived after Returned")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .msg.ai .plan .plan-verdict")
            page.click("#system-save")
            page.wait_for_selector("#system-saved[data-dirty=false]", state="attached")
            # Without this browser's copy, a reload opens the saved draft, and opening it is one undoable edit.
            page.evaluate("() => localStorage.clear()")
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.wait_for_selector("#chat-log .plan .plan-verdict")
            assert page.get_attribute("#undo", "title") == "Undo open the saved work (Ctrl+Z)"
            assert page.locator("#chat-log .recovered").count() == 0
            # A change after the save is kept by the browser; on reload it comes back instead of the older save.
            page.uncheck("#chat-log .plan .plan-steps > li:nth-child(1) input")
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(1).rejected")
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.wait_for_selector("#chat-log .recovered")
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(1).rejected")
            page.wait_for_timeout(1000)  # the Save mark refreshes on a timer
            assert page.text_content("#status-saved").startswith("Unsaved changes · ")
            # Saving it makes the two agree again.
            page.click("#system-save")
            page.wait_for_selector("#system-saved[data-dirty=false]", state="attached")
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_navigation_recovers_without_an_edit_and_rejects_stale_or_foreign_selection():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser fixture

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click('.outline button[data-id="state:Overdue"]')
            page.click("#tab-screens")
            kept = page.evaluate("""() => {
                const pack = PlayIDE.pack().id;
                const key = `playide.navigation.v1:${pack}:`;
                return {key, value: JSON.parse(localStorage.getItem(key)),
                    draft: localStorage.getItem(`playide.draft.v1:${pack}:`)};
            }""")
            assert kept["value"] == {"v": 1, "tab": "screens", "selected": "state:Overdue"}
            assert kept["draft"] is None  # navigation does not create an edit or an undo step
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.get_attribute("#tab-screens", "aria-selected") == "true"
            assert page.text_content("#inspector h3") == "State Overdue"
            assert page.is_disabled("#undo") and page.is_hidden("#run")
            assert page.evaluate("PlayIDE.runningBuild()") is None

            # A different case and a different pack cannot supply this view's selection.
            page.evaluate("""key => {
                localStorage.removeItem(key);
                localStorage.setItem(key + 'another-case', JSON.stringify({v: 1, tab: 'laws', selected: 'state:Overdue'}));
                localStorage.setItem('playide.navigation.v1:another-pack:', JSON.stringify({v: 1, tab: 'laws', selected: 'state:Overdue'}));
            }""", kept["key"])
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.evaluate("PlayIDE.tab()") == "states"
            assert page.evaluate("PlayIDE.selected()") == ""

            # Browser storage is untrusted. Removed elements and unsupported tabs are not reopened.
            page.evaluate("""key => localStorage.setItem(key, JSON.stringify({v: 1,
                tab: 'missing-panel', selected: 'transition:REMOVED', approved: true, checks: 'PASS'}))""", kept["key"])
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.evaluate("PlayIDE.tab()") == "states"
            assert page.evaluate("PlayIDE.selected()") == ""
            assert page.evaluate("PlayIDE.runningBuild()") is None
            assert page.evaluate("key => Object.keys(JSON.parse(localStorage.getItem(key))).sort()", kept["key"]) == ["selected", "tab", "v"]
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_navigation_is_restored_after_the_draft_model_is_checked():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser fixture

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.fill("#chat-input", "add state Lost after Overdue then add Renew from Overdue to Lost for Librarian")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .plan .plan-verdict.ok", timeout=30_000)
            page.click('#chat-log .plan .plan-tools .primary:has-text("Preview on the diagram")')
            page.click('.outline button[data-id="state:Lost"]')
            page.click("#tab-classes")
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.wait_for_selector("#chat-log .recovered")
            assert page.get_attribute("#tab-classes", "aria-selected") == "true"
            assert page.evaluate("PlayIDE.selected()") == "state:Lost"
            assert page.text_content("#inspector h3") == "State Lost"
            assert "Lost" not in page.evaluate("PlayIDE.base().states")
            assert "Lost" in page.evaluate("PlayIDE.model().states")
            assert page.evaluate("PlayIDE.runningBuild()") is None
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_a_kept_draft_the_page_cannot_read_is_set_aside_and_the_page_still_opens():
    """Browser storage is untrusted (ADR-0236): before, a draft in another shape stopped the page opening on every reload."""
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser fixture

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            key = page.evaluate("() => `playide.draft.v1:${PlayIDE.pack().id}:`")
            page.click('#draw-palette [data-kind="state"]')
            box = page.locator("#canvas").bounding_box()
            page.mouse.click(box["x"] + 12, box["y"] + 12)
            page.wait_for_selector(".inline-edit input:focus")
            page.keyboard.type("Archived")
            page.keyboard.press("Enter")
            page.wait_for_selector("#plan-banner:not([hidden])")
            real = page.evaluate("k => JSON.parse(localStorage.getItem(k))", key)
            good = real["stack"][-1]
            broken = {
                "at as text": {**real, "at": str(real["at"])},
                "plan without steps": {**real, "stack": [{**good, "doc": {"plan": {"uid": 1}}}], "at": 0},
                "an empty entry": {**real, "stack": [None, good], "at": 1},
                "no document": {**real, "stack": [{**good, "doc": None}], "at": 0},
                "steps not a list": {**real, "stack": [{**good, "doc": {"plan": {"uid": 1, "steps": "x", "accepted": []}}}], "at": 0},
            }
            for name, draft in broken.items():
                raw = json.dumps(draft)
                page.evaluate("([k, v]) => { localStorage.removeItem(k + ':unreadable'); localStorage.setItem(k, v); }", [key, raw])
                page.reload()
                page.wait_for_selector("body[data-ready=true]", timeout=20_000)
                assert page.is_hidden("#plan-banner") and page.is_disabled("#undo"), name  # the model in force, no plan
                assert page.evaluate("k => localStorage.getItem(k + ':unreadable')", key) == raw, name  # set aside, not lost
                assert "could not read" in page.text_content("#chat-log"), name
            # A second unreadable draft is set aside beside the first, never over it.
            raw = json.dumps(broken["no document"])
            page.evaluate("([k, v]) => { localStorage.setItem(k + ':unreadable', 'earlier'); localStorage.setItem(k, v); }", [key, raw])
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=20_000)
            assert page.evaluate("k => [localStorage.getItem(k + ':unreadable'), localStorage.getItem(k + ':unreadable:2')]", key) == ["earlier", raw]
            # A good draft still comes back.
            page.evaluate("([k, v]) => localStorage.setItem(k, v)", [key, json.dumps(real)])
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=20_000)
            assert "Recovered your unsaved work" in page.text_content("#chat-log")
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_a_draft_kept_on_an_earlier_model_is_not_overwritten_by_the_next_edit():
    """Inspection 2026-11-13 (ADR-0245): the note said an earlier browser draft "is retained", but the first edit on the
    new model wrote this browser's draft under the same key, so after a reload the earlier draft was gone."""
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser fixture

    def place(page, name):
        page.click('#draw-palette [data-kind="state"]')
        box = page.locator("#canvas").bounding_box()
        page.mouse.click(box["x"] + 12, box["y"] + 12)
        page.wait_for_selector(".inline-edit input:focus")
        page.keyboard.type(name)
        page.keyboard.press("Enter")
        page.wait_for_selector("#plan-banner:not([hidden])")

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            key = page.evaluate("() => `playide.draft.v1:${PlayIDE.pack().id}:`")
            place(page, "Archived")
            earlier = page.evaluate("k => JSON.parse(localStorage.getItem(k))", key)
            earlier["model"] = "0"  # written on another model in force
            raw = json.dumps(earlier)
            page.evaluate("([k, v]) => localStorage.setItem(k, v)", [key, raw])
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=20_000)
            assert "An earlier browser draft is retained" in page.text_content("#chat-log")
            assert page.evaluate("k => localStorage.getItem(k + ':earlier')", key) == raw
            place(page, "Shelved")  # an edit on the new model: kept under the draft key, the earlier one beside it
            assert page.evaluate("k => localStorage.getItem(k + ':earlier')", key) == raw
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=20_000)
            log = page.text_content("#chat-log")  # the newer work comes back, and the earlier draft is still offered
            assert "Recovered your unsaved work" in log and "An earlier browser draft is retained" in log
            # A second retained draft (numbered key) is offered too.
            page.evaluate("([k, v]) => localStorage.setItem(k + ':earlier:2', v)", [key, json.dumps({**earlier, "saved": earlier["saved"] + 1})])
            page.evaluate("k => localStorage.removeItem(k)", key)
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=20_000)
            assert page.locator("#chat-log .recovered button:text-is('Reopen earlier draft')").count() == 2
            page.locator("text=Reopen earlier draft").first.click()
            page.wait_for_selector("#plan-banner:not([hidden])")
            assert "Archived" in page.evaluate("() => JSON.stringify(PlayIDE.document().plan.steps)")
            assert page.evaluate("k => localStorage.getItem(k + ':earlier')", key) is None  # reopened: now the draft
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_recovered_work_that_matches_the_saved_draft_is_not_unsaved():
    """Inspection 2026-11-13 (ADR-0245, D6): the saved draft was compared without each step's round and request, so the
    same work, recovered from this browser after a reload, showed "Unsaved changes" and asked before leaving."""
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
            page.wait_for_selector("#chat-log .msg.ai .plan .plan-verdict")
            page.click("#system-save")
            page.wait_for_selector("#system-saved[data-dirty=false]", state="attached")
            page.reload()  # this browser's copy comes back: the same work as the save
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.wait_for_selector("#chat-log .recovered")
            page.wait_for_timeout(1000)  # the Save mark refreshes on a timer
            assert page.get_attribute("#system-saved", "data-dirty") == "false"
            assert page.is_disabled("#system-save")
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_an_outdated_browser_draft_is_not_recovered_as_the_latest_work_when_storage_is_full():
    """Inspection 2026-11-13 (ADR-0245, D10): when storage could not hold even the current snapshot, the previous draft
    stayed under the key, and a reload brought that older work back as "your unsaved work"."""
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser fixture

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            key = page.evaluate("() => `playide.draft.v1:${PlayIDE.pack().id}:`")
            page.fill("#chat-input", "add state Archived after Returned")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .msg.ai .plan .plan-verdict")
            older = page.evaluate("k => localStorage.getItem(k)", key)
            # Storage is now full for the draft key: the next edit cannot be kept.
            page.evaluate("""k => { const set = Storage.prototype.setItem;
                Storage.prototype.setItem = function (name, value) { if (name === k) throw new DOMException("full", "QuotaExceededError"); return set.call(this, name, value); }; }""", key)
            page.uncheck("#chat-log .plan .plan-steps > li:nth-child(1) input")
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(1).rejected")
            assert "Not kept" in page.text_content("#status-saved")
            assert page.evaluate("k => [localStorage.getItem(k), localStorage.getItem(k + ':earlier')]", key) == [None, older]
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            log = page.text_content("#chat-log")
            assert "Recovered your unsaved work" not in log and "An earlier browser draft from" in log
            # Reopening it while storage is still full keeps the retained copy: it is the only one a reload would find.
            page.evaluate("""k => { const set = Storage.prototype.setItem;
                Storage.prototype.setItem = function (name, value) { if (name === k) throw new DOMException("full", "QuotaExceededError"); return set.call(this, name, value); }; }""", key)
            page.click("text=Reopen earlier draft")
            page.wait_for_selector("#chat-log .plan .plan-verdict")
            assert page.evaluate("k => localStorage.getItem(k + ':earlier')", key) == older
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_an_edit_made_while_undo_reloads_the_screens_is_kept():
    """Inspection 2026-11-13 (ADR-0245, D7): undoing a screen edit waited for the server's screens with the restore
    still in progress, so an edit made in that wait was applied but left out of the history and the browser draft."""
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser fixture

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.fill("#chat-input", "add state Archived after Returned")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .msg.ai .plan .plan-verdict")
            page.click("#tab-screens")
            page.wait_for_selector("#screen-card .screen-title")
            page.fill("#screen-card .screen-title", "Borrow a book")
            page.press("#screen-card .screen-title", "Enter")
            page.click("#tab-states")
            assert page.get_attribute("#undo", "title") == "Undo retitle a screen (Ctrl+Z)"
            # The server is slow to send the model's own screens back.
            page.evaluate("""() => { const real = window.fetch; window.fetch = (url, ...rest) => String(url).includes('/api/play/screens')
                ? new Promise((done) => setTimeout(() => done(real(url, ...rest)), 1500)) : real(url, ...rest); }""")
            page.click("#undo")  # the screen edit: its screens reload while the person keeps working
            page.uncheck("#chat-log .plan .plan-steps > li:nth-child(1) input")
            page.wait_for_selector("#chat-log .plan .plan-steps > li:nth-child(1).rejected")
            page.wait_for_timeout(2000)
            assert page.get_attribute("#undo", "title") == "Undo reject step 1 (Ctrl+Z)"
            assert page.evaluate("() => PlayIDE.document().plan.accepted") == [False]
            key = page.evaluate("() => `playide.draft.v1:${PlayIDE.pack().id}:`")
            kept = page.evaluate("k => JSON.parse(localStorage.getItem(k))", key)
            assert kept["stack"][kept["at"]]["label"] == "reject step 1"
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_two_tabs_on_one_system_keep_each_others_work():
    """Inspection 2026-11-14 (ADR-0250, D15 and D16): two tabs on one system shared the browser draft key, so the tab
    that wrote last replaced the other tab's kept work (and one that undid back to nothing deleted it), and each
    tab's Save replaced the other's saved draft unseen."""
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser fixture

    def ask(page, text):
        page.fill("#chat-input", text)
        page.click("#chat-send")
        page.wait_for_selector("#chat-log .msg.ai .plan .plan-verdict")

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            context = chrome.new_context(viewport={"width": 1600, "height": 900})
            first, second = context.new_page(), context.new_page()
            errors: list[str] = []
            for page in (first, second):
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"{server.base_url}/play#{server.token}")
                page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            ask(first, "add state Archived after Returned")
            ask(second, "add state Shelved after Returned")  # the other tab's work is kept beside, not replaced
            key = first.evaluate("() => `playide.draft.v1:${PlayIDE.pack().id}:`")
            kept = first.evaluate("k => Object.keys(localStorage).filter((x) => x.startsWith(k)).map((x) => localStorage.getItem(x)).join(' ')", key)
            assert "Archived" in kept and "Shelved" in kept
            second.wait_for_selector("#chat-log .recovered:has-text('open in another tab too')")
            # Save in the first tab, then in the second: the second is refused until pressed again.
            first.click("#system-save")
            first.wait_for_selector("#system-saved[data-dirty=false]", state="attached")
            second.click("#system-save")
            second.wait_for_selector("#system-saved:has-text('DRAFT_CHANGED')", state="attached")
            saved = second.evaluate("() => PlayIDE.api('/api/play/draft')")["draft"]
            assert saved["steps"][0]["transaction"]["state"] == "Archived"
            second.click("#system-save")
            second.wait_for_selector("#system-saved[data-dirty=false]", state="attached")
            assert second.evaluate("() => PlayIDE.api('/api/play/draft')")["draft"]["steps"][0]["transaction"]["state"] == "Shelved"
            # The first tab closes; a reload of the second offers the first tab's work to reopen.
            first.close()
            second.reload()
            second.wait_for_selector("body[data-ready=true]", timeout=60_000)
            log = second.text_content("#chat-log")
            assert "Recovered your unsaved work" in log and "Work from another tab on this system" in log
            second.locator("text=Reopen earlier draft").first.click()
            second.wait_for_selector("#plan-banner:not([hidden])")
            assert "Archived" in second.evaluate("() => JSON.stringify(PlayIDE.document().plan.steps)")
            assert errors == []
        finally:
            chrome.close()
