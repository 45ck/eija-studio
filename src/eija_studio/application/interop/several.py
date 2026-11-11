"""Importing an action that leaves several states (ADR-0232): each arrow is matched to the transition leaving its
source, and a transition id is minted for each new one."""
from __future__ import annotations

import re
from typing import Any

from eija_studio.domain.models import Transition, Workflow

from .model import Edge

def _new_id(action: str, taken: set[str]) -> str:
    base = "TR-" + (re.sub(r"[^A-Z0-9_-]", "", action.upper()) or "X")
    ident, n = base[:64], 1
    while ident in taken:
        n += 1
        ident = f"{base[:60]}-{n}"
    taken.add(ident)
    return ident


def _single(model: Workflow, wanted: list[tuple[Edge, str, str]], action: str) -> bool:
    """Whether the action is one arrow in the file and at most one transition in the model: then a moved arrow is a
    retarget of that transition. Otherwise each arrow is matched to the transition leaving its source (ADR-0232)."""
    return sum(a == action for _, a, _ in wanted) == 1 and len(model.sources(action)) <= 1


def _several_steps(model: Workflow, edge: Edge, action: str, role: str, taken: set[str], shared: set[str]) -> list[dict[str, Any]]:
    """An arrow of an action that leaves several states: keep or add the transition from its source. The target and
    role every such transition shares are set once per action, through any one of them."""
    steps: list[dict[str, Any]] = []
    old = model.transition_for(action)
    if old is not None and action not in shared:
        shared.add(action)
        if old.to_state != edge.target:
            steps.append({"kind": "retarget_transition", "transition": old.id, "end": "target", "state": edge.target})
        if old.role != role:
            steps.append({"kind": "set_role", "transition": old.id, "role": role})
    if edge.source not in model.sources(action):
        steps.append({"kind": "add_transition", "id": _new_id(action, taken), "action": action,
                      "from_state": edge.source, "to_state": edge.target, "role": role})
    return steps


def _source_dropped(model: Workflow, wanted: list[tuple[Edge, str, str]], t: Transition) -> bool:
    """A transition of an action matched arrow by arrow (ADR-0232) whose source no arrow of that action leaves now."""
    sources = {edge.source for edge, action, _ in wanted if action == t.action}
    return bool(sources) and not _single(model, wanted, t.action) and t.from_state not in sources


def _gone_transitions(model: Workflow, wanted: list[tuple[Edge, str, str]], named: set[str]) -> list[tuple[dict[str, Any], str]]:
    return [({"kind": "remove_transition", "transition": t.id}, f"transition {t.action}")
            for t in model.transitions if t.action not in named or _source_dropped(model, wanted, t)]
