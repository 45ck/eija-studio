"""Linked objects (issue #93 item 4, ADR-0241): the states a record's linked objects are in, as the checkers try them.

A record links to objects of other classes through reference fields (ADR-0235). A workflow may give such an object a
small lifecycle (`Workflow.objects`), and a transition may move it (`Transition.then`). Other records can link to the
same object, so any state of its lifecycle can be the one a step meets. The checkers therefore try a step with its
objects in every state (`combinations`), and the ordinary cases of the built app's oracle use the states a run of this
record alone reaches (`along`).
"""
from __future__ import annotations

from collections import deque
from itertools import product

from .models import Transition, Workflow


def combinations(model: Workflow, transition: Transition | None) -> list[dict[str, str]]:
    """Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves
    none. A lifecycle has at most 8 states and a transition moves at most 2 objects, so this is at most 64."""
    lifecycles = [model.lifecycle(s.link) for s in (transition.then if transition is not None else ())]
    present = [o for o in lifecycles if o is not None]
    return [dict(zip([o.link for o in present], states, strict=True)) for states in product(*(o.states for o in present))]


def along(model: Workflow) -> dict[str, dict[str, str]]:
    """For each state a record can reach, the states its linked objects are in when only this record moves them, from
    every object in its initial state: the first such combination found breadth-first. Empty without linked objects."""
    if not model.objects:
        return {}
    start = (model.initial_state, tuple(sorted((o.link, o.initial) for o in model.objects)))
    seen, queue = {start[0]: dict(start[1])}, deque([start])
    visited = {start}
    while queue:
        state, objects = queue.popleft()
        for t in (t for t in model.transitions if t.from_state == state):
            following = _moved(model, t, dict(objects))
            if following is None:
                continue
            node = (t.to_state, tuple(sorted(following.items())))
            if node not in visited:
                visited.add(node)
                seen.setdefault(t.to_state, following)
                queue.append(node)
    return seen


def _moved(model: Workflow, transition: Transition, objects: dict[str, str]) -> dict[str, str] | None:
    """The objects' states after `transition`, or None when one of its moves is not possible from their states."""
    after = dict(objects)
    for step in transition.then:
        lifecycle = model.lifecycle(step.link)
        target = lifecycle.move(step.event, after.get(step.link)) if lifecycle is not None else None
        if target is None:
            return None
        after[step.link] = target
    return after


def admitting(model: Workflow, transition: Transition | None) -> dict[str, str] | None:
    """The first combination of states (as `combinations` orders them) from which `transition` can move every object it
    names; `{}` when it moves none, None when no combination can."""
    if transition is None:
        return {}
    return next((objects for objects in combinations(model, transition) if _moved(model, transition, objects) is not None), None)
