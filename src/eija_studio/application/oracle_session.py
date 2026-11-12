"""The in-memory session the app oracle asks the kernel through (ADR-0150): one record, nothing persists."""
from __future__ import annotations

from itertools import count
from typing import Any

from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import Pack
from .memo import model_hash
from .runtime import execute

UNKNOWN_ACTOR = "unknown-actor"


class OracleSession:
    """In-memory answers to exactly the port calls `execute` makes for one instance. Nothing persists."""

    def __init__(self, pack: Pack, model: Workflow, state: str, values: dict[str, Any] | None = None,
                 waited: float | None = None):
        self.record_values = dict(values or {})
        # How long the record has been in its state: the model's longest time event unless a case says otherwise, so
        # every time event is due in the ordinary cases (ADR-0237). A committed step enters a state afresh.
        self.since = float(model.longest_wait if waited is None else waited)
        self.actors = {a.id: a.model_dump() for a in pack.fixtures.actors}
        self.item: dict[str, Any] = {"id": "r1", "case_id": "app", "model_hash": model_hash(model), "state": state, "version": 0}
        self.operations: dict[str, dict[str, Any]] = {}
        self.acted: list[tuple[str, str]] = []
        self.audited: list[str] = []  # the audit entries and outbox rows the kernel writes, in order
        self.queued: list[list[str]] = []

    def create_instance(self, item: dict[str, Any]) -> None:
        self.item = dict(item)

    def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None:
        return self.item if instance_id == self.item["id"] else None

    def acts(self, instance_id: str) -> list[tuple[str, str]]:
        return list(self.acted)

    def record_act(self, instance_id: str, action: str, actor_id: str) -> None:
        self.acted.append((action, actor_id))

    def values(self, instance_id: str) -> dict[str, Any]:
        return dict(self.record_values)

    def elapsed(self, instance_id: str) -> float | None:
        return self.since

    def actor(self, actor_id: str) -> dict[str, Any]:
        if actor_id not in self.actors:
            raise DomainError("UNKNOWN_ACTOR", "Actor is not in the trusted fixture directory")
        return self.actors[actor_id]

    def find_operation(self, operation_id: str) -> dict[str, Any] | None:
        return self.operations.get(operation_id)

    def update_instance(self, item: dict[str, Any], expected: int) -> None:
        self.item = dict(item)
        self.since = 0.0

    def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None:
        self.operations[operation_id] = {"binding": binding, "result": result}

    def event(self, kind: str, body: dict[str, Any]) -> None:
        self.audited.append(kind)

    def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None:
        self.queued.append([effect, recipient])


def kernel_answer(pack: Pack, model: Workflow, session: OracleSession, actor: str, action: str, version: int,
            operation: str = "op-1") -> dict[str, Any]:
    command = ExecuteCommand(operation_id=operation, actor_id=actor, instance_id="r1", action=action, expected_version=version)
    try:
        result = execute(session, "app", model, command, pack=pack)  # type: ignore[arg-type]  # duck-typed session
    except DomainError as refused:
        return {"outcome": "REFUSED", "code": refused.code}
    if result["duplicate"]:
        return {"outcome": "DUPLICATE", "state": result["instance"]["state"]}
    return {"outcome": "COMMITTED", "state": result["instance"]["state"], "effects": result["effects"]}


def absent(base: str, taken: set[str]) -> str:
    """A name guaranteed not to be in `taken`, so a negative case can never collide with a declared one."""
    return next(name for name in (base if n == 0 else f"{base}{n}" for n in count()) if name not in taken)
