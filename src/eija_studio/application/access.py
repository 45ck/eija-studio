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

from eija_studio.domain.models import DomainError, ExecuteCommand, Transition, Workflow
from eija_studio.domain.pack import Pack
from .runtime import execute, initialise
from .simulation import CASE, MemorySession


def _ordered(model: Workflow) -> list[Transition]:
    return sorted(model.transitions, key=lambda t: t.id)


def _try(pack: Pack, model: Workflow, transition: Transition, actor_id: str, session: MemorySession | None = None,
         record: str | None = None) -> str | None:
    """None if the kernel commits `transition` for this actor, else its refusal code. Without a record, a fresh one is
    started in the transition's source state."""
    session = session or MemorySession(pack)
    record = record or initialise(session, CASE, model, state=transition.from_state, pack=pack)["id"]  # type: ignore[arg-type]
    item = session.instances[record]
    command = ExecuteCommand(operation_id=f"access-{transition.id}-{actor_id}-{item['version']}", actor_id=actor_id,
                             instance_id=record, action=transition.action, expected_version=item["version"])
    try:
        execute(session, CASE, model, command, pack=pack)  # type: ignore[arg-type]  # duck-typed port
    except DomainError as refused:
        return refused.code
    return None


def _cell(pack: Pack, model: Workflow, t: Transition) -> dict[str, Any]:
    actors = [a for a in pack.fixtures.actors if a.role == t.role]
    tried = [{"actor": a.id, "refused": _try(pack, model, t, a.id)} for a in actors]
    return {"action": t.action, "transition": t.id, "to": t.to_state, "assigned_only": "actor_assigned" in t.guards,
            "actors": tried}


def matrix(pack: Pack, model: Workflow) -> dict[str, Any]:
    """Every role's actions from every state, each tried in the kernel with the fixture actors in that role."""
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", "The workflow belongs to a different pack")
    roles = [r.id for r in pack.roles]
    cells: dict[str, dict[str, list[dict[str, Any]]]] = {s: {r: [] for r in roles} for s in model.states}
    for t in _ordered(model):
        cells[t.from_state].setdefault(t.role, []).append(_cell(pack, model, t))
    return {"roles": roles, "states": list(model.states), "initial": model.initial_state, "cells": cells}


def _keys(grid: dict[str, Any]) -> set[tuple[str, str, str, str]]:
    return {(state, role, c["action"], c["to"]) for state, row in grid["cells"].items() for role, cs in row.items() for c in cs}


def _named(key: tuple[str, str, str, str]) -> dict[str, str]:
    return dict(zip(("state", "role", "action", "to"), key, strict=True))


def access(pack: Pack, model: Workflow, base: Workflow | None = None) -> dict[str, Any]:
    """The matrix for `model`, and, when `base` differs, the permissions it adds and removes compared with `base`."""
    grid = matrix(pack, model)
    changes: dict[str, list[dict[str, str]]] = {"added": [], "removed": []}
    if base is not None and base.semantic_hash != model.semantic_hash:
        now, before = _keys(grid), _keys(matrix(pack, base))
        changes = {"added": [_named(k) for k in sorted(now - before)], "removed": [_named(k) for k in sorted(before - now)]}
    return {"format": "eija.access.v1", "pack": pack.id, "model": model.semantic_hash, **grid, "changes": changes,
            "limits": ["Each cell is tried in the kernel with the pack's fixture actors on a fresh record; other actors "
                       "are refused or let through by the same guards."]}


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


def _replay(pack: Pack, model: Workflow, path: list[Transition]) -> list[dict[str, Any]] | str:
    """Take `path` on one record in the kernel: the steps it committed, or the refusal code that stopped it."""
    session = MemorySession(pack)
    record = initialise(session, CASE, model, pack=pack)["id"]  # type: ignore[arg-type]
    steps = []
    for t in path:
        actor = _taker(pack, model, t) or ""
        code = _try(pack, model, t, actor, session, record)
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


def reach(pack: Pack, model: Workflow, target: str, without: str | None = None) -> dict[str, Any]:
    """Can a record reach `target` with no step taken by role `without` (or at all, when it is None)?"""
    _check(pack, model, target, without)
    question = {"target": target, "without": without, "model": model.semantic_hash}
    allowed = {t.id for t in model.transitions if t.role != without}
    if _path(model, target, allowed) is None:
        return _unreachable(question, without)
    # Search only transitions some fixture actor can take in the kernel, then replay the path on one record.
    path = _path(model, target, _usable(pack, model, allowed))
    if path is None:
        return _not_shown(question, "The model has a path, but no fixture actor could take every step in the kernel; other actors might.")
    steps = _replay(pack, model, path)
    if isinstance(steps, str):
        return _not_shown(question, f"The kernel refused {steps} on replay.")
    return question | {"verdict": "REACHABLE", "path": steps, "why": _reached(target, steps)}
