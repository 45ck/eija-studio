"""The shared UML picture every interchange format reads into and writes from (ADR-0190).

PlayIDE's model is one pack: a state machine (`Workflow`), an optional class model (`DataModel`) and the use cases
derived from both. This module is the small, format-free picture of those UML elements that the four formats share,
plus the two places their text meets the kernel's vocabulary:

* the UML transition label, `trigger [guard] / effect, effect`, where the trigger is the action, the guard names the
  role (and `assigned` when the action needs an assigned actor), and the effects are the action's required effects;
* the UML type of an attribute, `String`, `Real`, `Boolean`, `Date` or an enumeration for a choice.

A parsed file becomes a `Parsed`, and every element a format reader could not read into it is a `skip`, with where it
was and why. Nothing here decides whether the result is allowed: that is `interop.mapping`, through the kernel.

Pure: no IO. Equal input gives equal output.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any

from eija_studio.domain.data import Attribute, DataModel
from eija_studio.domain.models import DomainError, Transition, Workflow
from eija_studio.domain.pack import Pack

GENERATOR = "PlayIDE (eija.uml-interop.v1)"
UML_TYPES = {"text": "String", "number": "Real", "boolean": "Boolean", "date": "Date"}
READ_TYPES = {"string": "text", "str": "text", "text": "text", "char": "text", "real": "number", "integer": "number",
              "int": "number", "float": "number", "double": "number", "decimal": "number", "number": "number",
              "long": "number", "boolean": "boolean", "bool": "boolean", "date": "date", "localdate": "date",
              "datetime": "date", "timestamp": "date"}
WIDENED = {"integer", "int", "long", "datetime", "timestamp"}  # read, but PlayIDE keeps less than the file said
MULTIPLICITIES = {"0..1": "0..1", "1": "1", "1..1": "1", "0..*": "0..*", "*": "0..*", "1..*": "1..*", "0..n": "0..*",
                  "1..n": "1..*", "n": "0..*"}
DEFAULT_MAX_LENGTH = 200
_LABEL = re.compile(r"^\s*(?P<trigger>[^\[/]*?)\s*(?:\[(?P<guard>[^\]]*)\])?\s*(?:/\s*(?P<effects>.*))?$")
_ROLE = re.compile(r"^role\s*(?:=|==|:)\s*(?P<role>[^\s].*?)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Edge:
    """One UML transition as a file drew it."""
    source: str
    target: str
    label: str
    where: str


@dataclass(frozen=True)
class Attr:
    name: str
    type: str  # the UML type name as written
    lower: int = 0
    upper: str = "1"
    max_length: int | None = None
    description: str = ""
    where: str = ""


@dataclass(frozen=True)
class Klass:
    name: str
    attributes: tuple[Attr, ...] = ()
    description: str = ""
    record: bool = False
    where: str = ""


@dataclass(frozen=True)
class Link:
    source: str
    target: str
    kind: str  # association | composition | aggregation
    role: str = ""
    source_multiplicity: str = "1"
    target_multiplicity: str = "0..*"
    where: str = ""


@dataclass
class Parsed:
    """What a format reader found. `states is None` means the file has no state machine at all."""
    states: list[str] | None = None
    initial: str | None = None
    edges: list[Edge] = field(default_factory=list)
    classes: list[Klass] | None = None
    enums: dict[str, tuple[str, ...]] = field(default_factory=dict)
    links: list[Link] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    derived: list[dict[str, str]] = field(default_factory=list)

    def skip(self, where: str, element: str, reason: str) -> None:
        self.skipped.append({"where": where, "element": element, "reason": reason})

    def derive(self, where: str, element: str) -> None:
        """An element PlayIDE derives from the model (use cases, final states), so reading it back would add nothing."""
        self.derived.append({"where": where, "element": element,
                             "reason": "derived from the state machine; PlayIDE redraws it from the imported model"})

    def state(self, name: str) -> None:
        if self.states is None:
            self.states = []
        if name not in self.states:
            self.states.append(name)

    def start(self, name: str, where: str) -> None:
        """An arrow from the initial pseudostate. A second one is reported, never silently dropped."""
        if self.initial not in (None, name):
            self.skip(where, f"initial -> {name}", f"a second initial state; kept {self.initial}")
        else:
            self.initial = name

    def klass(self, klass: Klass) -> None:
        if self.classes is None:
            self.classes = []
        self.classes.append(klass)


# ---- labels -------------------------------------------------------------------------------------------------

def guard_text(transition: Transition) -> str:
    return f"role = {transition.role}" + (" and assigned" if "actor_assigned" in transition.guards else "")


def transition_label(transition: Transition) -> str:
    """`Action [role = Role and assigned] / Kind:Effect, Kind:Effect`, the UML `trigger [guard] / effects`."""
    label = f"{transition.action} [{guard_text(transition)}]"
    return label + (" / " + ", ".join(transition.required_effects) if transition.required_effects else "")


@dataclass(frozen=True)
class Label:
    trigger: str
    role: str | None
    assigned: bool | None  # None: the guard did not say
    effects: tuple[str, ...] | None  # None: the label has no effect part
    unread: tuple[str, ...]  # guard terms outside PlayIDE's closed guard vocabulary


def _guard_terms(guard: str) -> tuple[str | None, bool | None, list[str]]:
    role: str | None = None
    assigned: bool | None = None if not guard.strip() else False
    unread: list[str] = []
    for term in (t.strip() for t in re.split(r"\s+and\s+|&&|,", guard) if t.strip()):
        found = _ROLE.match(term)
        if found:
            role = found.group("role").strip("'\"")
        elif term.lower() in ("assigned", "actor assigned", "actor_assigned"):
            assigned = True
        else:
            unread.append(term)
    return role, assigned, unread


def parse_label(text: str) -> Label:
    match = _LABEL.match(" ".join(text.split()))
    if match is None:  # pragma: no cover - the pattern matches every string
        return Label("", None, None, None, (text,))
    role, assigned, unread = _guard_terms(match.group("guard") or "")
    effects = match.group("effects")
    listed = tuple(e.strip() for e in re.split(r"[,;]", effects) if e.strip()) if effects is not None else None
    return Label(match.group("trigger").strip(), role, assigned, listed, tuple(unread))


# ---- the pack's UML elements --------------------------------------------------------------------------------

def terminals(model: Workflow) -> list[str]:
    """States no transition leaves: UML final states are drawn after them."""
    sources = {t.from_state for t in model.transitions}
    return [s for s in model.states if s not in sources]


def enum_name(entity: str, attribute: Attribute, taken: set[str]) -> str:
    base = entity + attribute.name[0].upper() + attribute.name[1:]
    name, n = base, 1
    while name in taken:
        n += 1
        name = f"{base}{n}"
    return name


def enumerations(data: DataModel) -> dict[tuple[str, str], str]:
    """(entity, attribute) -> enumeration name for every choice attribute, stable and collision-free."""
    taken = {e.name for e in data.entities}
    out: dict[tuple[str, str], str] = {}
    for entity in data.entities:
        for attribute in entity.attributes:
            if attribute.type == "choice":
                out[entity.name, attribute.name] = enum_name(entity.name, attribute, taken)
                taken.add(out[entity.name, attribute.name])
    return out


def attribute_type(entity: str, attribute: Attribute, enums: dict[tuple[str, str], str]) -> str:
    return enums[entity, attribute.name] if attribute.type == "choice" else UML_TYPES[attribute.type]


def multiplicity(attribute: Attribute) -> str:
    return "1" if attribute.required else "0..1"


def use_case_links(model: Workflow) -> list[tuple[str, str]]:
    """(role, action) pairs: who performs which use case, in transition-id order."""
    pairs: list[tuple[str, str]] = []
    for t in sorted(model.transitions, key=lambda t: t.id):
        if (t.role, t.action) not in pairs:
            pairs.append((t.role, t.action))
    return pairs


def not_carried(pack: Pack, data: DataModel | None, *extra: str) -> list[str]:
    """Parts of the pack that are not UML and so no UML file carries: an export lists them instead of dropping them."""
    found = [f"{len(pack.laws)} laws (open them in PlayIDE's Laws tab)"] if pack.laws else []
    found += [f"{len(pack.meanings)} meanings"] if pack.meanings else []
    found.append("the effect catalog's kinds and recipients")
    found.append("fixtures, verifiers, the meaning-check journey and the language")
    if data is None:
        found.append("no class model: this pack has no data.json")
    return found + list(extra)


def export_report(fmt: str, pack: Pack, model: Workflow, data: DataModel | None, *extra: str) -> dict[str, Any]:
    return {"format": "eija.uml-export.v1", "to": fmt, "pack": pack.id, "model": model.semantic_hash,
            "data": data.digest if data else None, "not_carried": not_carried(pack, data, *extra)}


MAX_XML_BYTES = 8_000_000  # XMI and draw.io files


def xml_root(text: str, what: str) -> ET.Element:
    """Parse an XML file safely: a DTD or entity is refused before parsing (nothing expands), and so is a large file."""
    if len(text.encode("utf-8")) > MAX_XML_BYTES:
        raise DomainError("IMPORT_TOO_LARGE", f"{what} is read up to {MAX_XML_BYTES} bytes")
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.IGNORECASE):
        raise DomainError("IMPORT_INVALID", f"{what} with a DTD or entities is refused")
    try:
        return ET.fromstring(text)  # noqa: S314 - DTDs and entities are refused above, so nothing expands
    except ET.ParseError as error:
        raise DomainError("IMPORT_INVALID", f"Not well-formed XML ({error.position[0]}:{error.position[1]})") from None
