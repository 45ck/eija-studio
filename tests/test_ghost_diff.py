"""How a change looks (ADR-0176): the model in force and the change as one union, each element with a status, removed
elements kept as ghosts, a moved arrow drawn once with its old route, and every change listed in a fixed order."""
from __future__ import annotations

from pathlib import Path

from eija_studio.application.diagrams import diff_summary
from eija_studio.application.ghost_diff import ghost_diff
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.transactions import parse_transaction

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
PLAN = [
    {"kind": "add_state", "state": "Lost", "after": "Overdue"},
    {"kind": "add_transition", "id": "TR-RENEW", "action": "Renew", "from_state": "Overdue", "to_state": "Lost", "role": "Librarian"},
    {"kind": "set_role", "transition": "TR-MARKOVERDUE", "role": "Member"},
    {"kind": "retarget_transition", "transition": "TR-RETURNLATE", "end": "target", "state": "Lost"},
    {"kind": "remove_transition", "transition": "TR-CANCEL"},
]


def changed() -> Workflow:
    return apply_transactions(LOAN.model, [parse_transaction(step) for step in PLAN], LOAN)


def by_key(ghost):
    return {t["key"]: t for t in ghost["transitions"]}


def test_every_element_of_both_models_is_drawn_with_its_status():
    before, after = LOAN.model, changed()
    ghost = ghost_diff(before, after)
    assert {s["name"] for s in ghost["states"]} == set(before.states) | set(after.states)
    assert {s["name"]: s["status"] for s in ghost["states"]}["Lost"] == "added"
    edges = by_key(ghost)
    assert edges["t:TR-RENEW"]["status"] == "added"
    assert edges["was:TR-CANCEL"]["status"] == "removed"  # a removed arrow stays, as a ghost
    assert edges["t:TR-MARKOVERDUE"]["status"] == "changed"
    assert edges["t:TR-MARKOVERDUE"]["fields"] == [{"field": "role", "before": "Clerk", "after": "Member"}]
    assert edges["t:TR-CHECKOUT"]["status"] == "same"


def test_a_moved_arrow_is_one_change_with_its_old_route_as_a_ghost():
    ghost = ghost_diff(LOAN.model, changed())
    edges = by_key(ghost)
    moved, was = edges["t:TR-RETURNLATE"], edges["was:TR-RETURNLATE"]
    assert moved["status"] == "moved" and (moved["from_state"], moved["to_state"]) == ("Overdue", "Lost")
    assert moved["was"] == {"from_state": "Overdue", "to_state": "Returned"}
    assert was["status"] == "was" and was["to_state"] == "Returned" and was["moved_to"] == "TR-RETURNLATE"
    [change] = [c for c in ghost["changes"] if c["ref"] == "t:TR-RETURNLATE"]
    assert change["change"] == "moved" and change["was"] == "was:TR-RETURNLATE"
    assert "now Overdue → Lost, was Overdue → Returned" in change["text"]


def test_the_change_list_names_every_change_once_in_a_fixed_order():
    ghost = ghost_diff(LOAN.model, changed())
    assert [c["n"] for c in ghost["changes"]] == list(range(1, len(ghost["changes"]) + 1))
    assert [c["text"] for c in ghost["changes"]] == [
        "Adds state Lost",
        "Removes Cancel [Member]: Requested → Cancelled",
        "Changes MarkOverdue (OnLoan → Overdue): role Clerk → Member",
        "Adds Renew [Librarian]: Overdue → Lost",
        "Moves ReturnLate: now Overdue → Lost, was Overdue → Returned",
    ]
    assert ghost["counts"] == {"added": 2, "removed": 1, "changed": 1, "moved": 1}
    cells = {s["name"] for s in ghost["states"]}
    for c in ghost["changes"]:  # every change points at a cell the page draws
        assert c["ref"] in by_key(ghost) or c["ref"].removeprefix("state:") in cells


def test_it_agrees_with_the_shared_definition_of_changed():
    before, after = LOAN.model, changed()
    ghost, summary = ghost_diff(before, after), diff_summary(before, after)
    edges = [t for t in ghost["transitions"] if t["status"] != "was"]
    assert sorted(t["action"] for t in edges if t["status"] == "added") == summary["added_actions"]
    assert sorted(t["action"] for t in edges if t["status"] == "removed") == summary["removed_actions"]
    assert sorted(t["action"] for t in edges if t["status"] in ("changed", "moved")) == sorted(summary["changed_actions"])


def test_reordering_either_model_changes_nothing():
    before, after = LOAN.model, changed()
    shuffled = Workflow.model_validate({**after.model_dump(mode="json"), "states": list(reversed(after.states)),
                                        "transitions": [t.model_dump(mode="json") for t in reversed(after.transitions)]})
    assert ghost_diff(before, shuffled) == ghost_diff(before, after)


def test_no_change_has_nothing_to_show_and_a_moved_start_is_one_change():
    same = ghost_diff(LOAN.model, LOAN.model)
    assert same["changes"] == [] and all(t["status"] == "same" for t in same["transitions"])
    assert not any(s["touched"] for s in same["states"])
    start = apply_transactions(LOAN.model, [parse_transaction({"kind": "set_initial", "state": "OnLoan"})], LOAN)
    ghost = ghost_diff(LOAN.model, start)
    assert ghost["initial"] == {"before": "Requested", "after": "OnLoan"}
    assert ghost["changes"][0] == {"n": 1, "ref": "initial-edge", "change": "moved", "was": "was:initial-edge",
                                   "text": "Records now start in OnLoan, not Requested"}
