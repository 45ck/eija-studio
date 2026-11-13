"""Fagan inspection of running and checking a design in place (2026-11-13): the run bar, Simulate, the Laws tab and
reachability. Each test pins one defect the inspection found, with a negative control where it has one.

The browser test is marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed
Chrome, or the Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

import pytest

from eija_studio.application.access import reach
from eija_studio.application.simulation import run_log
from eija_studio.domain.pack import load_pack
from test_play_kernel_features import kernel_loan

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "src/eija_studio/resources/web"
CARD = ".msg.ai:last-child"


def test_a_run_with_idle_turns_numbers_its_steps_apart_from_its_entries(tmp_path):
    """The premise of the run bar fix: with initiators (ADR-0231) a turn may log nothing, so the run's step numbers
    and the trace's places differ, and a stop names a step number, not a place."""
    pack = load_pack(kernel_loan(tmp_path))
    log = run_log(pack, pack.model, seed=1, steps=500, breakpoints=["state:Returned"])
    places = [i + 1 for i in range(len(log["trace"]))]
    assert [e["step"] for e in log["trace"]] != places  # seed 1 is the run bar's seed
    stop = log["stops"][0]
    entry = next(e for e in log["trace"] if e["step"] == stop["step"])
    assert entry["to"] == "Returned"  # the step the stop names entered the breakpoint's state
    assert log["trace"][stop["step"] - 1]["step"] != stop["step"]  # read as a place, it is another step


def test_the_run_bar_finds_a_stop_by_the_entrys_step_not_its_place():
    source = (WEB / "play-run.js").read_text(encoding="utf-8")
    assert "s.step === stepOf(n)" in source and "s.step === n)" not in source
    assert "pos = e.step" not in source and "e.step === pos" not in source


def test_reach_without_the_only_initiator_is_unreachable(tmp_path):
    pack = load_pack(kernel_loan(tmp_path))  # only a Member may start a loan
    answer = reach(pack, pack.model, "Requested", "Member")
    assert answer["verdict"] == "UNREACHABLE" and "ROLE_CANNOT_START" in answer["why"]
    # Negative control: without another role, a Member starts the record and the kernel commits the path.
    assert reach(pack, pack.model, "OnLoan", "Clerk")["verdict"] == "REACHABLE"


def test_reach_needs_a_fixture_actor_who_may_start_a_record(tmp_path):
    folder = kernel_loan(tmp_path)
    doc = json.loads((folder / "pack.json").read_text(encoding="utf-8"))
    doc["fixtures"]["actors"] = [a for a in doc["fixtures"]["actors"] if a["role"] != "Member"]
    (folder / "pack.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    pack = load_pack(folder)
    answer = reach(pack, pack.model, "OnLoan")
    assert answer["verdict"] == "NOT_SHOWN" and "may start a record" in answer["why"]


def test_reach_is_unchanged_for_a_model_without_initiators(tmp_path):
    pack = load_pack(ROOT / "packs/library-loan")
    assert not pack.model.initiators
    assert reach(pack, pack.model, "Returned")["verdict"] == "REACHABLE"


def test_laws_link_a_transition_through_its_action_and_paint_the_run_on_its_source():
    source = (WEB / "play-laws.js").read_text(encoding="utf-8")
    assert "law.subject.includes(ref)" not in source and '"action:" + t.action' in source
    assert "transitionFor(step.action, step.from)" in source


def test_simulate_drops_a_result_of_a_model_no_longer_on_screen():
    source = (WEB / "play.js").read_text(encoding="utf-8")
    body = source[source.index("async function simulate()"):source.index("// Undo, redo and autosave")]
    assert body.index("key !== viewKey()") < body.index("showSim(result)")


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
def test_checking_in_place_agrees_with_the_kernel_in_a_real_browser(tmp_path):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    folder = kernel_loan(tmp_path)
    pack = load_pack(folder)
    expected = run_log(pack, pack.model, seed=1, steps=500, breakpoints=["state:Returned"])
    stop = expected["stops"][0]["step"]
    with ephemeral_eija_server(pack=folder) as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-assist=ready]", timeout=60_000)

            # The run bar pauses on the step that entered the breakpoint's state, and shows that step.
            page.evaluate("() => window.PlayIDE.select('state:Returned', false)")
            page.keyboard.press("F9")
            page.select_option("#run-speed", "0")
            page.click("#run-play")
            page.wait_for_function("() => document.body.dataset.run === 'paused'", timeout=60_000)
            assert page.inner_text("#run-status") == f"Paused at step {stop}: breakpoint on Returned"
            now = page.inner_text("#debug-now")
            assert "Returned" in now and "committed" in now, now
            current = page.inner_text("#debug-log li.current")
            assert current.startswith(f"{stop}\n") and current == page.inner_text("#debug-log li:last-child")
            page.keyboard.press("Shift+F5")

            # Stop while the run's log is still loading: the run does not start after it.
            page.evaluate("""() => { const f = window.fetch; window.fetch = async (u, o) => { const r = await f(u, o);
                if (/api\\/play\\/(run|simulate)/.test(String(u))) await new Promise((ok) => setTimeout(ok, 3000)); return r; }; }""")
            page.evaluate("() => window.PlayIDE.select('state:Cancelled', false)")
            page.keyboard.press("F9")  # a new breakpoint forgets nothing, but a new log is fetched for the next run
            page.click("#run-play")
            page.click("#run-stop")
            page.wait_for_timeout(4_000)
            assert page.evaluate("() => document.body.dataset.run") == "idle"

            # Inspect its laws, from a transition: the laws about its action are linked.
            transition = page.evaluate("() => window.PlayIDE.model().transitions.find((t) => t.action === 'Return').id")
            page.evaluate(f"async () => await window.PlayLaws.showFor('transition:{transition}')")
            limits = page.inner_text("#laws-limits")
            assert "four-eyes" in limits and "clerk-never-takes-returns" in limits, limits

            # Simulate, then preview a change before the result arrives: the old run is not painted on the new model.
            page.evaluate("() => window.PlayIDE.showTab('states')")
            page.click("#simulate")
            page.fill("#chat-input", "add state Lost after Overdue")
            page.click("#chat-send")
            page.wait_for_selector(f"{CARD} .plan-verdict", timeout=60_000)
            page.click(f"{CARD} .plan-tools .primary:has-text('Preview on the diagram')")
            page.wait_for_timeout(4_000)
            assert "Lost" in page.evaluate("() => window.PlayIDE.model().states")
            assert page.evaluate("() => document.getElementById('sim').hidden")  # nothing claims a run of this model
            assert not re.search(r"Simulation refused", page.inner_text("#sim-summary"))
            assert "Not simulated since the last change" in page.inner_text("#check-list")
            assert errors == []
        finally:
            chrome.close()



def test_reach_counts_a_record_a_signal_starts(tmp_path):
    """A workflow that receives a signal (ADR-0242) starts a record on delivery with no person's role, so leaving out
    its only initiator does not make its states unreachable."""
    folder = tmp_path / "library-fines"
    shutil.copytree(ROOT / "packs/library-fines", folder)
    doc = json.loads((folder / "pack.json").read_text(encoding="utf-8"))
    doc["model"]["initiators"] = ["Member"]
    (folder / "pack.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    pack = load_pack(folder)
    answer = reach(pack, pack.model, "Issued", "Member")
    assert answer["verdict"] == "REACHABLE" and "Signal:LateReturn from library-loan" in answer["why"]
    # Negative control: the same workflow without the signal has no other way to start a record.
    del doc["model"]["receives"]
    (folder / "pack.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    pack = load_pack(folder)
    assert reach(pack, pack.model, "Issued", "Member")["verdict"] == "UNREACHABLE"
