"""Seeded simulation of people using the app built from a model (ADR-0152). Every step is decided by the kernel.

Simulated users are the pack's fixture actors. At each step one of them starts a record or picks one they can work on
and tries an action: usually one their role is offered from the record's state, sometimes any declared action (a slip),
and sometimes with an out-of-date version (someone else got there first). Revoked or unassigned actors still try, as
people do, and the kernel refuses them. `runtime.execute` decides each attempt against an in-memory unit of work, so
the counts, refusal codes and effects are the kernel's own answers, not a second reading of the model. The same seed
gives the same run. Nothing persists and no effect leaves the process.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from typing import Any

from eija_studio.domain.models import DomainError, ExecuteCommand, Transition, Workflow
from eija_studio.domain.pack import Pack
from .runtime import execute, initialise

CASE = "simulation"
MAX_STEPS = 5000
TRACE_LIMIT = 60  # steps kept in order for the run log and the sequence view
NEW_RECORD = 0.2  # chance a step starts a new record instead of acting on an open one
SLIP = 0.1  # chance a user tries a declared action that does not leave the record's state
STALE = 0.05  # chance a user acts on a version someone else has already changed


class MemorySession:
    """The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect."""

    def __init__(self, pack: Pack):
        self.actors = {a.id: a.model_dump() for a in pack.fixtures.actors}
        self.instances: dict[str, dict[str, Any]] = {}
        self.operations: dict[str, dict[str, Any]] = {}
        self.audit: list[str] = []
        self.outbox: list[str] = []

    def actor(self, actor_id: str) -> dict[str, Any]:
        if actor_id not in self.actors:
            raise DomainError("UNKNOWN_ACTOR", "Actor is not in the trusted fixture directory")
        return self.actors[actor_id]

    def create_instance(self, item: dict[str, Any]) -> None:
        self.instances[item["id"]] = dict(item)

    def find_instance(self, instance_id: str, case_id: str) -> dict[str, Any] | None:
        item = self.instances.get(instance_id)
        return dict(item) if item and item["case_id"] == case_id else None

    def update_instance(self, item: dict[str, Any], expected: int) -> None:
        if self.instances[item["id"]]["version"] != expected:
            raise DomainError("STALE_VERSION", "Concurrent state update")
        self.instances[item["id"]] = dict(item)

    def find_operation(self, operation_id: str) -> dict[str, Any] | None:
        return self.operations.get(operation_id)

    def record_operation(self, operation_id: str, binding: str, result: dict[str, Any]) -> None:
        self.operations[operation_id] = {"binding": binding, "result": result}

    def event(self, kind: str, body: dict[str, Any]) -> None:
        self.audit.append(kind)

    def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None:
        self.outbox.append(effect)


class _Dice:
    """Seeded choices from SHA-256 of (seed, draw number): the same seed gives the same run on every platform and Python
    version, which `random.Random`'s algorithms do not promise. Not for secrets; nothing here is one."""

    def __init__(self, seed: int):
        self.seed, self.draws = seed, 0

    def _next(self) -> int:
        self.draws += 1
        return int.from_bytes(sha256(f"{self.seed}:{self.draws}".encode()).digest()[:8], "big")

    def chance(self, p: float) -> bool:
        return self._next() < p * 2**64

    def choice(self, items: list[Any]) -> Any:
        return items[self._next() % len(items)]


class _Run:
    """Tallies for one simulation; `report` turns them into plain data."""

    def __init__(self, model: Workflow):
        self.model = model
        self.labels: dict[str, str] = {}  # kernel ids are random; the report names records R1, R2, ... in creation order
        self.commits: Counter[str] = Counter()
        self.refusals: dict[str, Counter[str]] = defaultdict(Counter)
        self.codes: Counter[str] = Counter()
        self.entered: Counter[str] = Counter()
        self.trace: list[dict[str, Any]] = []

    def log(self, step: dict[str, Any]) -> None:
        if len(self.trace) < TRACE_LIMIT:
            self.trace.append(step)


def _ordered(model: Workflow) -> list[Transition]:
    """Transitions by id. Their order in the document is not semantic (the semantic hash sorts them), so seeded
    choices must not depend on it: the same seed and model hash always give the same run."""
    return sorted(model.transitions, key=lambda t: t.id)


def _actions_for(model: Workflow, actor: dict[str, Any], state: str) -> list[str]:
    """The actions a user in this role would expect to take from `state`: what the app offers their role."""
    return [t.action for t in _ordered(model) if t.from_state == state and t.role == actor["role"]]


def _attempt(session: MemorySession, pack: Pack, model: Workflow, run: _Run, rng: _Dice, n: int,
             actor: dict[str, Any], record: str) -> None:
    item = session.instances[record]
    mine = _actions_for(model, actor, item["state"])
    action = rng.choice([t.action for t in _ordered(model)]) if not mine or rng.chance(SLIP) else rng.choice(mine)
    version = item["version"] - 1 if item["version"] > 0 and rng.chance(STALE) else item["version"]
    command = ExecuteCommand(operation_id=f"sim-{n}", actor_id=actor["id"], instance_id=record, action=action,
                             expected_version=version)
    step = {"step": n, "actor": actor["id"], "role": actor["role"], "record": run.labels[record], "action": action,
            "from": item["state"]}
    transition = next(t for t in model.transitions if t.action == action)
    try:
        result = execute(session, CASE, model, command, pack=pack)  # type: ignore[arg-type]  # duck-typed port
    except DomainError as refused:
        run.refusals[transition.id][refused.code] += 1
        run.codes[refused.code] += 1
        run.log(step | {"outcome": "REFUSED", "code": refused.code})
        return
    to = result["instance"]["state"]
    run.commits[transition.id] += 1
    run.entered[to] += 1
    run.log(step | {"outcome": "COMMITTED", "to": to, "effects": result["effects"]})


def simulate(pack: Pack, model: Workflow, *, seed: int = 1, steps: int = 500) -> dict[str, Any]:
    """Run `steps` seeded attempts by the pack's fixture actors through the kernel and report where they went."""
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", "The workflow belongs to a different pack")
    if not 1 <= steps <= MAX_STEPS:
        raise DomainError("INVALID_STEPS", f"Give between 1 and {MAX_STEPS} steps")
    actors = [a.model_dump() for a in pack.fixtures.actors]
    if not actors:
        raise DomainError("NO_ACTORS", "The pack has no fixture actors to simulate")
    rng, session, run = _Dice(seed), MemorySession(pack), _Run(model)
    for n in range(1, steps + 1):
        _step(session, pack, model, run, rng, n, rng.choice(actors))
    return _report(pack, model, seed, steps, session, run)


def _step(session: MemorySession, pack: Pack, model: Workflow, run: _Run, rng: _Dice, n: int, actor: dict[str, Any]) -> None:
    """One user's turn: start a record, or act on one they can work on (any record if none)."""
    records = list(session.instances)  # creation order, not the kernel's random ids, so a seed replays exactly
    workable = [r for r in records if _actions_for(model, actor, session.instances[r]["state"])]
    if records and not rng.chance(NEW_RECORD) and (workable or not rng.chance(NEW_RECORD)):
        _attempt(session, pack, model, run, rng, n, actor, rng.choice(workable or records))
        return
    record = initialise(session, CASE, model, pack=pack)["id"]  # type: ignore[arg-type]
    run.labels[record] = f"R{len(run.labels) + 1}"
    run.entered[model.initial_state] += 1
    run.log({"step": n, "actor": actor["id"], "role": actor["role"], "record": run.labels[record],
             "outcome": "CREATED", "to": model.initial_state})


def _finding(severity: str, element: str, text: str) -> dict[str, str]:
    return {"severity": severity, "element": element, "text": text}


def _stuck(model: Workflow, run: _Run, state: str) -> bool:
    """A state with ways out, none of which any user managed to take."""
    leaving = [t for t in model.transitions if t.from_state == state]
    return bool(leaving) and not any(run.commits[t.id] for t in leaving)


def _state_findings(model: Workflow, run: _Run, occupancy: Counter[str]) -> list[dict[str, str]]:
    """States no record reached, and non-final states holding records that no action ever moved on."""
    unreached = [_finding("warning", "state:" + s, f"No record reached {s}") for s in sorted(model.states) if run.entered[s] == 0]
    stuck = [_finding("warning", "state:" + s, f"{occupancy[s]} record(s) got stuck in {s}: nobody could move them on")
             for s in sorted(model.states) if occupancy[s] and _stuck(model, run, s)]
    return unreached + stuck


def _findings(model: Workflow, run: _Run, occupancy: Counter[str]) -> list[dict[str, str]]:
    """Things worth a look, worst first. Each names the element it is about so the IDE can select it."""
    never = [_finding("warning", "transition:" + t.id, f"{t.action} never succeeded in this run")
             for t in _ordered(model) if run.commits[t.id] == 0]
    refused = []
    for t in sorted(_ordered(model), key=lambda t: -sum(run.refusals.get(t.id, Counter()).values())):
        codes = run.refusals.get(t.id)
        if codes:
            code, count = codes.most_common(1)[0]
            refused.append(_finding("info", "transition:" + t.id,
                                    f"{t.action} refused {sum(codes.values())} time(s), mostly {code} ({count})"))
    return never + _state_findings(model, run, occupancy) + refused


def _report(pack: Pack, model: Workflow, seed: int, steps: int, session: MemorySession, run: _Run) -> dict[str, Any]:
    occupancy = Counter(item["state"] for item in session.instances.values())
    attempts = sum(run.commits.values()) + sum(run.codes.values())
    return {
        "format": "eija.simulation.v1", "pack": pack.id, "model": model.semantic_hash, "seed": seed, "steps": steps,
        "records": len(session.instances), "attempts": attempts, "committed": sum(run.commits.values()),
        "refused": sum(run.codes.values()), "codes": dict(run.codes.most_common()),
        "transitions": {t.id: {"committed": run.commits[t.id], "refused": dict(run.refusals.get(t.id, {}))} for t in model.transitions},
        "states": {s: {"entered": run.entered[s], "now": occupancy[s]} for s in model.states},
        "effects": {"audit": dict(Counter(session.audit)), "outbox": dict(Counter(session.outbox))},
        "findings": _findings(model, run, occupancy), "trace": run.trace,
        "limits": ["Simulated users are the pack's fixture actors acting at random, not measured human behaviour.",
                   "Each attempt is decided by the kernel against in-memory storage; no effect leaves the process."],
    }
