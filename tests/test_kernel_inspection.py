"""Regression tests for the kernel defects the Fagan inspection of 13 November 2026 found (ADR-0246).

The inspection read the kernel line by line against its ADRs: `domain/policy.py`, `domain/models.py`, `domain/laws.py`,
`domain/value_guards.py`, `domain/transactions.py`, `domain/impact.py` and `application/runtime.py`. Each test below
fails on the code before the fix and names the defect it pins (K1 to K8 in
docs/quality/inspection-2026-11-13-kernel.md).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from eija_studio.application.law_proof import prove_laws
from eija_studio.application.runtime import execute, initialise
from eija_studio.application.simulation import MemorySession
from eija_studio.domain.impact import model_impact
from eija_studio.domain.laws import PathRequires, Step, evaluate_run, evaluate_table
from eija_studio.domain.models import DomainError, ExecuteCommand, ValueGuard, Workflow
from eija_studio.domain.pack import PACKS_ROOT, default_pack, load_pack
from eija_studio.domain.policy import apply_structural_all, apply_transactions, check_policy, transition
from eija_studio.domain.transactions import parse_transaction
from eija_studio.domain.value_guards import points

LOAN = load_pack(PACKS_ROOT / "library-loan")
DESK = load_pack(PACKS_ROOT / "refund-desk")
OPS = load_pack(PACKS_ROOT / "ai-ops")


def edit(pack, *transactions: dict) -> Workflow:
    return apply_structural_all(pack.model, [parse_transaction(tx) for tx in transactions], pack)


# ---- K1: a transition held by a role the pack does not declare -----------------------------------------------

def test_k1_a_transition_held_by_an_undeclared_role_is_refused_by_name():
    """The pack loader refuses its own model if a transition names an undeclared role, and the policy refused an
    undeclared initiator (ADR-0231), but a candidate could give any action to a role nobody can hold."""
    cancel = LOAN.model.transition_for("Cancel")
    candidate = edit(LOAN, {"kind": "set_role", "transition": cancel.id, "role": "Ghost"})
    assert check_policy(candidate, LOAN) == ["UNDECLARED_ROLE:" + cancel.id]
    with pytest.raises(DomainError) as refused:
        apply_transactions(LOAN.model, [parse_transaction({"kind": "set_role", "transition": cancel.id, "role": "Ghost"})], LOAN)
    assert refused.value.code == "POLICY_BLOCKED" and refused.value.details["codes"] == ["UNDECLARED_ROLE:" + cancel.id]


def test_k1_every_declared_role_still_passes():
    assert check_policy(LOAN.model, LOAN) == []
    cancel = LOAN.model.transition_for("Cancel")
    assert all(not c.startswith("UNDECLARED_ROLE")
               for r in LOAN.roles for c in check_policy(edit(LOAN, {"kind": "set_role", "transition": cancel.id, "role": r.id}), LOAN))


# ---- K2: path_requires on the initial state -------------------------------------------------------------------

def _cycle(*transitions: tuple[str, str, str]) -> Workflow:
    """A workflow of the excursion pack over states A, B, C with these (action, source, target) transitions."""
    pack = default_pack()
    return Workflow(id=pack.id, initial_state="A", states=("A", "B", "C"),
                    transitions=tuple(transition(a, s, t, "Teacher", pack, transition_id=f"T{i}") for i, (a, s, t) in enumerate(transitions)))


LAW = PathRequires(id="back-via-b", code="BACK_VIA_B", kind="path_requires", state="A", via="B")


def test_k2_path_law_on_the_initial_state_holds_when_every_way_back_passes_the_waypoint():
    """A record starts in A without passing B, which `evaluate_run` (and the law proof) do not count as entering A.
    The table check did: it reported every model with such a law as broken, so the policy refused models no run breaks."""
    model = _cycle(("Submit", "A", "B"), ("Recommend", "B", "A"))
    assert evaluate_table([LAW], model) == []
    assert evaluate_run([LAW], "A", [Step("Submit", "Teacher", "A", "B"), Step("Recommend", "Teacher", "B", "A")], set()) == []


def test_k2_path_law_on_the_initial_state_still_catches_a_way_back_around_the_waypoint():
    model = _cycle(("Submit", "A", "B"), ("Recommend", "A", "C"), ("Approve", "C", "A"))
    assert [v.code for v in evaluate_table([LAW], model)] == ["BACK_VIA_B"]
    assert [v.code for v in evaluate_run([LAW], "A", [Step("Recommend", "Teacher", "A", "C"), Step("Approve", "Teacher", "C", "A")],
                                         set())] == ["BACK_VIA_B"]


def test_k2_path_law_on_another_state_is_unchanged():
    law = PathRequires(id="c-via-b", code="C_VIA_B", kind="path_requires", state="C", via="B")
    assert evaluate_table([law], _cycle(("Submit", "A", "B"), ("Recommend", "B", "C"))) == []
    assert [v.code for v in evaluate_table([law], _cycle(("Submit", "A", "B"), ("Recommend", "A", "C")))] == ["C_VIA_B"]


# ---- K3 and K4: value guards over a value that is not a date, or not a scalar --------------------------------

DUE = ValueGuard(attribute="due", op="lt", value="2026-12-01")


@pytest.mark.parametrize("value", ["1999", "", "2026-1-5", "soon", "2026-02-30"])
def test_k3_a_date_guard_is_not_met_by_text_that_is_not_a_date(value):
    """`[due < 2026-12-01]` compared any text with the date as strings, so "1999" and "" were before it."""
    assert not DUE.holds({"due": value})


def test_k3_a_date_guard_still_orders_real_dates():
    assert DUE.holds({"due": "2026-11-30"}) and not DUE.holds({"due": "2026-12-01"})
    assert ValueGuard(attribute="due", op="ge", value="2026-12-01").holds({"due": "2027-01-01"})


@pytest.mark.parametrize("value", [["2026-01-01"], {"y": 2026}, ("a",), b"2026-01-01"])
@pytest.mark.parametrize("guard", [DUE, ValueGuard(attribute="due", op="eq", value="x"), ValueGuard(attribute="due", op="ne", value="x")])
def test_k4_a_guard_fails_closed_on_a_value_that_is_no_kind_it_compares(guard, value):
    """A list or object was classed as text, so an ordering guard raised TypeError out of the kernel."""
    assert guard.holds({"due": value}) is False


def _guarded_loan() -> Workflow:
    data = LOAN.model.model_dump(mode="json")
    cancel = next(t for t in data["transitions"] if t["action"] == "Cancel")
    cancel["conditions"] = [DUE.model_dump(mode="json")]
    return Workflow.model_validate(data)


def test_k4_execute_refuses_a_non_scalar_value_with_the_guard_code_instead_of_crashing():
    model = _guarded_loan()
    session = MemorySession(LOAN)
    item = initialise(session, "case", model, pack=LOAN)
    session.record_values[item["id"]] = {"due": ["2026-01-01"]}
    actor = next(a for a in LOAN.fixtures.actors if a.role == model.transition_for("Cancel").role and a.active)
    command = ExecuteCommand(operation_id="op-1", actor_id=actor.id, instance_id=item["id"], action="Cancel", expected_version=0)
    with pytest.raises(DomainError) as refused:
        execute(session, "case", model, command, pack=LOAN)
    assert refused.value.code == "VALUE_GUARD_DENIED"


# ---- K5: adding a source to an action that has a time event, a value guard or a linked step ------------------

@pytest.mark.parametrize("pack,action", [(DESK, "EscalateStale"), (OPS, "OpenWindow")])
def test_k5_add_transition_gives_a_new_source_what_the_action_shares(pack, action):
    """ADR-0232: one action may leave several states while its transitions are alike apart from id and source. The
    added transition got only the pack's declared guards and effects, so an action with `after(...)` or `target.lock`
    could never gain a source: the edit was refused as incoherent."""
    existing = pack.model.transition_for(action)
    source = next(s for s in pack.model.states if s not in pack.model.sources(action) and s != existing.to_state)
    model = edit(pack, {"kind": "add_transition", "id": "TR-NEW", "action": action, "from_state": source,
                        "to_state": existing.to_state, "role": existing.role})
    added = model.transition_for(action, source)
    assert added.id == "TR-NEW"
    assert (added.after, added.then, added.conditions) == (existing.after, existing.then, existing.conditions)


def test_k5_a_value_guarded_action_can_gain_a_source():
    model = _guarded_loan()
    cancel = model.transition_for("Cancel")
    source = next(s for s in model.states if s not in model.sources("Cancel") and s != cancel.to_state)
    tx = parse_transaction({"kind": "add_transition", "id": "TR-CANCEL-2", "action": "Cancel", "from_state": source,
                            "to_state": cancel.to_state, "role": cancel.role})
    added = apply_structural_all(model, [tx], LOAN).transition_for("Cancel", source)
    assert added.conditions == (DUE,)


# ---- K6: true and 1 are one point ------------------------------------------------------------------------------

def test_k6_points_keep_a_number_equal_to_a_truth_value():
    """`dict.fromkeys` merged True with 1 and False with 0, so the law proof and Simulate never tried the numbers."""
    tried = points([ValueGuard(attribute="x", op="eq", value=True), ValueGuard(attribute="x", op="eq", value=1),
                    ValueGuard(attribute="x", op="eq", value=0)])
    assert [p for p in tried if p is True] == [True] and [p for p in tried if p is False] == [False]
    assert any(p == 1 and not isinstance(p, bool) for p in tried) and any(p == 0 and not isinstance(p, bool) for p in tried)


def test_k6_the_law_proof_tries_the_number_a_truth_value_hid():
    """A law the record can break only when `x = 1` was reported as holding."""
    data = LOAN.model.model_dump(mode="json")
    for t in data["transitions"]:
        if t["action"] == "Cancel":
            t["conditions"] = [{"attribute": "x", "op": "eq", "value": 1}]
        elif t["from_state"] == LOAN.model.initial_state:
            t["conditions"] = [{"attribute": "x", "op": "eq", "value": True}]
    model = Workflow.model_validate(data)
    cancelled = {t.to_state for t in model.transitions if t.action == "Cancel"}
    report = prove_laws(LOAN, model)
    assert set(report["search"]["reached"]) >= cancelled


# ---- K7: a change outside the transitions has an impact ------------------------------------------------------

def test_k7_who_may_start_a_record_is_an_impact():
    after = Workflow.model_validate(LOAN.model.model_dump(mode="json") | {"initiators": ["Librarian"]})
    report = model_impact(LOAN.model, after)
    assert report["model_changes"] == ["initiators"]
    assert "review-packet" in report["affected"]


def test_k7_a_new_initial_state_is_an_impact():
    other = next(s for s in LOAN.model.states if s != LOAN.model.initial_state)
    report = model_impact(LOAN.model, edit(LOAN, {"kind": "set_initial", "state": other}))
    assert report["model_changes"] == ["initial_state"] and "review-packet" in report["affected"]


def test_k7_a_linked_lifecycle_change_marks_the_actions_that_move_it():
    data = OPS.model.model_dump(mode="json")
    obj = data["objects"][0]
    obj["states"].append("Retired")
    obj["moves"].append({"event": "lock", "from_state": "Retired", "to_state": obj["moves"][0]["to_state"]})
    after = Workflow.model_validate(data)
    movers = sorted({t.action for t in OPS.model.transitions if any(s.link == obj["link"] for s in t.then)})
    report = model_impact(OPS.model, after)
    assert report["model_changes"] == ["objects"] and report["changed_actions"] == movers


def test_k7_an_unchanged_model_has_no_impact_and_keeps_its_report_shape():
    report = model_impact(LOAN.model, LOAN.model)
    assert report["changed_actions"] == [] and report["affected"] == [] and "model_changes" not in report


# ---- K8: names a model holds outside its transitions are bounded ---------------------------------------------

@pytest.mark.parametrize("name", ["", "x" * 61])
def test_k8_an_initiator_role_name_is_bounded_like_a_transition_role(name):
    with pytest.raises(ValidationError):
        Workflow.model_validate(LOAN.model.model_dump(mode="json") | {"initiators": [name]})


@pytest.mark.parametrize("name", ["", "x" * 61])
def test_k8_a_linked_object_state_name_is_bounded_like_a_workflow_state(name):
    data = OPS.model.model_dump(mode="json")
    data["objects"][0]["states"].append(name)
    with pytest.raises(ValidationError):
        Workflow.model_validate(data)


def test_packs_are_unaffected():
    for directory in sorted(Path(PACKS_ROOT).iterdir()):
        if (directory / "pack.json").is_file():
            pack = load_pack(directory)
            assert check_policy(pack.model, pack) == [], directory.name
