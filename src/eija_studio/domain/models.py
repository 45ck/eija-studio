from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from hashlib import sha256
import json
from threading import Lock
from typing import Any, Literal, TypeVar
from pydantic import BaseModel, ConfigDict, Field, model_validator


class DomainError(ValueError):
    """Stable error code: never expose provider secrets or arbitrary exception text."""
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        # ``details`` is structured and safe to show: {"codes": [...], "refs": ["law:<id>", "transition:<id>", ...]}.
        self.code, self.message, self.details = code, message, details
        super().__init__(message)


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def canonical(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def fingerprint(value: Any) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


_T = TypeVar("_T")


class IdentityMemo:
    """A small, bounded memo for pure functions of frozen contracts, keyed by the identity of the arguments (ADR-0191).

    The kernel asks the same question of one unchanged model thousands of times (every oracle case and every explored
    step checks the policy and hashes the model). A frozen contract never changes after validation, so its answer
    can be kept while that very object is alive; the memo holds the objects themselves, so an id is never reused
    for a different object while its entry exists. A copy or an edit is a new object and is computed afresh."""

    def __init__(self, size: int = 128):
        self._size, self._lock = size, Lock()
        self._entries: OrderedDict[tuple[int, ...], tuple[tuple[Any, ...], Any]] = OrderedDict()

    def get(self, args: tuple[Any, ...], compute: Callable[[], _T]) -> _T:
        key = tuple(map(id, args))
        with self._lock:
            hit = self._entries.get(key)
            if hit is not None and all(a is b for a, b in zip(hit[0], args, strict=True)):
                self._entries.move_to_end(key)
                return hit[1]
        value = compute()
        with self._lock:
            self._entries[key] = (args, value)
            self._entries.move_to_end(key)
            while len(self._entries) > self._size:
                self._entries.popitem(last=False)
        return value


_HASHES = IdentityMemo()


Guard = Literal["actor_active", "role_current", "actor_assigned", "state_equals", "expected_version", "operation_binding"]
BASE_GUARDS: tuple[Guard, ...] = ("actor_active", "role_current", "state_equals", "expected_version", "operation_binding")


class Transition(Contract):
    id: str = Field(pattern=r"^[A-Z][A-Z0-9_-]{0,63}$")
    action: str = Field(min_length=1, max_length=60)
    from_state: str = Field(min_length=1, max_length=60)
    to_state: str = Field(min_length=1, max_length=60)
    role: str = Field(min_length=1, max_length=60)
    guards: tuple[Guard, ...]
    required_effects: tuple[str, ...]
    forbidden_effects: tuple[str, ...]

    @model_validator(mode="after")
    def guarded(self) -> Transition:
        if not set(BASE_GUARDS).issubset(self.guards):
            raise ValueError("Mandatory guards cannot be removed")
        if len(set(self.guards)) != len(self.guards):
            raise ValueError("Duplicate guards")
        if len(set(self.required_effects)) != len(self.required_effects):
            raise ValueError("Duplicate required effects")
        if set(self.required_effects) & set(self.forbidden_effects):
            raise ValueError("Required/forbidden effect conflict")
        return self


class Workflow(Contract):
    schema_version: Literal["eija.workflow.v1"] = "eija.workflow.v1"
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")  # the id of the domain pack the workflow belongs to
    initial_state: str
    states: tuple[str, ...] = Field(min_length=1, max_length=32)
    transitions: tuple[Transition, ...] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def coherent(self) -> Workflow:
        if len(set(self.states)) != len(self.states) or self.initial_state not in self.states:
            raise ValueError("Duplicate states or missing initial state")
        ids, keys, actions = set(), set(), set()
        for t in self.transitions:
            if t.from_state not in self.states or t.to_state not in self.states:
                raise ValueError("Dangling transition state")
            if t.id in ids or (t.from_state, t.action, t.role) in keys or t.action in actions:
                raise ValueError("Duplicate or ambiguous transition/action")
            ids.add(t.id); keys.add((t.from_state, t.action, t.role)); actions.add(t.action)
        return self

    @property
    def semantic_hash(self) -> str:
        return _HASHES.get((self,), self._semantic_hash)

    def _semantic_hash(self) -> str:
        # Order of definitions is non-semantic, but state/action identities are not.
        data = self.model_dump(mode="json")
        data["states"] = sorted(data["states"])
        data["transitions"] = sorted(data["transitions"], key=lambda x: x["id"])
        for t in data["transitions"]:
            for key in ("guards", "required_effects", "forbidden_effects"):
                t[key] = sorted(t[key])
        return fingerprint(data)


MEANING_ID = r"^[a-z][a-z0-9_]{0,39}$"


class Alternative(Contract):
    interpretation: str = Field(pattern=MEANING_ID)  # a meaning id of the active pack; the service checks it exists
    explanation: str = Field(min_length=1, max_length=1600)


class Proposal(Contract):
    summary: str = Field(min_length=1, max_length=1600)
    alternatives: tuple[Alternative, ...] = Field(min_length=1, max_length=4)
    unknowns: tuple[str, ...] = Field(max_length=10)

    @model_validator(mode="after")
    def unique(self) -> Proposal:
        ids = [a.interpretation for a in self.alternatives]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate interpretation")
        if any(len(x) > 1600 for x in self.unknowns):
            raise ValueError("Unknown description too long")
        return self


class SemanticTransaction(Contract):
    """DEPRECATED closed vocabulary, superseded by the open one in ``domain.transactions`` (WBS 1.3).

    Kept for one caller only: verification/bend/bend_generate.py, whose bytes the committed Bend proof binds
    (changing them turns that evidence non-PASS until Docker regenerates it, WBS 1.4). ``policy.apply_transaction``
    reads it as "apply the pack's first supported meaning". The service, HTTP, pack meanings and stored cases never
    accept it: a stored case holding one is refused with ``CASE_SCHEMA_OLD``."""
    kind: Literal["enable_recommendation"]


class LayoutChange(Contract):
    node: str = Field(min_length=1, max_length=60)
    x: int = Field(ge=0, le=2000)
    y: int = Field(ge=0, le=2000)


class ExecuteCommand(Contract):
    operation_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,100}$")
    actor_id: str = Field(min_length=1, max_length=80)
    instance_id: str = Field(min_length=1, max_length=80)
    action: str = Field(min_length=1, max_length=60)
    expected_version: int = Field(ge=0, strict=True)


class Principal(Contract):
    id: str
    capabilities: frozenset[str]

    def require(self, capability: str) -> None:
        if capability not in self.capabilities:
            raise DomainError("AUTHORITY_REQUIRED", f"Capability required: {capability}")


OWNER = Principal(id="local-owner", capabilities=frozenset({"select", "edit", "approve", "apply"}))
AGENT = Principal(id="agent", capabilities=frozenset())
