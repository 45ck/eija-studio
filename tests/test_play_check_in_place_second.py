"""Second Fagan inspection of running and checking a design in place (2026-11-14), across every sector pack. Each test
pins one finding (E-01 to E-09 in docs/engineering/2026-11-14-INSPECTION-CHECK-IN-PLACE-2.md), with a negative control
where it has one. The request-ordering rule (E-07 to E-09) is pinned in tests/test_play_answers_follow_view.py.

The browser test is marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise). It uses the installed
Chrome, or the Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from eija_studio.application.access import _try, access, reach
from eija_studio.application.runtime import initialise
from eija_studio.application.simulation import CASE, MemorySession, run_log, simulate  # access tries cells in this case
from eija_studio.domain.pack import load_pack

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "src/eija_studio/resources/web"
PACKS = sorted(p.name for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file())
CARD = ".msg.ai:last-child"


def _allowed(report):
    return {c["transition"] for row in report["cells"].values() for cs in row.values() for c in cs
            if any(not a["refused"] for a in c["actors"])}


@pytest.mark.parametrize("name", PACKS)
def test_permissions_and_reach_agree_with_what_simulate_commits(name):
    """E-01: a transition Simulate commits has a fixture actor the matrix lets through, and a state Simulate enters is
    reachable at all. A time event or a linked object it moves used to make the matrix refuse everyone."""
    pack = load_pack(ROOT / "packs" / name)
    run = simulate(pack, pack.model, seed=1, steps=500)
    committed = {t for t, r in run["transitions"].items() if r["committed"]}
    assert committed <= _allowed(access(pack, pack.model))
    for state, r in run["states"].items():
        if r["entered"]:
            assert reach(pack, pack.model, state)["verdict"] == "REACHABLE", state


def test_a_timed_step_and_an_object_move_are_tried_on_a_ready_record():
    ai_ops, refunds = load_pack(ROOT / "packs/ai-ops"), load_pack(ROOT / "packs/refund-desk")
    cells = [c for row in access(ai_ops, ai_ops.model)["cells"].values() for cs in row.values() for c in cs]
    window = next(c for c in cells if c["action"] == "OpenWindow")
    assert window["moves"] == ["target.lock"] and window["actors"] == [{"actor": "deploy-window", "refused": None}]
    cells = [c for row in access(refunds, refunds.model)["cells"].values() for cs in row.values() for c in cs]
    escalate = next(c for c in cells if c["action"] == "EscalateStale")
    assert escalate["after"].startswith("after(") and escalate["actors"][0]["refused"] is None
    path = reach(refunds, refunds.model, "WithSupervisor")["path"]
    assert [s["action"] for s in path][-1] == "EscalateStale"
    # Negative control: the kernel itself is unchanged. On a record that has not waited it still refuses the step.
    model = refunds.model
    t = next(x for x in model.transitions if x.action == "EscalateStale")
    session = MemorySession(refunds)
    record = initialise(session, CASE, model, state=t.from_state, pack=refunds)["id"]
    assert _try(refunds, model, t, "sla-clock", session, record) == "TIMER_NOT_DUE"


def test_a_permission_whose_time_event_changes_is_listed_as_changed():
    pack = load_pack(ROOT / "packs/refund-desk")
    data = pack.model.model_dump(mode="json")
    for t in data["transitions"]:
        if t["action"] == "EscalateStale":
            t["after"] = {"amount": t["after"]["amount"] + 1, "unit": t["after"]["unit"]}
    later = type(pack.model).model_validate(data)
    changed = access(pack, later, pack.model)["changes"]["changed"]
    assert [c["action"] for c in changed] == ["EscalateStale"] and changed[0]["before"] != changed[0]["after"]


def test_a_stop_on_a_slip_names_the_action_it_refused():
    """E-04: "the kernel refused Approve from Lodged", not "an action from Lodged"."""
    pack = load_pack(ROOT / "packs/building-permit")
    log = run_log(pack, pack.model, seed=1, steps=500, break_on_refusal=True)
    stop = next(s for s in log["stops"] if s["elements"][0].startswith("state:"))
    entry = next(e for e in log["trace"] if e["step"] == stop["step"])
    assert stop["action"] == entry["action"] and stop["action"]
    assert "stop.action || \"an action\"" in (WEB / "play-run.js").read_text(encoding="utf-8")


def test_the_count_up_never_shows_a_number_below_zero():
    """E-02: a frame's time can come before the start the count-up read, which made 1 - (1 - f)^3 negative."""
    source = (WEB / "play-game.js").read_text(encoding="utf-8")
    body = source[source.index("function countUp()"):source.index("function init()")]
    assert "Math.max(0, Math.min(1," in body


def test_the_simulated_check_follows_what_was_simulated_not_what_is_painted():
    """E-03: Stop and Restart clear the diagram; they simulate nothing and change no model, so the check stays."""
    source = (WEB / "play.js").read_text(encoding="utf-8")
    checks = source[source.index("function checksNow()"):source.index("function renderHealth()")]
    assert "simulated && simKey === key" in checks and "sim && simKey" not in checks
    clearing = source[source.index("function clearSimPanel()"):source.index("function step(entry)")]
    assert "simulated" not in clearing


def test_simulate_and_the_run_bar_take_the_diagram_in_turn():
    """E-05: a run on the run bar ends when a Simulate result is shown, and Run or Step hides a Simulate result."""
    source = (WEB / "play-run.js").read_text(encoding="utf-8")
    assert 'addEventListener("playide:simulated", simulated)' in source
    assert source.count("yieldSimulate();") == 2


def test_a_part_that_becomes_not_applicable_is_no_moment():
    """E-06: undoing an AI plan unchecked used to pop "✓ AI steps checked"."""
    source = (WEB / "play-game.js").read_text(encoding="utf-8")
    assert "|| !c.ok || c.na) return;" in source and "if (c.ok && !c.na) everPassed.add" in source


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


SLOW = """([pattern, needle, ms]) => { const f = window.fetch; window.fetch = async (u, o) => { const r = await f(u, o);
  if (new RegExp(pattern).test(String(u)) && String((o || {}).body || '').includes(needle)) await new Promise((ok) => setTimeout(ok, ms));
  return r; }; }"""


@pytest.mark.browser
@pytest.mark.slow
@browser
def test_running_and_checking_agree_with_the_kernel_in_a_real_browser():
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, api.sync_playwright() as playwright:
        chrome = _launch(api, playwright)
        try:
            page = chrome.new_page(viewport={"width": 1920, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-assist=ready]", timeout=60_000)
            page.evaluate("""() => { window.__seen = []; const box = document.getElementById('sim-summary');
              new MutationObserver(() => window.__seen.push(box.innerText)).observe(box, { childList: true, subtree: true, characterData: true });
              window.__notes = []; new MutationObserver(() => { const n = document.querySelector('#game-notes .game-note');
                if (n) window.__notes.push(n.textContent); }).observe(document.getElementById('game-notes'), { childList: true, subtree: true }); }""")

            # E-05: Simulate during a run ends the run; the diagram shows Simulate's counts, as its panel says.
            page.select_option("#run-speed", "700")
            page.click("#run-play")
            page.wait_for_timeout(1_500)
            page.click("#simulate")
            page.wait_for_function("() => /went through/.test(document.getElementById('sim-summary').innerText)", timeout=60_000)
            page.wait_for_timeout(1_500)
            assert page.evaluate("() => document.body.dataset.run") == "idle"
            assert page.inner_text("#run-status").startswith("Ended the run")
            # E-02: no number on the way up is below zero.
            assert not [s for s in page.evaluate("() => window.__seen") if "-" in s]

            # E-03: a run and Stop leave the Simulated check as it was.
            page.select_option("#run-speed", "0")
            page.click("#run-play")
            page.wait_for_function("() => document.body.dataset.run !== 'idle'", timeout=60_000)
            page.click("#run-stop")
            assert page.locator("#check-list li.ok", has_text="Simulated").count() == 1

            # E-07: an answer to an earlier reachability question, landing late, is not shown under the new one.
            page.evaluate("() => window.PlayIDE.showTab('access')")
            page.wait_for_selector("form.reach select", timeout=60_000)
            page.evaluate(SLOW, ["api/play/reach", '"target":"Returned"', 2_500])
            selects = page.locator("form.reach select")
            selects.nth(0).select_option("Returned")
            selects.nth(1).select_option("Librarian")
            page.click("form.reach button[type=submit]")
            selects.nth(0).select_option("OnLoan")
            selects.nth(1).select_option("")
            page.click("form.reach button[type=submit]")
            page.wait_for_timeout(3_500)
            assert page.inner_text("#reach-answer").startswith("Yes"), page.inner_text("#reach-answer")

            # E-06: undoing an AI plan nobody looked at is not "AI steps checked".
            page.evaluate("() => window.PlayIDE.showTab('states')")
            page.fill("#chat-input", "add state Lost after Overdue")
            page.click("#chat-send")
            page.wait_for_selector(f"{CARD} .plan-verdict", timeout=60_000)
            page.wait_for_timeout(1_000)
            page.click("#undo")
            page.wait_for_timeout(2_000)
            assert "✓ AI steps checked" not in page.evaluate("() => window.__notes")
            assert errors == []
        finally:
            chrome.close()
