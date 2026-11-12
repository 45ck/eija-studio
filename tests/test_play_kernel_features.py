"""The kernel features of ADR-0231 to ADR-0235 as a person meets them in PlayIDE, found by walking the IDE in a browser:
a test gives the record values a guard over values reads, the permissions matrix and reachability try a guarded
transition on a record whose values meet it, chat plan mode edits an action that leaves several states, the outline
tells those transitions apart, use case lines end on the ellipse, and the components tab's refusal sits below its bar.

The browser test is marked `browser`: it runs only with EIJA_BROWSER_TESTS=1 (NOT_RUN otherwise), with the installed
Chrome or the Chromium at EIJA_CHROMIUM, and never downloads a browser.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
from pathlib import Path

import pytest

from eija_studio.adapters.plan_proposals import OfflinePlanProposer
from eija_studio.application.access import matrix, reach
from eija_studio.application.scenario_run import record_steps, run_scenarios
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.domain.scenarios import Scenario, load_scenarios

ROOT = Path(__file__).resolve().parents[1]
GUARD = {"attribute": "renewals", "op": "le", "value": 3}


def kernel_loan(tmp_path: Path, *, values: bool = True) -> Path:
    """Library loan with every new kernel feature: only members start a loan (ADR-0231), Return leaves OnLoan and
    Overdue (ADR-0232), whoever checks a loan out does not take its return (ADR-0233), CheckOut needs
    [renewals ≤ 3] (ADR-0234), and the borrower is a built reference (ADR-0235)."""
    pack_dir = tmp_path / "library-loan"
    shutil.copytree(ROOT / "packs" / "library-loan", pack_dir)
    doc = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    model = doc["model"]
    model["initiators"] = ["Member"]
    for t in model["transitions"]:
        if t["action"] == "CheckOut":
            t["conditions"] = [GUARD]
    late = copy.deepcopy(next(t for t in model["transitions"] if t["action"] == "Return"))
    model["transitions"].append(late | {"id": "TR-RETURN-OVERDUE", "from_state": "Overdue"})
    doc["laws"].append({"id": "four-eyes", "kind": "distinct_actors", "code": "FOUR_EYES",
                        "description": "Whoever checks a loan out does not also take its return.", "actions": ["CheckOut", "Return"]})
    (pack_dir / "pack.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    data = json.loads((pack_dir / "data.json").read_text(encoding="utf-8"))
    for link in data["associations"]:
        if link["role"] == "borrower":
            link["built"] = True
    (pack_dir / "data.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    tests = json.loads((pack_dir / "scenarios.json").read_text(encoding="utf-8"))
    for scenario in tests["scenarios"]:
        if values and any(s["action"] == "CheckOut" and "state" in s["then"] for s in scenario["steps"]):
            scenario["values"] = {"renewals": 1}
    (pack_dir / "scenarios.json").write_text(json.dumps(tests, indent=2) + "\n", encoding="utf-8", newline="\n")
    return pack_dir


def test_a_test_gives_the_record_values_a_guard_reads(tmp_path):
    pack = load_pack(kernel_loan(tmp_path))
    run = run_scenarios(pack, pack.model, load_scenarios(kernel_loan(tmp_path / "again"), pack.id))
    assert run["status"] == "PASS", run
    lent = next(s for s in run["scenarios"] if s["id"] == "lend-and-return")
    assert lent["values"] == {"renewals": 1}
    # Negative control: the same tests without values are refused by the guard, and the failure says which guard.
    bare = load_pack(kernel_loan(tmp_path / "bare", values=False))
    failed = run_scenarios(bare, bare.model, load_scenarios(kernel_loan(tmp_path / "bare2", values=False), bare.id))
    why = next(s for s in failed["scenarios"] if s["id"] == "lend-and-return")["why"]
    assert "VALUE_GUARD_DENIED" in why and "renewals ≤ 3" in why and "give the test record values" in why
    # Too many renewals: the guard refuses, so a recorded test expects exactly that.
    steps = record_steps(pack, pack.model, None, [("librarian-assigned", "CheckOut")], {"renewals": 4})
    assert steps[0]["then"] == {"refused": "VALUE_GUARD_DENIED"}


def test_scenario_values_keep_old_digests_and_are_checked():
    plain = Scenario(id="a", title="t", steps=[{"actor": "x", "action": "A", "then": {"state": "B"}}])
    assert "values" not in plain.model_dump(mode="json")  # every existing scenarios.json keeps its digest
    with pytest.raises(ValueError, match="not an attribute name"):
        Scenario(id="a", title="t", values={"Bad name": 1}, steps=[{"actor": "x", "action": "A", "then": {"state": "B"}}])


def test_permissions_and_reach_try_a_guarded_transition_on_values_that_meet_it(tmp_path):
    pack = load_pack(kernel_loan(tmp_path))
    cell = matrix(pack, pack.model)["cells"]["Requested"]["Librarian"][0]
    assert cell["when"] == ["renewals ≤ 3"]
    assert {a["actor"]: a["refused"] for a in cell["actors"]}["librarian-assigned"] is None
    # One record takes the whole path: values meeting the guard, and a second librarian for the return (four eyes).
    answer = reach(pack, pack.model, "Returned")
    assert answer["verdict"] == "REACHABLE" and answer["values"] == {"renewals": 2}
    assert [s["actor"] for s in answer["path"]] == ["librarian-assigned", "librarian-unassigned"]
    # Negative control: a guard no value meets leaves the path not shown, never reachable.
    never = pack.model.model_copy(update={"transitions": tuple(
        t.model_copy(update={"conditions": (*t.conditions, t.conditions[0].model_copy(update={"op": "gt"}))}) if t.conditions else t
        for t in pack.model.transitions)})
    assert reach(pack, never, "OnLoan")["verdict"] == "NOT_SHOWN"


@pytest.mark.parametrize(("request_text", "steps"), [
    ("allow Clerk to Return", [{"kind": "set_role", "transition": "TR-RETURN", "role": "Clerk"}]),  # the kernel changes both
    ("remove Return", [{"kind": "remove_transition", "transition": "TR-RETURN"},
                       {"kind": "remove_transition", "transition": "TR-RETURN-OVERDUE"}]),
    ("remove Return from Overdue", [{"kind": "remove_transition", "transition": "TR-RETURN-OVERDUE"}]),
    ("move Return from Overdue source to Requested",
     [{"kind": "retarget_transition", "transition": "TR-RETURN-OVERDUE", "end": "source", "state": "Requested"}]),
    ("move Return target to Cancelled", [{"kind": "retarget_transition", "transition": "TR-RETURN", "end": "target", "state": "Cancelled"}]),
])
def test_chat_edits_an_action_that_leaves_several_states(tmp_path, request_text, steps):
    pack = load_pack(kernel_loan(tmp_path))
    assert [s["transaction"] for s in OfflinePlanProposer().propose(request_text, pack.model, pack)["steps"]] == steps


@pytest.mark.parametrize(("request_text", "said"), [
    ("move Return source to Requested", "Return leaves OnLoan, Overdue: say which"),
    ("remove Return from Cancelled", "Return does not leave Cancelled"),
])
def test_an_ambiguous_or_wrong_source_is_named(tmp_path, request_text, said):
    pack = load_pack(kernel_loan(tmp_path))
    with pytest.raises(DomainError, match=said):
        OfflinePlanProposer().propose(request_text, pack.model, pack)


# Each use case line must end on its ellipse, not on the ellipse's bounding box; |norm - 1| is how far off it is.
ELLIPSE_ENDS = """() => {
  const svg = document.querySelector('#usecase-canvas svg'), off = [];
  const ellipses = [...svg.querySelectorAll('ellipse')].map((e) => ({cx: +e.getAttribute('cx'), cy: +e.getAttribute('cy'),
    rx: +e.getAttribute('rx'), ry: +e.getAttribute('ry')})).filter((e) => e.rx > 40);
  for (const path of svg.querySelectorAll('path')) {
    const d = (path.getAttribute('d') || '').trim(), n = d.match(/-?[0-9.]+/g);
    if (!/^M[^A-Za-z]*L[^A-Za-z]*$/.test(d) || n.length !== 4) continue;  // a straight association line, not an actor
    const ends = [[+n[0], +n[1]], [+n[n.length - 2], +n[n.length - 1]]];
    const best = Math.min(...ends.flatMap(([x, y]) => ellipses.map((e) => Math.abs(((x - e.cx) / e.rx) ** 2 + ((y - e.cy) / e.ry) ** 2 - 1))));
    if (Number.isFinite(best)) off.push(best);
  }
  return off;
}"""


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_the_new_kernel_features_read_right_in_a_real_browser(tmp_path):
    api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci or demos extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - demos start a real server; only this opt-in test needs it

    with ephemeral_eija_server(pack=kernel_loan(tmp_path)) as server, api.sync_playwright() as playwright:
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
            # The outline tells apart two transitions one action labels, by the state each leaves.
            outline = page.locator("#outline-transitions button").all_inner_texts()
            assert "Return [Librarian] from OnLoan" in outline and "Return [Librarian] from Overdue" in outline
            # Selecting one offers phrases that name it, and chat reads them.
            page.locator('#outline-transitions [data-id="transition:TR-RETURN-OVERDUE"]').click()
            assert page.locator('#chat-suggest [data-phrase="remove Return from Overdue"]').count() == 1
            page.fill("#chat-input", "remove Return from Overdue")
            page.click("#chat-send")
            page.wait_for_selector("#chat-log .plan .plan-verdict.ok", timeout=30_000)
            # The tests give the record values the guard reads, and pass.
            page.click("#tab-tests")
            page.click("#tests-run")
            page.wait_for_selector("#tests-summary:has-text('All 7 tests pass')", timeout=30_000)
            assert "with renewals = 1" in page.inner_text("#tests-list")
            # The permissions matrix tries CheckOut on a record whose values meet its guard, and says so.
            page.click("#tab-access")
            page.wait_for_selector(".access-grid")
            checkout = page.locator(".perm", has=page.locator("button.perm-name", has_text="CheckOut"))
            assert "when [renewals ≤ 3]" in checkout.inner_text()
            assert "✓ librarian-assigned" in checkout.inner_text()
            page.select_option('.reach select[aria-label="State"]', "Returned")
            page.click(".reach button.primary")
            page.wait_for_selector(".reach-answer .verdict.ok")
            assert "renewals = 2" in page.inner_text(".reach-answer")
            # Use case lines end on the ellipse, not short of it.
            page.click("#tab-usecases")
            page.wait_for_selector("#usecase-canvas svg ellipse")
            off = page.evaluate(ELLIPSE_ENDS)
            assert off and max(off) < 0.12, off
            # The built borrower is on no screen, so no app is built: the components tab says so below its lens bar.
            page.click("#tab-components")
            said = page.wait_for_selector("#component-canvas .empty.under-bar")
            bar = page.locator("#component-bar").bounding_box()
            text_top = page.evaluate("""(p) => { const r = document.createRange(); r.selectNodeContents(p);
                return r.getBoundingClientRect().top; }""", said)
            assert text_top >= bar["y"] + bar["height"], (text_top, bar)
            said.query_selector("button").click()
            page.wait_for_selector("#screens:not([hidden])")
            assert errors == []
        finally:
            chrome.close()
