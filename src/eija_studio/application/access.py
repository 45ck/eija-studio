"""Who can do what (ADR-0171): the model's permissions as a role by state matrix, each cell checked by the kernel, and
reachability questions such as "can a record reach this state without that role ever acting?".

The matrix is a projection of the model's transitions; every cell is also tried in the kernel with each of the pack's
fixture actors in that role, on a fresh record in that state, so it says who the kernel actually lets through and why
the others are refused. Comparing two models (the base and a previewed plan) flags the cells that change.

A reachability answer has three outcomes. UNREACHABLE is a proof over the model: no sequence of its transitions
avoids the role, and guards can only refuse more, so no actor can do it. REACHABLE comes with a path the kernel
committed step by step on one record, with fixture actors. NOT_SHOWN means the model has such a path but no fixture
actor could take it in the kernel; other actors might. Nothing persists and no effect leaves the process.
"""
from __future__ import annotations

from collections import deque
from typing import Any

from eija_studio.domain.models import DomainError, ExecuteCommand, Transition, ValueGuard, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.data import data_for
from eija_studio.domain.value_guards import points
from .runtime import execute, initialise
from .simulation import CASE, MemorySession


def _ordered(model: Workflow) -> list[Transition]:
    return sorted(model.transitions, key=lambda t: t.id)


def _guards(transitions: list[Transition]) -> dict[str, list[ValueGuard]]:
    """Every guard over values of these transitions, grouped by the attribute it reads, in name order."""
    found: dict[str, list[ValueGuard]] = {}
    for t in transitions:
        for guard in t.conditions:
            found.setdefault(guard.attribute, []).append(guard)
    return dict(sorted(found.items()))


def _choices(pack: Pack) -> dict[str, tuple[str, ...]]:
    """The record class's choice attributes and their declared choices, the only values a record of them can hold."""
    data = data_for(pack)
    record = next((e for e in data.entities if e.name == data.record), None) if data else None
    return {a.name: a.choices for a in record.attributes if a.type == "choice"} if record else {}


def meeting(pack: Pack, transitions: list[Transition]) -> dict[str, Any] | None:
    """A record's values that meet every guard over values of these transitions (ADR-0234): {} when they have none,
    None when no values meet them all. A cell is about who may act, so it is tried on a record whose values let it.

    A guard reads one attribute, so each attribute is solved on its own, among the values that stand for every value
    its guards tell apart; a choice attribute only among its declared choices, since a record can hold no other."""
    grouped = _guards(transitions)
    choices = _choices(pack) if grouped else {}
    values: dict[str, Any] = {}
    for attribute, guards in grouped.items():
        candidates = choices.get(attribute) or [v for v in points(guards) if v is not None]
        value = next((v for v in candidates if all(g.holds({attribute: v}) for g in guards)), None)
        if value is None:
            return None
        values[attribute] = value
    return values


def _try(pack: Pack, model: Workflow, transition: Transition, actor_id: str, session: MemorySession | None = None,
         record: str | None = None) -> str | None:
    """None if the kernel commits `transition` for this actor, else its refusal code. Without a record, a fresh one is
    started in the transition's source state, with values that meet the transition's guards over values, if any."""
    session = session or MemorySession(pack)
    if record is None:
        record = initialise(session, CASE, model, state=transition.from_state, pack=pack)["id"]  # type: ignore[arg-type]
        session.record_values[record] = meeting(pack, [transition]) or {}
        _ready(session, model, transition, record)
    item = session.instances[record]
    command = ExecuteCommand(operation_id=f"access-{transition.id}-{actor_id}-{item['version']}", actor_id=actor_id,
                             instance_id=record, action=transition.action, expected_version=item["version"])
    try:
        execute(session, CASE, model, command, pack=pack)  # type: ignore[arg-type]  # duck-typed port
    except DomainError as refused:
        return refused.code
    return None


def _ready(session: MemorySession, model: Workflow, transition: Transition, record: str) -> None:
    """Make a fresh record able to take `transition` but for who acts, as a simulated record can: wait out its time
    event (ADR-0237) and link each object it moves to one in a state that event moves from (ADR-0241). Without this a
    timed step or one that moves an object was refused for everyone, though Simulate commits it."""
    if transition.after is not None:
        session.wait(transition.after.seconds)
    for step in transition.then:
        lifecycle = model.lifecycle(step.link)
        if lifecycle is not None:
            start = next((m.from_state for m in lifecycle.moves if m.event == step.event), lifecycle.initial)
            session.link(record, step.link, f"{lifecycle.entity} {record}:{step.link}", start)


def _cell(pack: Pack, model: Workflow, t: Transition) -> dict[str, Any]:
    actors = [a for a in pack.fixtures.actors if a.role == t.role]
    tried = [{"actor": a.id, "refused": _try(pack, model, t, a.id)} for a in actors]
    return {"action": t.action, "transition": t.id, "to": t.to_state, "assigned_only": "actor_assigned" in t.guards,
            "actors": tried} | ({"when": [str(g) for g in t.conditions]} if t.conditions else {}) \
        | ({"after": str(t.after)} if t.after is not None else {}) | ({"moves": [str(m) for m in t.then]} if t.then else {})


def matrix(pack: Pack, model: Workflow) -> dict[str, Any]:
    """Every role's actions from every state, each tried in the kernel with the fixture actors in that role."""
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", "The workflow belongs to a different pack")
    roles = [r.id for r in pack.roles]
    cells: dict[str, dict[str, list[dict[str, Any]]]] = {s: {r: [] for r in roles} for s in model.states}
    for t in _ordered(model):
        cells[t.from_state].setdefault(t.role, []).append(_cell(pack, model, t))
    return {"roles": roles, "states": list(model.states), "initial": model.initial_state, "cells": cells}


Key = tuple[str, str, str, str]


def _conditions(cell: dict[str, Any]) -> list[str]:
    """What, beyond the role, a cell's permission depends on: being assigned, guards over the record's values, a time
    event and the linked objects it moves."""
    return ((["assigned only"] if cell["assigned_only"] else []) + [f"when [{w}]" for w in cell.get("when", [])]
            + ([cell["after"]] if "after" in cell else []) + [f"moves {m}" for m in cell.get("moves", [])])


def _keys(grid: dict[str, Any]) -> dict[Key, list[str]]:
    return {(state, role, c["action"], c["to"]): _conditions(c)
            for state, row in grid["cells"].items() for role, cs in row.items() for c in cs}


def _named(key: Key) -> dict[str, str]:
    return dict(zip(("state", "role", "action", "to"), key, strict=True))


def _changes(now: dict[Key, list[str]], before: dict[Key, list[str]]) -> dict[str, list[dict[str, Any]]]:
    """Permissions added and removed, and those kept whose conditions changed (being assigned, a guard over values):
    a plan that only tightens or loosens who may take an action changes who can do what too."""
    changed = [_named(k) | {"before": before[k], "after": now[k]} for k in sorted(set(now) & set(before)) if now[k] != before[k]]
    return {"added": [_named(k) for k in sorted(set(now) - set(before))],
            "removed": [_named(k) for k in sorted(set(before) - set(now))], "changed": changed}


def access(pack: Pack, model: Workflow, base: Workflow | None = None) -> dict[str, Any]:
    """The matrix for `model`, and, when `base` differs, the permissions it adds, removes and changes compared with
    `base`."""
    grid = matrix(pack, model)
    changes: dict[str, list[dict[str, Any]]] = {"added": [], "removed": [], "changed": []}
    if base is not None and base.semantic_hash != model.semantic_hash:
        changes = _changes(_keys(grid), _keys(matrix(pack, base)))
    return {"format": "eija.access.v1", "pack": pack.id, "model": model.semantic_hash, **grid, "changes": changes,
            "limits": ["Each cell is tried in the kernel with the pack's fixture actors on a fresh record, made ready as "
                       "Simulate's records are: values that meet its guards, its time event waited out, and a linked "
                       "object that can make its move. Other actors are refused or let through by the same guards."]}


def _path(model: Workflow, target: str, usable: set[str]) -> list[Transition] | None:
    """The shortest sequence of usable transitions from the initial state to `target` (breadth first, by id)."""
    back: dict[str, Transition | None] = {model.initial_state: None}
    queue = deque([model.initial_state])
    while queue:
        state = queue.popleft()
        if state == target:
            path: list[Transition] = []
            while (step := back[state]) is not None:
                path.append(step)
                state = step.from_state
            return path[::-1]
        for t in _ordered(model):
            if t.from_state == state and t.id in usable and t.to_state not in back:
                back[t.to_state] = t
                queue.append(t.to_state)
    return None


def _unreachable(question: dict[str, Any], without: str | None) -> dict[str, Any]:
    return question | {"verdict": "UNREACHABLE", "path": [], "why": "No sequence of the model's transitions gets there"
                       + (f" without {without}" if without else "") + ". Guards can only refuse more, so no actor can."}


def _not_shown(question: dict[str, Any], why: str) -> dict[str, Any]:
    return question | {"verdict": "NOT_SHOWN", "path": [], "why": why}


def _taker(pack: Pack, model: Workflow, t: Transition) -> str | None:
    """The first fixture actor in the transition's role the kernel lets take it from a fresh record, if any."""
    return next((a.id for a in pack.fixtures.actors if a.role == t.role and _try(pack, model, t, a.id) is None), None)


def _replay(pack: Pack, model: Workflow, path: list[Transition], values: dict[str, Any],
            starter: str | None = None) -> list[dict[str, Any]] | str:
    """Take `path` on one record in the kernel, started by a holder of role `starter` when the model names who may
    start one (ADR-0231): the steps it committed, or the refusal code that stopped it."""
    session = MemorySession(pack)
    record = initialise(session, CASE, model, pack=pack, role=starter)["id"]  # type: ignore[arg-type]
    session.record_values[record] = values
    for lifecycle in model.objects:  # a new object per link, in its initial state, as Simulate starts one (ADR-0241)
        session.link(record, lifecycle.link, f"{lifecycle.entity} 1", lifecycle.initial)
    steps: list[dict[str, Any]] = []
    for t in path:
        if t.after is not None:  # the record waits out a time event before its timed step (ADR-0237)
            session.wait(t.after.seconds)
        # The first fixture actor in the role the kernel lets take this step on this record: one who took an earlier
        # step may be refused by a separation of duties law (ADR-0233), and another of the role may not.
        code: str | None = "ROLE_DENIED"
        actor = ""
        for candidate in (a.id for a in pack.fixtures.actors if a.role == t.role):
            code = _try(pack, model, t, candidate, session, record)
            if code is None:
                actor = candidate
                break
        if code is not None:  # a guard that depends on more than the actor and the state; reported, never hidden
            return f"{t.action} ({code})"
        steps.append({"transition": t.id, "action": t.action, "role": t.role, "actor": actor, "from": t.from_state, "to": t.to_state})
    return steps


def _check(pack: Pack, model: Workflow, target: str, without: str | None) -> None:
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", "The workflow belongs to a different pack")
    if target not in model.states:
        raise DomainError("UNKNOWN_STATE", f"The model has no state {target}")
    if without is not None and without not in {r.id for r in pack.roles}:
        raise DomainError("UNKNOWN_ROLE", f"The pack has no role {without}")


def _reached(target: str, steps: list[dict[str, Any]]) -> str:
    return (f"Every record starts in {target}." if not steps
            else "The kernel committed every step of this path on one record, with fixture actors.")


def _usable(pack: Pack, model: Workflow, allowed: set[str]) -> set[str]:
    """The allowed transitions some fixture actor can take in the kernel."""
    return {t.id for t in model.transitions if t.id in allowed and _taker(pack, model, t)}


def _starter(pack: Pack, model: Workflow, without: str | None) -> tuple[str | None, str | None]:
    """Who starts the record (ADR-0231): (a role a fixture actor holds that may start one, None) or (None, why not).
    A model that names no initiators lets anyone start a record, so there is nothing to choose. A workflow that receives
    a signal (ADR-0242) also starts a record when one is delivered, with no person's role, so it starts one that way
    when no starting role is left or held; `runtime.receive` starts it exactly as a role-less `initialise` does."""
    if not model.initiators:
        return None, None
    roles = [r for r in model.initiators if r != without]
    held = next((r for r in roles if any(a.role == r for a in pack.fixtures.actors)), None)
    if held or model.receives:
        return held, None
    if not roles:
        return None, "unreachable"
    return None, f"Only {', '.join(roles)} may start a record, and no fixture actor holds that role; other actors might."


def _started(model: Workflow, starter: str | None) -> str:
    """How the replayed record was started, when the model limits that and no starting role was used: by a signal."""
    if not model.initiators or starter is not None:
        return ""
    signals = ", ".join(f"{r.signal} from {r.sender}" for r in model.receives)
    return f" The record was started by a signal from another workflow ({signals}), as the kernel starts one on delivery."


def reach(pack: Pack, model: Workflow, target: str, without: str | None = None) -> dict[str, Any]:
    """Can a record reach `target` with no step taken by role `without` (or at all, when it is None)? Starting the record
    is a step too: when the model names who may start one, a record without them does not exist (ADR-0231), unless a
    signal from another workflow starts it (ADR-0242)."""
    _check(pack, model, target, without)
    question = {"target": target, "without": without, "model": model.semantic_hash}
    starter, unstarted = _starter(pack, model, without)
    if unstarted == "unreachable":
        return question | {"verdict": "UNREACHABLE", "path": [], "why": f"Only {', '.join(model.initiators)} may start a record "
                           f"and no signal starts one, so without {without} no record exists to reach {target}. "
                           "The kernel refuses anyone else (ROLE_CANNOT_START)."}
    allowed = {t.id for t in model.transitions if t.role != without}
    if _path(model, target, allowed) is None:
        return _unreachable(question, without)
    # Search only transitions some fixture actor can take in the kernel, then replay the path on one record.
    if unstarted:
        return _not_shown(question, unstarted)
    path = _path(model, target, _usable(pack, model, allowed))
    if path is None:
        return _not_shown(question, "The model has a path, but no fixture actor could take every step in the kernel; other actors might.")
    values = meeting(pack, path)  # one record takes the whole path, so its values must meet every guard on it (ADR-0234)
    if values is None:
        return _not_shown(question, "The model has a path, but no one record's values meet every guard over values on it.")
    steps = _replay(pack, model, path, values, starter)
    if isinstance(steps, str):
        return _not_shown(question, f"The kernel refused {steps} on replay.")
    return question | {"verdict": "REACHABLE", "path": steps, "why": _reached(target, steps) + _started(model, starter)} | ({"values": values} if values else {})
