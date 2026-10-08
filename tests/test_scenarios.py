"""Law files and test cases as files PlayIDE opens, edits as drafts and runs (ADR-0177).

Scenarios are a pack's test cases, run by the kernel. The negative controls break the kernel or the model one way
each and require the scenario that pins that behaviour to fail at the right step, naming the diagram element.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application import runtime
from eija_studio.application.law_proof import compare_laws, prove_laws, with_laws
from eija_studio.application.scenario_run import record_steps, run_scenarios
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.scenarios import parse_scenarios, scenarios_for
from eija_studio.interfaces.cli import main
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
PACKS = ("excursion", "library-loan", "eija-review-slice")
LOAN = load_pack(ROOT / "packs" / "library-loan")
SESSION = "synthetic-scenarios-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


def scenario(report, scenario_id):
    return next(s for s in report["scenarios"] if s["id"] == scenario_id)


def loan_without(*actions: str) -> Workflow:
    data = LOAN.model.model_dump(mode="json")
    data["transitions"] = [t for t in data["transitions"] if t["action"] not in actions]
    return Workflow.model_validate(data)


@pytest.mark.parametrize("pack", PACKS)
def test_every_shipped_pack_has_scenarios_and_they_pass(pack):
    loaded = load_pack(ROOT / "packs" / pack)
    scenarios = scenarios_for(loaded)
    assert len(scenarios.scenarios) >= 5
    report = run_scenarios(loaded, loaded.model, scenarios)
    assert report["status"] == "PASS" and report["failed"] == 0
    assert report == run_scenarios(loaded, loaded.model, scenarios)  # deterministic


def test_a_recorded_test_expects_what_the_kernel_did_and_passes():
    steps = record_steps(LOAN, LOAN.model, None, [("librarian-assigned", "CheckOut"), ("member-a", "Return")])
    assert [s["then"] for s in steps] == [{"state": "OnLoan"}, {"refused": "ROLE_DENIED"}]
    document = {"id": LOAN.id, "scenarios": [{"id": "recorded", "title": "Recorded", "steps": steps}]}
    assert run_scenarios(LOAN, LOAN.model, parse_scenarios(document, LOAN.id))["status"] == "PASS"
    with pytest.raises(DomainError) as unknown:
        record_steps(LOAN, LOAN.model, "Nowhere", [("member-a", "Cancel")])
    assert unknown.value.code == "STATE_UNKNOWN"


def test_a_wrong_expectation_fails_at_its_step_and_the_rest_is_not_run():
    steps = [{"actor": "member-a", "action": "CheckOut", "then": {"state": "OnLoan"}},
             {"actor": "librarian-assigned", "action": "Return", "then": {"state": "Returned"}}]
    document = {"id": LOAN.id, "scenarios": [{"id": "wrong", "title": "A member lends", "steps": steps}]}
    report = run_scenarios(LOAN, LOAN.model, parse_scenarios(document, LOAN.id))
    result = scenario(report, "wrong")
    assert report["status"] == "FAIL" and result["failed_step"] == 0
    assert result["steps"][0]["actual"] == {"refused": "ROLE_DENIED"}
    assert "transition:TR-CHECKOUT" in result["steps"][0]["cells"]
    assert result["steps"][1]["status"] == "NOT_RUN"


def test_scenarios_file_is_checked():
    good = {"actor": "member-a", "action": "Cancel", "then": {"state": "Cancelled"}}
    with pytest.raises(DomainError) as both:
        parse_scenarios({"id": LOAN.id, "scenarios": [{"id": "x", "title": "x", "steps": [good | {"then": {"state": "A", "refused": "B"}}]}]}, LOAN.id)
    assert both.value.code == "SCENARIOS_INVALID"
    with pytest.raises(DomainError) as twice:
        parse_scenarios({"id": LOAN.id, "scenarios": [{"id": "x", "title": "x", "steps": [good]}] * 2}, LOAN.id)
    assert twice.value.code == "SCENARIOS_INVALID"
    with pytest.raises(DomainError) as other:
        parse_scenarios({"id": "excursion", "scenarios": []}, LOAN.id)
    assert other.value.code == "SCENARIOS_PACK_MISMATCH"


def test_a_start_state_the_model_lacks_fails_the_scenario():
    document = {"id": LOAN.id, "scenarios": [{"id": "gone", "title": "x", "start": "Archived",
                                              "steps": [{"actor": "member-a", "action": "Cancel", "then": {"state": "Cancelled"}}]}]}
    result = scenario(run_scenarios(LOAN, LOAN.model, parse_scenarios(document, LOAN.id)), "gone")
    assert result["status"] == "FAIL" and "Archived" in result["why"]


def test_a_model_the_policy_refuses_runs_no_scenario():
    data = LOAN.model.model_dump(mode="json")
    next(t for t in data["transitions"] if t["action"] == "CheckOut")["role"] = "Member"
    report = run_scenarios(LOAN, Workflow.model_validate(data), scenarios_for(LOAN))
    assert report["status"] == "REFUSED" and {s["status"] for s in report["scenarios"]} == {"NOT_RUN"}


# ---- negative controls ------------------------------------------------------------------------------------------

def test_negative_control_a_kernel_that_ignores_roles_fails_the_authority_tests(monkeypatch):
    monkeypatch.setattr(runtime, "check_actor", lambda actor, transition, command: None)
    report = run_scenarios(LOAN, LOAN.model, scenarios_for(LOAN))
    result = scenario(report, "member-cannot-lend")
    assert report["status"] == "FAIL" and result["status"] == "FAIL"
    assert result["steps"][0]["actual"] == {"state": "OnLoan"}


def test_negative_control_removing_a_transition_fails_the_test_that_uses_it():
    report = run_scenarios(LOAN, loan_without("ReturnLate"), scenarios_for(LOAN))
    result = scenario(report, "overdue-then-late-return")
    assert result["failed_step"] == 2 and result["steps"][2]["actual"] == {"refused": "ACTION_DENIED"}
    assert result["steps"][2]["cells"] == ["state:Overdue"]  # the transition is gone; the state it was drawn from is shown
    assert scenario(report, "lend-and-return")["status"] == "PASS"


# ---- the law file ---------------------------------------------------------------------------------------------

def laws_of(pack):
    return [law.model_dump(mode="json", exclude_none=True) for law in pack.laws]


def test_the_law_file_round_trips_and_a_draft_lists_what_it_changes():
    assert with_laws(LOAN, laws_of(LOAN)) == LOAN
    draft = [law for law in laws_of(LOAN) if law["id"] != "returned-requires-loan"]
    draft.append({"id": "onloan-only-via-checkout", "kind": "state_only_via", "code": "ONLOAN_NOT_VIA_CHECKOUT",
                  "description": "A loan starts only by checking it out.", "state": "OnLoan", "actions": ["CheckOut"]})
    changed = with_laws(LOAN, draft)
    assert compare_laws(LOAN, changed) == {"added": ["onloan-only-via-checkout"], "removed": ["returned-requires-loan"], "changed": []}
    assert prove_laws(changed)["status"] == "HOLDS"


def test_a_stricter_draft_law_the_model_breaks_is_reported():
    draft = [*laws_of(LOAN), {"id": "onloan-final", "kind": "state_final", "code": "FINAL_STATE_LEFT:OnLoan",
                              "description": "Nothing leaves OnLoan.", "state": "OnLoan"}]
    report = prove_laws(with_laws(LOAN, draft))
    assert report["status"] == "REFUSED"
    assert next(v for v in report["laws"] if v["id"] == "onloan-final")["status"] == "BROKEN"


def test_an_invalid_law_file_says_where():
    draft = [*laws_of(LOAN), {"id": "ghost", "kind": "state_final", "code": "X", "description": "x", "state": "Nowhere"}]
    with pytest.raises(DomainError) as invalid:
        with_laws(LOAN, draft)
    assert invalid.value.code == "LAWS_INVALID" and any("laws[ghost]" in p for p in invalid.value.details["problems"])


def test_cli_runs_the_scenarios(capsys, tmp_path):
    assert main(["scenarios", "--pack", str(ROOT / "packs" / "library-loan")]) == 0
    assert '"status": "PASS"' in capsys.readouterr().out
    workflow = tmp_path / "workflow.json"
    workflow.write_text(loan_without("ReturnLate").model_dump_json(), encoding="utf-8")
    assert main(["scenarios", "--pack", str(ROOT / "packs" / "library-loan"), "--workflow", str(workflow)]) == 2


# ---- PlayIDE --------------------------------------------------------------------------------------------------

@pytest.fixture
def loan_client(tmp_path):
    studio = harness_studio(tmp_path / "loan", pack=load_pack(ROOT / "packs" / "library-loan"))
    app = create_app(studio, SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"])
    app.state.play.stop()


def test_playide_runs_the_tests_on_the_shown_change(loan_client):
    assert loan_client.post("/api/play/tests", json={}, headers={"Origin": HEADERS["Origin"]}).status_code == 401
    report = loan_client.post("/api/play/tests", json={}, headers=HEADERS).json()
    assert report["status"] == "PASS" and report["file"]["path"] == "packs/library-loan/scenarios.json"
    assert {a["id"] for a in report["actors"]} >= {"member-a", "clerk"}
    steps = [s["transaction"] for s in loan_client.post("/api/play/plan", json={"request": "remove transition ReturnLate"},
                                                        headers=HEADERS).json()["steps"]]
    changed = loan_client.post("/api/play/tests", json={"plan": steps}, headers=HEADERS).json()
    assert scenario(changed, "overdue-then-late-return")["status"] == "FAIL"
    tried = loan_client.post("/api/play/tests/try", json={"steps": [["member-a", "Cancel"]]}, headers=HEADERS).json()
    assert tried["steps"] == [{"actor": "member-a", "action": "Cancel", "then": {"state": "Cancelled"}}]
    draft = report["file"]["document"]
    draft["scenarios"].append({"id": "added", "title": "Added here", "steps": tried["steps"]})
    assert loan_client.post("/api/play/tests", json={"scenarios": draft}, headers=HEADERS).json()["passed"] == len(draft["scenarios"])
    assert "/assets/play-tests.js" in loan_client.get("/play").text and loan_client.get("/assets/play-tests.js").status_code == 200


def test_playide_proves_a_draft_law_file_without_saving_it(loan_client):
    report = loan_client.post("/api/play/laws", json={}, headers=HEADERS).json()
    assert report["file"]["path"] == "packs/library-loan/pack.json" and "draft" not in report["file"]
    assert {v["kind"] for v in report["file"]["verifiers"]} >= {"runtime_matrix", "bend_proof"}
    draft = [law for law in report["file"]["laws"] if law["id"] != "returned-final"]
    proved = loan_client.post("/api/play/laws", json={"laws": draft}, headers=HEADERS).json()
    assert proved["file"]["draft"]["removed"] == ["returned-final"]
    assert "returned-final" not in {law["id"] for law in proved["file"]["draft_pack"]["laws"]}
    assert loan_client.post("/api/play/laws", json={}, headers=HEADERS).json()["file"]["laws"] == report["file"]["laws"]  # unsaved
    bad = loan_client.post("/api/play/laws", json={"laws": [*draft, {"id": "x"}]}, headers=HEADERS)
    assert bad.status_code >= 400 and bad.json()["code"] == "LAWS_INVALID"
