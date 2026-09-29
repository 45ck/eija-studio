"""Negative controls: the differential harness must FAIL when the kernel is deliberately broken.

A passing property suite is only evidence if the same suite fails against a wrong implementation. Each
mutant below breaks one rule the specification states (ARCHITECTURE.md, "Runtime commit sequence") by
monkeypatching the running kernel, then requires the stateful machine to falsify it with an
``AssertionError`` (never some other exception, which would mean the harness itself is broken).

The mutants live in tests only; nothing here changes the shipped kernel.
"""
from __future__ import annotations

import pytest
from hypothesis import HealthCheck, Phase, settings
from hypothesis.stateful import run_state_machine_as_test

from eija_studio.application import runtime, service
from eija_studio.domain.models import fingerprint
from .property_support import examples
from .test_runtime_differential import PreviewRuntimeMachine

REAL_EXECUTE = runtime.execute
REAL_CHECK_ACTOR = runtime.check_actor


def binding_of(case_id, model, command) -> str:
    return fingerprint({"case": case_id, "subject": model.semantic_hash, "command": command.model_dump(mode="json")})


def duplicate_result(session, case_id, command, prior) -> dict:
    return {"duplicate": True, "committed": False, "instance": dict(session.find_instance(command.instance_id, case_id)),
            "original_result": prior["result"], "effects": []}


def replay_before_authority(session, case_id, model, command, *, fault=None, pack=None):
    """Mutant: a cached success is returned without re-checking the actor (violates ADR-007)."""
    prior = session.find_operation(command.operation_id)
    if prior is not None and prior["binding"] == binding_of(case_id, model, command):
        return duplicate_result(session, case_id, command, prior)
    return REAL_EXECUTE(session, case_id, model, command, fault=fault, pack=pack)


def conflict_treated_as_replay(session, case_id, model, command, *, fault=None, pack=None):
    """Mutant: an operation id already used for a different request is answered as a replay."""
    prior = session.find_operation(command.operation_id)
    if prior is not None and session.find_instance(command.instance_id, case_id) is not None:
        transition = next((t for t in model.transitions if t.action == command.action), None)
        if transition is not None:
            REAL_CHECK_ACTOR(session.actor(command.actor_id), transition, command)
            return duplicate_result(session, case_id, command, prior)
    return REAL_EXECUTE(session, case_id, model, command, fault=fault, pack=pack)


def stale_version_ignored(session, case_id, model, command, *, fault=None, pack=None):
    """Mutant: the optimistic-concurrency check is skipped by rewriting the caller's expected version."""
    row = session.find_instance(command.instance_id, case_id)
    if row is not None and row["version"] != command.expected_version:
        command = command.model_copy(update={"expected_version": row["version"]})
    return REAL_EXECUTE(session, case_id, model, command, fault=fault, pack=pack)


def assignment_not_required(actor, transition, command):
    """Mutant: an unassigned teacher may recommend."""
    REAL_CHECK_ACTOR({**actor, "assigned": 1}, transition, command)


def revocation_not_checked(actor, transition, command):
    """Mutant: a revoked actor keeps acting."""
    REAL_CHECK_ACTOR({**actor, "active": 1}, transition, command)


MUTANTS = {
    "replay_before_authority": (service, "execute", replay_before_authority),
    "conflict_treated_as_replay": (service, "execute", conflict_treated_as_replay),
    "stale_version_ignored": (service, "execute", stale_version_ignored),
    "assignment_not_required": (runtime, "check_actor", assignment_not_required),
    "revocation_not_checked": (runtime, "check_actor", revocation_not_checked),
}


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_reference_detects_mutant(name, monkeypatch):
    module, attribute, mutant = MUTANTS[name]
    monkeypatch.setattr(module, attribute, mutant)
    with pytest.raises(AssertionError):
        run_state_machine_as_test(PreviewRuntimeMachine, settings=settings(
            max_examples=examples(150), stateful_step_count=30, database=None, derandomize=True,
            phases=[Phase.generate], report_multiple_bugs=False, suppress_health_check=list(HealthCheck)))


def test_mutation_harness_is_not_vacuous(monkeypatch):
    """Guard against the mutants silently failing to install: the unmutated kernel passes the same run."""
    assert service.execute is REAL_EXECUTE and runtime.check_actor is REAL_CHECK_ACTOR
    run_state_machine_as_test(PreviewRuntimeMachine, settings=settings(
        max_examples=examples(20), stateful_step_count=20, database=None, derandomize=True,
        suppress_health_check=list(HealthCheck)))
