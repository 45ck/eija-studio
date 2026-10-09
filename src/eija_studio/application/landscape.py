"""The system landscape (ADR-0203): the workflows that make up one system, drawn as a UML component diagram, and the
places where their class diagrams disagree.

A workflow is a pack: one state machine moving one record class (`data.json`'s `record`). Nothing here is written by
hand for the landscape. Two workflows belong to one system when their class diagrams name the same class, the way two
UML packages that import one class are related. The workflow whose record a class is owns it; any other workflow that
names it uses that workflow. Each workflow provides its actions, each held by the roles its transitions name, and
publishes its notification effects (the outbox the built app writes). Roles with the same name in two workflows are one
actor.

The checks are the questions an architect asks first when two teams model the same thing: who owns this class, do the
copies agree, and do two workflows both claim to move the same record. Each finding names the classes, attributes and
workflows it is about. They are design checks over the documents; the built apps do not call each other, which the
result says.

Pure: takes parsed packs and data models, reads no files.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from eija_studio.domain.data import Attribute, DataModel, Entity
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack

FORMAT = "eija.landscape.v1"
LIMITS = ("Workflows are linked by the classes their class diagrams name; the built apps do not call each other yet, "
          "so a link is a design dependency the kernel does not run (cross-workflow messages are issue #93).")


def _shape(attribute: Attribute) -> str:
    """How an attribute reads on a class diagram, with what a copy must agree on."""
    text = f"{attribute.type}"
    if attribute.type == "text":
        text += f" max {attribute.max_length}"
    if attribute.type == "choice":
        text += " {" + ", ".join(attribute.choices) + "}"
    return text + (" required" if attribute.required else "")


def _held(model: Workflow) -> dict[str, set[str]]:
    """The roles each action's transitions give it to."""
    held: dict[str, set[str]] = {}
    for t in model.transitions:
        held.setdefault(t.action, set()).add(t.role)
    return held


def _emitted(model: Workflow) -> set[str]:
    """The effects a transition requires: the runtime writes only these, so a catalog entry no transition names is not
    published."""
    return {e for t in model.transitions for e in t.required_effects}


def _final(model: Workflow) -> list[str]:
    return sorted(s for s in model.states if not any(t.from_state == s for t in model.transitions))


def _workflow(pack: Pack, data: DataModel | None, model: Workflow) -> dict[str, Any]:
    held = _held(model)
    return {
        "id": pack.id, "name": pack.pack.name, "record": data.record if data else None,
        "states": len(model.states), "final_states": _final(model),
        "provides": [{"action": a.id, "roles": sorted(held.get(a.id, ()))} for a in pack.actions],
        "publishes": [{"effect": e.id, "recipient": e.recipient} for e in pack.effects.catalog
                      if e.kind == "notification" and e.id in _emitted(model)],
        "roles": sorted(r.id for r in pack.roles),
        "classes": sorted(e.name for e in data.entities) if data else [],
        "model": model.semantic_hash,
    }


def _connected(focus: str, classes: dict[str, set[str]]) -> list[str]:
    """The workflows reachable from `focus` through classes they share, in id order."""
    seen, todo = {focus}, [focus]
    while todo:
        here = todo.pop()
        for other, names in classes.items():
            if other not in seen and names & classes[here]:
                seen.add(other)
                todo.append(other)
    return sorted(seen)


def _differ(name: str, attribute: str, shapes: dict[str, str]) -> list[dict[str, Any]]:
    if len(set(shapes.values())) < 2:
        return []
    said = "; ".join(f"{shape} in {wf}" for wf, shape in sorted(shapes.items()))
    return [{"code": "CLASS_COPIES_DIFFER", "severity": "warning", "subject": [f"class:{name}", f"attribute:{name}.{attribute}"],
             "workflows": sorted(shapes), "message": f"{name}.{attribute} is declared two ways: {said}."}]


def _not_on_owner(name: str, attribute: str, shapes: dict[str, str], owner: str | None) -> list[dict[str, Any]]:
    if owner is None or owner in shapes:
        return []
    users = sorted(shapes)
    return [{"code": "ATTRIBUTE_NOT_ON_OWNER", "severity": "warning", "subject": [f"class:{name}", f"attribute:{name}.{attribute}"],
             "workflows": [owner, *users],
             "message": f"{name}.{attribute} is in {', '.join(users)} but not in {owner}, which owns {name}: add it there or drop it here."}]


def _compare(name: str, copies: dict[str, Entity], owner: str | None) -> list[dict[str, Any]]:
    """Attributes that two copies of one class declare differently, and attributes a user adds to an owned class."""
    found: list[dict[str, Any]] = []
    for attribute in sorted({a.name for e in copies.values() for a in e.attributes}):
        shapes = {wf: _shape(a) for wf, e in copies.items() for a in e.attributes if a.name == attribute}
        found += _differ(name, attribute, shapes) + _not_on_owner(name, attribute, shapes, owner)
    return found


def _class_findings(name: str, copies: dict[str, Entity], owners: list[str]) -> list[dict[str, Any]]:
    if len(owners) > 1:
        return [{"code": "RECORD_MOVED_TWICE", "severity": "warning", "subject": [f"class:{name}"], "workflows": owners,
                 "message": f"{name} is the record of {' and '.join(owners)}: two state machines move it, and nothing "
                            f"says which state it is really in."}]
    owner = owners[0] if owners else None
    found = _compare(name, copies, owner)
    if owner is None:
        found.insert(0, {"code": "CLASS_HAS_NO_OWNER", "severity": "consider", "subject": [f"class:{name}"], "workflows": sorted(copies),
                         "message": f"{name} is declared by {' and '.join(sorted(copies))}, and no workflow moves it. "
                                    f"Decide which one owns it (or give it a workflow of its own), so the others follow one definition."})
    return found


def _recipients(workflows: list[dict[str, Any]], actors: set[str]) -> list[dict[str, Any]]:
    lowered = {a.lower() for a in actors}
    return [{"code": "RECIPIENT_IS_NOT_AN_ACTOR", "severity": "consider", "subject": [f"workflow:{w['id']}", f"effect:{p['effect']}"],
             "workflows": [w["id"]], "message": f"{w['id']} notifies {p['recipient']!r} ({p['effect']}), which is no role in the system."}
            for w in workflows for p in w["publishes"] if p["recipient"] and p["recipient"].lower() not in lowered]


def _names(data: DataModel | None) -> set[str]:
    return {e.name for e in data.entities} if data else set()


def _owners(workflows: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Each record class and the workflows that move it."""
    owners: dict[str, list[str]] = {}
    for w in workflows:
        if w["record"]:
            owners.setdefault(w["record"], []).append(w["id"])
    return owners


def _copies(members: list[str], data: dict[str, DataModel | None]) -> dict[str, dict[str, Entity]]:
    """Each class two or more of the workflows name, with each workflow's copy of it."""
    copies: dict[str, dict[str, Entity]] = {}
    for wid in members:
        model = data[wid]
        for entity in model.entities if model else ():
            copies.setdefault(entity.name, {})[wid] = entity
    return {name: found for name, found in sorted(copies.items()) if len(found) > 1}


def _owner(owners: dict[str, list[str]], name: str) -> str | None:
    found = owners.get(name, [])
    return found[0] if len(found) == 1 else None


def _actors(workflows: list[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    """Roles of one name are one actor: per workflow, the actions it holds there."""
    actors: dict[str, dict[str, list[str]]] = {}
    for w in workflows:
        for role in w["roles"]:
            actors.setdefault(role, {})[w["id"]] = [p["action"] for p in w["provides"] if role in p["roles"]]
    return dict(sorted(actors.items()))


def _links(shared: dict[str, dict[str, Entity]], owners: dict[str, list[str]]) -> list[dict[str, str]]:
    """A workflow that names a class another workflow owns uses that workflow, through that class."""
    return [{"source": user, "target": owner, "class": name} for name, found in shared.items()
            if (owner := _owner(owners, name)) for user in sorted(found) if user != owner]


def _findings(shared: dict[str, dict[str, Entity]], owners: dict[str, list[str]], workflows: list[dict[str, Any]],
              actors: set[str]) -> list[dict[str, Any]]:
    found = [f for name, copies in shared.items() for f in _class_findings(name, copies, sorted(owners.get(name, [])))]
    return found + _recipients(workflows, actors)


def landscape(focus: str, systems: Iterable[tuple[Pack, DataModel | None, Workflow]], unreadable: Iterable[str] = ()) -> dict[str, Any]:
    """The system the workflow `focus` is part of: its workflows, actors, links and findings (ADR-0203).

    `systems` are the workflows that could be part of it (the packs beside the open one, each with its data model and the
    model shown for it), the open one included. Workflows that share no class with the open one's system are listed
    under `elsewhere`, so nothing is silently left out; `unreadable` names folders whose documents the kernel's checks
    refused. Pack ids must be unique; the caller reports a second folder with an id already read as unreadable."""
    by_id = {pack.id: (pack, data, model) for pack, data, model in systems}
    data = {wid: found[1] for wid, found in by_id.items()}
    members = _connected(focus, {wid: _names(d) for wid, d in data.items()})
    workflows = [_workflow(*by_id[wid]) for wid in members]
    owners, shared, actors = _owners(workflows), _copies(members, data), _actors(workflows)
    findings = _findings(shared, owners, workflows, set(actors))
    return {
        "format": FORMAT, "focus": focus, "workflows": workflows,
        "actors": [{"name": name, "workflows": held} for name, held in actors.items()],
        "links": _links(shared, owners),
        "classes": [{"name": name, "owner": _owner(owners, name), "in": sorted(found)} for name, found in shared.items()],
        "findings": findings,
        "counts": {s: len([f for f in findings if f["severity"] == s]) for s in ("warning", "consider")},
        "elsewhere": sorted(set(by_id) - set(members)),
        "unreadable": sorted(unreadable),
        "limits": [LIMITS],
    }
