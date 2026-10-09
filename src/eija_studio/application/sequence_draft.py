"""Scenarios drafted from the model, for a system that has none yet (ADR-0195).

A system started from a sketch has a state machine and fixture actors but no `scenarios.json`, so its Sequences and
Tests tabs would be empty. `draft_scenarios` proposes some: the shortest path to each final state, each step taken
by a fixture actor in the transition's role, and one step someone in another role must be refused. What each step
must do is not written here: `scenario_run.record_steps` asks the kernel, so a draft states what the model does now.
It is a draft, never saved: the person keeps it by editing or downloading `scenarios.json`.
"""
from __future__ import annotations

import re
from collections import deque

from eija_studio.domain.models import Transition, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.scenarios import Scenarios, parse_scenarios
from .scenario_run import record_steps

MAX_DRAFTS = 6


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40].strip("-") or "state"


def _actor_for(pack: Pack, t: Transition) -> str | None:
    """A fixture actor the kernel should let take `t`: in its role, active, and assigned when it must be."""
    fits = [a for a in pack.fixtures.actors if a.role == t.role and a.active and (a.assigned or "actor_assigned" not in t.guards)]
    return fits[0].id if fits else None


def _shortest(model: Workflow) -> dict[str, list[Transition]]:
    """The shortest path of transitions (taken in id order, so the draft is stable) to every state."""
    paths: dict[str, list[Transition]] = {model.initial_state: []}
    queue = deque([model.initial_state])
    while queue:
        state = queue.popleft()
        for t in sorted((t for t in model.transitions if t.from_state == state), key=lambda t: t.id):
            if t.to_state not in paths:
                paths[t.to_state] = [*paths[state], t]
                queue.append(t.to_state)
    return paths


def _ends(model: Workflow) -> list[str]:
    """The final states (no transition leaves them), or every reachable state but the first when there are none."""
    sources = {t.from_state for t in model.transitions}
    finals = [s for s in model.states if s not in sources]
    return finals or [s for s in model.states if s != model.initial_state]


def _journeys(pack: Pack, model: Workflow) -> list[tuple[str, list[tuple[str, str]]]]:
    paths, found = _shortest(model), []
    for state in _ends(model):
        path = paths.get(state)
        actors = [_actor_for(pack, t) for t in path or []]
        if path and all(actors):
            found.append((state, [(str(a), t.action) for a, t in zip(actors, path, strict=True)]))
    return found


def _outsider(pack: Pack, model: Workflow) -> tuple[str, str, list[tuple[str, str]]] | None:
    """Someone active in another role tries the first step: the kernel must refuse it."""
    first = next((t for t in sorted(model.transitions, key=lambda t: t.id) if t.from_state == model.initial_state), None)
    other = next((a for a in pack.fixtures.actors if first and a.active and a.role != first.role), None)
    if first is None or other is None:
        return None
    return f"Only the {first.role} role may {first.action}", f"only-{_slug(first.role)}-{_slug(first.action)}"[:60], [(other.id, first.action)]


def draft_scenarios(pack: Pack, model: Workflow) -> Scenarios:
    """Scenarios for a system with none: each step's expectation is what the kernel does on `model`."""
    drafts = [(f"{model.initial_state} to {state}", f"reach-{_slug(state)}", steps) for state, steps in _journeys(pack, model)]
    outsider = _outsider(pack, model)
    if outsider:
        drafts.append(outsider)
    seen: dict[str, int] = {}
    scenarios = []
    for title, sid, steps in drafts[:MAX_DRAFTS]:
        seen[sid] = seen.get(sid, 0) + 1  # two states can share a slug (Done_A, Done__A): ids must stay unique
        scenarios.append({"id": sid if seen[sid] == 1 else f"{sid}-{seen[sid]}", "title": title, "steps": record_steps(pack, model, None, steps)})
    return parse_scenarios({"id": pack.id, "scenarios": scenarios}, pack.id)


def scenarios_or_draft(pack: Pack, scenarios: Scenarios, base: Workflow) -> tuple[Scenarios, str]:
    """The pack's scenarios ("pack"), or a draft from the model in force when it has none ("drafted")."""
    return (scenarios, "pack") if scenarios.scenarios else (draft_scenarios(pack, base), "drafted")
