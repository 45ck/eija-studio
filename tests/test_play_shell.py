"""PlayIDE shell (ADR-0173): the assets are served and every region the page's scripts address is on the page, and in a
real browser the bottom panel opens on what has just run, the regions hide and come back from the keyboard (with keys the browser does not keep), the
choice survives a reload, the checks open as a popover and the review view has no chat.

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
SESSION = "synthetic-play-shell-test"
ORIGIN = "http://127.0.0.1:8765"
# Ids the other PlayIDE scripts look up; the shell moves regions around them and must keep every one.
KEPT = ("health", "checks", "runbar", "run-play", "simulate", "build", "toast", "score", "model-name", "outline-states",
        "inspector", "canvas", "draw-palette", "plan-banner", "chat-log", "chat-input", "chat-send", "debug", "sim", "run",
        "run-frame", "tab-laws", "tab-access", "tab-review", "laws", "access-panel", "review", "canvas-help")


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace"), SESSION)
    yield TestClient(app, base_url=ORIGIN)
    app.state.play.stop()


def test_the_shell_is_served_and_keeps_every_id_the_page_scripts_use(client):
    page = client.get("/play").text
    assert page.index("/assets/play-shell.js") < page.index("/assets/play.js")
    assert page.index("/assets/play-shell.css") > page.index("/assets/play.css")
    for name in ("play-shell.js", "play-shell.css"):
        assert client.get(f"/assets/{name}").status_code == 200
    for id_ in KEPT:
        assert page.count(f'id="{id_}"') == 1, id_
    # The run output lives in the bottom panel, the inspector under the outline, the chat alone on the right.
    assert page.index('class="dock"') < page.index('id="debug"') < page.index('id="sim"') < page.index('id="run"')
    assert page.index('class="explorer"') < page.index('id="outline-states"') < page.index('id="inspector"') < page.index('class="workbench"')
    side = page[page.index('<aside class="side">'):page.index("</aside>", page.index('<aside class="side">'))]
    assert 'id="chat-log"' in side and 'id="inspector"' not in side and 'id="sim"' not in side


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_the_shell_reveals_hides_and_remembers_its_regions_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
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
            url = f"{server.base_url}/play#{server.token}"
            page.goto(url)
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            # Nothing has run, so the panel is closed and cannot be opened empty.
            page.wait_for_selector('body[data-dock="closed"][data-left="open"][data-chat="open"]')
            assert page.is_disabled("#toggle-dock")
            # Simulate fills the panel and brings it to the front on the Simulation tab.
            page.click("#simulate")
            page.wait_for_selector('body[data-dock="open"] #dock-tab-sim[aria-selected="true"]', timeout=30_000)
            assert page.is_visible("#sim-summary") and page.is_hidden("#dock-tab-run")
            # The checks open as a popover over the chat and close with Escape.
            page.click("#health")
            assert page.is_visible("#check-list")
            page.keyboard.press("Escape")
            page.wait_for_selector("#checks", state="hidden")
            # Ctrl+Alt+P the panel, Ctrl+B the side bar, Ctrl+Alt+C the chat (which takes focus when it opens). Ctrl+J and
            # Ctrl+L belong to the browser, so they are not used.
            page.click("#canvas")
            for key, attr in (("Control+Alt+KeyP", "dock"), ("Control+KeyB", "left"), ("Control+Alt+KeyC", "chat")):
                page.keyboard.press(key)
                page.wait_for_selector(f'body[data-{attr}="closed"]')
            assert page.is_hidden("#chat-input") and page.is_hidden("#outline-states")
            # A hidden region leaves its column empty: the diagrams keep the width and nothing slides into it.
            assert page.evaluate("document.querySelector('.stage').clientWidth") > 1400
            page.keyboard.press("Control+Alt+KeyC")
            page.wait_for_selector('body[data-chat="open"]')
            assert page.evaluate("document.activeElement.id") == "chat-input"
            assert page.evaluate("document.querySelector('.side').getBoundingClientRect().left") > 1100  # still on the right
            # Tabs that do not fit scroll, and More tabs lists them; picking one scrolls it into view and nothing in the
            # tool bar covers the strip.
            page.set_viewport_size({"width": 1100, "height": 800})
            page.wait_for_selector("#tabs-more:not([hidden])")
            page.click("#tabs-more")
            page.keyboard.press("Tab")  # focus leaves the menu, so it closes
            page.wait_for_selector("#tabs-menu", state="hidden")
            assert page.get_attribute("#tabs-more", "aria-expanded") == "false"
            page.click("#tabs-more")
            page.click("#tabs-menu button:has-text('Permissions')")
            page.wait_for_selector('#tab-access[aria-selected="true"]')
            in_view = """() => { const s = document.querySelector('.stage-tools .tabs'), t = document.getElementById('tab-access');
                return t.offsetLeft >= s.scrollLeft - 1 && t.offsetLeft + t.offsetWidth <= s.scrollLeft + s.clientWidth + 1; }"""
            for _ in range(20):  # the strip scrolls smoothly; the page's CSP rules out wait_for_function with a string
                if page.evaluate(in_view):
                    break
                page.wait_for_timeout(100)
            assert page.evaluate(in_view)
            assert page.evaluate("""() => { const r = document.querySelector('.stage-tools .tabs').getBoundingClientRect();
                return [...document.querySelectorAll('.stage-tools > :not(.tabs):not(.tabs-menu)')].filter((e) => e.offsetParent)
                    .every((e) => e.getBoundingClientRect().left >= r.right - 0.5); }""")
            page.set_viewport_size({"width": 1600, "height": 900})
            page.click("#tab-states")
            # The layout is kept in this browser.
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.wait_for_selector('body[data-left="closed"][data-chat="open"]')
            page.click("#toggle-left")
            page.wait_for_selector('body[data-left="open"]')
            # The review view has no chat column and no chat toggle.
            page.goto(f"{server.base_url}/play?view=review#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.wait_for_selector('body[data-chat="closed"]')
            assert page.is_hidden("#toggle-chat") and page.is_hidden("#chat-input")
            assert errors == []
        finally:
            chrome.close()
