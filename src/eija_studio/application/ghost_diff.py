"""How a change looks on the state machine: both models on one canvas, with nothing hidden (ADR-0176).

`ghost_diff(before, after)` is a pure function of two `Workflow`s. It returns the union of their states and
transitions, each with a status, so a page can draw the model in force, the change, and every step between them on
one stable layout:

* `same`, `added` and `removed` by membership. A removed state or transition stays in the picture as a ghost, so a
  deleted path is seen rather than missed (LemonTree, for example, does not draw a deleted element at all).
* `changed`: the action keeps its endpoints and any other field changed. `fields` lists each one with its before and
  after, using `domain.impact.changed_fields`, the one definition of "changed" the ripple and the Mermaid diff share.
* `moved`: the action now joins other states. The new route is drawn, and the old one stays as a `was` ghost
  (key `was:<id>`), so a moved arrow is one change, not an unrelated delete and add.

Every change is also listed, in a fixed order, with a sentence and the cell it is about, so a reviewer can step
through them like hunks in a code review. What this does NOT establish: whether a change is right or what it does at
run time; the ripple (ADR-0158) and the kernel answer those.
"""
from __future__ import annotations

from typing import Any

from eija_studio.domain.impact import changed_fields
from eija_studio.domain.models import Transition, Workflow

FORMAT = "eija.ghost-diff.v1"
FIELD_TEXT = {"id": "id", "from_state": "from", "to_state": "to", "role": "role", "guards": "guards",
              "required_effects": "effects", "forbidden_effects": "never"}


def _shown(value: Any) -> Any:
    return sorted(value) if isinstance(value, tuple) else value


def _fields(old: Transition, new: Transition) -> list[dict[str, Any]]:
    return [{"field": f, "before": _shown(getattr(old, f)), "after": _shown(getattr(new, f))}
            for f in changed_fields(old, new) if f not in ("from_state", "to_state")]


def _edge(t: Transition, key: str, status: str, **extra: Any) -> dict[str, Any]:
    return {"key": key, "id": t.id, "action": t.action, "from_state": t.from_state, "to_state": t.to_state, "role": t.role,
            "guards": sorted(t.guards), "required_effects": sorted(t.required_effects),
            "forbidden_effects": sorted(t.forbidden_effects), "status": status, **extra}


def _field_text(f: dict[str, Any]) -> str:
    before, after = f["before"], f["after"]
    if isinstance(before, list):
        parts = [f"+{x}" for x in after if x not in before] + [f"-{x}" for x in before if x not in after]
        return f"{FIELD_TEXT[f['field']]} {' '.join(parts)}"
    return f"{FIELD_TEXT[f['field']]} {before} → {after}"


def _action_edges(old: Transition | None, new: Transition | None) -> list[dict[str, Any]]:
    if old is None:
        return [_edge(new, "t:" + new.id, "added")] if new is not None else []
    if new is None:
        return [_edge(old, "was:" + old.id, "removed")]
    fields = _fields(old, new)
    if (old.from_state, old.to_state) != (new.from_state, new.to_state):
        was = {"from_state": old.from_state, "to_state": old.to_state}
        return [_edge(new, "t:" + new.id, "moved", fields=fields, was=was), _edge(old, "was:" + old.id, "was", moved_to=new.id)]
    return [_edge(new, "t:" + new.id, "changed" if fields else "same", fields=fields)]


def _change(edge: dict[str, Any]) -> dict[str, Any] | None:
    a, route, status = edge["action"], f"{edge['from_state']} → {edge['to_state']}", edge["status"]
    details = "; ".join(_field_text(f) for f in edge.get("fields", []))
    if status in ("added", "removed"):
        verb = "Adds" if status == "added" else "Removes"
        return {"ref": edge["key"], "change": status, "text": f"{verb} {a} [{edge['role']}]: {route}"}
    if status == "moved":
        was = f"{edge['was']['from_state']} → {edge['was']['to_state']}"
        return {"ref": edge["key"], "change": "moved", "text": f"Moves {a}: now {route}, was {was}" + (f"; {details}" if details else ""),
                "was": "was:" + edge["id"]}
    if status == "changed":
        return {"ref": edge["key"], "change": "changed", "text": f"Changes {a} ({route}): {details}"}
    return None


def _states(before: Workflow, after: Workflow, edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every state of both models, by name, with its status, and whether a change touches it (an edge or the start)."""
    status = {s: "same" if s in after.states else "removed" for s in before.states}
    status |= {s: "added" for s in after.states if s not in before.states}
    touched = {s for e in edges if e["status"] != "same" for s in (e["from_state"], e["to_state"])}
    if before.initial_state != after.initial_state:
        touched |= {before.initial_state, after.initial_state}
    return [{"name": s, "status": status[s], "touched": s in touched} for s in sorted(status)]


def _changes(before: Workflow, after: Workflow, states: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The fixed reading order: the start, then states, then transitions by action."""
    changes: list[dict[str, Any]] = []
    if before.initial_state != after.initial_state:
        changes.append({"ref": "initial-edge", "change": "moved",
                        "text": f"Records now start in {after.initial_state}, not {before.initial_state}", "was": "was:initial-edge"})
    changes += [{"ref": "state:" + s["name"], "change": s["status"], "text": f"{'Adds' if s['status'] == 'added' else 'Removes'} state {s['name']}"}
                for s in states if s["status"] != "same"]
    changes += [c for e in sorted(edges, key=lambda e: (e["action"], e["key"])) if (c := _change(e))]
    return [{"n": i + 1, **c} for i, c in enumerate(changes)]


def ghost_diff(before: Workflow, after: Workflow) -> dict[str, Any]:
    """The union of two state machines, each element with its status, and the ordered list of changes."""
    a, b = {t.action: t for t in before.transitions}, {t.action: t for t in after.transitions}
    edges = sorted((e for action in set(a) | set(b) for e in _action_edges(a.get(action), b.get(action))),
                   key=lambda e: (e["from_state"], e["to_state"], e["action"], e["key"]))
    states = _states(before, after, edges)
    changes = _changes(before, after, states, edges)
    counts = {k: sum(c["change"] == k for c in changes) for k in ("added", "removed", "changed", "moved")}
    return {"format": FORMAT, "before": before.semantic_hash, "after": after.semantic_hash,
            "initial": {"before": before.initial_state, "after": after.initial_state},
            "states": states, "transitions": edges, "changes": changes, "counts": counts}
