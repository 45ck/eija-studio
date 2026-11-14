"""Review a change in PlayIDE (ADR-0175): what changed, how risky, and what the kernel does differently on both models."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application.review import behaviour_diff, review_change, row_text
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.transactions import parse_transaction

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
RENEW = {"kind": "add_transition", "id": "TR-RENEW", "action": "Renew", "from_state": "Overdue", "to_state": "OnLoan", "role": "Librarian"}


def changed(*steps: dict) -> object:
    return apply_transactions(LOAN.model, [parse_transaction(s) for s in steps], LOAN)


def by_text(review: dict) -> dict[str, dict]:
    return {item["text"]: item for item in review["items"]}


def test_a_deleted_path_is_high_risk_first_and_its_kernel_behaviour_is_asked_before_it_is_shown():
    review = review_change(LOAN, LOAN.model, changed(RENEW, {"kind": "remove_transition", "transition": "TR-RETURNLATE"}))
    assert review["changed"] and review["risk"] == {"high": 1, "medium": 1, "low": 0}
    first, second = review["items"]
    assert first["text"] == "Remove ReturnLate: Overdue → Returned, by Librarian" and first["risk"] == "high"
    assert first["element"] == "transition:TR-RETURNLATE" and first["change"] == "removed"
    assert second["text"] == "Add Renew: Overdue → OnLoan, by Librarian" and second["risk"] == "medium"
    rows = {r["n"]: r for r in review["behaviour"]["rows"]}
    late = rows[first["rows"][0]]
    assert (late["action"], late["state"], late["before"]["outcome"], late["after"]) == (
        "ReturnLate", "Overdue", "COMMITTED", {"outcome": "REFUSED", "code": "ACTION_DENIED"})
    assert late["actors"] == ["librarian-assigned", "librarian-unassigned"]  # the revoked librarian was refused before too
    assert first["question"]["answer"] == "no" and second["question"]["answer"] == "yes"
    assert "can a Librarian take ReturnLate on a record in Overdue" in first["question"]["text"]


def test_knock_on_effects_nobody_edited_are_reviewed_too():
    review = review_change(LOAN, LOAN.model, changed({"kind": "remove_transition", "transition": "TR-MARKOVERDUE"}))
    items = by_text(review)
    gone = items["Overdue can no longer be reached"]
    assert gone["risk"] == "high" and not gone["edited"] and gone["element"] == "state:Overdue"
    assert "CheckOut → MarkOverdue" in gone["reasons"][0]
    assert items["Remove MarkOverdue: OnLoan → Overdue, by Clerk"]["edited"]
    assert "No record reached Overdue" in review["simulation"]["new_findings"]
    stuck = review_change(LOAN, LOAN.model, changed({"kind": "remove_transition", "transition": "TR-RETURNLATE"}))
    assert by_text(stuck)["Records in Overdue get stuck"]["reasons"] == [
        "Before, records left Overdue by ReturnLate; now nothing leaves it."]


def test_changing_who_may_act_is_high_risk_and_the_kernel_shows_who_is_now_refused():
    review = review_change(LOAN, LOAN.model, changed({"kind": "set_role", "transition": "TR-MARKOVERDUE", "role": "Librarian"}))
    (item,) = review["items"]
    assert item["text"] == "Change MarkOverdue: OnLoan → Overdue, by Librarian"
    assert item["risk"] == "high" and item["reasons"] == ["Changes who may act: Clerk → Librarian."]
    rows = [r for r in review["behaviour"]["rows"] if r["n"] in item["rows"]]
    assert {(r["role"], r["after"]["outcome"]) for r in rows} == {("Clerk", "REFUSED"), ("Librarian", "COMMITTED")}
    assert item["question"]["text"].startswith("After this change, can a Clerk take MarkOverdue") and item["question"]["answer"] == "no"


def test_the_same_model_has_nothing_to_review_and_the_kernel_agrees_with_itself():
    review = review_change(LOAN, LOAN.model, LOAN.model)
    assert not review["changed"] and review["items"] == [] and review["behaviour"]["rows"] == []
    actors, states, actions = len(LOAN.fixtures.actors), len(LOAN.model.states), len(LOAN.model.transitions)
    assert behaviour_diff(LOAN, LOAN.model, LOAN.model)["attempts"] == 2 * actors * states * actions


def test_a_model_from_another_pack_is_refused():
    excursion = load_pack(ROOT / "packs" / "excursion")
    with pytest.raises(DomainError) as refused:
        review_change(LOAN, excursion.model, LOAN.model)
    assert refused.value.code == "WORKFLOW_PACK_MISMATCH"


def test_the_seeded_simulation_runs_on_both_sides():
    review = review_change(LOAN, LOAN.model, changed({"kind": "remove_transition", "transition": "TR-RETURNLATE"}))
    sim = review["simulation"]
    assert sim["before"]["model"] == LOAN.model.semantic_hash and sim["after"]["model"] == review["after"]
    assert (sim["seed"], sim["steps"]) == (1, 500) and sim["before"]["committed"] != sim["after"]["committed"]


def test_a_renamed_state_is_one_low_risk_change_with_nothing_to_run():
    review = review_change(LOAN, LOAN.model, changed({"kind": "rename_state", "state": "Overdue", "to": "Late"}))
    (item,) = review["items"]
    assert (item["text"], item["risk"], item["change"], item["element"]) == ("Rename state Overdue to Late", "low", "renamed", "state:Late")
    assert item["reasons"] == ["Only the name changes: the 2 transitions that used Overdue now use Late."]
    assert item["states"] == ["Overdue", "Late"] and item["rows"] == [] and item["question"] is None
    assert review["renamed"] == {"Overdue": "Late"} and review["behaviour"]["rows"] == []
    assert review["simulation"]["new_findings"] == review["simulation"]["gone_findings"] == []


def test_other_edits_to_a_renamed_state_are_reviewed_under_its_new_name():
    review = review_change(LOAN, LOAN.model, changed({"kind": "rename_state", "state": "Overdue", "to": "Late"},
                                                     {"kind": "remove_transition", "transition": "TR-RETURNLATE"}))
    items = by_text(review)
    assert review["risk"] == {"high": 2, "medium": 0, "low": 1}
    assert items["Remove ReturnLate: Late → Returned, by Librarian"]["question"]["answer"] == "no"
    assert items["Records in Late get stuck"]["risk"] == "high"
    assert items["Rename state Overdue to Late"]["reasons"] == ["Only the name changes: the 1 transition that used Overdue now uses Late."]


def test_a_new_state_that_takes_over_only_some_arrows_is_not_a_rename():
    review = review_change(LOAN, LOAN.model, changed({"kind": "add_state", "state": "Late"},
                                                     {"kind": "retarget_transition", "transition": "TR-MARKOVERDUE", "end": "target", "state": "Late"}))
    assert review["renamed"] == {} and "Add state Late" in by_text(review)


def test_a_finding_about_a_renamed_state_stays_the_same_finding_whatever_the_name():
    lost = changed({"kind": "add_state", "state": "Lost (manual)"},
                   {"kind": "add_transition", "id": "TR-RENEW", "action": "Renew", "from_state": "Lost (manual)", "to_state": "OnLoan", "role": "Librarian"})
    found = apply_transactions(lost, [parse_transaction({"kind": "rename_state", "state": "Lost (manual)", "to": "Lost"})], LOAN)
    review = review_change(LOAN, lost, found)
    assert review["renamed"] == {"Lost (manual)": "Lost"}
    assert "No record reached Lost (manual)" in review["simulation"]["before"]["findings"]
    assert review["simulation"]["new_findings"] == review["simulation"]["gone_findings"] == []



def test_a_role_change_on_a_guarded_step_is_seen_on_a_record_whose_values_meet_the_guard(tmp_path):
    """Inspection 2026-11-14 R1: each attempt began on a record with no values, so a step behind a guard over values
    (ADR-0234) was refused on both sides and a role change on it showed no rows, no question and no kernel answer."""
    pack_dir = tmp_path / "library-loan"
    shutil.copytree(ROOT / "packs" / "library-loan", pack_dir)
    doc = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    for t in doc["model"]["transitions"]:
        if t["action"] == "Cancel":
            t["conditions"] = [{"attribute": "renewals", "op": "le", "value": 3}]
    (pack_dir / "pack.json").write_text(json.dumps(doc), encoding="utf-8")
    pack = load_pack(pack_dir)
    cancel = next(t for t in pack.model.transitions if t.action == "Cancel")
    after = apply_transactions(pack.model, [parse_transaction({"kind": "set_role", "transition": cancel.id, "role": "Librarian"})], pack)
    review = review_change(pack, pack.model, after)
    rows = [r for r in review["behaviour"]["rows"] if r["action"] == "Cancel"]
    assert len(rows) == 2 and all(r["values"]["renewals"] <= 3 for r in rows)
    assert " with renewals " in row_text(rows[0])
    (item,) = [i for i in review["items"] if "Cancel" in i["text"]]
    assert item["question"]["text"] == "After this change, can a Librarian take Cancel on a record in Requested?"
    assert item["question"]["answer"] == "yes"


def test_a_role_change_on_a_timed_step_is_seen_once_its_time_event_is_due():
    """Inspection 2026-11-14 R1: each attempt began on a record that had just entered its state, so a step with a time
    event (ADR-0237) was refused TIMER_NOT_DUE on both sides and a role change on it showed nothing."""
    desk = load_pack(ROOT / "packs" / "refund-desk")
    after = apply_transactions(desk.model, [parse_transaction({"kind": "set_role", "transition": "TR-ESCALATE", "role": "Supervisor"})], desk)
    review = review_change(desk, desk.model, after)
    rows = {r["role"]: r for r in review["behaviour"]["rows"] if r["action"] == "EscalateStale"}
    assert rows["SlaTimer"]["before"]["outcome"] == "COMMITTED" and rows["SlaTimer"]["after"]["code"] == "ROLE_DENIED"
    assert rows["Supervisor"]["after"]["outcome"] == "COMMITTED"
    (item,) = [i for i in review["items"] if "EscalateStale" in i["text"]]
    assert item["question"]["answer"] == "no" and "SlaTimer" in item["question"]["text"]


def test_a_change_to_value_guards_time_events_or_linked_steps_is_reviewed_not_a_crash():
    """Inspection 2026-11-14 R2: review_change raised KeyError on a changed value guard (ADR-0234) or linked step
    (ADR-0241) and read a time event (ADR-0237) as a renamed id; diff_summary sorted guard objects, so two guards on one
    transition raised TypeError in the plan preview, the review and the case's diagrams."""
    from eija_studio.application.diagram_catalog import _summary_table
    from eija_studio.application.diagrams import diff_summary
    from eija_studio.domain.models import Workflow
    raw = LOAN.model.model_dump(mode="json")
    for t in raw["transitions"]:
        if t["action"] == "Return":
            t["conditions"] = [{"attribute": "renewals", "op": "le", "value": 3}, {"attribute": "renewals", "op": "ge", "value": 0}]
        if t["action"] == "MarkOverdue":
            t["after"] = {"amount": 14, "unit": "days"}
    after = Workflow.model_validate(raw)
    changes = diff_summary(LOAN.model, after)["changed_actions"]
    assert changes["Return"] == [{"field": "conditions", "before": [], "after": ["renewals ≤ 3", "renewals ≥ 0"]}]
    assert changes["MarkOverdue"] == [{"field": "after", "before": None, "after": "after(14 days)"}]
    assert "renewals ≤ 3" in _summary_table(LOAN.model, after)
    reasons = {i["text"].split(":")[0]: (i["risk"], i["reasons"]) for i in review_change(LOAN, LOAN.model, after)["items"]}
    assert reasons["Change Return"] == ("low", ["Adds guard over values: renewals ≤ 3, renewals ≥ 0."])
    assert reasons["Change MarkOverdue"] == ("low", ["Adds a time event after(14 days): the step now waits that long in its source state."])
    back = {i["text"].split(":")[0]: (i["risk"], i["reasons"]) for i in review_change(LOAN, after, LOAN.model)["items"]}
    assert back["Change Return"][0] == "high" and back["Change MarkOverdue"] == ("high", ["Drops its time event after(14 days): it may be taken at once."])
