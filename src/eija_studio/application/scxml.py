"""The workflow state machine as a W3C SCXML statechart (ADR-0165).

SCXML is the W3C standard for executable state machines, with a normative interpretation algorithm. Exporting the
model to it does two things. Any SCXML engine can run the state diagram, so the model is not locked to EIJA. And an
independent engine gives a second opinion on what the diagram means: `verification/scxml/differential.py` runs every
case of the app oracle (ADR-0150) on the exported chart and requires the same outcome as the kernel.

The export is a projection of one run-to-completion step of `runtime.execute`, not a second interpreter that anything
runs in production. What it keeps and what it leaves to the kernel:

* A state is an atomic `<state>`; the initial state is the chart's `initial`.
* An action is an event. A transition fires on its action's event from its source state only (`state_equals`).
* The actor is resolved by whoever sends the event, as the kernel's `UnitOfWork.actor` port does, and travels in the
  event data (`event_data`). `actor_active`, `role_current` and `actor_assigned` (when the transition has it) become
  the transition's `cond`, and an actor not in the directory sends `known` False.
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


def guard_condition(transition: Transition) -> str:
    """The transition's `cond`: the actor checks of `runtime.check_actor` and the version check, over the event data."""
    terms = ["_event.data.known", "_event.data.active", f"_event.data.role == {_literal(transition.role)}"]
    if "actor_assigned" in transition.guards:
        terms.append("_event.data.assigned")
    terms.append("_event.data.expected_version == version")
    return " and ".join(terms)


def event_data(actor: dict[str, Any] | None, expected_version: int) -> dict[str, Any]:
    """What the sender of an event attaches: the actor as the directory knows it (None if unknown) and the version."""
    if actor is None:
        return {"known": False, "active": False, "role": "", "assigned": False, "expected_version": expected_version}
    return {"known": True, "active": bool(actor["active"]), "role": str(actor["role"]),
            "assigned": bool(actor["assigned"]), "expected_version": expected_version}


def _transition(parent: ET.Element, transition: Transition) -> None:
    element = ET.SubElement(parent, "transition", {"event": scxml_id(transition.action),
                                                   "target": scxml_id(transition.to_state),
                                                   "cond": guard_condition(transition)})
    ET.SubElement(element, "assign", {"location": "version", "expr": "version + 1"})
    for effect in transition.required_effects:
        ET.SubElement(element, "assign", {"location": "effects", "expr": f"effects + [{_literal(effect)}]"})


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
    for state in model.states:
        element = ET.SubElement(root, "state", {"id": scxml_id(state)})
        for transition in sorted((t for t in model.transitions if t.from_state == state), key=lambda t: t.id):
            _transition(element, transition)
    ET.indent(root, space="  ")
    note = (f"Generated by EIJA ({FORMAT}) from pack {pack.id} {pack.pack.version}, model {model.semantic_hash}. "
            "Do not edit: change the model and export again.").replace("--", "- -")  # "--" may not appear in a comment
    return '<?xml version="1.0" encoding="UTF-8"?>\n<!-- ' + note + " -->\n" + ET.tostring(root, encoding="unicode") + "\n"
