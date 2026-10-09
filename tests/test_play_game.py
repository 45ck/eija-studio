"""PlayIDE game layer (ADR-0208): the assets are served, the layer only listens to the page and never awards points or
calls the server, and in a real browser its moments follow real results: the next check to run, the ring's ready state
once every check passes, a dot for each step the kernel decided, a nudge when a change makes a build stale, and a
"caught it" note when unticking an AI step turns a refused plan into one the policy allows.

The browser test is marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed
Chrome, or the Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "src/eija_studio/resources/web"
SESSION = "synthetic-play-game-test"
ORIGIN = "http://127.0.0.1:8765"
CARD = ".msg.ai:last-child"


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace"), SESSION)
    yield TestClient(app, base_url=ORIGIN)
    app.state.play.stop()


def test_the_play_page_loads_the_game_layer_after_play_js(client):
    page = client.get("/play").text
    assert page.index("/assets/play.js") < page.index("/assets/play-game.js")
    for name in ("play-game.js", "play-game.css"):
        assert client.get(f"/assets/{name}").status_code == 200


def test_the_game_layer_listens_and_never_awards_or_calls_the_server():
    source = (WEB / "play-game.js").read_text(encoding="utf-8")
    assert "fetch(" not in source and "/api/" not in source and "localStorage" not in source
    assert not re.search(r"\bearn\(", source)  # play.js awards points; this layer only shows them
    play = (WEB / "play.js").read_text(encoding="utf-8")
    for event in ("playide:checks", "playide:earn", "playide:step", "playide:simulated"):
        assert f'new CustomEvent("{event}"' in play or f'new CustomEvent("{event}"' in (WEB / "play-run.js").read_text(encoding="utf-8")
    # Every check on the ring has a stable id the layer keys its moments on.
    assert all(f'id: "{check}"' in play for check in ("ai", "screens", "conformance", "simulated")) and 'id = "ripple"' in play


def test_every_animation_stops_for_reduced_motion():
    css = (WEB / "play-game.css").read_text(encoding="utf-8")
    animated = set(re.findall(r"([.#][\w.#-]+)\{[^}]*animation:game-", css))
    reduced = css[css.index("prefers-reduced-motion"):]
    assert animated and all(selector.split(".")[-1] in reduced for selector in animated)
    assert "still()" in (WEB / "play-game.js").read_text(encoding="utf-8")


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
def test_moments_follow_real_results_in_a_real_browser():
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
            assert "game-ready" not in (page.get_attribute("#health", "class") or "")  # nothing built or simulated yet
            page.click("#health")
            assert "Build & run" in page.inner_text("#check-next")
            page.click("#check-next button")  # the page's own Build & run
            page.wait_for_selector("#score:has-text('cases match the kernel')", timeout=600_000)
            page.wait_for_selector("#game-notes .game-note.pass:has-text('Conformance')", timeout=10_000)
            assert "Simulate" in page.inner_text("#check-next")

            seen = page.evaluate("""() => new Promise((done) => {
                let most = 0, notes = '';
                const watch = setInterval(() => {
                  most = Math.max(most, document.querySelectorAll('.game-traffic').length);
                  notes += document.getElementById('game-notes').innerText;
                }, 30);
                document.getElementById('simulate').click();
                setTimeout(() => { clearInterval(watch); done({ most, notes }); }, 4000);
            })""")
            assert seen["most"] > 0  # the run's real steps went by as traffic
            assert "Every check passes on this model" in seen["notes"]
            page.wait_for_selector("#health.game-ready", timeout=10_000)
            assert "Ready." in page.inner_text("#check-next")

            page.fill("#chat-input", "add state Lost after Overdue then allow Member to CheckOut")
            page.click("#chat-send")
            page.wait_for_selector(f"{CARD} .plan-verdict", timeout=60_000)
            assert "game-ready" not in page.get_attribute("#health", "class")
            page.click(f"{CARD} .plan-steps > li:nth-child(2) input")  # untick the protected step: the policy allows the rest
            page.wait_for_selector("#game-notes .game-note.caught", timeout=30_000)
            assert "+3" in page.inner_text("#game-notes .game-note.caught")
            assert "game-stale" not in (page.get_attribute("#build", "class") or "")  # still looking at the model that was built
            page.click(f"{CARD} .plan-tools .primary:has-text('Preview on the diagram')")
            page.wait_for_selector("#build.game-stale", timeout=30_000)  # the build was of the model, not of this change
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_agents_show_as_diamonds_and_gaps_and_disagreements_count_down_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/refund-desk") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-assist=ready]", timeout=60_000)
            seen = page.evaluate("""() => new Promise((done) => {
                let diamonds = 0, squares = 0, notes = '';
                const watch = setInterval(() => {
                  diamonds = Math.max(diamonds, document.querySelectorAll('g.game-traffic > path[d^="M0-7.5"]').length);
                  squares = Math.max(squares, document.querySelectorAll('g.game-traffic > rect').length);
                  notes += document.getElementById('game-notes').innerText;
                }, 30);
                document.getElementById('simulate').click();
                setTimeout(() => { clearInterval(watch); done({ diamonds, squares, notes }); }, 3000);
            })""")
            assert seen["diamonds"] > 0 and seen["squares"] > 0  # the support agent, and the timer and payment system
            assert "The kernel stopped AI agents" in seen["notes"]
            assert "AI agents" in page.inner_text("#sim")  # the same count Simulate reports per kind
            assert "an AI agent" in page.inner_text("#game-legend")

            # The game layer's side of the greenfield list and the System lens: an item going away and the list
            # emptying, and disagreements going down to none. The events carry what those views computed.
            notes = page.evaluate("""() => new Promise((done) => {
                let text = '';
                const watch = setInterval(() => { text += document.getElementById('game-notes').innerText + '|'; }, 30);
                const send = (name, detail) => document.dispatchEvent(new CustomEvent(name, { detail }));
                send('playide:missing', { key: 'k', items: [{ id: 'a', text: 'A screen for Approve' }, { id: 'b', text: 'A way into Paid' }] });
                send('playide:missing', { key: 'k', items: [{ id: 'b', text: 'A way into Paid' }] });
                send('playide:missing', { key: 'k', items: [] });
                setTimeout(() => { clearInterval(watch); done(text); }, 300);
            })""")
            assert "A screen for Approve" in notes and "Nothing missing: ready to build" in notes
            notes = page.evaluate("""() => new Promise((done) => {
                let text = '';
                const watch = setInterval(() => { text += document.getElementById('game-notes').innerText + '|'; }, 30);
                const send = (name, detail) => document.dispatchEvent(new CustomEvent(name, { detail }));
                send('playide:landscape', { warning: 2 });
                send('playide:landscape', { warning: 1 });
                send('playide:landscape', { warning: 0 });
                setTimeout(() => { clearInterval(watch); done(text); }, 300);
            })""")
            assert "1 disagreement resolved, 1 left" in notes and "agree now" in notes
            assert errors == []
        finally:
            chrome.close()
