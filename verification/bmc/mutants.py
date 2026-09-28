"""Seeded faults ("mutants") of the runtime, used to show the checker can find real bugs.

Each mutant replaces `application.runtime.execute` (or one of its helpers) with a deliberately broken
variant and names the invariant that the search must then violate. A checker that passes the real
runtime AND fails every mutant has demonstrated fault-detection power for these classes of fault.
It has not demonstrated it for faults outside them.
"""
from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from unittest import mock

from eija_studio.application import runtime
from eija_studio.domain.models import DomainError

ExecuteFn = Callable[..., dict]


@dataclass(frozen=True)
class Mutant:
    name: str
    description: str
    expected_invariants: frozenset[str]
    activate: Callable[[], AbstractContextManager[ExecuteFn]]


def _replay_first(real: ExecuteFn) -> ExecuteFn:
    """Serve a cached success BEFORE checking current authority (the flaw the kernel review names)."""
    def execute(session, case_id, model, command, **kw):
        prior = session.find_operation(command.operation_id)
        if prior is not None:
            row = session.find_instance(command.instance_id, case_id)
            return {"duplicate": True, "committed": False, "instance": dict(row),
                    "original_result": prior["result"], "effects": []}
        return real(session, case_id, model, command, **kw)
    return execute


def _stale_accepted(real: ExecuteFn) -> ExecuteFn:
    """Ignore the caller's expected_version (last writer wins)."""
    def execute(session, case_id, model, command, **kw):
        row = session.find_instance(command.instance_id, case_id)
        if row is not None:
            command = command.model_copy(update={"expected_version": row["version"]})
        return real(session, case_id, model, command, **kw)
    return execute


def _replay_reapplies(real: ExecuteFn) -> ExecuteFn:
    """A replay writes a second audit event."""
    def execute(session, case_id, model, command, **kw):
        result = real(session, case_id, model, command, **kw)
        if result["duplicate"]:
            session.event("Audit:ExcursionSubmitted", {"case_id": case_id, "operation_id": command.operation_id,
                                                         "actor_id": command.actor_id})
        return result
    return execute


def _lenient_check(skip_active: bool = False, skip_role: bool = False, skip_assigned: bool = False):
    def check(actor, transition, command):
        if not actor["active"] and not skip_active:
            raise DomainError("ACTOR_REVOKED", "Actor is not active at commit time")
        if actor["role"] != transition.role and not skip_role:
            raise DomainError("ROLE_DENIED", "Actor does not hold the current required role")
        if "actor_assigned" in transition.guards and not actor["assigned"] and not skip_assigned:
            raise DomainError("ASSIGNMENT_DENIED", "Actor is not assigned in the trusted fixture directory")
    return check


@contextmanager
def _wrapped(factory: Callable[[ExecuteFn], ExecuteFn]) -> Iterator[ExecuteFn]:
    yield factory(runtime.execute)


@contextmanager
def _patched_check(**skips: bool) -> Iterator[ExecuteFn]:
    with mock.patch.object(runtime, "check_actor", _lenient_check(**skips)):
        yield runtime.execute


MUTANTS: tuple[Mutant, ...] = (
    Mutant("revocation_ignored", "check_actor no longer rejects an inactive actor",
           frozenset({"AUTHORITY-ON-COMMIT"}), lambda: _patched_check(skip_active=True)),
    Mutant("assignment_ignored", "Recommend no longer requires the actor to be assigned",
           frozenset({"AUTHORITY-ON-COMMIT"}), lambda: _patched_check(skip_assigned=True)),
    Mutant("role_ignored", "check_actor no longer compares the actor's role with the transition's",
           frozenset({"AUTHORITY-ON-COMMIT"}), lambda: _patched_check(skip_role=True)),
    Mutant("replay_before_authority", "a recorded operation is replayed before the actor is re-authorised",
           frozenset({"AUTHORITY-BEFORE-REPLAY"}), lambda: _wrapped(_replay_first)),
    Mutant("stale_version_accepted", "expected_version is overwritten with the current version",
           frozenset({"CAS-ON-COMMIT"}), lambda: _wrapped(_stale_accepted)),
    Mutant("replay_reapplies_effects", "a replay appends a second audit event",
           frozenset({"REPLAY-HAS-NO-EFFECT"}), lambda: _wrapped(_replay_reapplies)),
)
