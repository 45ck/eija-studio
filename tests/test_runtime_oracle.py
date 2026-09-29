"""Exact-oracle tests of the generic runtime (`application/runtime.py`), added by the mutation lane (ADR-0033).

They drive `initialise` and `execute` directly against the ephemeral SQLite unit of work, so each test
runs in milliseconds and can pin the *result shape*, the *stable error code* of every refusal, the audit
and outbox payloads, and the ordering guarantees (authority before replay). The pre-existing runtime
tests go through the whole Studio and mostly assert only that something was refused.
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from eija_studio.adapters.sqlite_store import SQLiteStore
from eija_studio.application import runtime
from eija_studio.domain.models import DomainError, ExecuteCommand, SemanticTransaction, Workflow
from eija_studio.domain.policy import apply_transaction, baseline

CASE = "case-1"


@pytest.fixture
def store(tmp_path):
    return SQLiteStore(tmp_path / "ws", durability="ephemeral")


def candidate() -> Workflow:
    return apply_transaction(baseline(), SemanticTransaction(kind="enable_recommendation"))


def start(store, model=None, state="Submitted", case=CASE) -> dict:
    with store.transaction() as u:
        return runtime.initialise(u, case, model or candidate(), state=state)


def command(item, actor="teacher-assigned", action="Recommend", version=0, op=None) -> ExecuteCommand:
    return ExecuteCommand(operation_id=op or uuid4().hex, actor_id=actor, instance_id=item["id"], action=action, expected_version=version)


def run(store, cmd, model=None, case=CASE):
    with store.transaction() as u:
        return runtime.execute(u, case, model or candidate(), cmd)


def refused(store, cmd, code, model=None, case=CASE):
    with pytest.raises(DomainError) as info:
        run(store, cmd, model, case)
    assert info.value.code == code
    return info.value


def snapshot(store, item):
    with store.transaction() as u:
        return u.find_instance(item["id"], CASE), u.effect_counts()


# ---- initialise -----------------------------------------------------------------------------------

def test_initialise_creates_a_version_zero_instance_bound_to_the_model():
    model = candidate()

    class Recorder:
        created = None
        def create_instance(self, item): self.created = item

    session = Recorder()
    item = runtime.initialise(session, CASE, model)
    assert set(item) == {"id", "case_id", "model_hash", "state", "version"}
    assert (item["case_id"], item["model_hash"], item["state"], item["version"]) == (CASE, model.semantic_hash, "Draft", 0)
    assert len(item["id"]) == 32 and item["id"] != runtime.initialise(session, CASE, model)["id"]
    assert session.created is not None and session.created["state"] == "Draft"


def test_initialise_honours_an_explicit_state_and_rejects_states_outside_the_model(store):
    assert start(store, state="Recommended")["state"] == "Recommended"
    with pytest.raises(DomainError) as info:
        start(store, baseline(), state="Recommended")  # the baseline has no Recommended state
    assert info.value.code == "INVALID_STATE"


def test_initialise_refuses_a_model_that_violates_protected_policy():
    data = baseline().model_dump(mode="json")
    next(t for t in data["transitions"] if t["action"] == "Approve")["role"] = "Teacher"
    with pytest.raises(DomainError) as info:
        runtime.initialise(object(), CASE, Workflow.model_validate(data))
    assert info.value.code == "POLICY_BLOCKED"


# ---- execute: the success path ---------------------------------------------------------------------

def test_successful_execution_reports_exactly_what_was_committed(store):
    item = start(store)
    cmd = command(item)
    result = run(store, cmd)
    assert set(result) == {"duplicate", "committed", "instance", "effects"}
    assert result["duplicate"] is False and result["committed"] is True
    assert result["effects"] == ["Audit:ExcursionRecommended", "Notification:RegistrarQueued"]
    assert (result["instance"]["state"], result["instance"]["version"]) == ("Recommended", 1)
    row, counts = snapshot(store, item)
    assert (row["state"], row["version"]) == ("Recommended", 1) and counts == {"audit": 1, "outbox": 1, "operations": 1}


def test_audit_and_outbox_payloads_are_complete_and_bound_to_the_operation(store):
    item = start(store)
    cmd = command(item)
    result = run(store, cmd)
    with store.transaction() as u:
        seen = u.observations(CASE)
    (event,) = seen["events"]
    assert event["kind"] == "Audit:ExcursionRecommended"
    assert event["body"] == {"case_id": CASE, "operation_id": cmd.operation_id, "actor_id": "teacher-assigned",
                             "instance_id": item["id"], "result": result}
    (message,) = seen["outbox"]
    assert message["id"] == f"{cmd.operation_id}:Notification:RegistrarQueued"
    assert (message["case_id"], message["operation_id"], message["kind"]) == (CASE, cmd.operation_id, "Notification:RegistrarQueued")


def test_each_action_produces_exactly_its_own_effects(store):
    for action, actor, state, effects in [
        ("Submit", "teacher-assigned", "Draft", ["Audit:ExcursionSubmitted"]),
        ("Approve", "registrar", "Recommended", ["Audit:ExcursionApproved"]),
        ("Reject", "registrar", "Recommended", ["Audit:ExcursionRejected"]),
        ("Revise", "teacher-assigned", "Rejected", ["Audit:ExcursionReopened"]),
    ]:
        item = start(store, state=state)
        assert run(store, command(item, actor, action))["effects"] == effects, action


def test_the_transition_target_becomes_the_new_state(store):
    item = start(store, state="Recommended")
    assert run(store, command(item, "registrar", "Approve"))["instance"]["state"] == "Approved"


# ---- execute: every refusal has a stable code and changes nothing ----------------------------------

@pytest.mark.parametrize("build,code", [
    (lambda item: command(item, actor="nobody"), "UNKNOWN_ACTOR"),
    (lambda item: command(item, actor="teacher-revoked"), "ACTOR_REVOKED"),
    (lambda item: command(item, actor="registrar"), "ROLE_DENIED"),
    (lambda item: command(item, actor="viewer"), "ROLE_DENIED"),
    (lambda item: command(item, actor="teacher-unassigned"), "ASSIGNMENT_DENIED"),
    (lambda item: command(item, action="Escalate"), "ACTION_DENIED"),
    (lambda item: command(item, action="Approve", actor="registrar"), "STATE_DENIED"),
    (lambda item: command(item, version=3), "STALE_VERSION"),
])
def test_refusals_carry_a_stable_code_and_leave_state_and_effects_untouched(store, build, code):
    item = start(store)
    before = snapshot(store, item)
    refused(store, build(item), code)
    assert snapshot(store, item) == before


def test_unknown_instance_and_instance_of_another_case_are_not_found(store):
    item = start(store)
    refused(store, command({"id": "f" * 32}), "NOT_FOUND")
    refused(store, command(item), "NOT_FOUND", case="another-case")


def test_an_instance_created_for_another_model_is_stale(store):
    item = start(store, baseline(), state="Draft")
    refused(store, command(item, action="Submit"), "STALE_INSTANCE")  # instance is bound to the baseline, executed against the candidate


def test_policy_is_enforced_before_anything_is_read_or_written(store):
    item = start(store)
    data = candidate().model_dump(mode="json")
    next(t for t in data["transitions"] if t["action"] == "Approve")["role"] = "Teacher"
    refused(store, command(item), "POLICY_BLOCKED", model=Workflow.model_validate(data))


def test_an_effect_without_an_adapter_is_refused_not_ignored(store, monkeypatch):
    """Defence in depth: policy forbids unknown effects, but `execute` must still refuse one it cannot perform."""
    data = candidate().model_dump(mode="json")
    next(t for t in data["transitions"] if t["action"] == "Recommend")["required_effects"] = ["Payment:Attempted"]
    monkeypatch.setattr(runtime, "ensure_policy", lambda model: None)
    model = Workflow.model_validate(data)
    item = start(store, model)
    before = snapshot(store, item)
    refused(store, command(item), "EFFECT_DENIED", model=model)
    assert snapshot(store, item) == before  # the state change made before the effect loop was rolled back too


# ---- replay and authority ordering ------------------------------------------------------------------

def test_replay_returns_the_original_result_without_repeating_effects(store):
    item = start(store)
    cmd = command(item)
    first = run(store, cmd)
    again = run(store, cmd)
    assert set(again) == {"duplicate", "committed", "instance", "original_result", "effects"}
    assert again["duplicate"] is True and again["committed"] is False and again["effects"] == []
    assert again["original_result"] == first
    assert again["instance"] == first["instance"]
    assert snapshot(store, item)[1] == {"audit": 1, "outbox": 1, "operations": 1}


def test_an_operation_id_is_bound_to_the_exact_request(store):
    item = start(store)
    cmd = command(item)
    run(store, cmd)
    for changed in (command(item, action="Submit", op=cmd.operation_id), command(item, version=1, op=cmd.operation_id)):
        refused(store, changed, "OPERATION_CONFLICT")


def test_replay_by_an_actor_who_lost_authority_is_refused_before_the_cache_is_consulted(store):
    item = start(store)
    cmd = command(item)
    run(store, cmd)
    with store.transaction() as u:
        u.db.execute("UPDATE actors SET active=0 WHERE id='teacher-assigned'")
    refused(store, cmd, "ACTOR_REVOKED")


def test_authority_is_checked_before_the_version_and_state_checks(store):
    item = start(store)
    refused(store, command(item, actor="registrar", version=9), "ROLE_DENIED")  # not STALE_VERSION
    refused(store, command(item, actor="teacher-revoked", action="Submit"), "ACTOR_REVOKED")  # not STATE_DENIED


def test_replay_precedes_the_version_check_so_a_retry_after_success_is_idempotent(store):
    item = start(store)
    cmd = command(item)
    run(store, cmd)
    assert run(store, cmd)["duplicate"] is True  # the instance is now at version 1, the command still says 0


def test_fault_hooks_fire_in_order_and_roll_back_everything(store):
    item = start(store)
    seen = []

    def fault(point):
        seen.append(point)
        if point == "after_operation":
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError), store.transaction() as u:
        runtime.execute(u, CASE, candidate(), command(item), fault=fault)
    assert seen == ["after_state", "after_effects", "after_operation"]
    row, counts = snapshot(store, item)
    assert (row["state"], row["version"]) == ("Submitted", 0) and counts == {"audit": 0, "outbox": 0, "operations": 0}
