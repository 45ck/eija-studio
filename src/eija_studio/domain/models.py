from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
import math
import re
from typing import Annotated, Any, Literal
from pydantic import (BaseModel, BeforeValidator, ConfigDict, Field, SerializerFunctionWrapHandler, StrictBool, StrictFloat, StrictInt,
                      StrictStr, model_serializer, model_validator)


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


Guard = Literal["actor_active", "role_current", "actor_assigned", "state_equals", "expected_version", "operation_binding"]
BASE_GUARDS: tuple[Guard, ...] = ("actor_active", "role_current", "state_equals", "expected_version", "operation_binding")


Comparison = Literal["eq", "ne", "lt", "le", "gt", "ge"]
SYMBOLS: dict[str, str] = {"eq": "=", "ne": "≠", "lt": "<", "le": "≤", "gt": ">", "ge": "≥"}
_COMPARE = {"eq": lambda a, b: a == b, "ne": lambda a, b: a != b, "lt": lambda a, b: a < b,
            "le": lambda a, b: a <= b, "gt": lambda a, b: a > b, "ge": lambda a, b: a >= b}


def iso_date(text: str) -> date | None:
    """The date a YYYY-MM-DD string names, or None. ISO dates compare as text in date order."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _kind(value: Any) -> str:
    """What a guard compares: a bool is not a number, and an int and a float are both numbers. NaN and infinity are
    no kind a guard compares (a record never holds one), so every guard over them fails closed."""
    if isinstance(value, float) and not math.isfinite(value):
        return "non-finite"
    return "boolean" if isinstance(value, bool) else "number" if isinstance(value, int | float) else "text"


class ValueGuard(Contract):
    """A UML guard over one of the record's values, such as ``[amount > 500]`` (issue #93, ADR-0234). The transition
    fires only when it holds. A value that is missing, or of another kind, never satisfies it (fail closed)."""
    attribute: str = Field(pattern=r"^[a-z][a-zA-Z0-9_]{0,39}$")
    op: Comparison
    value: StrictBool | StrictInt | StrictFloat | StrictStr

    @model_validator(mode="after")
    def comparable(self) -> ValueGuard:
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("A guard compares with a finite number")
        if isinstance(self.value, str) and len(self.value) > 200:
            raise ValueError("A guard's text is at most 200 characters")
        if isinstance(self.value, str) and self.op not in ("eq", "ne") and iso_date(self.value) is None:
            raise ValueError("Only a date (YYYY-MM-DD) or a number is compared with <, ≤, > or ≥")
        if isinstance(self.value, bool) and self.op not in ("eq", "ne"):
            raise ValueError("A true/false value is only compared with = or ≠")
        return self

    def holds(self, values: dict[str, Any]) -> bool:
        actual = values.get(self.attribute)
        if actual is None or _kind(actual) != _kind(self.value):
            return False
        return bool(_COMPARE[self.op](actual, self.value))

    def __str__(self) -> str:
        shown = json.dumps(self.value, ensure_ascii=False) if isinstance(self.value, str | bool) else repr(self.value)
        return f"{self.attribute} {SYMBOLS[self.op]} {shown}"


TimeUnit = Literal["minutes", "hours", "days"]
SECONDS: dict[str, int] = {"minutes": 60, "hours": 3600, "days": 86400}


class Delay(Contract):
    """A UML time event, ``after(14 days)`` (issue #93, ADR-0237): the transition may be taken only once the record has
    been in its source state this long. Time is measured from when the record entered that state, which every
    committed step does, a step back into the same state included. An unknown entry time never counts as due."""
    amount: StrictInt = Field(ge=1, le=10_000)
    unit: TimeUnit

    @property
    def seconds(self) -> int:
        return self.amount * SECONDS[self.unit]

    def due(self, elapsed: float | None) -> bool:
        return elapsed is not None and math.isfinite(elapsed) and elapsed >= self.seconds

    @property
    def span(self) -> str:
        """The duration in words: ``2 days``, ``1 hour``."""
        return f"{self.amount} {self.unit[:-1] if self.amount == 1 else self.unit}"

    def __str__(self) -> str:
        return f"after({self.span})"


class Transition(Contract):
    id: str = Field(pattern=r"^[A-Z][A-Z0-9_-]{0,63}$")
    action: str = Field(min_length=1, max_length=60)
    from_state: str = Field(min_length=1, max_length=60)
    to_state: str = Field(min_length=1, max_length=60)
    role: str = Field(min_length=1, max_length=60)
    guards: tuple[Guard, ...]
    required_effects: tuple[str, ...]
    forbidden_effects: tuple[str, ...]
    # Guards over the record's values (ADR-0234); all must hold. Empty is left out of every dump, so transitions
    # without them keep their exact bytes and hashes.
    conditions: tuple[ValueGuard, ...] = Field(default=(), max_length=8)
    # A time event (ADR-0237): taken only once the record has been in the source state this long. None is left out of
    # every dump, so transitions without one keep their exact bytes and hashes.
    after: Delay | None = None

    @model_serializer(mode="wrap")
    def _omit_unconditional(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        data: dict[str, Any] = handler(self)
        if not self.conditions:
            data.pop("conditions", None)
        if self.after is None:
            data.pop("after", None)
        return data

    def admits(self, values: dict[str, Any]) -> ValueGuard | None:
        """The first condition these record values fail, or None when the transition's conditions all hold."""
        return next((c for c in self.conditions if not c.holds(values)), None)

    @model_validator(mode="after")
    def guarded(self) -> Transition:
        if not set(BASE_GUARDS).issubset(self.guards):
            raise ValueError("Mandatory guards cannot be removed")
        if len(set(self.guards)) != len(self.guards):
            raise ValueError("Duplicate guards")
        if len(set(self.required_effects)) != len(self.required_effects):
            raise ValueError("Duplicate required effects")
        if len(set(self.forbidden_effects)) != len(self.forbidden_effects):
            raise ValueError("Duplicate forbidden effects")
        if set(self.required_effects) & set(self.forbidden_effects):
            raise ValueError("Required/forbidden effect conflict")
        if len(guard_keys(self.conditions)) != len(self.conditions):
            raise ValueError("Duplicate value guard")
        return self


def _is_tree(states: tuple[str, ...], composites: tuple[Composite, ...]) -> bool:
    """Composite names are new and unique, each holds known, distinct children including its initial one, each state or
    composite has at most one parent, and no composite holds itself. True when there are none."""
    names = [c.name for c in composites]
    return (_distinct(names) and not set(names) & set(states) and _known_children(states, composites)
            and _acyclic({child: c.name for c in composites for child in c.states}))


def _distinct(items: list[str]) -> bool:
    return len(set(items)) == len(items)


def _known_children(states: tuple[str, ...], composites: tuple[Composite, ...]) -> bool:
    """Each child is a state or a composite, held by one composite only, and each composite's initial is its child."""
    children = [child for c in composites for child in c.states]
    known = set(states) | {c.name for c in composites}
    return _distinct(children) and set(children) <= known and all(c.initial in c.states for c in composites)


def _acyclic(parent: dict[str, str]) -> bool:
    """No chain of parents comes back to where it started."""
    for start in parent:
        seen, node = {start}, start
        while node in parent:
            node = parent[node]
            if node in seen:
                return False
            seen.add(node)
    return True


def guard_keys(conditions: tuple[ValueGuard, ...]) -> frozenset[str]:
    """Value guards as a set compared by their JSON, as the semantic hash compares them. Pydantic equality would make
    ``[x = true]`` equal ``[x = 1]`` (``True == 1`` in Python), though no record value satisfies both."""
    return frozenset(canonical(c) for c in conditions)


def _shape(t: Transition) -> tuple[Any, ...]:
    """What every transition one action labels must share: all but its id and source state (ADR-0232)."""
    return (t.to_state, t.role, frozenset(t.guards), frozenset(t.required_effects), frozenset(t.forbidden_effects),
            guard_keys(t.conditions), t.after)


class Composite(Contract):
    """A UML composite state (issue #93 item 3, ADR-0240): a named group of states, or of other composites, with the
    child a transition into the group enters first. A record is always in exactly one plain state; the composite is the
    set of states inside it. The kernel runs the flat machine, so a composite never changes what a step does. A
    transition the group's states all share is drawn once from the group, and SCXML gets a nested `<state>`."""
    name: str = Field(min_length=1, max_length=60)
    states: tuple[str, ...] = Field(min_length=1, max_length=32)  # its children: states or other composites
    initial: str = Field(min_length=1, max_length=60)


class Workflow(Contract):
    schema_version: Literal["eija.workflow.v1"] = "eija.workflow.v1"
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")  # the id of the domain pack the workflow belongs to
    initial_state: str
    states: tuple[str, ...] = Field(min_length=1, max_length=32)
    transitions: tuple[Transition, ...] = Field(min_length=1, max_length=64)
    # Roles that may start a record (ADR-0231, issue #142). Empty means any active actor, as before: an empty tuple is
    # left out of every dump, so models that do not name initiators keep their exact bytes and hashes.
    initiators: tuple[str, ...] = Field(default=(), max_length=16)
    # Composite states (ADR-0240). Empty is left out of every dump, so flat models keep their exact bytes and hashes.
    composites: tuple[Composite, ...] = Field(default=(), max_length=16)

    @model_serializer(mode="wrap")
    def _omit_open_start(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        data: dict[str, Any] = handler(self)
        if not self.initiators:
            data.pop("initiators", None)
        if not self.composites:
            data.pop("composites", None)
        return data

    @model_validator(mode="after")
    def coherent(self) -> Workflow:
        if len(set(self.states)) != len(self.states) or self.initial_state not in self.states:
            raise ValueError("Duplicate states or missing initial state")
        ids: set[str] = set()
        keys: set[tuple[str, str]] = set()
        shapes: dict[str, tuple[Any, ...]] = {}
        for t in self.transitions:
            if t.from_state not in self.states or t.to_state not in self.states:
                raise ValueError("Dangling transition state")
            # One action may leave several states (issue #148, ADR-0232), but from each state at most once, and every
            # transition it labels must be the same apart from its id and source state.
            if t.id in ids or (t.from_state, t.action) in keys or shapes.setdefault(t.action, _shape(t)) != _shape(t):
                raise ValueError("Duplicate or ambiguous transition/action")
            ids.add(t.id); keys.add((t.from_state, t.action))
        return self._grouped()

    def _grouped(self) -> Workflow:
        """Initiators are distinct and composite states form a tree (ADR-0231, ADR-0240)."""
        if len(set(self.initiators)) != len(self.initiators):
            raise ValueError("Duplicate initiator role")
        if not _is_tree(self.states, self.composites):
            raise ValueError("Composite states must form a tree over the states")
        return self

    def composite(self, name: str) -> Composite | None:
        return next((c for c in self.composites if c.name == name), None)

    def parent(self, name: str) -> str | None:
        """The composite that directly holds a state or composite, or None at the top level."""
        return next((c.name for c in self.composites if name in c.states), None)

    def ancestors(self, name: str) -> tuple[str, ...]:
        """The composites holding a state or composite, innermost first."""
        found: list[str] = []
        parent = self.parent(name)
        while parent is not None:
            found.append(parent)
            parent = self.parent(parent)
        return tuple(found)

    def leaves(self, name: str) -> tuple[str, ...]:
        """The plain states inside a composite, in model order; a plain state is its own only leaf."""
        group = self.composite(name)
        if group is None:
            return (name,) if name in self.states else ()
        inside = {leaf for child in group.states for leaf in self.leaves(child)}
        return tuple(s for s in self.states if s in inside)

    def entry(self, name: str) -> str:
        """The plain state a transition into `name` enters: a composite's initial child, followed down."""
        group = self.composite(name)
        return name if group is None else self.entry(group.initial)

    def transition_for(self, action: str, state: str | None = None) -> Transition | None:
        """The transition ``action`` takes from ``state``; without a state, or when it does not leave that state,
        any transition it labels (they differ only in id and source, ADR-0232). None when the action is not modelled."""
        labelled = [t for t in self.transitions if t.action == action]
        return next((t for t in labelled if t.from_state == state), labelled[0] if labelled else None)

    @property
    def longest_wait(self) -> int:
        """The longest time event on any transition, in seconds; 0 when the model has none (ADR-0237). Waiting this
        long in a state makes every time event leaving it due."""
        return max((t.after.seconds for t in self.transitions if t.after is not None), default=0)

    def sources(self, action: str) -> tuple[str, ...]:
        """The states ``action`` leaves, in model order."""
        return tuple(t.from_state for t in self.transitions if t.action == action)

    @property
    def semantic_hash(self) -> str:
        # Order of definitions is non-semantic, but state/action identities are not.
        data = self.model_dump(mode="json")
        data["states"] = sorted(data["states"])
        data["transitions"] = sorted(data["transitions"], key=lambda x: x["id"])
        if "initiators" in data:  # who may start a record is a set (ADR-0231); absent when empty, so old hashes hold
            data["initiators"] = sorted(data["initiators"])
        if "composites" in data:  # a set of groups, each over a set of children (ADR-0240); absent when empty
            data["composites"] = sorted(({**c, "states": sorted(c["states"])} for c in data["composites"]),
                                        key=lambda c: c["name"])
        for t in data["transitions"]:
            for key in ("guards", "required_effects", "forbidden_effects"):
                t[key] = sorted(t[key])
            if "conditions" in t:  # a set of guards (ADR-0234); absent when empty, so old hashes hold
                t["conditions"] = sorted(t["conditions"], key=canonical)
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


def _json_integer(value: Any) -> int:
    """An integer as JSON Schema's `"type": "integer"` reads one (ADR-0238): an int, or a float with no fractional part
    (`1.0`, which `json.dumps(1.0)` writes). A string, a boolean or a fractional float is refused. Pydantic's lax int
    took `"5"` and `true`, and its strict int refused `1.0`, so neither matched the published contracts."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("must be a JSON integer")
    if isinstance(value, float) and not (math.isfinite(value) and value.is_integer()):
        raise ValueError("must be a whole number")
    return int(value)


JsonInt = Annotated[int, BeforeValidator(_json_integer)]


class LayoutChange(Contract):
    node: str = Field(min_length=1, max_length=60)
    x: JsonInt = Field(ge=0, le=2000)
    y: JsonInt = Field(ge=0, le=2000)


class ExecuteCommand(Contract):
    operation_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,100}$")
    actor_id: str = Field(min_length=1, max_length=80)
    instance_id: str = Field(min_length=1, max_length=80)
    action: str = Field(min_length=1, max_length=60)
    expected_version: JsonInt = Field(ge=0)


class Principal(Contract):
    id: str
    capabilities: frozenset[str]

    def require(self, capability: str) -> None:
        if capability not in self.capabilities:
            raise DomainError("AUTHORITY_REQUIRED", f"Capability required: {capability}")


OWNER = Principal(id="local-owner", capabilities=frozenset({"select", "edit", "approve", "apply"}))
AGENT = Principal(id="agent", capabilities=frozenset())
