"""Import: what a UML file says, turned into typed edits and judged by the kernel (ADR-0190).

A file never replaces the model. Its state machine is compared with the model in force and the difference becomes
the same typed semantic transactions a drawn edit or a chat plan uses (`domain.transactions`): add a state, add a
transition for a declared action, retarget an end, change a role, remove what the file no longer has. Each edit is
applied by the kernel with the pack's declared guards and effects, so a file cannot choose them, and the result is
judged by the protected policy and the laws, exactly as any other candidate. Its class model is validated as a
`data.json` by the same contract the built app uses.

Nothing is dropped silently. Every element lands in one of three lists:

* `mapped`: read and kept;
* `defaulted`: read, but PlayIDE kept or filled something the file did not say (with what and why);
* `unmapped`: not imported, with the reason (outside the vocabulary, undeclared in the pack, or refused by the kernel).

Pure: nothing is written. The caller decides whether to keep the candidate.
"""
from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

from eija_studio.domain.data import ATTRIBUTE_NAME, NAME, DataModel
from eija_studio.domain.models import DomainError, Transition, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_structural_all, check_policy
from eija_studio.domain.transactions import Transaction, parse_transaction
from eija_studio.application.law_proof import prove_laws

from .model import (DEFAULT_MAX_LENGTH, MULTIPLICITIES, READ_TYPES, WIDENED, Attr, Edge, Klass, Label, Link, Parsed, kind_label,
                    parse_label)

FORMAT = "eija.uml-import.v1"


class ImportReport:
    def __init__(self, skipped: list[dict[str, str]], derived: list[dict[str, str]]):
        self.derived = [dict(d) for d in derived]
        self.mapped: list[dict[str, str]] = []
        self.defaulted: list[dict[str, str]] = []
        self.unmapped: list[dict[str, str]] = [dict(s) for s in skipped]

    def add(self, bucket: str, where: str, element: str, reason: str = "") -> None:
        entry = {"where": where, "element": element} | ({"reason": reason} if reason else {})
        getattr(self, bucket).append(entry)


# ---- state machine ------------------------------------------------------------------------------------------

def _role(label: Label, edge: Edge, current: Transition | None, report: ImportReport) -> str | None:
    if label.role is not None:
        return label.role
    if current is not None:
        report.add("defaulted", edge.where, f"{label.trigger}: role", f"the file names no role; kept {current.role}")
        return current.role
    report.add("unmapped", edge.where, f"transition {label.trigger}", "the guard names no role (write [role = <a declared role>])")
    return None


def _declared_checks(pack: Pack, label: Label, edge: Edge, report: ImportReport) -> None:
    """Guards and effects are declared per action by the pack. Say so where the file disagrees."""
    spec = pack.action(label.trigger)
    if spec is None:
        return
    if label.assigned is not None and label.assigned != ("actor_assigned" in spec.guards):
        report.add("defaulted", edge.where, f"{label.trigger}: guard",
                   f"the pack declares {'an assigned' if 'actor_assigned' in spec.guards else 'any'} actor for "
                   f"{label.trigger}; kept the pack's guards")
    if label.effects is not None and set(label.effects) != set(spec.required_effects):
        report.add("defaulted", edge.where, f"{label.trigger}: effects",
                   f"the pack declares {', '.join(spec.required_effects) or 'no effects'}; kept the pack's")
    for term in label.unread:
        report.add("unmapped", edge.where, f"{label.trigger}: guard {term!r}",
                   "not in PlayIDE's guard vocabulary (role, assigned); value guards are planned (issue #93)")


def _edge_action(pack: Pack, edge: Edge, current: dict[str, Transition], seen: set[str],
                 report: ImportReport) -> tuple[Label, str] | None:
    label = parse_label(edge.label)
    if not label.trigger:
        report.add("unmapped", edge.where, f"{edge.source} -> {edge.target}",
                   "a transition needs a trigger: the action that fires it")
        return None
    if label.trigger in seen:
        report.add("unmapped", edge.where, f"transition {label.trigger}",
                   "an action is one transition in PlayIDE; this is a second one")
        return None
    seen.add(label.trigger)
    if pack.action(label.trigger) is None:
        report.add("unmapped", edge.where, f"transition {label.trigger}",
                   f"action {label.trigger} is not declared by pack {pack.id}; its guards and effects must be declared first")
        return None
    role = _role(label, edge, current.get(label.trigger), report)
    if role is None:
        return None
    if role not in {r.id for r in pack.roles}:
        report.add("unmapped", edge.where, f"transition {label.trigger}", f"role {role} is not declared by pack {pack.id}")
        return None
    _declared_checks(pack, label, edge, report)
    return label, role


def _new_id(action: str, taken: set[str]) -> str:
    base = "TR-" + (re.sub(r"[^A-Z0-9_-]", "", action.upper()) or "X")
    ident, n = base[:64], 1
    while ident in taken:
        n += 1
        ident = f"{base[:60]}-{n}"
    taken.add(ident)
    return ident


def _edit_steps(model: Workflow, wanted: list[tuple[Edge, str, str]], taken: set[str]) -> list[dict[str, Any]]:
    by_action = {t.action: t for t in model.transitions}
    steps: list[dict[str, Any]] = []
    for edge, action, role in wanted:
        old = by_action.get(action)
        if old is None:
            steps.append({"kind": "add_transition", "id": _new_id(action, taken), "action": action,
                          "from_state": edge.source, "to_state": edge.target, "role": role})
            continue
        if old.from_state != edge.source:
            steps.append({"kind": "retarget_transition", "transition": old.id, "end": "source", "state": edge.source})
        if old.to_state != edge.target:
            steps.append({"kind": "retarget_transition", "transition": old.id, "end": "target", "state": edge.target})
        if old.role != role:
            steps.append({"kind": "set_role", "transition": old.id, "role": role})
    return steps


def _partial(parsed: Parsed, wanted: list[tuple[Edge, str, str]]) -> int:
    """How many transitions or composite states of the file's state machine were not read."""
    return len(parsed.edges) - len(wanted) + sum(1 for s in parsed.skipped if s["element"].startswith("composite state"))


def _removals(model: Workflow, parsed: Parsed, wanted: list[tuple[Edge, str, str]], named: set[str],
              report: ImportReport) -> list[dict[str, Any]]:
    """What the file no longer has, removed only when its whole state machine was read (issue #165).

    A transition the file renamed to an undeclared action, or drew in a way PlayIDE cannot read, is missing from what
    was read; removing it would offer a plan that breaks the model. So a partial read removes nothing and says so."""
    removals = [({"kind": "remove_transition", "transition": t.id}, f"transition {t.action}")
                for t in model.transitions if t.action not in named]
    removals += [({"kind": "remove_state", "state": s}, f"state {s}") for s in model.states if s not in (parsed.states or [])]
    missed = _partial(parsed, wanted)
    if not missed:
        return [step for step, _ in removals]
    why = (f"kept: {missed} part{'s' if missed > 1 else ''} of the file's state machine could not be read, so the import "
           "removes nothing. Fix the file and import it again, or remove it on the diagram")
    for _, element in removals:
        report.add("unmapped", "state machine", f"removing {element}", why)
    return []


def _steps(model: Workflow, parsed: Parsed, wanted: list[tuple[Edge, str, str]], named: set[str],
           report: ImportReport) -> list[dict[str, Any]]:
    """The difference as typed edits: add states, set the initial state, add and change transitions, then remove."""
    states = parsed.states or []
    steps: list[dict[str, Any]] = [{"kind": "add_state", "state": s} for s in states if s not in model.states]
    if parsed.initial not in (None, model.initial_state):
        steps.append({"kind": "set_initial", "state": parsed.initial})
    steps += _edit_steps(model, wanted, {t.id for t in model.transitions})
    return steps + _removals(model, parsed, wanted, named, report)


def _apply(pack: Pack, model: Workflow, steps: list[dict[str, Any]],
           report: ImportReport) -> tuple[Workflow, list[dict[str, Any]]]:
    """Each edit applied by the kernel in turn; a refused edit is reported and the rest still tried."""
    applied: list[dict[str, Any]] = []
    for step in steps:
        try:
            tx: Transaction = parse_transaction(step)
            model = apply_structural_all(model, [tx], pack)
        except DomainError as error:
            report.add("unmapped", "kernel", _describe(step), f"{error.code}: {error.message}")
            continue
        applied.append(step)
    return model, applied


def _describe(step: dict[str, Any]) -> str:
    return " ".join(f"{k}={v}" for k, v in step.items())


def _state_names(parsed: Parsed, report: ImportReport) -> bool:
    for name in parsed.states or []:
        if not 1 <= len(name) <= 60:
            report.add("unmapped", "state machine", f"state {name[:40]!r}", "a state name has 1 to 60 characters")
            return False
    return True


def _record_states(parsed: Parsed, report: ImportReport) -> None:
    for name in parsed.states or []:
        report.add("mapped", "state machine", f"state {name}")


def _wanted(pack: Pack, model: Workflow, parsed: Parsed, seen: set[str], report: ImportReport) -> list[tuple[Edge, str, str]]:
    """The file's transitions PlayIDE can read, as (edge, action, role); `seen` collects the actions named."""
    current = {t.action: t for t in model.transitions}
    wanted: list[tuple[Edge, str, str]] = []
    for edge in parsed.edges:
        found = _edge_action(pack, edge, current, seen, report)
        if found is not None:
            wanted.append((edge, found[0].trigger, found[1]))
    return wanted


def _record_transitions(candidate: Workflow, wanted: list[tuple[Edge, str, str]], report: ImportReport) -> None:
    """A transition is read when the kernel's candidate has it exactly as the file draws it."""
    drawn = {t.action: (t.from_state, t.to_state, t.role) for t in candidate.transitions}
    for edge, action, role in wanted:
        if drawn.get(action) == (edge.source, edge.target, role):
            report.add("mapped", edge.where, f"transition {action} ({edge.source} -> {edge.target}, {role})")


def import_state_machine(pack: Pack, model: Workflow, parsed: Parsed, report: ImportReport) -> dict[str, Any]:
    if parsed.states is None:
        return {"found": False}
    if not parsed.states or not _state_names(parsed, report):
        report.add("unmapped", "state machine", "state machine", "it has no usable states")
        return {"found": True, "changed": False, "candidate": None}
    if parsed.initial is None:
        report.add("defaulted", "state machine", "initial state", f"the file marks none; kept {model.initial_state}")
    seen: set[str] = set()
    wanted = _wanted(pack, model, parsed, seen, report)
    candidate, applied = _apply(pack, model, _steps(model, parsed, wanted, seen, report), report)
    _record_states(parsed, report)
    _record_transitions(candidate, wanted, report)
    refused = check_policy(candidate, pack)
    laws = prove_laws(pack, candidate)["status"] if not refused else "NOT_RUN"
    return {"found": True, "changed": candidate.semantic_hash != model.semantic_hash, "transactions": applied,
            "candidate": candidate.model_dump(mode="json"), "policy": refused, "laws": laws}


# ---- class model --------------------------------------------------------------------------------------------

def _attribute_type(attr: Attr, enums: dict[str, tuple[str, ...]], where: str, element: str,
                    report: ImportReport) -> dict[str, Any] | None:
    if attr.type in enums:
        return {"type": "choice", "choices": list(enums[attr.type])}
    read = READ_TYPES.get(attr.type.lower())
    if read is None:
        report.add("unmapped", where, element, f"type {attr.type or '(none)'} is not a PlayIDE attribute type "
                   "(String, Real, Boolean, Date or an enumeration); a class-typed attribute is an association")
        return None
    if attr.type.lower() in WIDENED:
        report.add("defaulted", where, element, f"{attr.type} is read as {read}")
    return {"type": read}


def _attribute(klass: Klass, attr: Attr, enums: dict[str, tuple[str, ...]], report: ImportReport) -> dict[str, Any] | None:
    element, where = f"{klass.name}.{attr.name}", attr.where or klass.where
    if attr.upper not in ("1", "0..1", ""):
        report.add("unmapped", where, element, f"multiplicity [{attr.lower}..{attr.upper}]: a collection of values is not "
                   "in the data vocabulary; draw an association to a class instead")
        return None
    typed = _attribute_type(attr, enums, where, element, report)
    if typed is None:
        return None
    out: dict[str, Any] = {"name": attr.name, "required": attr.lower >= 1} | typed
    if attr.max_length is not None and out["type"] == "text":
        out["max_length"] = attr.max_length
    elif out["type"] == "text":
        report.add("defaulted", where, element, f"no maximum length; PlayIDE uses {DEFAULT_MAX_LENGTH}")
    return out | ({"description": attr.description[:300]} if attr.description else {})


def _entity(klass: Klass, enums: dict[str, tuple[str, ...]], report: ImportReport) -> dict[str, Any] | None:
    if not re.fullmatch(NAME, klass.name):
        report.add("unmapped", klass.where, f"class {klass.name}", "a class name is UpperCamelCase letters and digits")
        return None
    attributes = []
    for attr in klass.attributes:
        if not re.fullmatch(ATTRIBUTE_NAME, attr.name):
            report.add("unmapped", attr.where or klass.where, f"{klass.name}.{attr.name}", "an attribute name is lowerCamelCase")
            continue
        found = _attribute(klass, attr, enums, report)
        if found is not None:
            attributes.append(found)
            report.add("mapped", attr.where or klass.where, f"{klass.name}.{attr.name}")
    report.add("mapped", klass.where, f"class {klass.name}")
    return {"name": klass.name, "attributes": attributes} | ({"description": klass.description[:300]} if klass.description else {})


def _link(link: Link, names: set[str], report: ImportReport) -> dict[str, Any] | None:
    element = f"{link.kind} {link.source} -> {link.target}"
    if link.source not in names or link.target not in names:
        report.add("unmapped", link.where, element, "it joins a class that was not imported")
        return None
    ends = [MULTIPLICITIES.get(m.replace(" ", "")) for m in (link.source_multiplicity, link.target_multiplicity)]
    if None in ends:
        report.add("unmapped", link.where, element, f"multiplicity {link.source_multiplicity} / {link.target_multiplicity}: "
                   "PlayIDE ends are 0..1, 1, 0..* or 1..*")
        return None
    report.add("mapped", link.where, element)
    return {"source": link.source, "target": link.target, "kind": link.kind, "role": link.role[:40],
            "source_multiplicity": ends[0], "target_multiplicity": ends[1]}


def _record(parsed: Parsed, names: list[str], data: DataModel | None, report: ImportReport) -> str:
    marked = [k.name for k in parsed.classes or [] if k.record and k.name in names]
    if marked:
        return marked[0]
    if data is not None and data.record in names:
        report.add("defaulted", "class model", "record class", f"the file marks none; kept {data.record}")
        return data.record
    report.add("defaulted", "class model", "record class", f"the file marks none; used the first class, {names[0]}")
    return names[0]


def _changes(before: DataModel | None, after: DataModel) -> dict[str, list[str]]:
    old = {e.name: e for e in before.entities} if before else {}
    new = {e.name: e for e in after.entities}
    return {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new)),
            "changed": sorted(n for n in set(new) & set(old) if new[n] != old[n])}


def _document(pack: Pack, data: DataModel | None, parsed: Parsed, entities: list[dict[str, Any]],
              report: ImportReport) -> dict[str, Any]:
    names = [e["name"] for e in entities]
    links = [x for link in parsed.links if (x := _link(link, set(names), report)) is not None]
    return {"schema_version": "eija.data.v1", "id": pack.id, "record": _record(parsed, names, data, report),
            "entities": entities, "associations": links}


def _validated(document: dict[str, Any], report: ImportReport) -> DataModel | list[str]:
    """The class model as the kernel's DataModel, or the reasons it refuses it (each also reported)."""
    try:
        return DataModel.model_validate(document)
    except ValidationError as error:
        problems = sorted({f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()})
    for problem in problems:
        report.add("unmapped", "kernel", "class model", "DATA_INVALID: " + problem)
    return problems


def import_class_model(pack: Pack, data: DataModel | None, parsed: Parsed, report: ImportReport) -> dict[str, Any]:
    if parsed.classes is None:
        return {"found": False}
    entities = [e for k in parsed.classes if (e := _entity(k, parsed.enums, report)) is not None]
    if not entities:
        report.add("unmapped", "class model", "class model", "no class could be imported")
        return {"found": True, "changed": False, "candidate": None}
    candidate = _validated(_document(pack, data, parsed, entities, report), report)
    if not isinstance(candidate, DataModel):
        return {"found": True, "changed": False, "candidate": None, "errors": candidate}
    return {"found": True, "changed": data is None or candidate.digest != data.digest,
            "candidate": candidate.model_dump(mode="json"), "changes": _changes(data, candidate)}


def _status(machine: dict[str, Any], classes: dict[str, Any], report: ImportReport) -> str:
    if not machine["found"] and not classes["found"]:
        return "EMPTY"
    if machine.get("policy") or (machine["found"] and machine.get("candidate") is None) or classes.get("errors"):
        return "REFUSED"
    return "PARTIAL" if report.unmapped else "CLEAN"


def import_actor_kinds(pack: Pack, parsed: Parsed, report: ImportReport) -> None:
    """Each actor's kind against its role's (ADR-0210). A kind is never changed by an import: kind laws read it, so a
    different kind is reported, to be changed in the pack's roles where the protected policy sees it."""
    for name, (kind, where) in (parsed.actors or {}).items():
        declared = pack.role_kind(name)
        if declared is None:
            report.add("unmapped", where, f"actor {name}", f"role {name} is not declared by pack {pack.id}")
        elif declared == kind:
            report.add("mapped", where, f"actor {name} ({kind_label(kind)})")
        else:
            report.add("unmapped", where, f"actor {name} kind",
                       f"the file draws {kind_label(kind)}; the pack declares {kind_label(declared)}. Kind laws read a "
                       "role's kind, so it is changed in the pack's roles, not by an import")


def import_parsed(fmt: str, parsed: Parsed, pack: Pack, model: Workflow, data: DataModel | None) -> dict[str, Any]:
    """The import report: the typed edits the kernel applied, its verdict, the candidate models and every element's fate."""
    report = ImportReport(parsed.skipped, parsed.derived)
    machine = import_state_machine(pack, model, parsed, report)
    classes = import_class_model(pack, data, parsed, report)
    import_actor_kinds(pack, parsed, report)
    return {"format": FORMAT, "from": fmt, "pack": pack.id, "model": model.semantic_hash,
            "status": _status(machine, classes, report), "state_machine": machine, "class_model": classes,
            "mapped": report.mapped, "defaulted": report.defaulted, "unmapped": report.unmapped, "derived": report.derived}
