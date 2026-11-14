"""Regression tests for the second, deeper inspection of the kernel, 14 November 2026 (ADR-0250).

The first inspection (ADR-0246) read each kernel function against its ADR. This one read how the features meet: who
starts a record against who acts on one, laws against the edits that rename or remove what they name, and every
executor of the kernel (Studio preview, Simulate, the app oracle, the law proof) against the others. Each test fails
on the code before the fix and names the defect it pins (D1, D2 in docs/quality/inspection-2026-11-14-kernel.md).
"""
from __future__ import annotations

import pytest

from eija_studio.application.app_runs import create_cases
from eija_studio.application.law_proof import prove_laws
from eija_studio.application.runtime import execute, initialise, receive
from eija_studio.application.simulation import MemorySession, run_log, simulate
from eija_studio.domain.laws import PROTECTING, StateFinal, evaluate_table, protects_absent
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.domain.policy import apply_structural_all, apply_transactions, check_policy
from eija_studio.domain.transactions import parse_transaction

PACKS = [load_pack(p) for p in sorted(PACKS_ROOT.iterdir()) if (p / "pack.json").is_file()]
LOAN = load_pack(PACKS_ROOT / "library-loan")


def edit(pack, *transactions: dict) -> Workflow:
    return apply_structural_all(pack.model, [parse_transaction(tx) for tx in transactions], pack)


# ---- D1: a revoked actor started records ----------------------------------------------------------------------

def test_d1_the_kernel_refuses_a_revoked_or_unknown_actor_starting_a_record():
    """The kernel refuses a revoked actor every action (ACTOR_REVOKED), and the built app refused one starting a record,
    but `initialise` knew only a role, so Simulate let revoked users start records in every shipped pack."""
    session = MemorySession(LOAN)
    with pytest.raises(DomainError) as revoked:
        initialise(session, "c", LOAN.model, pack=LOAN, actor_id="librarian-revoked")
    assert revoked.value.code == "ACTOR_REVOKED"
    with pytest.raises(DomainError) as unknown:
        initialise(session, "c", LOAN.model, pack=LOAN, actor_id="nobody")
    assert unknown.value.code == "UNKNOWN_ACTOR"
    assert initialise(session, "c", LOAN.model, pack=LOAN, actor_id="member-a")["state"] == LOAN.model.initial_state


def test_d1_an_actor_is_judged_by_their_role_when_the_model_names_its_initiators():
    model = Workflow.model_validate(LOAN.model.model_dump(mode="json") | {"initiators": ["Librarian"]})
    with pytest.raises(DomainError) as member:
        initialise(MemorySession(LOAN), "c", model, pack=LOAN, actor_id="member-a")
    assert member.value.code == "ROLE_CANNOT_START"
    assert initialise(MemorySession(LOAN), "c", model, pack=LOAN, actor_id="librarian-assigned")["version"] == 0


@pytest.mark.parametrize("pack", PACKS, ids=lambda p: p.id)
def test_d1_simulate_never_lets_a_revoked_user_start_a_record(pack):
    revoked = {a.id for a in pack.fixtures.actors if not a.active}
    log = run_log(pack, pack.model, seed=1, steps=300)
    assert not [e for e in log["trace"] if e["outcome"] == "CREATED" and e["actor"] in revoked]
    tried = [e for e in log["trace"] if e.get("start")]
    assert all(e["outcome"] == "REFUSED" and e["code"] == "ACTOR_REVOKED" and e["actor"] in revoked for e in tried)
    assert all(e["from"] == pack.model.initial_state and e["transition"] is None for e in tried)


def test_d1_a_refused_start_is_counted_and_stops_a_run_that_breaks_on_refusal():
    report = simulate(LOAN, LOAN.model, seed=1, steps=300)
    starts = [e for e in run_log(LOAN, LOAN.model, seed=1, steps=300)["trace"] if e.get("start")]
    assert starts and report["codes"]["ACTOR_REVOKED"] >= len(starts)
    stops = run_log(LOAN, LOAN.model, seed=1, steps=300, break_on_refusal=True)["stops"]
    first = next(s for s in stops if s["step"] == starts[0]["step"])
    assert first == {"step": starts[0]["step"], "reason": "exception", "elements": ["state:" + LOAN.model.initial_state],
                     "code": "ACTOR_REVOKED"}


@pytest.mark.parametrize("pack", PACKS, ids=lambda p: p.id)
def test_d1_the_app_oracle_asks_the_kernel_who_may_start_a_record(pack):
    """The oracle's expectations are the kernel's own answers now, and they did not change."""
    by_actor = {c["actor"]: c["expect"] for c in create_cases(pack, pack.model)}
    for actor in pack.fixtures.actors:
        if not actor.active:
            assert by_actor[actor.id] == {"outcome": "REFUSED", "code": "ACTOR_REVOKED"}
    assert [e for a, e in by_actor.items() if a not in {x.id for x in pack.fixtures.actors}] == [
        {"outcome": "REFUSED", "code": "UNKNOWN_ACTOR"}]


# ---- D2: renaming or removing a protected state switched its laws off -------------------------------------------

def test_d2_renaming_a_protected_state_breaks_the_laws_that_protect_it():
    """Laws name states. `rename_state` moved every transition to the new name, so a law about `Returned` judged a
    model with no `Returned`, held vacuously, and the policy passed it."""
    renamed = edit(LOAN, {"kind": "rename_state", "state": "Returned", "to": "Done"})
    assert check_policy(renamed, LOAN) == ["FINAL_STATE_LEFT:Returned", "LOAN_RETURN_WITHOUT_CHECKOUT", "PROTECTED_STATE:Returned"]
    refs = {r for v in evaluate_table(LOAN.laws, renamed) for r in v.refs}
    assert "state:Returned" in refs


def test_d2_a_rename_can_no_longer_launder_an_edit_the_laws_forbid():
    """Rename the protected end state, then let a Member's Cancel enter it: each edit alone is refused or harmless,
    and together they passed the policy before the fix."""
    direct = [{"kind": "retarget_transition", "transition": "TR-CANCEL", "end": "target", "state": "Returned"}]
    with pytest.raises(DomainError) as refused:
        apply_transactions(LOAN.model, [parse_transaction(tx) for tx in direct], LOAN)
    assert "PROTECTED_STATE:Returned" in refused.value.details["codes"]
    laundered = [{"kind": "rename_state", "state": "Returned", "to": "Done"},
                 {"kind": "retarget_transition", "transition": "TR-CANCEL", "end": "target", "state": "Done"}]
    with pytest.raises(DomainError) as still:
        apply_transactions(LOAN.model, [parse_transaction(tx) for tx in laundered], LOAN)
    assert still.value.code == "POLICY_BLOCKED" and "PROTECTED_STATE:Returned" in still.value.details["codes"]


@pytest.mark.parametrize("pack", PACKS, ids=lambda p: p.id)
def test_d2_every_shipped_model_and_meaning_keeps_the_states_its_laws_protect(pack):
    """No shipped model loses a protected state, so no shipped pack is refused by the rule."""
    assert check_policy(pack.model, pack) == []
    for meaning in (m for m in pack.meanings if m.supported):
        candidate = apply_structural_all(pack.model, meaning.transactions, pack)
        assert not [law.id for law in pack.laws if protects_absent(law, candidate)], meaning.id


def test_d2_only_laws_that_protect_a_state_are_judged_so():
    """A law that requires something of a state (an action's target, its sources, an end) is already stricter
    without it; only laws that guard a state (who enters it, by what route, that nothing leaves it) would go quiet."""
    assert {k.__name__ for k in PROTECTING} == {"StateFinal", "RoleNeverEnters", "StateOnlyVia", "OnlyKindEnters",
                                                 "PathRequires", "PathRequiresKind"}
    law = StateFinal(id="gone-final", code="GONE_FINAL", kind="state_final", state="Gone")
    assert [v.refs for v in evaluate_table([law], LOAN.model)] == [("law:gone-final", "state:Gone")]
    scoped = StateFinal(id="gone-final", code="GONE_FINAL", kind="state_final", state="Gone",
                        when={"action_present": "Renew"})
    assert evaluate_table([scoped], LOAN.model) == []  # a law that does not apply is not judged


def test_d2_the_law_proof_reports_the_refusal_not_a_vacuous_hold():
    renamed = edit(LOAN, {"kind": "rename_state", "state": "Returned", "to": "Done"})
    report = prove_laws(LOAN, renamed)
    assert report["status"] == "REFUSED"
    verdicts = {v["id"]: v["status"] for v in report["laws"]}
    assert verdicts["returned-final"] == verdicts["returned-only-via-return"] == "BROKEN"


# ---- D3: the runtime ran a model under another pack's catalog and laws -------------------------------------------

def test_d3_the_runtime_refuses_a_model_named_for_another_pack():
    """Every application entry point (Simulate, the law proof, the app generator, SCXML) refused a workflow of another
    pack, but the kernel's own `initialise`, `execute` and `receive` did not: the policy judged the model under the
    pack it was handed, so a model named for one pack could pass another's laws and run as its workflow."""
    foreign = Workflow.model_validate(LOAN.model.model_dump(mode="json") | {"id": "excursion"})
    assert check_policy(foreign, LOAN) == []  # the policy alone does not tell: the catalog fits
    session = MemorySession(LOAN)
    for call in (lambda: initialise(session, "c", foreign, pack=LOAN),
                 lambda: execute(session, "c", foreign, ExecuteCommand(operation_id="o", actor_id="member-a", instance_id="r",
                                                                        action="Cancel", expected_version=0), pack=LOAN),
                 lambda: receive(session, "c", foreign, "Signal:Any", "sender", "o", pack=LOAN)):
        with pytest.raises(DomainError) as refused:
            call()
        assert refused.value.code == "WORKFLOW_PACK_MISMATCH"
