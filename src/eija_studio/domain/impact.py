from __future__ import annotations
from collections import deque
from .models import Workflow


def closure(graph: dict[str, list[str]], roots: list[str], budget: int | None = None) -> dict:
    """Edges mean source affects target. Fixed point, cycle-safe; no silent depth cap."""
    if budget is not None and budget < 0:
        raise ValueError("Negative traversal budget")
    queue, visited = deque(sorted(set(roots))), set()
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


def model_impact(before: Workflow, after: Workflow) -> dict:
    a, b = {t.action: t for t in before.transitions}, {t.action: t for t in after.transitions}
    changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    graph: dict[str, list[str]] = {}
    for action in sorted(set(a) | set(b)):
        chain = [f"rule:{action}", f"runtime:{action}", f"state-view:{action}", f"journey:{action}",
                 f"obligation:{action}", f"receipt:{action}", "review-packet", "local-decision"]
        for source, target in zip(chain, chain[1:]):
            graph.setdefault(source, []).append(target)
    report = closure(graph, ["rule:" + x for x in changed])
    return {**report, "changed_actions": changed, "graph": graph,
            "envelope": "All dependencies encoded by this excursion projection mapping; not every real-world consequence."}
