"""The pack's scenarios drawn as sequence diagrams the kernel checks (ADR-0195): one source, `scenarios.json`
(ADR-0177), one runner, `scenario_run`. A step the model can't do is flagged at that message with the kernel's reason,
a step that expects a refusal is a neg fragment that must be refused, and a change shows the scenarios it breaks or
fixes. Negative oracles included: refused messages, a neg the kernel lets through, a wrong refusal code, a wrong
state, an unreachable message, and malformed drafts."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.new_system import sketch_documents
from eija_studio.application.sequence_draft import draft_scenarios, scenarios_or_draft
from eija_studio.application.sequences import check_sequences
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack, parse_pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.scenarios import parse_scenarios, scenarios_for
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
SESSION = "synthetic-sequences-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


def step(actor, action, state=None, refused=None):
    return {"actor": actor, "action": action, "then": {"state": state} if state else {"refused": refused}}


def one(*steps, start=None):
    scenario = {"id": "s", "title": "S", "steps": list(steps)} | ({"start": start} if start else {})
    return parse_scenarios({"id": "library-loan", "scenarios": [scenario]}, "library-loan")


def checked(scenarios, model=LOAN.model, base=None):
    return check_sequences(LOAN, model, scenarios, base)


def by_ref(sequence):
    return {m["ref"]: m for m in sequence["messages"]}


def clerk_returns_late():
    t = next(t for t in LOAN.model.transitions if t.action == "ReturnLate")
    return apply_transactions(LOAN.model, [parse_transaction({"kind": "set_role", "transition": t.id, "role": "Clerk"})], LOAN)


def test_every_packs_scenarios_are_drawn_and_produced_by_the_kernel():
    for name in ("library-loan", "excursion", "eija-review-slice"):
        pack = load_pack(ROOT / "packs" / name)
        report = check_sequences(pack, pack.model, scenarios_for(pack))
        assert report["status"] == "PRODUCIBLE" and len(report["sequences"]) == len(scenarios_for(pack).scenarios), name
    report = checked(scenarios_for(LOAN))
    late = report["sequences"][1]
    assert [(m["verdict"], m["states"], m["transition"]) for m in late["messages"]] == [
        ("OK", ["OnLoan"], "TR-CHECKOUT"), ("OK", ["Overdue"], "TR-MARKOVERDUE"), ("OK", ["Returned"], "TR-RETURNLATE")]
    assert [v["text"] for v in late["invariants"]] == ["{Requested}", "{OnLoan}", "{Overdue}", "{Returned}"]
    assert [e["label"] for e in late["effects"] if e["ref"] == "0"] == ["Audit: LoanCheckedOut", "Notification: MemberNotified"]  # lost messages
    assert [(a["ref"], a["y0"] < a["y1"]) for a in late["activations"]] == [("0", True), ("1", True), ("2", True)]
    cancels = report["sequences"][6]
    assert [(f["operator"], f["verdict"], f["refused"]) for f in cancels["fragments"]] == [("neg", "HOLDS", "STATE_DENIED")]
    assert [(r["label"], r["tone"]) for r in cancels["replies"]] == [("refused: STATE_DENIED", "expected")]


def test_a_step_the_model_cant_do_is_flagged_where_the_kernel_refuses_it_and_the_rest_is_not_reached():
    for first, code, why in [
        (step("librarian-assigned", "Renew", "OnLoan"), "ACTION_DENIED", "Renew is not in the model"),
        (step("member-a", "CheckOut", "OnLoan"), "ROLE_DENIED", "member-a is a Member; CheckOut is for a Librarian"),
        (step("librarian-assigned", "Return", "Returned"), "STATE_DENIED", "Return does not leave Requested"),
        (step("nobody", "CheckOut", "OnLoan"), "UNKNOWN_ACTOR", "nobody is not one of the pack's actors"),
    ]:
        sequence = checked(one(first, step("librarian-assigned", "CheckOut", "OnLoan")))["sequences"][0]
        a, b = by_ref(sequence)["0"], by_ref(sequence)["1"]
        assert (sequence["verdict"], a["verdict"], a["code"]) == ("BROKEN", "BROKEN", code)
        assert a["why"].endswith(why) and a["why"].startswith("Expected it moves to") and sequence["first_problem"] == a["why"]
        assert b["verdict"] == "NOT_REACHED" and sequence["replies"][0]["tone"] == "bad"
        assert [v["ref"] for v in sequence["invariants"]] == ["start"]


def test_a_neg_the_kernel_lets_through_refuses_for_another_reason_or_a_wrong_state_is_broken():
    allowed = checked(one(step("librarian-assigned", "CheckOut", refused="ROLE_DENIED")))["sequences"][0]
    assert allowed["verdict"] == "BROKEN" and allowed["fragments"][0]["verdict"] == "BROKEN"
    assert allowed["invariants"][-1] | {"y": 0} == {"ref": "0", "lifeline": "record:loan", "y": 0, "text": "{OnLoan}", "tone": "bad"}
    wrong = checked(one(step("member-a", "CheckOut", refused="STATE_DENIED")))["sequences"][0]
    assert (wrong["fragments"][0]["verdict"], wrong["messages"][0]["code"]) == ("BROKEN", "ROLE_DENIED")
    assert "member-a is a Member" in wrong["first_problem"]
    elsewhere = checked(one(step("member-a", "Cancel", "Returned")))["sequences"][0]["messages"][0]
    assert (elsewhere["verdict"], elsewhere["states"]) == ("BROKEN", ["Cancelled"])
    nowhere = checked(one(step("member-a", "Cancel", "Cancelled"), start="Lost"))["sequences"][0]
    assert nowhere["verdict"] == "BROKEN" and "Lost" in nowhere["first_problem"] and nowhere["messages"][0]["verdict"] == "NOT_REACHED"


def test_a_change_shows_the_scenarios_it_breaks_and_fixes():
    report = checked(scenarios_for(LOAN), clerk_returns_late(), LOAN.model)
    late = report["sequences"][1]
    assert report["changed"] and (late["verdict"], late["was"], late["change"]) == ("BROKEN", "PRODUCIBLE", "breaks")
    third = by_ref(late)["2"]
    assert (third["verdict"], third["was"], third["change"], third["code"]) == ("BROKEN", "OK", "changed", "ROLE_DENIED")
    assert by_ref(late)["0"]["change"] == "same"
    assert [s["change"] for s in report["sequences"]].count("same") == len(report["sequences"]) - 1
    renew = one(step("librarian-assigned", "CheckOut", "OnLoan"), step("clerk", "MarkOverdue", "Overdue"), step("librarian-assigned", "Renew", "OnLoan"))
    renewing = apply_transactions(LOAN.model, [parse_transaction({"kind": "add_transition", "id": "TR-RENEW", "action": "Renew",
                                                                   "from_state": "Overdue", "to_state": "OnLoan", "role": "Librarian"})], LOAN)
    fixed = checked(renew, renewing, LOAN.model)["sequences"][0]
    assert (fixed["verdict"], fixed["was"], fixed["change"], by_ref(fixed)["2"]["change"]) == ("PRODUCIBLE", "BROKEN", "fixes", "added")


def test_the_layout_puts_lifelines_in_columns_and_rows_top_to_bottom():
    sequence = checked(scenarios_for(LOAN))["sequences"][6]
    xs = [lifeline["x"] for lifeline in sequence["lifelines"]]
    assert xs == sorted(set(xs)) and [lifeline["kind"] for lifeline in sequence["lifelines"]] == ["actor", "actor", "record", "effect"]
    ys = [m["y"] for m in sequence["messages"]]
    assert ys == sorted(ys) and len(set(ys)) == len(ys) and max(ys) < sequence["height"]
    frame, inside = sequence["fragments"][0], by_ref(sequence)["1"]
    assert frame["y0"] < inside["y"] < frame["y1"] and frame["y0"] > by_ref(sequence)["0"]["y"]


def test_sequences_export_through_the_existing_mermaid_and_plantuml_emitters():
    sequence = checked(scenarios_for(LOAN))["sequences"][6]
    mermaid, plantuml = sequence["export"]["mermaid"], sequence["export"]["plantuml"]
    assert "member_a->>loan: Cancel()" in mermaid and "opt neg: refused#58; STATE_DENIED" in mermaid
    assert "group neg [refused: STATE_DENIED]" in plantuml and "loan --> librarian_assigned : refused: STATE_DENIED" in plantuml
    assert "note over loan : {Requested}" in plantuml and "note over loan : {Cancelled}" in plantuml  # the invariants the canvas draws
    assert plantuml.index("{Requested}") < plantuml.index("Cancel()") < plantuml.index("{Cancelled}")


def test_a_system_without_scenarios_gets_a_draft_whose_expectations_the_kernel_wrote():
    sketch = "Booked -> InRepair : StartRepair [Mechanic]\nInRepair -> Ready : FinishRepair [Mechanic]\nReady -> Collected : Collect [Customer]\nBooked -> Cancelled : Cancel [Customer]"
    pack = parse_pack(sketch_documents("Bike repair", "Repair", sketch, "bike-repair")["pack.json"])
    drafted, source = scenarios_or_draft(pack, scenarios_for(pack), pack.model)
    assert source == "drafted" and [s.title for s in drafted.scenarios] == ["Booked to Collected", "Booked to Cancelled", "Only the Customer role may Cancel"]
    assert drafted == draft_scenarios(pack, pack.model)  # deterministic
    assert drafted.scenarios[2].steps[0].then.refused == "ROLE_DENIED"  # what the kernel answered, not a guess
    assert check_sequences(pack, pack.model, drafted)["status"] == "PRODUCIBLE"
    assert scenarios_or_draft(LOAN, scenarios_for(LOAN), LOAN.model)[1] == "pack"  # a pack's own scenarios win


def test_scenarios_of_another_pack_are_refused():
    with pytest.raises(DomainError) as refused:
        check_sequences(LOAN, LOAN.model, parse_scenarios({"id": "excursion", "scenarios": []}, "excursion"))
    assert refused.value.code == "SCENARIOS_PACK_MISMATCH"


@pytest.fixture
def client(tmp_path):
    studio = harness_studio(tmp_path / "workspace", pack=LOAN)
    app = create_app(studio, SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"]), studio
    app.state.play.stop()


def test_the_route_checks_the_shown_model_against_the_model_in_force_and_saves_nothing(client):
    client, studio = client
    with studio.store.transaction() as u:
        before = u.active()["model"]
    assert client.post("/api/play/sequences", json={}, headers={"Origin": HEADERS["Origin"]}).status_code == 401
    plain = client.post("/api/play/sequences", json={}, headers=HEADERS).json()
    assert (plain["source"], plain["status"], plain["changed"]) == ("pack", "PRODUCIBLE", False)
    t = next(t for t in LOAN.model.transitions if t.action == "ReturnLate")
    plan = [{"kind": "set_role", "transition": t.id, "role": "Clerk"}]
    planned = client.post("/api/play/sequences", json={"plan": plan}, headers=HEADERS).json()
    assert planned["changed"] and planned["sequences"][1]["change"] == "breaks"
    draft = one(step("librarian-assigned", "Renew", "OnLoan")).model_dump(mode="json", exclude_none=True)
    edited = client.post("/api/play/sequences", json={"scenarios": draft}, headers=HEADERS).json()
    assert (edited["source"], edited["status"]) == ("edited", "BROKEN")
    malformed = client.post("/api/play/sequences", json={"scenarios": {"id": "library-loan", "scenarios": [{"id": "x"}]}}, headers=HEADERS).json()
    assert malformed["code"] == "SCENARIOS_INVALID"
    ripple = client.post("/api/play/ripple", json={"plan": plan}, headers=HEADERS).json()
    assert [i["code"] for i in ripple["diagrams"]["sequences"]] == ["SEQUENCE_BROKEN"]
    with studio.store.transaction() as u:
        assert u.active()["model"] == before
    page = client.get("/play").text
    assert "/assets/play-sequence.js" in page and client.get("/assets/play-sequence.js").status_code == 200
    assert client.get("/assets/play-sequence.css").status_code == 200


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: real-browser check; set EIJA_BROWSER_TESTS=1")
def test_the_sequences_tab_draws_flags_and_edits_in_a_real_browser():
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
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click("#tab-sequences")
            page.wait_for_selector(".seq-verdict.ok")
            page.click("#seq-list li:nth-child(2) button")
            assert page.evaluate("PlaySequence.result().sequences.length") == 7
            assert page.evaluate("Boolean(PlayIDE.diagram('sequences'))")  # the Changes view navigates on this graph
            page.select_option("#seq-actor", "librarian-assigned")
            page.select_option("#seq-action", "Renew")
            page.click("#seq-add button")  # the new step expects what the kernel does: Renew is refused, drawn as a neg
            for _ in range(100):  # the page's CSP has no unsafe-eval, so poll rather than wait_for_function
                if page.evaluate("PlaySequence.result().sequences[1].steps") == 4:
                    break
                page.wait_for_timeout(100)
            assert page.evaluate("PlaySequence.result().sequences[1].fragments.map((f) => f.verdict)") == ["HOLDS"]
            page.select_option("#inspector select[aria-label='What it must do']", "state:OnLoan")
            page.wait_for_selector(".seq-verdict.bad")  # now it expects a move the model can't make: flagged with the reason
            assert "Renew is not in the model" in page.inner_text("#seq-verdict")
            assert page.inner_text("#tab-sequences .badge") == "✗ 1"
            problems = page.inner_text("#seq-problems")  # a red tab names the scenario, the step and why, with the way out
            assert "1 of 7 scenarios fail" in problems and "Step 4, Renew" in problems and "Expect what the model does now" in problems
            assert page.evaluate("PlayTests.draft().scenarios[1].steps.length") == 4  # one draft, shared with the Tests tab
            assert errors == []
        finally:
            chrome.close()
