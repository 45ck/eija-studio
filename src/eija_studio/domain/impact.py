from __future__ import annotations
from collections import deque
from typing import Any
from .models import Transition, Workflow


def closure(graph: dict[str, list[str]], roots: list[str], budget: int | None = None) -> dict[str, Any]:
    """Edges mean source affects target. Fixed point, cycle-safe; no silent depth cap."""
    if budget is not None and budget < 0:
        raise ValueError("Negative traversal budget")
    queue: deque[str] = deque(sorted(set(roots)))
    visited: set[str] = set()
    while queue:
        if budget is not None and len(visited) >= budget:
            frontier = sorted(set(queue) - visited)
            return {"affected": sorted(visited), "complete": not frontier, "frontier": frontier}
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        queue.extend(n for n in sorted(graph.get(node, [])) if n not in visited)
    return {"affected": sorted(visited), "complete": True, "frontier": []}


def changed_fields(old: Transition, new: Transition) -> list[str]:
    """Semantic differences of one action's transition. Guards and effects are sets (their order is non-semantic,
    as in `Workflow.semantic_hash`), so shuffling them is not a change. The single definition of "changed"
    shared by the ripple and the diagram diff."""
    fields = [name for name in ("id", "from_state", "to_state", "role") if getattr(old, name) != getattr(new, name)]
    fields += [name for name in ("guards", "required_effects", "forbidden_effects")
               if set(getattr(old, name)) != set(getattr(new, name))]
    return fields


def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]:
    a, b = {t.action: t for t in before.transitions}, {t.action: t for t in after.transitions}
    changed = sorted(k for k in set(a) | set(b) if k not in a or k not in b or changed_fields(a[k], b[k]))
    graph: dict[str, list[str]] = {}
    for action in sorted(set(a) | set(b)):
        chain = [f"rule:{action}", f"runtime:{action}", f"state-view:{action}", f"journey:{action}",
                 f"obligation:{action}", f"receipt:{action}", "review-packet", "local-decision"]
        for source, target in zip(chain, chain[1:]):
            graph.setdefault(source, []).append(target)
    report = closure(graph, ["rule:" + x for x in changed])
    return {**report, "changed_actions": changed, "graph": graph,
            "envelope": "All dependencies encoded by this projection mapping; not every real-world consequence."}
