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
from collections.abc import Callable
from typing import Any

from eija_studio.domain.data import Attribute
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack, PackError, parse_pack
from eija_studio.domain.scenarios import Scenarios, parse_scenarios

from .new_system import RECORD, checked_documents, sketch_documents, summary
from .ports import SystemDescriber
from .scenario_run import record_steps, run_scenarios
from .sequence_draft import journeys

MAX_DESCRIPTION = 4000


def _fields(raw: Any) -> list[dict[str, Any]]:
    """The describer's fields as data-model attributes; one the data model would refuse is a problem, never dropped."""
    if not isinstance(raw, list):
        raise PackError(["the describer gave no list of fields"])
    try:
        return [Attribute.model_validate(f).model_dump(mode="json") for f in raw]
    except ValueError as error:
        raise PackError([f"field: {error}"]) from None


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "case"


def _case(pack: Pack, model: Workflow, title: str, steps: list[tuple[str, str]]) -> dict[str, Any]:
    return {"id": _slug(title), "title": title, "steps": record_steps(pack, model, None, steps)}


def _refusal(pack: Pack, model: Workflow) -> dict[str, Any] | None:
    """The first step out of the initial state in the model's own order (the one a person reads first), taken by an
    actor whose role may not take it."""
    first = next((t for t in model.transitions if t.from_state == model.initial_state), None)
    if first is None:
        return None
    other = next((a for a in pack.fixtures.actors if a.role != first.role and a.active and a.assigned), None)
    return None if other is None else _case(pack, model, f"{other.role} cannot {first.action}", [(other.id, first.action)])


def _end_cases(pack: Pack, record: str, model: Workflow) -> list[dict[str, Any]]:
    """The way to each end state (`sequence_draft.journeys`, the drafting the Sequences tab uses), recorded by the kernel."""
    return [_case(pack, model, f"{record} reaches {state}", steps) for state, steps in journeys(pack, model)]


def tests_for(pack: Pack, record: str, model: Workflow | None = None) -> dict[str, Any]:
    """Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a
    role that may not take it. They pin down what the kernel does now, so a later change that alters it shows.
    `model` is the model to record on (the pack's own when None)."""
    model = pack.model if model is None else model
    scenarios = _end_cases(pack, record, model)
    refusal = _refusal(pack, model)
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


def update_tests(pack: Pack, model: Workflow, scenarios: Scenarios, record: str) -> dict[str, Any]:
    """The tests brought up to date with `model`, for the person to keep or not (What's missing's "Update the tests",
    ADR-0216). A test that still passes stays as it is. A failing one is recorded again by the kernel when the model
    still has its way (the same id from `tests_for`), and is dropped when it has none: its end state or step is gone.
    The way to a new end state is added. Nothing is saved: the result is a draft of `scenarios.json`."""
    run = {s["id"]: s["status"] for s in run_scenarios(pack, model, scenarios)["scenarios"]}
    fresh = {s["id"]: s for s in _end_cases(pack, record, model)}
    kept, changes = [], []
    for scenario in scenarios.model_dump(mode="json", exclude_none=True)["scenarios"]:
        if run.get(scenario["id"]) != "FAIL":
            kept.append(scenario)
        elif scenario["id"] in fresh:
            kept.append(fresh[scenario["id"]] | {"title": scenario["title"]})
            changes.append({"change": "recorded again", "title": scenario["title"]})
        else:
            changes.append({"change": "removed", "title": scenario["title"]})
    ids = {s["id"] for s in kept}
    for scenario in fresh.values():
        if scenario["id"] not in ids and scenario["id"] not in run:
            kept.append(scenario)
            changes.append({"change": "added", "title": scenario["title"]})
    document = {"schema_version": "eija.scenarios.v1", "id": pack.id, "scenarios": kept}
    parse_scenarios(document, pack.id)  # the kernel's own check of the file, as for any draft
    return {"document": document, "changes": changes}
