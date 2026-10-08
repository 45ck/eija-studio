"""Ripple (ADR-0158): a change to the state machine shows its effect on every other diagram, and the proposer's
follow-on edits are re-checked by the policy or the screen design check before the person can take them."""
from __future__ import annotations

from pathlib import Path

from eija_studio.adapters.plan_proposals import OfflinePlanProposer
from eija_studio.application.components import app_components
from eija_studio.application.ripple import check_follow_ons, ripple
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.screens import Screens, check_screens, default_screens, screens_for
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.app_build import app_files

ROOT = Path(__file__).resolve().parents[1]

LOAN = load_pack(ROOT / "packs" / "library-loan")
DATA = data_for(LOAN)
ADD_LOST = {"kind": "add_state", "state": "Lost", "after": "Overdue"}
RENEW = {"kind": "add_transition", "id": "TR-RENEW", "action": "Renew", "from_state": "Overdue", "to_state": "Lost", "role": "Librarian"}
NO_LATE_RETURN = {"kind": "remove_transition", "transition": "TR-RETURNLATE"}


def built(model: Workflow, screens: Screens):
    try:
        files, manifest = app_files(LOAN, model, screens)
    except DomainError as error:
        return error, []
    return (files, manifest["oracle"]["cases"]), app_components(files)["components"]


def report(plan: list[dict], screens: Screens | None = None) -> tuple[dict, Workflow, Screens]:
    candidate = apply_transactions(LOAN.model, [parse_transaction(step) for step in plan], LOAN)
    before = screens_for(LOAN, LOAN.model, DATA)
    after = screens if screens is not None else screens_for(LOAN, candidate, DATA)
    (old, _), (new, components) = built(LOAN.model, before), built(candidate, after)
    return ripple(LOAN.model, candidate, DATA, (before, after), (old, new), components), candidate, after


def follow_ons(plan: list[dict], screens: Screens | None = None) -> tuple[dict, list[dict]]:
    result, candidate, after = report(plan, screens)
    document = OfflinePlanProposer().follow_on(result, candidate, LOAN)
    return result, check_follow_ons(document, LOAN.model, plan, LOAN, candidate, after, DATA)


def texts(result: dict, diagram: str) -> list[str]:
    return [item["text"] for item in result["diagrams"][diagram]]


def test_a_new_state_ripples_into_the_class_diagram_and_the_generated_files():
    result, _, _ = report([ADD_LOST])
    assert "Adds state Lost" in texts(result, "states")
    assert texts(result, "classes") == ["LoanState gains the literal Lost"]
    assert texts(result, "usecases") == [] and texts(result, "screens") == []
    assert "app/model.json is regenerated" in texts(result, "components")
    assert result["conformance"]["cases_before"] < result["conformance"]["cases_after"]
    assert [p["code"] for p in result["problems"]] == ["STATE_UNREACHABLE"] and result["agree"]  # a warning: it still builds


def test_the_ai_proposes_a_way_into_an_unreachable_state_and_the_policy_checks_it():
    _, steps = follow_ons([ADD_LOST])
    assert [(s["status"], s["text"], s["fixes"]) for s in steps] == [
        ("applies", "Add Renew: Overdue → Lost, by Librarian", "STATE_UNREACHABLE")]
    taken, _, _ = report([ADD_LOST, steps[0]["transaction"]])
    assert taken["problems"] == []  # taking it leaves nothing out of step


def test_a_new_action_is_a_new_use_case_with_its_own_screen():
    result, _, _ = report([ADD_LOST, RENEW])
    assert texts(result, "usecases") == ["New use case Renew", "Librarian now takes Renew"]
    assert texts(result, "screens") == ["Renew gets a default screen"]
    assert "app/screens.json is regenerated" in texts(result, "components")


def test_a_removed_action_strands_its_screen_until_the_follow_on_removes_it():
    result, steps = follow_ons([NO_LATE_RETURN])
    assert not result["agree"] and result["conformance"]["cases_after"] is None  # the app cannot be built
    assert {p["code"] for p in result["problems"]} == {"STATE_NO_EXIT", "SCREEN_UNKNOWN_USE_CASE", "SCREENS_BLOCKED"}
    assert texts(result, "usecases") == ["Use case ReturnLate is gone"]
    fix = next(s for s in steps if s.get("screen_step", {}).get("op") == "remove")
    assert fix["status"] == "applies" and fix["problems_left"] == 0
    fixed, _, _ = report([NO_LATE_RETURN], Screens.model_validate(fix["screens"]))
    assert fixed["agree"] and fixed["conformance"]["cases_after"] > 0
    assert "The screen for ReturnLate is dropped" in texts(fixed, "screens")


def test_a_state_left_with_no_way_out_gets_a_proposed_exit_where_its_neighbours_go():
    _, steps = follow_ons([NO_LATE_RETURN])
    exit_step = next(s for s in steps if "transaction" in s)
    assert exit_step["text"] == "Add ReturnLate: Overdue → Returned, by Librarian" and exit_step["status"] == "applies"


def test_designed_screens_miss_a_new_action_and_the_ai_proposes_its_default_screen():
    designed = default_screens(LOAN, LOAN.model, DATA)  # designed before the change, so it has no screen for Renew
    result, steps = follow_ons([ADD_LOST, RENEW], designed)
    assert any(p["code"] == "SCREEN_MISSING_USE_CASE" for p in result["problems"]) and not result["agree"]
    add = next(s for s in steps if s.get("screen_step", {}).get("op") == "add")
    assert add["status"] == "applies" and add["screen_step"]["screen"]["use_case"] == "Renew"
    candidate = apply_transactions(LOAN.model, [parse_transaction(s) for s in (ADD_LOST, RENEW)], LOAN)
    assert check_screens(Screens.model_validate(add["screens"]), candidate, DATA) == []


def test_follow_ons_are_untrusted_and_rechecked():
    _, candidate, after = report([ADD_LOST])
    proposed = {"steps": [
        {"transaction": {"kind": "set_role", "transition": "TR-CHECKOUT", "role": "Member"}, "why": "protected"},
        {"transaction": {"kind": "nonsense"}},
        {"transaction": {"kind": "set_role", "transition": "TR-CANCEL", "role": "Librarian"}},  # allowed, but fixes nothing
        {"screen": {"op": "remove", "use_case": "Nowhere"}},
        {"screen": {"op": "add", "screen": {"use_case": "Cancel", "title": "Again"}}},  # a second screen fixes nothing
        "not a step",
    ]}
    checked = check_follow_ons(proposed, LOAN.model, [ADD_LOST], LOAN, candidate, after, DATA)
    assert [s["status"] for s in checked] == ["does_not_apply"] * 6
    assert "PROTECTED_AUTHORITY" in checked[0]["code"]
    assert checked[2]["code"] == checked[4]["code"] == "FOLLOW_ON_FIXES_NOTHING"
