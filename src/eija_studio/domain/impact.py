from __future__ import annotations
from collections import deque
from typing import Any
from .models import Transition, Workflow, canonical, guard_keys


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
    fields += ["conditions"] if guard_keys(old.conditions) != guard_keys(new.conditions) else []
    fields += ["after"] if old.after != new.after else []  # a time event (ADR-0237)
    return fields + (["then"] if set(old.then) != set(new.then) else [])  # steps on linked objects (ADR-0241)


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


START = ("initial_state", "initiators", "receives")  # what decides how a record starts (ADR-0231, ADR-0242)


def _lifecycles(model: Workflow) -> dict[str, str]:
    """Each linked object's lifecycle (ADR-0241) by link, as comparable text: its moves are a set."""
    return {o.link: canonical(o.model_dump(mode="json") | {"states": sorted(o.states), "moves": sorted(map(canonical, o.moves))})
            for o in model.objects}


def model_changes(before: Workflow, after: Workflow) -> list[str]:
    """What changed outside the transitions that changes what the kernel does: how a record starts, and the lifecycles
    of linked objects. States alone and composite states (drawing only, ADR-0240) change no step."""
    found = ["initial_state"] if before.initial_state != after.initial_state else []
    found += ["initiators"] if set(before.initiators) != set(after.initiators) else []
    found += ["receives"] if {canonical(r) for r in before.receives} != {canonical(r) for r in after.receives} else []
    return found + (["objects"] if _lifecycles(before) != _lifecycles(after) else [])


def _moving(before: Workflow, after: Workflow) -> set[str]:
    """The actions that move a linked object whose lifecycle changed: what they do now depends on it."""
    old, new = _lifecycles(before), _lifecycles(after)
    links = {link for link in old.keys() | new.keys() if old.get(link) != new.get(link)}
    return {t.action for t in (*before.transitions, *after.transitions) if any(s.link in links for s in t.then)}


def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]:
    """The ripple of a change. Changed transitions root it; so does a change to how a record starts or to a linked
    object's lifecycle (`model_changes`, present only when there is one, so other reports keep their bytes; ADR-0246)."""
    changed = sorted(_changed_actions(before, after) | _moving(before, after))
    graph = _chains(before, after)
    elements = model_changes(before, after)
    starts = ["record-start"] if set(elements) & set(START) else []
    for source, target in zip(["record-start", "review-packet"], ["review-packet", "local-decision"]) if starts else ():
        graph.setdefault(source, []).append(target)
    report = closure(graph, ["rule:" + x for x in changed] + starts)
    return {**report, "changed_actions": changed, "graph": graph,
            "envelope": "All dependencies encoded by this projection mapping; not every real-world consequence."} | (
        {"model_changes": elements} if elements else {})


def _changed_actions(before: Workflow, after: Workflow) -> set[str]:
    a, b = keyed(before, after)
    return {(a.get(k) or b[k]).action for k in set(a) | set(b) if k not in a or k not in b or changed_fields(a[k], b[k])}


def _chains(before: Workflow, after: Workflow) -> dict[str, list[str]]:
    """Each action's dependency chain, from its rule to the local decision."""
    graph: dict[str, list[str]] = {}
    for action in sorted({t.action for t in (*before.transitions, *after.transitions)}):
        chain = [f"rule:{action}", f"runtime:{action}", f"state-view:{action}", f"journey:{action}",
                 f"obligation:{action}", f"receipt:{action}", "review-packet", "local-decision"]
        for source, target in zip(chain, chain[1:]):
            graph.setdefault(source, []).append(target)
    return graph
