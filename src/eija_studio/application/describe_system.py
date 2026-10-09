"""Describe your app (ADR-0216): a new system from one description, like starting an app in Lovable or Replit.

A describer (an application port; offline here) reads the description as an app shape: a record class, a state
machine in the sketch's label notation, roles and the record's fields. Nothing it says is trusted. The documents are
built exactly as a sketch's are (`new_system.sketch_documents`, ADR-0185), the fields are added to the record class
and checked by the data model's own contract, and test cases are recorded by running the kernel: the path to each end
state and one refusal, each step written as what the kernel did (`scenario_run.record_steps`). Laws are not
generated: a law is protected policy, so the person writes it (the Laws tab), and "What's missing" says none is set.
Every other view (use cases, screens, sequences, components, permissions) is derived from these documents as for any
system.
"""
from __future__ import annotations

import re
from collections import deque
from collections.abc import Callable
from typing import Any

from eija_studio.domain.data import Attribute
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack, PackError, parse_pack

from .new_system import RECORD, checked_documents, sketch_documents, summary
from .ports import SystemDescriber
from .scenario_run import record_steps

MAX_DESCRIPTION = 4000


def _fields(raw: Any) -> list[dict[str, Any]]:
    """The describer's fields as data-model attributes; one the data model would refuse is a problem, never dropped."""
    if not isinstance(raw, list):
        raise PackError(["the describer gave no list of fields"])
    try:
        return [Attribute.model_validate(f).model_dump(mode="json") for f in raw]
    except ValueError as error:
        raise PackError([f"field: {error}"]) from None


def _arrivals(model: Workflow) -> dict[str, Any]:
    """For each reachable state, the transition that first reaches it breadth-first (None for the initial state)."""
    came: dict[str, Any] = {model.initial_state: None}
    queue = deque([model.initial_state])
    while queue:
        state = queue.popleft()
        for t in model.transitions:
            if t.from_state == state and t.to_state not in came:
                came[t.to_state] = t
                queue.append(t.to_state)
    return came


def _paths(model: Workflow) -> list[list[Any]]:
    """The shortest path of transitions from the initial state to each end state (one nothing leaves), in model order."""
    leaves = {t.from_state for t in model.transitions}
    came = _arrivals(model)
    paths = []
    for end in (s for s in model.states if s not in leaves and s != model.initial_state and s in came):
        path: list[Any] = []
        at = end
        while came[at] is not None:
            path.insert(0, came[at])
            at = came[at].from_state
        paths.append(path)
    return paths


def _actor(pack: Pack, role: str) -> str | None:
    return next((a.id for a in pack.fixtures.actors if a.role == role and a.active and a.assigned), None)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "case"


def _case(pack: Pack, title: str, steps: list[tuple[str, str]]) -> dict[str, Any]:
    return {"id": _slug(title), "title": title, "steps": record_steps(pack, pack.model, None, steps)}


def _refusal(pack: Pack) -> dict[str, Any] | None:
    """The first step out of the initial state, taken by an actor whose role may not take it."""
    model = pack.model
    first = next((t for t in model.transitions if t.from_state == model.initial_state), None)
    if first is None:
        return None
    other = next((a for a in pack.fixtures.actors if a.role != first.role and a.active and a.assigned), None)
    return None if other is None else _case(pack, f"{other.role} cannot {first.action}", [(other.id, first.action)])


def tests_for(pack: Pack, record: str) -> dict[str, Any]:
    """Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a
    role that may not take it. They pin down what the kernel does now, so a later change that alters it shows."""
    scenarios = []
    for path in _paths(pack.model):
        steps = [(_actor(pack, t.role) or "", t.action) for t in path]
        if path and all(actor for actor, _ in steps):
            scenarios.append(_case(pack, f"{record} reaches {path[-1].to_state}", steps))
    refusal = _refusal(pack)
    return {"schema_version": "eija.scenarios.v1", "id": pack.id, "scenarios": scenarios + ([refusal] if refusal else [])}


def _read(text: str, describer: SystemDescriber) -> dict[str, Any]:
    """What the describer reads in `text`, with a record name the kernel accepts; `PackError` otherwise."""
    if not 1 <= len(text) <= MAX_DESCRIPTION:
        raise PackError([f"description: say what the app is for in 1 to {MAX_DESCRIPTION} characters"])
    try:
        read = describer.describe(text)
    except DomainError as error:
        raise PackError([error.message]) from None
    record = str(read.get("record") or "Record")
    if not RECORD.match(record):
        raise PackError([f"record: the describer named {record!r}, not a UML class name"])
    return read | {"record": record}


def describe_documents(text: str, name: str, id_for: Callable[[str], str],
                       describer: SystemDescriber) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """The documents of a new system described in `text`, checked by the kernel, and what the describer read. The
    system is called `name`, or what the describer calls it; `id_for` gives the pack id for a name."""
    read = _read(text.strip(), describer)
    record = read["record"]
    called = name.strip() or str(read.get("name") or record + "s")[:80]
    documents = sketch_documents(called, record, str(read.get("sketch") or ""), id_for(called))
    documents["data.json"]["entities"][0]["attributes"] += [f for f in _fields(read.get("fields", [])) if f["name"] != "title"]
    documents["scenarios.json"] = tests_for(parse_pack(documents["pack.json"]), record)
    reading = {"provider": describer.name, "live": describer.live, "template": read.get("template"),
               "reading": [str(x)[:300] for x in read.get("reading", [])][:8]}
    return checked_documents(documents), reading  # the same checks every new system's documents pass


def described_summary(documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """What a described system has in every view, for the form to say before it is created."""
    base = summary(documents)
    record = documents["data.json"]["entities"][0]
    return base | {"fields": [a["name"] for a in record["attributes"]],
                   "tests": [s["title"] for s in documents["scenarios.json"]["scenarios"]], "laws": 0}
