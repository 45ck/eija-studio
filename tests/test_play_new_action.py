"""Drawing a transition on a system you started may name a new action or role (ADR-0201): the canvas offers the declared
names and accepts a new one, which the step declares, as chat already could. A shipped pack keeps its fixed list.

The served check runs everywhere; the browser test is marked `browser` and runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN
otherwise). It uses the installed Chrome, or the Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from test_play_greenfield import HEADERS, SKETCH, post, served  # noqa: F401 - served is a fixture
from test_play_place import CENTRE, _at, _launch, _steps

ROOT = Path(__file__).resolve().parents[1]


def test_the_status_says_whether_the_open_system_is_your_own(served):  # noqa: F811 - the fixture
    client, _ = served
    assert client.get("/api/status", headers=HEADERS).json()["pack"]["own_system"] is False
    post(client, "/api/play/systems/new", {"name": "Coffee orders", "record": "Order", "sketch": SKETCH})
    assert client.get("/api/status", headers=HEADERS).json()["pack"]["own_system"] is True


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_a_drawn_transition_can_name_a_new_action_on_your_own_system_in_a_real_browser():
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
            # A shipped pack: the action is picked from its fixed list.
            page.click('#draw-palette [data-kind="transition"]')
            page.mouse.click(*_at(page, CENTRE, "state:Overdue"))
            page.mouse.click(*_at(page, CENTRE, "state:Returned"))
            page.wait_for_selector(".inline-edit select:focus")
            page.keyboard.press("Escape")

            # Start your own system, then draw a transition with an action it does not declare yet.
            status = page.evaluate("""async ([token, sketch]) => (await fetch('/api/play/systems/new', { method: 'POST',
                headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: 'Coffee orders', record: 'Order', sketch }) })).status""", [server.token, SKETCH])
            assert status == 200
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click('#draw-palette [data-kind="transition"]')
            page.mouse.click(*_at(page, CENTRE, "state:Ready"))
            page.mouse.click(*_at(page, CENTRE, "state:Placed"))
            page.wait_for_selector(".inline-edit input:focus")
            page.keyboard.press("Control+A")
            page.keyboard.type("Remake")
            assert "New action: the step declares Remake" in page.inner_text(".inline-edit")
            page.keyboard.press("Enter")
            _steps(page, 1)
            page.wait_for_selector(".msg .plan-verdict", timeout=30_000)
            assert "Remake" in page.inner_text(".msg .plan-steps")
            assert "allows" in page.inner_text(".msg .plan-verdict")
            assert errors == []
        finally:
            chrome.close()
