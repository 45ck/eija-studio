"""Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).

A scenario starts a new record (in the model's initial state unless it names another), then lists steps. Each step
is a fixture actor taking an action, and what must happen: the record moves to a state, or the kernel refuses with a
code. Scenarios decide nothing; they pin down what the kernel does, so a change to the model that alters it shows up
as a failing test. They live in an optional `scenarios.json` beside the pack's `pack.json` with their own digest.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError, model_validator

from .models import Contract, DomainError, fingerprint
from .pack import Pack, pack_directory

SCENARIOS_FILE = "scenarios.json"
NAME = r"^[A-Za-z][A-Za-z0-9_:-]{0,59}$"


class Then(Contract):
    """What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code)."""
    state: str | None = Field(default=None, pattern=NAME)
    refused: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_:]{0,59}$")

    @model_validator(mode="after")
    def one(self) -> Then:
        if (self.state is None) == (self.refused is None):
            raise ValueError("give exactly one of state or refused")
        return self


class ScenarioStep(Contract):
    actor: str = Field(min_length=1, max_length=60)  # a fixture actor id
    action: str = Field(pattern=NAME)
    then: Then


class Scenario(Contract):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,59}$")
    title: str = Field(min_length=1, max_length=120)
    start: str | None = Field(default=None, pattern=NAME)  # None starts where a new record starts
    steps: tuple[ScenarioStep, ...] = Field(min_length=1, max_length=40)


class Scenarios(Contract):
    schema_version: Literal["eija.scenarios.v1"] = "eija.scenarios.v1"
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")  # the pack these scenarios belong to
    scenarios: tuple[Scenario, ...] = Field(default=(), max_length=200)

    @model_validator(mode="after")
    def unique(self) -> Scenarios:
        ids = [s.id for s in self.scenarios]
        if len(set(ids)) != len(ids):
            raise ValueError("two scenarios share an id")
        return self

    @property
    def digest(self) -> str:
        return fingerprint(self)


def parse_scenarios(document: Any, pack_id: str) -> Scenarios:
    try:
        scenarios = Scenarios.model_validate(document)
    except ValidationError as error:
        raise DomainError("SCENARIOS_INVALID", "; ".join(sorted(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()))) from None
    if scenarios.id != pack_id:
        raise DomainError("SCENARIOS_PACK_MISMATCH", "The scenarios belong to a different pack")
    return scenarios


def load_scenarios(directory: str | Path, pack_id: str) -> Scenarios | None:
    """The scenarios in `directory`, or None when it has no `scenarios.json`."""
    path = Path(directory) / SCENARIOS_FILE
    if not path.is_file():
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise DomainError("SCENARIOS_INVALID", f"{SCENARIOS_FILE} is not readable JSON") from error
    return parse_scenarios(document, pack_id)


def scenarios_for(pack: Pack) -> Scenarios:
    """The scenarios beside this pack's `pack.json`, or none."""
    directory = pack_directory(pack)
    found = load_scenarios(directory, pack.id) if directory is not None else None
    return found if found is not None else Scenarios(id=pack.id)
