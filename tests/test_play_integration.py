"""PlayIDE features working together on the workbench shell, in a real browser: the chat's own example plan passes
the policy for the open pack, a paused run keeps who tried what in view, a role in the outline opens the Permissions
tab, the plan banner does not offer to open the Review tab while it is open, asking whether a
state can be reached at all treats Yes as expected, the status bar names the selection as the outline does,
an empty Review tab uses the whole tab, the screen designer fits a laptop screen,
the Tests tab's buttons, the review view's title bar and the Import / Export menu fit too,
and Ctrl+K reaches Systems but offers nothing that edits in the review view.

Marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed Chrome, or the
Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
@pytest.mark.parametrize("pack", ["library-loan", "excursion"])
def test_playide_features_fit_together_in_a_real_browser(pack):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs" / pack) as server, api.sync_playwright() as playwright:
        try:
            executable = os.environ.get("EIJA_CHROMIUM")
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            # With nothing to review, the Review tab's message takes the whole tab rather than leaving an empty column.
            page.click("#tab-review")
            page.wait_for_selector("#review[data-empty] .review-canvas .empty")
            assert page.is_hidden("#review .review-list")
            page.click("#tab-states")
            # The example the chat offers is a plan the policy accepts, sent exactly as shown.
            page.fill("#chat-input", page.text_content("#chat-example"))
            page.click("#chat-send")
            preview = page.get_by_role("button", name="Preview on the diagram").first
            preview.wait_for(timeout=30_000)
            assert preview.is_enabled(), page.text_content("#chat-log")
            preview.click()
            page.wait_for_selector("#plan-banner:not([hidden])")
            assert page.is_visible("#plan-review")
            page.click("#plan-review")
            page.wait_for_selector("#review:not([hidden])")
            assert page.is_hidden("#plan-review")  # already there
            page.wait_for_selector("#review:not([data-empty]) .review-list")
            page.click("#plan-back")
            page.click("#tab-states")
            # A role is not a diagram element: the inspector says what that role may do (ADR-0215), and links to permissions.
            page.locator("#outline-roles button").first.click()
            page.wait_for_selector("#inspector .role-cases")
            page.click("#inspector button:has-text('Who can do what')")
            page.wait_for_selector("#access-panel:not([hidden])")
            # Asked whether a record can reach a state at all, Yes is the expected answer, not a warning.
            page.click(".reach button.primary")
            page.wait_for_selector(".reach-answer .verdict.ok")
            page.click("#tab-states")
            # Paused on a breakpoint, the panel shows who tried what, not only the foot of the log.
            page.locator("#outline-transitions button").first.click()
            # The status bar names the selection as the outline does, not by its id.
            assert page.text_content("#status-selection") == "transition " + page.locator("#outline-transitions button").first.text_content()
            page.locator("#outline-states button").nth(1).click()
            page.keyboard.press("F9")
            before = page.locator("#simulate").bounding_box()
            page.click("#run-play")
            page.wait_for_selector("#run-status:has-text('Paused')", timeout=60_000)
            assert page.locator("#simulate").bounding_box()["x"] == before["x"]  # the run status does not push the tool bar
            now, body = page.locator("#debug-now").bounding_box(), page.locator(".dock-body").bounding_box()
            assert now and body and body["y"] <= now["y"] < body["y"] + body["height"]
            # On a laptop screen with the side bar and the chat open, the screen designer stacks the record attributes
            # under the screen rather than squeezing it, so nothing spills sideways.
            page.set_viewport_size({"width": 1280, "height": 800})
            page.click("#tab-screens")
            page.wait_for_selector("#screen-card .screen-field")
            assert page.evaluate("""() => { const d = document.getElementById('screens');
                return d.scrollWidth <= d.clientWidth && document.getElementById('screen-card').clientWidth >= 360; }""")
            # The Tests tab's buttons stay inside the tab, and the review view's title bar keeps its buttons on one line.
            page.click("#tab-tests")
            page.wait_for_selector("#tests-file:not(:empty)")  # the file chip widens the text beside the buttons
            assert page.evaluate("""() => { const t = document.getElementById('tests'), r = t.getBoundingClientRect();
                return t.scrollWidth <= t.clientWidth
                    && [...t.querySelectorAll('.head-tools button')].every((b) => b.getBoundingClientRect().right <= r.right - 8); }""")
            # Ctrl+K reaches Systems; in the review view it offers nothing that changes the model.
            options = """() => [...document.querySelectorAll('.palette-dialog [role=option]')].map((e) => e.textContent)"""
            page.keyboard.press("Control+k")
            page.keyboard.type("system")
            assert any("Open another system" in o for o in page.evaluate(options))
            page.keyboard.press("Escape")
            # The Import / Export menu wraps its longer lines rather than spilling past its edge.
            page.click("#uml-menu")
            page.wait_for_selector("#uml-pop:not([hidden])")
            assert page.evaluate("""() => { const p = document.getElementById('uml-pop'), r = p.getBoundingClientRect();
                return [...p.querySelectorAll('span')].every((s) => s.getBoundingClientRect().right <= r.right); }""")
            page.keyboard.press("Escape")
            page.goto(f"{server.base_url}/play?view=review#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.evaluate("""() => { const tops = [...document.querySelectorAll('.bar-end > *')].filter((e) => e.offsetParent)
                .map((e) => e.getBoundingClientRect()); return tops.every((r) => r.height < 40 && Math.abs(r.top - tops[0].top) < 8); }""")
            page.keyboard.press("Control+k")
            page.keyboard.type("undo")
            assert not any("Undo" in o for o in page.evaluate(options))
            page.keyboard.press("Escape")
            assert errors == []
        finally:
            chrome.close()
