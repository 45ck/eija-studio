"""XMI: the pack as an OMG UML 2.5.1 model in XMI 2.5.1, and back (ADR-0190).

XMI is how UML tools exchange models: Enterprise Architect, Cameo/MagicDraw, Papyrus, Visual Paradigm, StarUML and
Modelio all read and write it. The export is plain UML with no profile, so any of them can open it:

* the record class owns the state machine as its `classifierBehavior` (UML's own way of saying "instances of this
  class move through this state machine"); without a class model the state machine is a packaged element;
* each action is a `Signal` with a `SignalEvent`; a transition's trigger names it, its guard is a `Constraint` whose
  `OpaqueExpression` holds `role = <Role> and assigned`, and its effect is an `OpaqueBehavior` listing the effects;
* attributes are `Property`s typed by the UML primitive types (`String`, `Real`, `Boolean`), a `Date` data type or an
  `Enumeration`, with `[1]` or `[0..1]`; a text attribute's maximum length is an OCL constraint
  `itemTitle.size() <= 200`; descriptions are `ownedComment`s;
* associations own both ends; composition and aggregation are on the end typed by the part;
* every role is an `Actor` and every action a `UseCase`, joined by associations.

`xmi_reader.py` reads XMI 2.1 to 2.5.1 from those tools.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

from eija_studio.domain.data import Attribute, DataModel
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack

from .model import GENERATOR, attribute_type, enumerations, export_report, guard_text, use_case_links

XMI_NS = "http://www.omg.org/spec/XMI/20131001"
UML_NS = "http://www.omg.org/spec/UML/20161101"
PRIMITIVES = "http://www.omg.org/spec/UML/20161101/PrimitiveTypes.xmi"
_X = f"{{{XMI_NS}}}"


def _id(*parts: str) -> str:
    """A stable xmi:id. XML ids are NCNames, so anything else is hex-encoded."""
    text = ".".join(parts)
    return text if re.fullmatch(r"[A-Za-z_][\w.-]*", text) else "_" + text.encode("utf-8").hex()


def _el(parent: ET.Element, tag: str, uml_type: str, ident: str, **attrs: str) -> ET.Element:
    return ET.SubElement(parent, tag, {f"{_X}type": f"uml:{uml_type}", f"{_X}id": ident, **attrs})


def _comment(parent: ET.Element, owner: str, text: str) -> None:
    if text:
        comment = _el(parent, "ownedComment", "Comment", owner + ".comment")
        ET.SubElement(comment, "body").text = text


def _opaque(parent: ET.Element, tag: str, kind: str, ident: str, language: str, body: str) -> ET.Element:
    element = _el(parent, tag, kind, ident)
    ET.SubElement(element, "language").text = language
    ET.SubElement(element, "body").text = body
    return element


def _bound(parent: ET.Element, owner: str, lower: str, upper: str) -> None:
    _el(parent, "lowerValue", "LiteralInteger", owner + ".lower", value=lower)
    _el(parent, "upperValue", "LiteralUnlimitedNatural", owner + ".upper", value=upper)


def _ends(multiplicity: str) -> tuple[str, str]:
    low, _, high = multiplicity.partition("..")
    return low, high or low


# ---- export -------------------------------------------------------------------------------------------------

def _state_machine(owner: ET.Element, tag: str, pack: Pack, model: Workflow) -> str:
    sm_id = _id("sm", model.id)
    machine = _el(owner, tag, "StateMachine", sm_id, name=pack.pack.name)
    region = _el(machine, "region", "Region", sm_id + ".region", name="main")
    _el(region, "subvertex", "Pseudostate", sm_id + ".initial", kind="initial")
    for state in model.states:
        _el(region, "subvertex", "State", _id("state", state), name=state)
    _el(region, "transition", "Transition", sm_id + ".start", source=sm_id + ".initial", target=_id("state", model.initial_state))
    for t in sorted(model.transitions, key=lambda t: t.id):
        ident = _id("transition", t.id)
        element = _el(region, "transition", "Transition", ident, name=t.id, source=_id("state", t.from_state), target=_id("state", t.to_state))
        _el(element, "trigger", "Trigger", ident + ".trigger", name=t.action, event=_id("event", t.action))
        guard = _el(element, "guard", "Constraint", ident + ".guard")
        _opaque(guard, "specification", "OpaqueExpression", ident + ".guard.spec", "PlayIDE", guard_text(t))
        if t.required_effects:
            _opaque(element, "effect", "OpaqueBehavior", ident + ".effect", "PlayIDE", ", ".join(t.required_effects))
    return sm_id


def _primitive(parent: ET.Element, type_name: str, dates: str) -> None:
    if type_name == "Date":
        parent.set("type", dates)
    else:
        ET.SubElement(parent, "type", {f"{_X}type": "uml:PrimitiveType", "href": f"{PRIMITIVES}#{type_name}"})


def _attribute(klass: ET.Element, entity: str, a: Attribute, uml_type: str, dates: str) -> None:
    """A `Property` typed by a primitive, the Date data type or an enumeration, and its OCL maxLength rule."""
    pid = _id("class", entity, a.name)
    prop = _el(klass, "ownedAttribute", "Property", pid, name=a.name)
    if a.type == "choice":
        prop.set("type", _id("enum", uml_type))
    else:
        _primitive(prop, uml_type, dates)
    _bound(prop, pid, "1" if a.required else "0", "1")
    _comment(prop, pid, a.description)
    if a.type == "text":
        rule = _el(klass, "ownedRule", "Constraint", pid + ".maxLength", name=f"{a.name} maxLength", constrainedElement=pid)
        _opaque(rule, "specification", "OpaqueExpression", pid + ".maxLength.spec", "OCL", f"{a.name}.size() <= {a.max_length}")


def _classes(model_el: ET.Element, data: DataModel) -> dict[str, ET.Element]:
    enums = enumerations(data)
    dates = _id("type", "Date")
    if any(a.type == "date" for e in data.entities for a in e.attributes):
        _el(model_el, "packagedElement", "DataType", dates, name="Date")
    out: dict[str, ET.Element] = {}
    for entity in data.entities:
        cid = _id("class", entity.name)
        klass = out[entity.name] = _el(model_el, "packagedElement", "Class", cid, name=entity.name)
        _comment(klass, cid, entity.description)
        for a in entity.attributes:
            _attribute(klass, entity.name, a, attribute_type(entity.name, a, enums), dates)
    for (entity_name, attribute), name in sorted(enums.items(), key=lambda kv: kv[1]):
        enum = _el(model_el, "packagedElement", "Enumeration", _id("enum", name), name=name)
        for choice in next(a.choices for a in data.entity(entity_name).attributes if a.name == attribute):
            _el(enum, "ownedLiteral", "EnumerationLiteral", _id("enum", name, choice), name=choice)
    return out


_AGGREGATION = {"composition": "composite", "aggregation": "shared", "association": "none"}


def _associations(model_el: ET.Element, data: DataModel) -> None:
    for n, link in enumerate(data.associations, 1):
        aid = _id("assoc", str(n), link.source, link.target)
        assoc = _el(model_el, "packagedElement", "Association", aid, memberEnd=f"{aid}.src {aid}.dst")
        src = _el(assoc, "ownedEnd", "Property", aid + ".src", type=_id("class", link.source), association=aid)
        _bound(src, aid + ".src", *_ends(link.source_multiplicity))
        dst = _el(assoc, "ownedEnd", "Property", aid + ".dst", type=_id("class", link.target), association=aid,
                  aggregation=_AGGREGATION[link.kind], **({"name": link.role} if link.role else {}))
        _bound(dst, aid + ".dst", *_ends(link.target_multiplicity))


def _use_cases(model_el: ET.Element, pack: Pack, model: Workflow) -> None:
    for declared in pack.roles:
        actor = _el(model_el, "packagedElement", "Actor", _id("actor", declared.id), name=declared.id)
        _comment(actor, _id("actor", declared.id), declared.description)
    for action in sorted({t.action for t in model.transitions}):
        _el(model_el, "packagedElement", "UseCase", _id("usecase", action), name=action)
        _el(model_el, "packagedElement", "Signal", _id("signal", action), name=action)
        _el(model_el, "packagedElement", "SignalEvent", _id("event", action), name=action, signal=_id("signal", action))
    for role, action in use_case_links(model):
        aid = _id("performs", role, action)
        assoc = _el(model_el, "packagedElement", "Association", aid, memberEnd=f"{aid}.actor {aid}.case")
        _el(assoc, "ownedEnd", "Property", aid + ".actor", type=_id("actor", role), association=aid)
        _el(assoc, "ownedEnd", "Property", aid + ".case", type=_id("usecase", action), association=aid)


def export(pack: Pack, model: Workflow, data: DataModel | None) -> tuple[str, dict[str, Any]]:
    ET.register_namespace("xmi", XMI_NS)
    ET.register_namespace("uml", UML_NS)
    root = ET.Element(f"{_X}XMI")
    model_el = ET.SubElement(root, f"{{{UML_NS}}}Model", {f"{_X}id": _id("model", pack.id), "name": pack.pack.name})
    _comment(model_el, _id("model", pack.id), pack.pack.description)
    classes = _classes(model_el, data) if data is not None else {}
    if data is not None:
        record = classes[data.record]
        sm_id = _state_machine(record, "ownedBehavior", pack, model)
        record.set("classifierBehavior", sm_id)
        _associations(model_el, data)
    else:
        _state_machine(model_el, "packagedElement", pack, model)
    _use_cases(model_el, pack, model)
    ET.indent(root, space="  ")
    note = f"GENERATED by {GENERATOR} from pack {pack.id} {pack.pack.version}, model {model.semantic_hash}."
    text = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- ' + note + " -->\n" + ET.tostring(root, encoding="unicode") + "\n"
    return text, export_report("xmi", pack, model, data)
