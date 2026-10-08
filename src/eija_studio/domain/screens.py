"""Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).

A screen belongs to one use case: creating a record (`use_case` null, so no workflow action, whatever its name, can
collide with it) or an action of the workflow. It lists the record
attributes it shows, in order and with their labels, and names its button. Screens decide how the app looks, never
what it may do: who may act, when and with what effect stays with the kernel. They live in an optional
`screens.json` beside the pack's `pack.json` with their own digest; a pack without one gets `default_screens`.
Authored screens are completed with a default screen for each use case they leave out, so a new action always has
one. `check_screens` is the design check PlayIDE runs as you edit, and an app is never built from screens it rejects.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError, model_validator

from .data import ATTRIBUTE_NAME, Attribute, DataModel
from .models import Contract, DomainError, Workflow, fingerprint
from .pack import Pack, pack_directory

SCREENS_FILE = "screens.json"
CREATE = None  # the use case that starts a record; every other use case is a workflow action, named by the action


class ScreenField(Contract):
    attribute: str = Field(pattern=ATTRIBUTE_NAME)
    label: str = Field(default="", max_length=60)  # empty shows the attribute's own name


class Screen(Contract):
    use_case: str | None = Field(default=CREATE, min_length=1, max_length=60)
    title: str = Field(min_length=1, max_length=60)
    fields: tuple[ScreenField, ...] = Field(default=(), max_length=40)
    button: str = Field(default="", max_length=40)  # empty shows the use case's name

    @model_validator(mode="after")
    def unique(self) -> Screen:
        names = [f.attribute for f in self.fields]
        if len(set(names)) != len(names):
            raise ValueError("An attribute appears twice on one screen")
        return self


class Screens(Contract):
    schema_version: Literal["eija.screens.v1"] = "eija.screens.v1"
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")  # the pack these screens belong to
    screens: tuple[Screen, ...] = Field(min_length=1, max_length=80)

    @property
    def digest(self) -> str:
        return fingerprint(self)

    def screen(self, use_case: str | None) -> Screen | None:
        return next((s for s in self.screens if s.use_case == use_case), None)


def parse_screens(document: Any, pack_id: str) -> Screens:
    try:
        screens = Screens.model_validate(document)
    except ValidationError as error:
        raise DomainError("SCREENS_INVALID", "; ".join(sorted(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()))) from None
    if screens.id != pack_id:
        raise DomainError("SCREENS_PACK_MISMATCH", "The screens belong to a different pack")
    return screens


def load_screens(pack_directory: str | Path, pack_id: str) -> Screens | None:
    """The pack's screens, or None when the pack has no `screens.json`."""
    path = Path(pack_directory) / SCREENS_FILE
    if not path.is_file():
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise DomainError("SCREENS_INVALID", f"{SCREENS_FILE} is not readable JSON") from error
    return parse_screens(document, pack_id)


def use_cases(model: Workflow) -> list[str | None]:
    """Creating a record (None), then each distinct action in transition-id order: the ellipses of the use case diagram."""
    actions: list[str] = []
    for t in sorted(model.transitions, key=lambda t: t.id):
        if t.action not in actions:
            actions.append(t.action)
    return [CREATE, *actions]


def _default_screen(case: str | None, attributes: tuple[Attribute, ...], record: str) -> Screen:
    shown = attributes if case is CREATE else tuple(a for a in attributes if a.required)
    return Screen(use_case=case, title=f"New {record}" if case is CREATE else str(case),
                  fields=tuple(ScreenField(attribute=a.name) for a in shown), button="Create" if case is CREATE else str(case))


def default_screens(pack: Pack, model: Workflow, data: DataModel | None) -> Screens:
    """One screen per use case: `create` asks for every record attribute; an action shows the required ones."""
    attributes = data.entity(data.record).attributes if data else ()
    record = data.record if data else "record"
    return Screens(id=pack.id, screens=tuple(_default_screen(case, attributes, record) for case in use_cases(model)))


def screens_for(pack: Pack, model: Workflow, data: DataModel | None) -> Screens:
    """The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults."""
    defaults = default_screens(pack, model, data)
    directory = pack_directory(pack)
    found = load_screens(directory, pack.id) if directory is not None else None
    if found is None:
        return defaults
    missing = [s for s in defaults.screens if found.screen(s.use_case) is None]
    return Screens(id=pack.id, screens=(*found.screens, *missing))


def _problem(code: str, use_case: str | None, text: str) -> dict[str, Any]:
    return {"code": code, "use_case": use_case, "text": text}


def _screen_problems(screen: Screen, known: set[str], required: set[str]) -> list[dict[str, Any]]:
    shown = {f.attribute for f in screen.fields}
    problems = [_problem("SCREEN_UNKNOWN_ATTRIBUTE", screen.use_case, f"{screen.title} shows {name}, which the record does not have")
                for name in sorted(shown - known)]
    if screen.use_case is CREATE:
        problems += [_problem("SCREEN_MISSING_REQUIRED", screen.use_case,
                              f"{screen.title} does not ask for {name}, which is required: nobody could create a record")
                     for name in sorted(required - shown)]
    return problems


def _coverage(screens: Screens, cases: list[str | None]) -> list[dict[str, Any]]:
    """Screens for use cases the model lacks, second screens for one use case, and use cases without a screen."""
    problems: list[dict[str, Any]] = []
    seen: set[str | None] = set()
    for screen in screens.screens:
        if screen.use_case not in cases:
            problems.append(_problem("SCREEN_UNKNOWN_USE_CASE", screen.use_case, f"{screen.title} is for {screen.use_case}, which the model does not have"))
        elif screen.use_case in seen:
            problems.append(_problem("SCREEN_DUPLICATE_USE_CASE", screen.use_case, f"{screen.use_case or 'Creating a record'} has more than one screen"))
        seen.add(screen.use_case)
    if CREATE not in seen:
        problems.append(_problem("SCREEN_MISSING_CREATE", CREATE, "There is no screen to create a record"))
    return problems + [_problem("SCREEN_MISSING_USE_CASE", case, f"{case} has no screen")
                       for case in cases if case is not CREATE and case not in seen]


def check_screens(screens: Screens, model: Workflow, data: DataModel | None) -> list[dict[str, Any]]:
    """Design problems, each with a stable code and the use case it is about. Empty means the screens can be built."""
    attributes = data.entity(data.record).attributes if data else ()
    known, required = {a.name for a in attributes}, {a.name for a in attributes if a.required}
    fields = [p for screen in screens.screens for p in _screen_problems(screen, known, required)]
    return _coverage(screens, use_cases(model)) + fields


def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None:
    problems = check_screens(screens, model, data)
    if problems:
        raise DomainError("SCREENS_BLOCKED", "The screens have design problems; no app is built",
                          {"codes": sorted({p["code"] for p in problems})})
