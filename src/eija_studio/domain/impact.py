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
    fields += [name for name in ("guards", "required_effects", "forbidden_effects", "conditions")
               if set(getattr(old, name)) != set(getattr(new, name))]
    return fields


def keyed(before: Workflow, after: Workflow) -> tuple[dict[str, Transition], dict[str, Transition]]:
    """Both models' transitions keyed for comparison. By action while it labels at most one transition in each model,
    so a moved source reads as a change of that transition; by action and source state ("Cancel from Paused") once it
    labels several in either (ADR-0232)."""
    olds, news = _labelled(before), _labelled(after)
    a: dict[str, Transition] = {}
    b: dict[str, Transition] = {}
    for action in olds.keys() | news.keys():
        single = len(olds.get(action, ())) <= 1 and len(news.get(action, ())) <= 1
        a |= {(action if single else f"{action} from {t.from_state}"): t for t in olds.get(action, ())}
        b |= {(action if single else f"{action} from {t.from_state}"): t for t in news.get(action, ())}
    return a, b


def _labelled(model: Workflow) -> dict[str, list[Transition]]:
    found: dict[str, list[Transition]] = {}
    for t in model.transitions:
        found.setdefault(t.action, []).append(t)
    return found


def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]:
    a, b = keyed(before, after)
    changed = sorted({(a.get(k) or b[k]).action for k in set(a) | set(b) if k not in a or k not in b or changed_fields(a[k], b[k])})
    graph: dict[str, list[str]] = {}
    for action in sorted({t.action for t in (*before.transitions, *after.transitions)}):
        chain = [f"rule:{action}", f"runtime:{action}", f"state-view:{action}", f"journey:{action}",
                 f"obligation:{action}", f"receipt:{action}", "review-packet", "local-decision"]
        for source, target in zip(chain, chain[1:]):
            graph.setdefault(source, []).append(target)
    report = closure(graph, ["rule:" + x for x in changed])
    return {**report, "changed_actions": changed, "graph": graph,
            "envelope": "All dependencies encoded by this projection mapping; not every real-world consequence."}
