"""Reading XMI 2.1 to 2.5.1 as UML (ADR-0190); `xmi.py` writes it.

The reader accepts XMI from Enterprise Architect, Cameo/MagicDraw, Papyrus, Visual Paradigm, StarUML and Modelio: it
matches elements by local name and `xmi:type`, so namespace versions do not matter. A document with a DTD is refused
(no entity expansion), and so is one over `MAX_XML_BYTES`.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from .model import Attr, Edge, Klass, Link, Parsed, xml_root
from .xmi_document import (XmiDocument, bounds_of, children, comment_text, local, located, multiplicity_of, of_type, texts,
                           uml_type, xattr)


def _vertex(doc: XmiDocument, element: ET.Element | None) -> tuple[str, str]:
    """(kind, name) of a transition end: kind is state, initial, final or other."""
    if element is None:
        return "other", ""
    kind = uml_type(element)
    if kind == "Pseudostate":
        return ("initial", "") if element.get("kind", "initial") == "initial" else ("other", element.get("kind", ""))
    if kind == "FinalState":
        return "final", ""
    return ("state", element.get("name") or "") if kind == "State" else ("other", kind)


def _trigger(doc: XmiDocument, transition: ET.Element) -> str:
    trigger = next((c for c in transition if local(c.tag) == "trigger"), None)
    if trigger is None:
        return ""
    event = doc.ref(trigger, "event")
    signal = doc.ref(event, "signal") if event is not None else None
    operation = doc.ref(event, "operation") if event is not None else None
    return trigger.get("name") or doc.name(signal) or doc.name(operation) or doc.name(event)


def _spec_text(doc: XmiDocument, holder: ET.Element | None) -> str:
    if holder is None:
        return ""
    spec = next((c for c in holder if local(c.tag) == "specification"), holder)
    return " ".join(" ".join(texts(spec, "body") or [spec.get("value") or ""]).split())


def _label(doc: XmiDocument, transition: ET.Element) -> str:
    guard = _spec_text(doc, next((c for c in transition if local(c.tag) == "guard"), None))
    effect = _spec_text(doc, next((c for c in transition if local(c.tag) == "effect"), None))
    return _trigger(doc, transition) + (f" [{guard}]" if guard else "") + (f" / {effect}" if effect else "")


def _subvertex(vertex: ET.Element, parsed: Parsed) -> None:
    kind = uml_type(vertex)
    if kind == "State" and children(vertex, "region"):
        parsed.skip(located(vertex), f"composite state {vertex.get('name')}", "composite states are planned (issue #93); its contents are not imported")
    elif kind == "State":
        parsed.state(vertex.get("name") or "")
    elif kind == "Pseudostate" and vertex.get("kind", "initial") != "initial":
        parsed.skip(located(vertex), f"{vertex.get('kind')} pseudostate", "only the initial pseudostate is in PlayIDE's state vocabulary")


def _region(doc: XmiDocument, region: ET.Element, parsed: Parsed) -> None:
    for vertex in children(region, "subvertex"):
        _subvertex(vertex, parsed)
    for transition in children(region, "transition"):
        _transition(doc, transition, parsed)


def _transition(doc: XmiDocument, transition: ET.Element, parsed: Parsed) -> None:
    (a_kind, a), (b_kind, b) = _vertex(doc, doc.ref(transition, "source")), _vertex(doc, doc.ref(transition, "target"))
    where = located(transition)
    if a_kind == "initial" and b_kind == "state":
        parsed.start(b, where)
    elif a_kind == "state" and b_kind == "final":
        return  # a final state: derived by PlayIDE
    elif a_kind == "state" and b_kind == "state":
        parsed.edges.append(Edge(a, b, _label(doc, transition), where))
    else:
        parsed.skip(where, f"transition {a or a_kind} -> {b or b_kind}", "it joins something that is not a PlayIDE state")


def _state_machines(doc: XmiDocument, root: ET.Element, parsed: Parsed) -> None:
    machines = [e for e in root.iter() if uml_type(e) == "StateMachine"]
    for extra in machines[1:]:
        parsed.skip(located(extra), f"state machine {extra.get('name')}", "PlayIDE reads one state machine per model; the first was read")
    if not machines:
        return
    parsed.states = []
    regions = [c for c in machines[0] if local(c.tag) == "region"]
    for extra in regions[1:]:
        parsed.skip(located(extra), f"region {extra.get('name')}", "orthogonal regions are not in PlayIDE's state vocabulary")
    if regions:
        _region(doc, regions[0], parsed)


def _property(doc: XmiDocument, prop: ET.Element, rules: dict[str, int]) -> Attr:
    target = doc.ref(prop, "type")
    type_name = doc.name(target) if target is not None else ""
    lower, upper = bounds_of(prop)
    return Attr(name=prop.get("name") or "", type=type_name, lower=int(lower) if lower.isdigit() else 0, upper=upper,
                max_length=rules.get(xattr(prop, "id") or ""), description=comment_text(prop), where=located(prop))


def _rules(doc: XmiDocument, klass: ET.Element) -> dict[str, int]:
    out: dict[str, int] = {}
    for rule in (c for c in klass if local(c.tag) == "ownedRule"):
        found = re.search(r"(\w+)\.size\(\)\s*<=\s*(\d+)", _spec_text(doc, rule))
        constrained = (rule.get("constrainedElement") or "").split()
        if found and constrained:
            out[constrained[0]] = int(found.group(2))
    return out


def _class(doc: XmiDocument, klass: ET.Element, record: bool, parsed: Parsed) -> None:
    rules = _rules(doc, klass)
    # a navigable association end is an ownedAttribute too; it is read with its association
    attributes = [_property(doc, prop, rules) for prop in children(klass, "ownedAttribute") if not prop.get("association")]
    for op in children(klass, "ownedOperation"):
        parsed.skip(located(op), f"{klass.get('name')}.{op.get('name')}()", "operations are not in PlayIDE's data vocabulary")
    if children(klass, "generalization"):
        parsed.skip(located(klass), f"{klass.get('name')} generalisation", "inheritance is not in PlayIDE's data vocabulary")
    parsed.klass(Klass(name=klass.get("name") or "", attributes=tuple(attributes), description=comment_text(klass),
                       record=record, where=located(klass)))


def _member_ends(doc: XmiDocument, assoc: ET.Element) -> list[ET.Element]:
    found = [doc.by_id.get(i) for i in (assoc.get("memberEnd") or "").split()]
    return [e for e in found if e is not None] or children(assoc, "ownedEnd")


def _is_class(element: ET.Element | None) -> bool:
    return element is not None and uml_type(element) == "Class"


def _source_first(ends: list[ET.Element]) -> tuple[ET.Element, ET.Element]:
    """(source, target): the aggregation kind is written on the end at the whole, which PlayIDE keeps as the source."""
    whole = [e.get("aggregation", "none") for e in ends]
    return (ends[1], ends[0]) if whole[0] in ("composite", "shared") and whole[1] == "none" else (ends[0], ends[1])


def _association(doc: XmiDocument, assoc: ET.Element, parsed: Parsed) -> None:
    ends = _member_ends(doc, assoc)
    types = [doc.ref(e, "type") for e in ends]
    classes = [_is_class(t) for t in types]
    if len(ends) != 2 or not all(classes):
        if any(classes):
            names = " - ".join(doc.name(t) for t in types)
            parsed.skip(located(assoc), f"association {names}", "PlayIDE reads binary associations between classes")
        return
    src, dst = _source_first(ends)
    kind = {"composite": "composition", "shared": "aggregation"}.get(dst.get("aggregation", "none"), "association")
    parsed.links.append(Link(doc.name(doc.ref(src, "type")), doc.name(doc.ref(dst, "type")), kind, dst.get("name") or "",
                             multiplicity_of(src), multiplicity_of(dst), located(assoc)))


_CLASS_TAGS = ("packagedElement", "ownedMember", "nestedClassifier")


def _class_model(doc: XmiDocument, root: ET.Element, parsed: Parsed) -> None:
    classes = [e for e in of_type(root, "Class") if local(e.tag) in _CLASS_TAGS]
    for enum in of_type(root, "Enumeration"):
        parsed.enums[enum.get("name") or ""] = tuple(lit.get("name") or "" for lit in children(enum, "ownedLiteral"))
    if not classes:
        return
    parsed.classes = []
    for klass in classes:
        _class(doc, klass, bool(klass.get("classifierBehavior")), parsed)
    for assoc in of_type(root, "Association"):
        _association(doc, assoc, parsed)
    _skip_other_kinds(root, parsed)


def _skip_other_kinds(root: ET.Element, parsed: Parsed) -> None:
    for kind in ("Interface", "Component", "Interaction", "Activity"):
        for element in of_type(root, kind):
            parsed.skip(located(element), f"{kind} {element.get('name')}", f"a UML {kind} is not in PlayIDE's model")


def _base(element: ET.Element) -> str | None:
    """The element a stereotype application extends: `base_Actor` as an attribute or as an `xmi:idref` child."""
    found = next((v for k, v in element.attrib.items() if local(k) == "base_Actor"), None)
    child = next((c for c in element if local(c.tag) == "base_Actor"), None)
    return found or (xattr(child, "idref") if child is not None else None)


def _actors(root: ET.Element, parsed: Parsed) -> None:
    """Each `Actor` with the stereotypes applied to it (ADR-0210): an application is any element whose `base_Actor`
    names the actor, whatever profile namespace the tool wrote, so «agent», «timer» and «system» read back by name."""
    applied: dict[str, list[str]] = {}
    for element in root.iter():
        base = _base(element)
        if base:
            applied.setdefault(base, []).append(local(element.tag))
    for actor in of_type(root, "Actor"):
        parsed.actor(" ".join((actor.get("name") or "").split()), applied.get(xattr(actor, "id") or "", []), located(actor))


def parse(text: str) -> Parsed:
    root = xml_root(text, "An XMI file")
    doc, parsed = XmiDocument(root), Parsed()
    _state_machines(doc, root, parsed)
    _class_model(doc, root, parsed)
    for kind in ("Actor", "UseCase"):
        if any(uml_type(e) == kind for e in root.iter()):
            parsed.derive(kind, f"{kind}s")
    _actors(root, parsed)
    return parsed
