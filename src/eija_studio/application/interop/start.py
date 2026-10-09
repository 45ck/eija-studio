"""Start a new system from a UML file (ADR-0190 with the new-system flow of ADR-0185).

Importing into an existing system compares the file with the model in force. A new system has no model yet, so the
file's state machine is the model: its actions and roles become the pack's declarations, written through the same
sketch the new-system form uses (`From -> To : Action [Role]`), and its guards and effects are kept where PlayIDE's
vocabulary can hold them. The class model becomes `data.json`. The kernel's pack check and protected policy judge the
result before anything is created; the caller creates it.

As with any import, nothing is dropped silently. The report lists every element as read (`mapped`), kept or filled
in by PlayIDE (`defaulted`), derived, or not imported with the reason (`unmapped`). What a UML file never carries
(laws, meanings, fixtures beyond one user per role) starts empty or default, as in a sketch. A role's kind (ADR-0210)
comes from its actor's stereotype on the use case diagram, «agent», «timer» or «system», else it is a person.
"""
from __future__ import annotations

from typing import Any

import re

from eija_studio.application.new_system import NAME, sketch_documents
from eija_studio.domain.data import parse_data
from eija_studio.domain.models import BASE_GUARDS, DomainError
from eija_studio.domain.pack import PackError, parse_pack
from eija_studio.domain.policy import check_policy

from .mapping import ImportReport, import_class_model
from .model import Edge, Label, Parsed, kind_label, parse_label

FORMAT = "eija.uml-start.v1"
DEFAULT_ROLE = "User"
_KINDS = {"audit": "audit", "notification": "notification"}


def _refusal(edge: Edge, label: Label, seen: dict[str, str]) -> tuple[str, str] | None:
    """(element, reason) when a new system cannot take this transition."""
    ends = f"{edge.source} -> {edge.target}"
    if not label.trigger:
        return ends, "the transition has no trigger; PlayIDE names every transition by its action"
    if label.trigger in seen:
        return (f"transition {label.trigger} ({ends})",
                f"action {label.trigger} already labels {seen[label.trigger]}; each action labels one transition")
    odd = [x for x in (edge.source, edge.target, label.trigger, label.role or DEFAULT_ROLE) if not re.fullmatch(NAME, x)]
    if odd:
        return (f"transition {label.trigger} ({ends})",
                f"{odd[0]!r} is not a name the built app's code can use (letters, digits and _, starting with a letter)")
    return None


def _kept_edges(parsed: Parsed, report: ImportReport) -> list[tuple[Edge, Label, str]]:
    """The transitions a new system can take: one per action, each named by its trigger and done by one role."""
    kept: list[tuple[Edge, Label, str]] = []
    seen: dict[str, str] = {}
    for edge in parsed.edges:
        label = parse_label(edge.label)
        refused = _refusal(edge, label, seen)
        if refused is not None:
            report.add("unmapped", edge.where, *refused)
            continue
        for term in label.unread:
            report.add("unmapped", edge.where, f"{label.trigger}: guard {term!r}",
                       "not in PlayIDE's guard vocabulary (role, assigned); value guards are planned (issue #93)")
        if label.role is None:
            report.add("defaulted", edge.where, f"{label.trigger}: role", f"the file names no role; used {DEFAULT_ROLE}")
        seen[label.trigger] = f"{edge.source} -> {edge.target}"
        kept.append((edge, label, label.role or DEFAULT_ROLE))
    return kept


def _effect(text: str, role: str, edge: Edge, trigger: str, report: ImportReport) -> dict[str, Any] | None:
    kind = _KINDS.get(text.split(":", 1)[0].strip().lower()) if ":" in text else None
    if kind is None:
        report.add("unmapped", edge.where, f"{trigger}: effect {text!r}",
                   "an effect is Audit:Name or Notification:Name in PlayIDE's effect vocabulary")
        return None
    if kind == "notification":
        report.add("defaulted", edge.where, f"{trigger}: {text} recipient",
                   f"no UML file carries a notification's recipient; used {role.lower()}")
        return {"id": text, "kind": kind, "recipient": role.lower()}
    return {"id": text, "kind": kind}


def _effects(edge: Edge, label: Label, role: str, report: ImportReport) -> list[dict[str, Any]]:
    """The action's effects as the file lists them: at most one audit and one notification, as the runtime records."""
    if not label.effects:
        report.add("defaulted", edge.where, f"{label.trigger}: effects",
                   f"the file lists none; PlayIDE records one audit entry, Audit:{label.trigger}")
        return [{"id": f"Audit:{label.trigger}", "kind": "audit"}]
    found: list[dict[str, Any]] = []
    for text in label.effects:
        effect = _effect(text, role, edge, label.trigger, report)
        if effect is not None and any(f["kind"] == effect["kind"] for f in found):
            report.add("unmapped", edge.where, f"{label.trigger}: effect {text!r}",
                       f"the runtime records at most one {effect['kind']} effect per action")
        elif effect is not None:
            found.append(effect)
    return found or _effects(edge, Label(label.trigger, label.role, label.assigned, None, ()), role, report)


def _declare(pack: dict[str, Any], kept: list[tuple[Edge, Label, str]], report: ImportReport) -> None:
    """The file's guards and effects, declared per action and repeated on its transition, as the policy requires."""
    actions = {a["id"]: a for a in pack["actions"]}
    transitions = {t["action"]: t for t in pack["model"]["transitions"]}
    catalog: dict[str, dict[str, Any]] = {}
    for edge, label, role in kept:
        effects = _effects(edge, label, role, report)
        catalog |= {e["id"]: e for e in effects if e["id"] not in catalog}
        guards = list(BASE_GUARDS) + (["actor_assigned"] if label.assigned else [])
        for declared in (actions[label.trigger], transitions[label.trigger]):
            declared["guards"], declared["required_effects"] = guards, [e["id"] for e in effects]
        report.add("mapped", edge.where, f"transition {label.trigger} ({edge.source} -> {edge.target}, {role})")
    pack["effects"]["catalog"] = list(catalog.values())


def _states(pack: dict[str, Any], parsed: Parsed, report: ImportReport) -> None:
    states = pack["model"]["states"]
    for name in parsed.states or []:
        if name in states:
            report.add("mapped", "state machine", f"state {name}")
        else:
            report.add("unmapped", "state machine", f"state {name}",
                       "no imported transition reaches or leaves it; a new system's states come from its transitions")
    if parsed.initial in states:
        pack["model"]["initial_state"] = parsed.initial
    else:
        report.add("defaulted", "state machine", "initial state",
                   f"the file marks {'none' if parsed.initial is None else 'one with no imported transition'}; "
                   f"used {pack['model']['initial_state']}, the source of the first transition")


def _kinds(pack: dict[str, Any], parsed: Parsed, report: ImportReport) -> None:
    """Each role's kind from its actor on the use case diagram (ADR-0210): «agent», «timer», «system», else a person."""
    if parsed.actors is None:
        report.add("defaulted", "use case diagram", "role kinds", "the file draws no actors; every role is a person")
        return
    roles = {r["id"]: r for r in pack["roles"]}
    for name, (kind, where) in parsed.actors.items():
        if name not in roles:
            report.add("unmapped", where, f"actor {name}",
                       f"{name!r} is not a name the built app's code can use (letters, digits and _, starting with a letter)")
            continue
        if kind != "human":
            roles[name]["kind"] = kind
        report.add("mapped", where, f"actor {name} ({kind_label(kind)})")
    for name in (r for r in roles if r not in parsed.actors):
        report.add("defaulted", "use case diagram", f"{name}: kind", "the file draws no actor for it; a person")


def _record(parsed: Parsed, record: str) -> str:
    classes = parsed.classes or []
    return next((k.name for k in classes if k.record), None) or (classes[0].name if classes else record)


def _class_model(documents: dict[str, Any], parsed: Parsed, record: str, report: ImportReport) -> None:
    pack = parse_pack(documents["pack.json"])
    if parsed.classes is None:
        report.add("defaulted", "class model", "class model",
                   f"the file has none; the record class is {record}, with one attribute, title")
        return
    found = import_class_model(pack, None, parsed, report)
    if found.get("candidate") is not None:
        documents["data.json"] = found["candidate"]
    else:
        report.add("defaulted", "class model", "class model",
                   f"it could not be imported; the record class is {record}, with one attribute, title")


def _sketch(parsed: Parsed, kept: list[tuple[Edge, Label, str]]) -> str:
    """The kept transitions as sketch lines; actors that perform nothing yet are still declared, as `roles:`."""
    sketch = "\n".join(f"{edge.source} -> {edge.target} : {label.trigger} [{role}]" for edge, label, role in kept)
    idle = [a for a in parsed.actors or {} if a not in {role for _, _, role in kept} and re.fullmatch(NAME, a)]
    return sketch + ("\nroles: " + ", ".join(idle) if idle else "")


def _judge(documents: dict[str, Any]) -> None:
    """The kernel's pack and data checks and the protected policy; `PackError` with what they refuse."""
    checked = parse_pack(documents["pack.json"])
    try:
        parse_data(documents["data.json"], checked.id)
    except DomainError as error:
        raise PackError([error.message]) from None
    refused = check_policy(checked.model, checked)
    if refused:
        raise PackError([f"the protected policy refuses it: {code}" for code in refused])


def start_documents(fmt: str, parsed: Parsed, name: str, pack_id: str, record: str = "Record") -> tuple[dict[str, Any], dict[str, Any]]:
    """The new system's documents and the import report; `PackError` when the kernel refuses them."""
    if not parsed.edges:
        raise PackError(["the file has no UML state machine with transitions; a new system starts from one"])
    report = ImportReport(parsed.skipped, parsed.derived)
    kept = _kept_edges(parsed, report)
    if not kept:
        raise PackError(["no transition in the file could be imported: " + "; ".join(u["reason"] for u in report.unmapped[:3])])
    record = _record(parsed, record)
    documents = sketch_documents(name, record, _sketch(parsed, kept), pack_id)
    pack = documents["pack.json"]
    _declare(pack, kept, report)
    _states(pack, parsed, report)
    _kinds(pack, parsed, report)
    pack["pack"]["description"] = f"Started in PlayIDE from a UML file ({fmt}): one {record} moving through {len(pack['model']['states'])} states."
    _class_model(documents, parsed, record, report)
    _judge(documents)
    return documents, {"format": FORMAT, "from": fmt, "status": "PARTIAL" if report.unmapped else "CLEAN",
                       "mapped": report.mapped, "defaulted": report.defaulted, "unmapped": report.unmapped,
                       "derived": report.derived}
