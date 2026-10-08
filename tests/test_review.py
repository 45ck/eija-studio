"""Review a change in PlayIDE (ADR-0175): what changed, how risky, and what the kernel does differently on both models."""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.application.review import behaviour_diff, review_change
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
