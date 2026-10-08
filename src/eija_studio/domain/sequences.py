"""Sequences: UML interactions between the pack's actors and its records, kept beside the pack (ADR-0185).

A sequence diagram here is a scenario: who sends which action to which record, in order. Lifelines are the pack's
fixture actors (`<actor id> : <role>`) and the records the scenario names; a message is an action. Combined
fragments are the three UML operators a scenario over a state machine needs:

* `opt [guard]`: the operand may or may not happen; what follows must work either way.
* `alt [guard] / [guard]`: one of two to four operands happens; what follows must work after each.
* `neg`: the operand is an invalid trace. The kernel must refuse it, optionally with a named refusal code.

Operands hold messages only; fragments do not nest. This file only describes sequences: whether the model can produce
one is decided by the kernel (`application.sequences`), never here. They live in an optional `sequences.json` beside the
pack's `pack.json`, with their own digest. A pack without one gets scenarios generated from the model in force.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError, model_validator

from .models import Contract, DomainError, fingerprint

SEQUENCES_FILE = "sequences.json"
RECORD = r"^[a-z][a-z0-9-]{0,23}$"
ACTION = r"^[A-Za-z][A-Za-z0-9_]{0,59}$"


class Message(Contract):
    actor: str = Field(min_length=1, max_length=80)  # a fixture actor's id; the kernel refuses one it does not know
    action: str = Field(pattern=ACTION)  # need not be modelled: an unmodelled action is the kernel's refusal to show
    record: str = Field(default="", max_length=24)  # empty: the interaction's first record


class Operand(Contract):
    guard: str = Field(default="", max_length=60)
    steps: tuple[Message, ...] = Field(min_length=1, max_length=20)


class Fragment(Contract):
    fragment: Literal["opt", "alt", "neg"]
    operands: tuple[Operand, ...] = Field(min_length=1, max_length=4)
    refused: str | None = Field(default=None, pattern=r"^[A-Z][A-Z_:]{0,59}$")  # neg only: the refusal code expected

    @model_validator(mode="after")
    def shape(self) -> Fragment:
        if self.fragment == "alt" and len(self.operands) < 2:
            raise ValueError("An alt fragment has two to four operands")
        if self.fragment != "alt" and len(self.operands) != 1:
            raise ValueError(f"An {self.fragment} fragment has exactly one operand")
        if self.refused is not None and self.fragment != "neg":
            raise ValueError("Only a neg fragment names the refusal it expects")
        return self


Step = Message | Fragment


class Interaction(Contract):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    title: str = Field(min_length=1, max_length=80)
    records: tuple[str, ...] = Field(default=("record",), min_length=1, max_length=3)
    steps: tuple[Step, ...] = Field(min_length=1, max_length=40)

    @model_validator(mode="after")
    def known_records(self) -> Interaction:
        if len(set(self.records)) != len(self.records) or not all(re.fullmatch(RECORD, r) for r in self.records):
            raise ValueError("Record names are distinct, lower case and short")
        named = {m.record for m in messages(self.steps) if m.record}
        if named - set(self.records):
            raise ValueError("A message names a record the interaction does not declare: " + ", ".join(sorted(named - set(self.records))))
        return self

    def record_of(self, message: Message) -> str:
        return message.record or self.records[0]


class Sequences(Contract):
    schema_version: Literal["eija.sequences.v1"] = "eija.sequences.v1"
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")  # the pack these sequences belong to
    sequences: tuple[Interaction, ...] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def unique(self) -> Sequences:
        ids = [s.id for s in self.sequences]
        if len(set(ids)) != len(ids):
            raise ValueError("Two sequences share an id")
        return self

    @property
    def digest(self) -> str:
        return fingerprint(self)


def messages(steps: tuple[Step, ...]) -> list[Message]:
    """Every message, fragments' operands included, in reading order."""
    out: list[Message] = []
    for step in steps:
        out += [step] if isinstance(step, Message) else [m for o in step.operands for m in o.steps]
    return out


def parse_sequences(document: Any, pack_id: str) -> Sequences:
    try:
        sequences = Sequences.model_validate(document)
    except ValidationError as error:
        raise DomainError("SEQUENCES_INVALID", "; ".join(sorted(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()))) from None
    if sequences.id != pack_id:
        raise DomainError("SEQUENCES_PACK_MISMATCH", "The sequences belong to a different pack")
    return sequences


def load_sequences(pack_directory: str | Path, pack_id: str) -> Sequences | None:
    """The pack's sequences, or None when the pack has no `sequences.json`."""
    path = Path(pack_directory) / SEQUENCES_FILE
    if not path.is_file():
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise DomainError("SEQUENCES_INVALID", f"{SEQUENCES_FILE} is not readable JSON") from error
    return parse_sequences(document, pack_id)
