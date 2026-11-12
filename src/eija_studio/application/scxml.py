"""The workflow state machine as a W3C SCXML statechart (ADR-0165).

SCXML is the W3C standard for executable state machines, with a normative interpretation algorithm. Exporting the
model to it does two things. Any SCXML engine can run the state diagram, so the model is not locked to EIJA. And an
independent engine gives a second opinion on what the diagram means: `verification/scxml/differential.py` runs every
case of the app oracle (ADR-0150) on the exported chart and requires the same outcome as the kernel.

The export is a projection of one run-to-completion step of `runtime.execute`, not a second interpreter that anything
runs in production. What it keeps and what it leaves to the kernel:

* A state is an atomic `<state>`; the initial state is the chart's `initial`. A composite state (ADR-0238) is a
  compound `<state>` holding its children, with its initial child as `initial`. An action that leaves every state
  inside a composite is carried once, on the composite, so the engine's own hierarchy decides it, and the differential
  checks that against the kernel's flat machine.
* An action is an event. A transition fires on its action's event from its source state only (`state_equals`).
* The actor is resolved by whoever sends the event, as the kernel's `UnitOfWork.actor` port does, and travels in the
  event data (`event_data`). `actor_active`, `role_current` and `actor_assigned` (when the transition has it) become
  the transition's `cond`, and an actor not in the directory sends `known` False.
* A guard over the record's values (`[amount > 500]`, ADR-0234) becomes a `cond` term over the event data too: whoever
  sends the event reads the record's values, as the kernel's `UnitOfWork.values` port does, and attaches each guarded
  attribute as `value_<name>` with `has_<name>` (False when the record has no value). The data model has already
  checked each value's type, so the chart compares without a type test.
* A time event (`after(14 days)`, ADR-0237) becomes a `cond` term over the event data as well: whoever sends the event
  reads how long the record has been in its state, as the kernel's `UnitOfWork.elapsed` port does, and attaches it as
  `elapsed` in seconds, with `has_elapsed` False when it is unknown, which is never due. It is not a delayed `<send>`: in the kernel a time
  event makes a step allowed, and an actor (usually a «timer» role) still takes it through the same checks.
* `expected_version` is a `version` variable in the datamodel, compared in the `cond` and incremented when the
  transition fires.
* Each required effect is appended, in declared order, to an `effects` list in the datamodel. Writing the audit log
  and the outbox stays with the kernel's typed adapters.
* `operation_binding` (an idempotent replay of the same operation id) is a property of the storage port, checked by the
  app's own conformance run. It is not projected.

Expressions use the Python datamodel, so the chart runs on engines with a Python datamodel. The states, transitions
and events are plain SCXML; an ECMAScript engine needs only the `cond` and `expr` strings rewritten.

Pure: no IO, no clock. The same pack and model always give the same bytes.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from typing import Any

from eija_studio.domain.models import DomainError, Transition, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import check_policy

NAMESPACE = "http://www.w3.org/2005/07/scxml"
FORMAT = "eija.scxml.v1"
_PLAIN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,62}$")


def scxml_id(name: str) -> str:
    """An XML/SCXML-safe id for a state or event name. Plain names are kept; any other name becomes `_` and its UTF-8
    bytes in hex. A plain name never starts with `_`, so the mapping is one-to-one."""
    return name if _PLAIN.fullmatch(name) else "_" + name.encode("utf-8").hex()


def _literal(text: str) -> str:
    return json.dumps(text, ensure_ascii=True)  # a JSON string literal is also a Python string literal


_OPERATORS = {"eq": "==", "ne": "!=", "lt": "<", "le": "<=", "gt": ">", "ge": ">="}


def _constant(value: object) -> str:
    return _literal(value) if isinstance(value, str) else repr(value)  # repr of a bool, int or finite float is Python


def _value_terms(transition: Transition) -> list[str]:
    return [f"_event.data.has_{g.attribute} and _event.data.value_{g.attribute} {_OPERATORS[g.op]} {_constant(g.value)}"
            for g in transition.conditions]


def guard_condition(transition: Transition) -> str:
    """The transition's `cond`: the actor checks of `runtime.check_actor`, its guards over record values and the
    version check, over the event data."""
    terms = ["_event.data.known", "_event.data.active", f"_event.data.role == {_literal(transition.role)}"]
    if "actor_assigned" in transition.guards:
        terms.append("_event.data.assigned")
    if transition.after is not None:
        terms.append(f"_event.data.has_elapsed and _event.data.elapsed >= {transition.after.seconds}")
    terms += _value_terms(transition)
    terms.append("_event.data.expected_version == version")
    return " and ".join(terms)


def event_data(actor: dict[str, Any] | None, expected_version: int, values: dict[str, Any] | None = None,
               attributes: tuple[str, ...] = (), elapsed: float | None = None, timed: bool = False) -> dict[str, Any]:
    """What the sender of an event attaches: the actor as the directory knows it (None if unknown), the version, the
    record's value of each guarded attribute in `attributes`, and, for a `timed` model, how long it has been in its state
    (`elapsed`, None when unknown)."""
    held = values or {}
    record = {f"has_{a}": held.get(a) is not None for a in attributes} | {f"value_{a}": held.get(a) for a in attributes}
    if timed:  # sent for a model with time events only
        record |= {"has_elapsed": elapsed is not None, "elapsed": 0 if elapsed is None else elapsed}
    if actor is None:
        return {"known": False, "active": False, "role": "", "assigned": False, "expected_version": expected_version} | record
    return {"known": True, "active": bool(actor["active"]), "role": str(actor["role"]),
            "assigned": bool(actor["assigned"]), "expected_version": expected_version} | record


def _transition(parent: ET.Element, transition: Transition) -> None:
    element = ET.SubElement(parent, "transition", {"event": scxml_id(transition.action),
                                                   "target": scxml_id(transition.to_state),
                                                   "cond": guard_condition(transition)})
    ET.SubElement(element, "assign", {"location": "version", "expr": "version + 1"})
    for effect in transition.required_effects:
        ET.SubElement(element, "assign", {"location": "effects", "expr": f"effects + [{_literal(effect)}]"})


def hoisted(model: Workflow) -> dict[str, list[Transition]]:
    """The transitions each state or composite carries in the chart. Where one action leaves every state inside a
    composite (ADR-0232 makes those transitions alike but for their source), the chart carries it once, on the
    composite, as UML draws it (ADR-0238). Larger composites are tried first, so the outermost group that fits wins."""
    carried: dict[str, list[Transition]] = {}
    groups = sorted(model.composites, key=lambda c: (-len(model.leaves(c.name)), c.name))
    for action in sorted({t.action for t in model.transitions}):
        for name, t in _carriers(model, groups, action):
            carried.setdefault(name, []).append(t)
    return {name: sorted(ts, key=lambda t: t.id) for name, ts in carried.items()}


def _carriers(model: Workflow, groups: list[Any], action: str) -> list[tuple[str, Transition]]:
    """Where one action's transitions sit in the chart: on each composite it leaves entirely, else on its source."""
    left = {t.from_state: t for t in sorted((t for t in model.transitions if t.action == action), key=lambda t: t.id)}
    found: list[tuple[str, Transition]] = []
    for group in groups:
        inside = model.leaves(group.name)
        if inside and all(s in left for s in inside):
            found.append((group.name, left[inside[0]]))
            for s in inside:
                del left[s]
    return found + list(left.items())


def _top_level(model: Workflow) -> list[str]:
    """States and composites at the top of the chart, in the order their first state appears in the model."""
    tops: list[str] = []
    for state in model.states:
        top = (model.ancestors(state) or (state,))[-1]
        if top not in tops:
            tops.append(top)
    return tops


def _element(parent: ET.Element, model: Workflow, name: str, leaving: dict[str, list[Transition]]) -> None:
    """One `<state>`: a plain state, or a composite holding its children with its initial child (ADR-0238)."""
    group = model.composite(name)
    attributes = {"id": scxml_id(name)} | ({"initial": scxml_id(group.initial)} if group else {})
    element = ET.SubElement(parent, "state", attributes)
    for transition in leaving.get(name, []):
        _transition(element, transition)
    for child in group.states if group else ():
        _element(element, model, child, leaving)


def to_scxml(pack: Pack, model: Workflow | None = None) -> str:
    """The model as an SCXML document. Refuses a model the protected policy blocks, as `eija build` does."""
    model = model if model is not None else pack.model
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", f"Workflow {model.id!r} does not belong to pack {pack.id!r}")
    errors = check_policy(model, pack)
    if errors:
        raise DomainError("POLICY_BLOCKED", "The protected policy refuses this workflow; it is not exported",
                          {"codes": sorted(errors)})
    root = ET.Element("scxml", {"xmlns": NAMESPACE, "version": "1.0", "datamodel": "python",
                                "name": scxml_id(model.id), "initial": scxml_id(model.initial_state)})
    datamodel = ET.SubElement(root, "datamodel")
    ET.SubElement(datamodel, "data", {"id": "version", "expr": "0"})
    ET.SubElement(datamodel, "data", {"id": "effects", "expr": "[]"})
    leaving = hoisted(model)
    for name in _top_level(model):
        _element(root, model, name, leaving)
    ET.indent(root, space="  ")
    note = (f"Generated by EIJA ({FORMAT}) from pack {pack.id} {pack.pack.version}, model {model.semantic_hash}. "
            "Do not edit: change the model and export again.").replace("--", "- -")  # "--" may not appear in a comment
    return '<?xml version="1.0" encoding="UTF-8"?>\n<!-- ' + note + " -->\n" + ET.tostring(root, encoding="unicode") + "\n"
