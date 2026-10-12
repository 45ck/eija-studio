"""The generated app's bounded navigation, derived from its existing contracts.

Destinations name actual React panels and existing use cases. They grant no
authority, introduce no HTTP routes and do not imply record update/delete support.
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from .data import DataModel
from .models import Contract, DomainError, Workflow, fingerprint
from .pack import Pack
from .screens import Screens, require_buildable


class RecordOperations(Contract):
    create: Literal["executable"] = "executable"
    read: Literal["executable"] = "executable"
    update: Literal["unsupported"] = "unsupported"
    delete: Literal["unsupported"] = "unsupported"


class Destination(Contract):
    id: str = Field(min_length=1, max_length=80)
    kind: Literal["records", "create", "detail", "action"]
    parent: str | None = Field(default=None, min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=60)
    panel: Literal["records", "create", "detail", "action-screen"]
    focus: Literal["records-title", "title", "detail-title", "action-screen"]
    record_required: bool = False
    use_case: str | None = Field(default=None, min_length=1, max_length=60)
    transition_ref: str | None = Field(default=None, pattern=r"^transition:[A-Z][A-Z0-9_-]{0,63}$")

    @model_validator(mode="after")
    def coherent(self) -> Destination:
        panels = {"records": ("records", "records-title", False), "create": ("create", "title", False),
                  "detail": ("detail", "detail-title", True), "action": ("action-screen", "action-screen", True)}
        if (self.panel, self.focus, self.record_required) != panels[self.kind]:
            raise ValueError("A destination must target its supported panel and record scope")
        if (self.kind == "action") != bool(self.use_case and self.transition_ref):
            raise ValueError("Only an action destination names a workflow use case and transition")
        if self.kind != "action" and (self.use_case is not None or self.transition_ref is not None):
            raise ValueError("Non-action destinations cannot name workflow actions")
        return self


class Navigation(Contract):
    schema_version: Literal["eija.navigation.v1"] = "eija.navigation.v1"
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    record: str | None = Field(default=None, pattern=r"^[A-Z][A-Za-z0-9]{0,39}$")
    capabilities: RecordOperations = Field(default_factory=RecordOperations)
    destinations: tuple[Destination, ...] = Field(min_length=3, max_length=67)

    @model_validator(mode="after")
    def coherent(self) -> Navigation:
        found = {item.id: item for item in self.destinations}
        if len(found) != len(self.destinations):
            raise ValueError("Duplicate navigation destination")
        _require_roots(found)
        for item in self.destinations:
            if item.id not in {"records", "new-record", "record-detail"} and (item.kind != "action" or item.parent != "record-detail"
                    or item.id != "action:" + str(item.transition_ref).removeprefix("transition:")):
                raise ValueError("Action destinations belong to record detail and their transition identity")
        return self

    @property
    def digest(self) -> str:
        return fingerprint(self)


def _require_roots(found: dict[str, Destination]) -> None:
    expected = {"records": ("records", None), "new-record": ("create", "records"),
                "record-detail": ("detail", "records")}
    for name, (kind, parent) in expected.items():
        if name not in found or (found[name].kind, found[name].parent) != (kind, parent):
            raise ValueError("Navigation needs the records, create and detail hierarchy")


def navigation_for(pack: Pack, model: Workflow, data: DataModel | None, screens: Screens) -> Navigation:
    """Project actual supported panels from one canonical workflow/data/screens snapshot."""
    if model.id != pack.id or screens.id != pack.id or (data is not None and data.id != pack.id):
        raise DomainError("NAVIGATION_PACK_MISMATCH", "Navigation contracts must belong to the same pack")
    require_buildable(screens, model, data)
    destinations = [Destination(id="records", kind="records", title="Records", panel="records", focus="records-title"),
                    Destination(id="new-record", kind="create", parent="records", title="New " + (data.record if data else "record"),
                                panel="create", focus="title"),
                    Destination(id="record-detail", kind="detail", parent="records", title="Record detail", panel="detail",
                                focus="detail-title", record_required=True)]
    for transition in sorted(model.transitions, key=lambda item: item.id):
        screen = screens.screen(transition.action)
        if screen is None:
            raise DomainError("NAVIGATION_SCREEN_MISSING", "A workflow action has no supported screen")
        destinations.append(Destination(id="action:" + transition.id, kind="action", parent="record-detail",
                                        title=screen.title, panel="action-screen", focus="action-screen", record_required=True,
                                        use_case=transition.action, transition_ref="transition:" + transition.id))
    return Navigation(id=pack.id, record=data.record if data else None, destinations=tuple(destinations))
