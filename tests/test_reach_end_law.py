"""The law that every record can still reach an end (ADR-0221, issue #151).

A record that can get somewhere it can never be finished from (a dead end, or a loop with no way out) is a stuck
case: a permit application nobody can decide, a refund nobody can close. The law names the ends; the policy refuses
a change that strands a reachable state, and the law proof judges it on the steps the kernel actually commits.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.application import runtime
from eija_studio.application.law_proof import prove_laws
from eija_studio.domain.laws import CanReachEnd, evaluate_run, evaluate_table, Step
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PackError, load_pack, parse_pack
from eija_studio.domain.policy import apply_structural_all, apply_transactions
from eija_studio.domain.transactions import RemoveTransition

ROOT = Path(__file__).resolve().parents[1]
PERMIT = load_pack(ROOT / "packs" / "building-permit")
LAW = "no-application-stuck"


def test_the_permit_pack_can_always_be_finished():
    report = prove_laws(PERMIT)
    law = next(v for v in report["laws"] if v["id"] == LAW)
    assert law["status"] == "HOLDS" and law["method"] == "reach" and law["kind"] == "can_reach_end"


def test_a_change_that_parks_an_application_with_no_way_out_is_refused_and_names_the_state():
    with pytest.raises(DomainError) as refused:
        apply_transactions(PERMIT.model, PERMIT.meaning("hold_application").transactions, PERMIT)
    assert refused.value.code == "POLICY_BLOCKED"
    assert {"law:" + LAW, "state:OnHold"} <= set(refused.value.details["refs"])
    assert "APPLICATION_STUCK" in refused.value.details["codes"]


def test_a_new_end_named_by_the_law_is_allowed():
    """Lapsing adds a state with no way out, but the law names it as an end, so the change is allowed."""
    model = apply_transactions(PERMIT.model, PERMIT.meaning("permit_lapse").transactions, PERMIT)
    assert "Lapsed" in model.states and not [v for v in evaluate_table(PERMIT.laws, model) if v.law == LAW]


def test_a_loop_with_no_exit_strands_every_state_in_it():
    """Remove both decisions: review and requests for information go round for ever, and so does the step before."""
    model = apply_structural_all(PERMIT.model, [RemoveTransition(kind="remove_transition", transition="TR-APPROVE"),
                                                RemoveTransition(kind="remove_transition", transition="TR-REFUSE")], PERMIT)
    found = [v for v in evaluate_table(PERMIT.laws, model) if v.law == LAW]
    assert len(found) == 1
    assert found[0].refs == ("law:" + LAW, "state:InReview", "state:InfoRequested", "state:Registered")


def test_an_unreachable_dead_end_does_not_count():
    """A state no record can get to strands nobody, so drawing a new state before its steps is not refused."""
    model = apply_transactions(PERMIT.model, PERMIT.meaning("hold_application").transactions[:1], PERMIT)
    assert "OnHold" in model.states


def test_it_is_not_judged_on_a_single_run():
    law = CanReachEnd(id="ends", code="STUCK", kind="can_reach_end", states=("Done",))
    assert evaluate_run([law], "Start", [Step("Go", "R", "Start", "Nowhere")], {"Go"}) == []


def test_an_end_the_pack_does_not_declare_is_refused():
    document = PERMIT.model_dump(mode="json")
    law = next(x for x in document["laws"] if x["id"] == LAW)
    law["states"] = [*law["states"], "Archived"]
    with pytest.raises(PackError) as refused:
        parse_pack(document)
    assert any("'Archived' is not declared" in d for d in refused.value.diagnostics)


def test_negative_control_a_kernel_that_never_lets_the_manager_act_strands_the_review(monkeypatch):
    """The table is fine; the kernel is not. The proof judges what the kernel commits, so it finds the stuck run."""
    check = runtime.check_actor

    def no_manager(actor, transition, command):
        if transition.role == "PermitManager":
            raise DomainError("ROLE_DENIED", "negative control")
        return check(actor, transition, command)

    monkeypatch.setattr(runtime, "check_actor", no_manager)
    law = next(v for v in prove_laws(PERMIT)["laws"] if v["id"] == LAW)
    assert law["status"] == "BROKEN" and law["stuck"] == ["InReview", "InfoRequested", "Registered"]
    assert [s["action"] for s in law["counterexample"]] == ["AcceptLodgement", "StartReview"]
