"""The data-model and role-kind phrases of the offline plan proposer (ADR-0202, #156): add a field to a class, remove
one, make one required or optional, and say what kind of actor holds a role. They apply only to a system the person
started; on a shipped pack the class diagram and the roles are the owner's. Like every phrase, what they read is an
untrusted proposal that the application re-checks.
"""
from __future__ import annotations

import re
from typing import Any

from eija_studio.application.new_system import FIELD as FIELD_NAME
from eija_studio.application.new_system import classes
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import Pack

TYPES = {"text": "text", "number": "number", "date": "date", "boolean": "boolean", "yes/no": "boolean", "choice": "choice"}
FIELD = r"(?:field|attribute)"
KINDS = {"person": "human", "human": "human", "ai agent": "agent", "agent": "agent", "bot": "agent", "timer": "timer",
         "scheduled job": "timer", "external system": "system", "system": "system"}  # ADR-0210 kinds of actor, in words
KIND = "(" + "|".join(sorted(KINDS, key=len, reverse=True)) + ")"
Classes = tuple[str, dict[str, list[str]]]  # the record class, and each class's attribute names


class DataPhrases:
    """The phrase handlers a clause reader (`plan_proposals._Clause`) gets for the class diagram and roles' kinds."""

    pack: Pack
    grows: bool
    fields: list[str]

    def role(self, name: str) -> str:
        raise NotImplementedError

    def _kind(self, made: str | None, named: str | None, kind: str) -> dict[str, Any]:
        """Who holds a role (#156, ADR-0210): only on a system you started, like the class diagram."""
        if not self.grows:
            raise DomainError("PLAN_DATA_FIXED", "This system's roles are its owner's; chat says who holds one only on a system you started")
        return {"kind": "set_role_kind", "role": self.role(made or named or ""), "to": KINDS[kind.lower()]}

    def _data(self) -> Classes:
        """The class diagram a data-model phrase changes: only on a system you started (ADR-0202)."""
        if not self.grows:
            raise DomainError("PLAN_DATA_FIXED", "This system's class diagram is its owner's; chat adds fields only on a system you started")
        data = classes(self.pack)
        if data is None:
            raise DomainError("PLAN_UNKNOWN_NAME", "This system has no class diagram to add a field to")
        return data

    def _class(self, data: Classes, name: str | None) -> str:
        if name is None:
            return data[0]
        found = next((e for e in data[1] if e.casefold() == name.casefold()), None)
        if found is None:
            raise DomainError("PLAN_UNKNOWN_NAME", f"The class diagram has no class {name}")
        return found

    def _field(self, data: Classes, entity: str, name: str) -> str:
        names = data[1][entity] + self.fields
        found = next((n for n in names if n.casefold() == name.casefold()), None)
        if found is None:
            raise DomainError("PLAN_UNKNOWN_NAME", f"{entity} has no field {name}")
        return found

    def _add_field(self, first: str | None, name: str, entity: str | None, kind: str | None, options: str | None,
                   last: str | None) -> dict[str, Any]:
        data = self._data()
        field = name[:1].lower() + name[1:]
        if not re.fullmatch(FIELD_NAME, field):
            raise DomainError("PLAN_UNKNOWN_NAME", f"A field is named with letters, digits and _ (not {name})")
        type_ = TYPES[(kind or "text").lower()]
        choices = [c.strip() for c in re.split(r",|\bor\b", options or "") if c.strip()]
        if (type_ == "choice") != bool(choices):
            raise DomainError("PLAN_UNKNOWN_NAME", "A choice field lists its choices, for example: as choice Small, Medium, Large")
        self.fields.append(field)
        required = "required" in f"{first or ''} {last or ''}".lower()
        attribute = {"name": field, "type": type_, "required": required} | ({"choices": choices} if choices else {})
        return {"kind": "add_attribute", "entity": self._class(data, entity), "attribute": attribute}

    def _remove_field(self, name: str, entity: str | None) -> dict[str, Any]:
        data = self._data()
        found = self._class(data, entity)
        return {"kind": "remove_attribute", "entity": found, "name": self._field(data, found, name)}

    def _require(self, name: str, how: str) -> dict[str, Any]:
        data = self._data()
        return {"kind": "set_required", "entity": data[0], "name": self._field(data, data[0], name),
                "required": how.lower() == "required"}
