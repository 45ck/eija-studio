"""PlayIDE shell (ADR-0173): the assets are served and every region the page's scripts address is on the page, and in a
real browser the bottom panel opens on what has just run, the regions hide and come back from the keyboard (with keys the browser does not keep), the
choice survives a reload, the checks open as a popover and the review view has no chat.

The browser test is marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed
Chrome, or the Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.interfaces.http import create_app
from eija_studio.adapters.providers.process import resolve_command, run_bounded
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
SESSION = "synthetic-play-shell-test"
ORIGIN = "http://127.0.0.1:8765"
# Ids the other PlayIDE scripts look up; the shell moves regions around them and must keep every one.
KEPT = ("health", "checks", "runbar", "run-play", "simulate", "build", "toast", "score", "model-name", "outline-states",
        "inspector", "canvas", "draw-palette", "plan-banner", "chat-log", "chat-input", "chat-send", "debug", "sim", "run",
        "run-frame", "tab-laws", "tab-access", "tab-review", "laws", "access-panel", "review", "canvas-help", "toggle-play",
        "split-play", "play-empty", "play-empty-build", "play-rebuild", "play-model-status", "live-trace", "live-status",
        "live-action", "live-outcome", "live-pause", "live-replay", "live-show", "live-steps", "live-inspector", "live-recording", "live-reconnect",
        "tab-c4", "c4-panel")


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace"), SESSION)
    yield TestClient(app, base_url=ORIGIN)
    app.state.play.stop()


def test_the_shell_is_served_and_keeps_every_id_the_page_scripts_use(client):
    page = client.get("/play").text
    assert page.index("/assets/play-shell.js") < page.index("/assets/play.js")
    assert page.index("/assets/play-shell.css") > page.index("/assets/play.css")
    for name in ("play-shell.js", "play-shell.css", "play-live.js", "play-live.css", "play-c4.js", "play-c4.css"):
        assert client.get(f"/assets/{name}").status_code == 200
    for id_ in KEPT:
        assert page.count(f'id="{id_}"') == 1, id_
    # The run output lives in the bottom panel, the inspector under the outline, the chat alone on the right.
    assert page.index('class="dock"') < page.index('id="debug"') < page.index('id="sim"') < page.index('id="run"')
    assert page.index('class="explorer"') < page.index('id="outline-states"') < page.index('id="inspector"') < page.index('class="workbench"')
    side = page[page.index('<aside class="side">'):page.index("</aside>", page.index('<aside class="side">'))]
    assert 'id="chat-log"' in side and 'id="inspector"' not in side and 'id="sim"' not in side


def test_the_play_layout_keeps_one_app_and_distinguishes_simulation_from_local_execution(client):
    page = client.get("/play").text
    assert page.count("<iframe") == 1
    assert 'id="toggle-play"' in page and 'aria-controls="play-empty run"' in page
    assert "Actual app trace shows recorded outcomes. Model simulation stays separate." in page
    assert "Model simulation</h2>" in page and "Local app</h2>" in page


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node is not installed")
def test_actual_app_trace_rejects_forged_stale_and_unconfirmed_observations():
    node = shutil.which("node")
    assert node is not None
    result = run_bounded(
        [*resolve_command(node), "--test", str(ROOT / "tests/web/play-live.test.cjs")],
        cwd=str(ROOT), input=None, env=dict(os.environ), timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_c4_tab_click_loads_current_structure_and_drills_without_claiming_runtime():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser test only

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        try:
            executable = os.environ.get("EIJA_CHROMIUM")
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 1000})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(error.stack or str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.is_hidden("#c4-panel")
            with page.expect_response("**/api/play/c4") as loaded:
                page.click("#tab-c4")
            response = loaded.value
            assert response.status == 200 and response.request.method == "POST"
            report = response.json()
            assert report["subject"]["format"] == "eija.build-subject.v1"
            assert report["subject"]["model_hash"] == page.evaluate("PlayIDE.status().baseline_semantic_hash")
            assert report["generation"]["conformance"] == "NOT_RUN"
            assert report["observation"]["runtime"] == "NOT_OBSERVED"
            page.wait_for_selector('#tab-c4[aria-selected="true"]')
            page.wait_for_selector('#c4-map [data-c4-node="system:generated-app"]')
            assert page.is_visible("#c4-panel") and page.is_hidden("#canvas")
            assert page.get_attribute("#tab-states", "aria-selected") == "false"
            assert page.evaluate("PlayC4.current().subject") == report["subject"]
            assert report["subject"]["digest"] in page.get_attribute("#c4-subject", "title")
            assert "No local app launch with this exact build subject" in page.text_content("#c4-status")
            assert page.evaluate("PlayIDE.runningBuild()") is None
            page.click('#c4-map [data-c4-node="system:generated-app"]')
            page.click("#c4-drill")
            page.wait_for_selector('#c4-levels [data-c4-level="containers"][aria-pressed="true"]')
            assert set(page.locator("#c4-map [data-c4-node]").evaluate_all("nodes => nodes.map(node => node.dataset.c4Node)")) == {
                node["id"] for node in report["levels"]["containers"]["nodes"]}
            page.click('#c4-map [data-c4-node="node:process"]')
            page.click("#c4-drill")
            page.wait_for_selector('#c4-levels [data-c4-level="components"][aria-pressed="true"]')
            assert page.locator("#c4-map [data-c4-node]").count() == len(report["levels"]["components"]["nodes"])
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_actual_owned_draft_action_and_role_trace_the_same_generated_build_vocabulary():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser test only

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        try:
            executable = os.environ.get("EIJA_CHROMIUM")
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 1000})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(error.stack or str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            # Isolated fixture setup uses the real authenticated system creation and checked typed preview services.
            created = page.evaluate("""() => PlayIDE.api('/api/play/systems/new', {name:'Shared lobby',record:'Lobby',
              sketch:'Open -> Done : Finish [Host]'})""")
            assert created["created"] is True
            page.reload()
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.evaluate("() => PlayIDE.pack().own_system") is True
            assert page.evaluate("() => PlayIDE.pack().actions.includes('Remake')") is False
            checked = page.evaluate("""() => PlayIDE.importPlan([{kind:'add_transition',id:'TR-REMAKE',action:'Remake',
              from_state:'Done',to_state:'Open',role:'GameMaster'}],'A game master can remake a finished lobby')""")
            assert checked["legal"] is True
            page.click("#toggle-play")
            page.click("#play-empty-build")
            page.wait_for_function("() => window.PlayLive && PlayLive.snapshot().fresh", timeout=60_000)
            vocabulary = page.evaluate("() => PlayIDE.runningBuild().vocabulary")
            assert "Remake" in vocabulary["actions"]
            assert {"id": "gamemaster-1", "role": "GameMaster"} in vocabulary["actors"]
            assert page.evaluate("() => PlayIDE.pack().actions.includes('Remake')") is False
            frame_element = page.locator("#run-frame").element_handle()
            assert frame_element is not None
            frame = frame_element.content_frame()
            assert frame is not None
            frame.wait_for_function("() => typeof runtimeConnection !== 'undefined' && runtimeConnection !== null")
            frame.wait_for_function("() => document.getElementById('create-button').disabled === false")
            frame.locator("#actor").select_option("host-1")
            frame.locator("#title").fill("Friday multiplayer lobby")
            if frame.locator("#field-title").count():
                frame.locator("#field-title").fill("Friday multiplayer lobby")
            frame.locator("#create-button").click()
            frame.wait_for_function("() => document.getElementById('current-state').textContent === 'Open'")
            frame.locator("#options button[title=Finish]").click()
            frame.locator("#action-screen button:not(.quiet)").click()
            page.wait_for_function("() => PlayLive.snapshot().entries.length === 1")
            frame.wait_for_function("() => document.getElementById('current-state').textContent === 'Done'")
            frame.locator("#actor").select_option("gamemaster-1")
            frame.wait_for_function("""() => {
              const button=document.querySelector('#options button[title=Remake]');return button && !button.disabled;
            }""")
            frame.locator("#options button[title=Remake]").click()
            frame.locator("#action-screen button:not(.quiet)").click()
            page.wait_for_function("() => PlayLive.snapshot().entries.length === 2")
            assert page.locator(".live-traffic").count() == 1
            frame.wait_for_function("() => document.getElementById('current-state').textContent === 'Open'")
            trace = page.evaluate("() => PlayLive.snapshot().entries[1]")
            observed = frame.evaluate("() => api('/api/records/' + state.selected + '?actor=' + state.actor)")
            assert (trace["action"], trace["actorId"], trace["transition"], trace["from"], trace["to"]) == (
                "Remake", "gamemaster-1", "TR-REMAKE", "Done", "Open")
            assert trace["modelHash"] == page.evaluate("() => PlayIDE.runningBuild().model") == observed["record"]["model_hash"]
            assert trace["recordId"] == observed["record"]["id"] and trace["version"] == observed["record"]["version"] == 2
            assert trace["operationId"] == observed["history"][1]["operation"]
            assert page.evaluate("() => PlayLive.snapshot().ignored") == 0 and errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_actual_local_actions_reach_the_model_and_replay_without_writing_to_the_app():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser test only

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        try:
            executable = os.environ.get("EIJA_CHROMIUM")
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 1000})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(error.stack or str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click("#toggle-play")
            page.click("#play-empty-build")
            page.wait_for_function("() => window.PlayLive && PlayLive.snapshot().fresh", timeout=60_000)
            frame_element = page.locator("#run-frame").element_handle()
            assert frame_element is not None
            frame = frame_element.content_frame()
            assert frame is not None
            frame.wait_for_function("() => typeof runtimeConnection !== 'undefined' && runtimeConnection !== null")
            frame.wait_for_function("() => document.getElementById('create-button').disabled === false")
            frame.locator("#actor").select_option("librarian-assigned")
            frame.locator("#title").fill("A traced library loan")
            frame.locator("#field-itemTitle").fill("Systems in Play")
            frame.locator("#field-memberCard").fill("TRACE-01")
            frame.locator("#field-dueDate").fill("2026-10-20")
            frame.locator("#field-format").select_option("Book")
            frame.locator("#create-button").click()
            frame.wait_for_function("() => document.getElementById('current-state').textContent === 'Requested'")
            assert page.evaluate("() => PlayLive.snapshot().entries") == []  # creating is not a transition trace
            frame.locator("#options button[title=CheckOut]").click()
            assert page.evaluate("() => PlayLive.snapshot().entries") == []  # opening is not a commit
            frame.locator("#action-screen button:not(.quiet)").click()
            page.wait_for_function("() => PlayLive.snapshot().entries.length === 1")
            assert page.locator(".live-traffic").count() == 1
            assert page.locator(".live-edge path, .live-edge polyline").count() > 0
            frame.wait_for_function("() => document.getElementById('current-state').textContent === 'OnLoan'")
            receipt = frame.evaluate("() => api('/api/records/' + state.selected + '?actor=' + state.actor)")
            first = page.evaluate("() => PlayLive.snapshot().entries[0]")
            assert (first["action"], first["from"], first["to"], first["transition"]) == (
                "CheckOut", "Requested", "OnLoan", "TR-CHECKOUT")
            assert first["recordId"] == receipt["record"]["id"] and first["version"] == receipt["record"]["version"] == 1
            assert first["operationId"] == receipt["history"][0]["operation"]
            assert first["modelHash"] == page.evaluate("() => PlayIDE.runningBuild().model")
            try:
                page.wait_for_selector(".live-arrival")
            except api.TimeoutError as exc:
                diagnostic = page.evaluate("""() => {
                  const trace=PlayLive.snapshot(),graph=PlayIDE.graph(),cell=graph.getDataModel().getCell('state:OnLoan');
                  const node=graph.getView().getState(cell).shape.node,box=node.getBoundingClientRect(),style=getComputedStyle(node);
                  return {fresh:trace.fresh,paused:trace.paused,tab:PlayIDE.tab(),entries:trace.entries.length,
                    connected:node.isConnected,arrivalClass:node.classList.contains('live-arrival'),
                    arrivals:document.querySelectorAll('.live-arrival').length,tokens:document.querySelectorAll('.live-traffic').length,
                    display:style.display,visibility:style.visibility,width:box.width,height:box.height};
                }""")
                diagnostic["page_errors"] = errors
                exc.add_note(f"Current destination and trace diagnostics: {diagnostic}")
                raise
            assert page.evaluate("""() => {
              const graph=PlayIDE.graph(),cell=graph.getDataModel().getCell('state:OnLoan');
              const node=graph.getView().getState(cell).shape.node;
              return node.isConnected && node.classList.contains('live-arrival');
            }""")
            assert "Requested → OnLoan" in page.locator("#live-outcome").inner_text()
            # Pausing preserves the inspected action while the actual app keeps committing.
            page.click("#live-pause")
            frame.locator("#actor").select_option("clerk")
            frame.wait_for_function("() => document.querySelector('#options button[title=MarkOverdue]').disabled === false")
            frame.locator("#options button[title=MarkOverdue]").click()
            frame.locator("#action-screen button:not(.quiet)").click()
            page.wait_for_function("() => PlayLive.snapshot().entries.length === 2")
            assert page.evaluate("() => PlayLive.snapshot().cursor") == 0
            assert "1 newer" in page.locator("#live-status").inner_text()
            before_replay = frame.evaluate("() => api('/api/records/' + state.selected + '?actor=' + state.actor)")
            page.click("#live-replay")
            assert "Replaying recorded outcomes" in page.locator("#live-status").inner_text()
            page.wait_for_function("() => !PlayLive.snapshot().replaying && PlayLive.snapshot().cursor === 1")
            after_replay = frame.evaluate("() => api('/api/records/' + state.selected + '?actor=' + state.actor)")
            assert after_replay == before_replay
            # A competing real local write makes the open action's expected version stale.
            page.click("#live-pause")
            frame.locator("#actor").select_option("librarian-assigned")
            frame.wait_for_function("() => document.querySelector('#options button[title=ReturnLate]').disabled === false")
            frame.locator("#options button[title=ReturnLate]").click()
            winner = frame.evaluate("""async () => {
              const record = (await api('/api/records/' + state.selected + '?actor=' + state.actor)).record;
              return api('/api/records/' + record.id + '/act', {action:'ReturnLate',actor:state.actor,
                expected_version:record.version,operation_id:crypto.randomUUID()});
            }""")
            assert winner["committed"] is True and winner["record"]["version"] == 3
            frame.locator("#action-screen button:not(.quiet)").click()
            page.wait_for_function("() => PlayLive.snapshot().entries.length === 3")
            refusal = page.evaluate("() => PlayLive.snapshot().entries[2]")
            assert refusal["kind"] == "refused" and refusal["code"] == "STALE_VERSION"
            assert refusal["from"] == refusal["to"] == "Overdue" and refusal["version"] == 2
            assert refusal["transition"] is None and page.locator(".live-traffic, .live-edge, .live-arrival").count() == 0
            assert "no commit reported" in page.locator("#live-outcome").inner_text()
            page.locator("#live-trace summary").click()
            assert "current state was not reported" in page.locator("#live-inspector").inner_text()
            # Forged source/origin and stale or malformed current-frame messages cannot add an entry or trigger an action.
            frame.evaluate("""() => parent.postMessage({type:'playide.runtime.v1',nonce:runtimeConnection.nonce,
              modelHash:'0'.repeat(64),kind:'committed',recordId:state.selected,version:4,
              operationId:crypto.randomUUID(),action:'ReturnLate',from:'Overdue',to:'Returned',
              actorId:state.actor,effects:[]},runtimeParentOrigin)""")
            page.wait_for_function("() => PlayLive.snapshot().ignored === 1")
            frame.evaluate("""() => parent.postMessage({type:'playide.runtime.v1',nonce:runtimeConnection.nonce,
              modelHash:state.app.model_hash,kind:'committed',recordId:'not-a-record',version:4,
              operationId:crypto.randomUUID(),action:'ReturnLate',from:'Overdue',to:'Returned',
              actorId:state.actor,effects:[]},runtimeParentOrigin)""")
            page.wait_for_function("() => PlayLive.snapshot().ignored === 2")
            page.evaluate("""() => {
              const {transition,observedGap,...data}=PlayLive.snapshot().entries[0];
              data.version=4;data.operationId=crypto.randomUUID();
              dispatchEvent(new MessageEvent('message',{source:document.getElementById('run-frame').contentWindow,
                origin:'https://attacker.invalid',data}));
            }""")
            page.evaluate("""() => dispatchEvent(new MessageEvent('message',{source:window,origin:location.origin,
              data:{type:'playide.runtime.v1',approve:true}}))""")
            assert len(page.evaluate("() => PlayLive.snapshot().entries")) == 3
            latest = frame.evaluate("() => api('/api/records/' + state.selected + '?actor=' + state.actor)")
            assert latest["record"]["version"] == 3 and len(latest["history"]) == 3
            # This programmatic typed edit exercises the actual preview service, not a mutation of the in-memory model.
            prior_source = page.get_attribute("#run-frame", "src")
            checked = page.evaluate("""() => PlayIDE.importPlan([{kind:'add_transition',id:'TR-RENEW',action:'Renew',
              from_state:'Overdue',to_state:'OnLoan',role:'Librarian'}],'Trace freshness test: allow renewal')""")
            assert checked["legal"] is True
            page.wait_for_function("() => !PlayLive.snapshot().fresh")
            assert page.get_attribute("#run-frame", "src") == prior_source
            assert "Earlier build" in page.locator("#live-status").inner_text()
            assert len(page.evaluate("() => PlayLive.snapshot().entries")) == 3
            frame.evaluate("""() => parent.postMessage({type:'playide.runtime.v1',nonce:runtimeConnection.nonce,
              modelHash:state.app.model_hash,kind:'committed',recordId:state.selected,version:4,
              operationId:crypto.randomUUID(),action:'ReturnLate',from:'Overdue',to:'Returned',
              actorId:state.actor,effects:[]},runtimeParentOrigin)""")
            assert len(page.evaluate("() => PlayLive.snapshot().entries")) == 3
            page.click("#build")
            page.wait_for_function("() => PlayLive.snapshot().fresh && PlayLive.snapshot().entries.length === 0", timeout=60_000)
            assert page.evaluate("() => PlayLive.snapshot().modelHash") != first["modelHash"]
            page.click("#run-stop")
            page.wait_for_function("() => !PlayLive.snapshot().fresh")
            assert "Earlier build" in page.locator("#live-status").inner_text()
            assert page.locator("#live-replay").is_disabled() and page.evaluate("() => PlayLive.snapshot().entries") == []
            assert errors == []
        finally:
            chrome.close()


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_design_and_play_keeps_the_real_app_visible_and_remembers_the_layout():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser test only

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        try:
            executable = os.environ.get("EIJA_CHROMIUM")
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except api.Error as exc:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(exc).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 1000})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            assert page.is_hidden("#play-empty")
            page.locator("#toggle-play").focus()
            page.keyboard.press("Enter")
            page.wait_for_selector('body[data-play="open"][data-play-arrangement="beside"]')
            assert page.is_visible("#play-empty-build") and page.is_visible("#canvas")
            assert page.get_attribute("#toggle-play", "aria-pressed") == "true"
            # The layout does not replace the person's panel choices.
            assert page.get_attribute("body", "data-left") == "open"
            assert page.get_attribute("body", "data-chat") == "open"
            page.locator("#split-play").focus()
            before = int(page.get_attribute("#split-play", "aria-valuenow"))
            page.keyboard.press("ArrowRight")
            assert int(page.get_attribute("#split-play", "aria-valuenow")) == before - 20
            page.reload()
            page.wait_for_selector('body[data-ready=true][data-play="open"]', timeout=60_000)
            assert int(page.get_attribute("#split-play", "aria-valuenow")) == before - 20
            page.click("#play-empty-build")
            page.wait_for_selector('body[data-play-app="running"] #run', timeout=60_000)
            assert page.is_visible("#run-frame") and page.is_hidden("#play-empty")
            assert page.locator("#play-model-status").text_content() == "Checked model on screen · fixture actors"
            source = page.get_attribute("#run-frame", "src")
            assert source and source != "about:blank"
            page.evaluate("window.__observedShellFrame = document.getElementById('run-frame').contentWindow")
            # A model simulation may appear alongside the app, but never pretends to report its local commits.
            page.click("#simulate")
            page.wait_for_selector('#dock-tab-sim[aria-selected="true"]', timeout=30_000)
            assert page.is_visible("#sim-summary") and page.is_visible("#run-frame")
            assert page.is_hidden("#dock-tab-run")
            page.click("#toggle-play")
            page.wait_for_selector('body[data-play="closed"]')
            assert page.is_visible("#run-frame")
            page.click("#toggle-play")
            assert page.get_attribute("#run-frame", "src") == source
            assert page.evaluate("window.__observedShellFrame === document.getElementById('run-frame').contentWindow")
            # The same presentation becomes a vertical split when the actual centre container narrows.
            page.click("#toggle-left")
            page.click("#toggle-chat")
            page.set_viewport_size({"width": 760, "height": 900})
            page.wait_for_selector('body[data-play-arrangement="stacked"]')
            assert page.get_attribute("#split-play", "aria-orientation") == "horizontal"
            assert page.is_visible("#canvas") and page.is_visible("#run-frame")
            page.locator("#split-play").focus()
            height = int(page.get_attribute("#split-play", "aria-valuenow"))
            page.keyboard.press("ArrowDown")
            assert int(page.get_attribute("#split-play", "aria-valuenow")) == height - 20
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            # Stopping is still the existing runtime stop: it blanks the one frame and returns the useful empty state.
            page.click("#run-stop")
            page.wait_for_selector('body[data-play-app="empty"] #play-empty')
            assert page.get_attribute("#run-frame", "src") == "about:blank"
            assert page.is_visible("#play-empty-build")
            assert errors == []
        finally:
            chrome.close()


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
