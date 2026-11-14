"""Composite states form a tree over a workflow's states (issue #93 item 3, ADR-0240).

Kept apart from `models.py` so the contracts module stays small; `Workflow` asks `is_tree` when it validates. Pure.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class Group(Protocol):
    """What the tree check reads of a composite state (`models.Composite`, frozen, so read-only here)."""
    @property
    def name(self) -> str: ...
    @property
    def states(self) -> tuple[str, ...]: ...
    @property
    def initial(self) -> str: ...


def is_tree(states: tuple[str, ...], composites: Sequence[Group]) -> bool:
    """Composite names are new and unique, each holds known, distinct children including its initial one, each state or
    composite has at most one parent, and no composite holds itself. True when there are none."""
    names = [c.name for c in composites]
    return (_distinct(names) and not set(names) & set(states) and _known_children(states, composites)
            and _acyclic({child: c.name for c in composites for child in c.states}))


def _distinct(items: list[str]) -> bool:
    return len(set(items)) == len(items)


def _known_children(states: tuple[str, ...], composites: Sequence[Group]) -> bool:
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
