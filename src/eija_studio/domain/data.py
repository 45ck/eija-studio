"""The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.

It lives in an optional `data.json` beside a pack's `pack.json`, with its own digest, so packs without one, their
digests and every receipt over them are unchanged. One entity is the workflow's record: the thing that moves through
the state machine. `check_values` is the only place record values are checked; the generated app calls it, so there
is no second reading of the rules.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any, Literal

from pydantic import Field, SerializerFunctionWrapHandler, ValidationError, model_serializer, model_validator

from .models import Contract, DomainError, fingerprint
from .pack import Pack, held, pack_directory

DATA_FILE = "data.json"
REFERENCE_LENGTH = 32  # an object id: what the built app's object store issues
NAME = r"^[A-Z][A-Za-z0-9]{0,39}$"  # UML class names: UpperCamelCase
ATTRIBUTE_NAME = r"^[a-z][a-zA-Z0-9_]{0,39}$"
FieldType = Literal["text", "number", "date", "boolean", "choice"]
Multiplicity = Literal["0..1", "1", "0..*", "1..*"]


class Attribute(Contract):
    name: str = Field(pattern=ATTRIBUTE_NAME)
    type: FieldType
    required: bool = False
    choices: tuple[Annotated[str, Field(min_length=1, max_length=60)], ...] = Field(default=(), max_length=32)  # only for "choice"; "" means unset
    max_length: int = Field(default=200, ge=1, le=5000)  # only for type "text"
    description: str = Field(default="", max_length=300)

    @model_validator(mode="after")
    def coherent(self) -> Attribute:
        if (self.type == "choice") != bool(self.choices):
            raise ValueError("A choice attribute needs choices, and only a choice attribute may have them")
        if len(set(self.choices)) != len(self.choices):
            raise ValueError("Duplicate choice")
        return self


class Entity(Contract):
    name: str = Field(pattern=NAME)
    attributes: tuple[Attribute, ...] = Field(default=(), max_length=40)
    description: str = Field(default="", max_length=300)

    @model_validator(mode="after")
    def unique(self) -> Entity:
        names = [a.name for a in self.attributes]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate attribute")
        return self


class Association(Contract):
    source: str = Field(pattern=NAME)
    target: str = Field(pattern=NAME)
    kind: Literal["association", "composition", "aggregation"] = "association"
    role: str = Field(default="", max_length=40)  # the target end's role name, e.g. "attendees"
    source_multiplicity: Multiplicity = "1"
    target_multiplicity: Multiplicity = "0..*"
    # Built (issue #145, ADR-0235): a to-one association from the record class becomes a reference field, named by the
    # role, that the app checks against stored objects of the other class. False is left out of every dump, so data
    # models that build nothing keep their exact bytes and digests.
    built: bool = False

    @model_serializer(mode="wrap")
    def _omit_drawn(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        data: dict[str, Any] = handler(self)
        if not self.built:
            data.pop("built", None)
        return data


class DataModel(Contract):
    schema_version: Literal["eija.data.v1"] = "eija.data.v1"
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")  # the pack this data model belongs to
    record: str = Field(pattern=NAME)  # the entity whose instances move through the workflow
    entities: tuple[Entity, ...] = Field(min_length=1, max_length=40)
    associations: tuple[Association, ...] = Field(default=(), max_length=80)

    @model_validator(mode="after")
    def coherent(self) -> DataModel:
        names = [e.name for e in self.entities]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate entity")
        if self.record not in names:
            raise ValueError("The record entity is not declared")
        for link in self.associations:
            if link.source not in names or link.target not in names:
                raise ValueError("Association to an undeclared entity")
        problem = _reference_problem(self)
        if problem:
            raise ValueError(problem)
        return self

    @property
    def digest(self) -> str:
        return fingerprint(self)

    def entity(self, name: str) -> Entity:
        return next(e for e in self.entities if e.name == name)


@dataclass(frozen=True)
class Reference:
    """A built to-one association seen from the record: the field `name` holds the id of a stored `target` object."""
    name: str
    target: str
    required: bool


def _record_end(data: DataModel, link: Association) -> tuple[str, Multiplicity] | None:
    """(other class, how many of it one record links to) when the record class is one end, the other end another class."""
    if link.source == data.record and link.target != data.record:
        return link.target, link.target_multiplicity
    if link.target == data.record and link.source != data.record:
        return link.source, link.source_multiplicity
    return None


def _link_problem(data: DataModel, link: Association, taken: set[str]) -> str:
    end = _record_end(data, link)
    if end is None or end[1] not in ("1", "0..1"):
        return "A built association links the record class to at most one object of another class"
    if not re.fullmatch(ATTRIBUTE_NAME, link.role) or link.role in taken:
        return "A built association needs a role name that is a free attribute name of the record class"
    return ""


def _reference_problem(data: DataModel) -> str:
    """Why the built associations cannot be reference fields, or "" when they can."""
    taken = {a.name for e in data.entities if e.name == data.record for a in e.attributes}
    for link in (x for x in data.associations if x.built):
        problem = _link_problem(data, link, taken)
        if problem:
            return problem
        taken.add(link.role)
    return ""


def references(data: DataModel | None) -> list[Reference]:
    """The record's reference fields, one per built association, in declaration order. Empty when nothing is built."""
    if data is None:
        return []
    found = []
    for link in (x for x in data.associations if x.built):
        end = _record_end(data, link)
        if end is not None:
            found.append(Reference(link.role, end[0], end[1] == "1"))
    return found


def record_fields(data: DataModel) -> tuple[Attribute, ...]:
    """What a record holds: the record class's attributes, then each reference field as text holding an object's id."""
    return data.entity(data.record).attributes + tuple(
        Attribute(name=r.name, type="text", required=r.required, max_length=REFERENCE_LENGTH,
                  description=f"The id of an existing {r.target}") for r in references(data))


def parse_data(document: Any, pack_id: str) -> DataModel:
    try:
        data = DataModel.model_validate(document)
    except ValidationError as error:
        raise DomainError("DATA_INVALID", "; ".join(sorted(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()))) from None
    if data.id != pack_id:
        raise DomainError("DATA_PACK_MISMATCH", "The data model belongs to a different pack")
    return data


def load_data(pack_directory: str | Path, pack_id: str) -> DataModel | None:
    """The pack's data model, or None when the pack has no `data.json`."""
    path = Path(pack_directory) / DATA_FILE
    if not path.is_file():
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise DomainError("DATA_INVALID", f"{DATA_FILE} is not readable JSON") from error
    return parse_data(document, pack_id)


def data_for(pack: Pack) -> DataModel | None:
    """The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`."""
    draft = held(pack, DATA_FILE)
    if isinstance(draft, DataModel):
        return draft
    directory = pack_directory(pack)
    return load_data(directory, pack.id) if directory is not None else None


def _text(attribute: Attribute, raw: Any) -> Any:
    if not isinstance(raw, str):
        raise DomainError("FIELD_TYPE", f"{attribute.name} must be text")
    if len(raw) > attribute.max_length:
        raise DomainError("FIELD_TOO_LONG", f"{attribute.name} is longer than {attribute.max_length} characters")
    return raw


def _number(attribute: Attribute, raw: Any) -> Any:
    if isinstance(raw, bool) or not isinstance(raw, int | float):
        raise DomainError("FIELD_TYPE", f"{attribute.name} must be a number")
    return raw


def _boolean(attribute: Attribute, raw: Any) -> Any:
    if not isinstance(raw, bool):
        raise DomainError("FIELD_TYPE", f"{attribute.name} must be true or false")
    return raw


def _date(attribute: Attribute, raw: Any) -> Any:
    if not isinstance(raw, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise DomainError("FIELD_TYPE", f"{attribute.name} must be a date (YYYY-MM-DD)")
    try:
        date.fromisoformat(raw)
    except ValueError:
        raise DomainError("FIELD_TYPE", f"{attribute.name} is not a real date") from None
    return raw


def _choice(attribute: Attribute, raw: Any) -> Any:
    if raw not in attribute.choices:
        raise DomainError("FIELD_CHOICE", f"{attribute.name} must be one of: {', '.join(attribute.choices)}")
    return raw


_CHECKS = {"text": _text, "number": _number, "boolean": _boolean, "date": _date, "choice": _choice}


def check_values(entity: Entity, values: dict[str, Any]) -> dict[str, Any]:
    """Validate a record's values against its entity. Empty text and None count as missing. Returns the clean values."""
    known = {a.name for a in entity.attributes}
    unknown = sorted(set(values) - known)
    if unknown:
        raise DomainError("UNKNOWN_FIELD", f"{entity.name} has no attribute {unknown[0]}")
    clean: dict[str, Any] = {}
    for attribute in entity.attributes:
        raw = values.get(attribute.name)
        if raw is None or raw == "":
            if attribute.required:
                raise DomainError("FIELD_REQUIRED", f"{attribute.name} is required")
            continue
        clean[attribute.name] = _CHECKS[attribute.type](attribute, raw)
    return clean


def _check_reference(ref: Reference, raw: Any, exists: Callable[[str, str], bool]) -> str | None:
    """The clean id a reference field holds, or None when it is empty and may be."""
    if raw is None or raw == "":
        if ref.required:
            raise DomainError("FIELD_REQUIRED", f"{ref.name} is required")
        return None
    if not isinstance(raw, str) or len(raw) > REFERENCE_LENGTH:
        raise DomainError("FIELD_TYPE", f"{ref.name} must be the id of a {ref.target}")
    if not exists(ref.target, raw):
        raise DomainError("REFERENCE_UNKNOWN", f"No {ref.target} has the id {raw}")
    return raw


def check_record(data: DataModel, values: dict[str, Any], exists: Callable[[str, str], bool]) -> dict[str, Any]:
    """Validate a record's values: its attributes with `check_values`, then each reference field, which must hold the id
    of a stored object of its class (`exists(class, id)`; ADR-0235). Returns the clean values."""
    refs = {r.name: r for r in references(data)}
    clean = check_values(data.entity(data.record), {k: v for k, v in values.items() if k not in refs})
    for ref in refs.values():
        found = _check_reference(ref, values.get(ref.name), exists)
        if found is not None:
            clean[ref.name] = found
    return clean
