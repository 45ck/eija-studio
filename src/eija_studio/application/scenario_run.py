"""Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).

Every step is decided by `runtime.execute` on an in-memory session holding the pack's fixture actors, exactly as the
built app's kernel would decide it; nothing here re-encodes a rule. A scenario stops at its first step whose outcome
differs from what it expects, and that step names the diagram elements involved so PlayIDE can show it.

Pure: no IO, no clock, no randomness.
"""
from __future__ import annotations

from typing import Any

from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import check_policy
from eija_studio.domain.scenarios import Scenario, Scenarios, ScenarioStep, Then
from . import runtime
from .simulation import MemorySession

FORMAT = "eija.scenario-run.v1"
CASE = "scenario"


class _Record:
    """One record in an in-memory session, advanced one step at a time by the kernel."""

    def __init__(self, pack: Pack, model: Workflow, state: str):
        self.pack, self.model = pack, model
        self.session = MemorySession(pack)
        self.session.create_instance({"id": "r", "case_id": CASE, "model_hash": model.semantic_hash, "state": state, "version": 0})
        self.steps = 0

    @property
    def state(self) -> str:
        return str(self.session.instances["r"]["state"])

    def take(self, actor: str, action: str) -> Then:
        """What the kernel does when `actor` takes `action` now: the state it moves to, or its refusal code."""
        self.steps += 1
        version = self.session.instances["r"]["version"]
        command = ExecuteCommand(operation_id=f"op-{self.steps}", actor_id=actor, instance_id="r", action=action,
                                 expected_version=version)
        try:
            result = runtime.execute(self.session, CASE, self.model, command, pack=self.pack)  # type: ignore[arg-type]
        except DomainError as error:
            return Then(refused=error.code)
        return Then(state=result["instance"]["state"])


def _cells(model: Workflow, action: str, source: str, target: str | None) -> list[str]:
    """The diagram elements a step touches: its transition, if modelled, and the states it leaves and reaches."""
    transition = next((t for t in model.transitions if t.action == action), None)
    found = [f"state:{source}"] + ([f"transition:{transition.id}"] if transition else [])
    return found + ([f"state:{target}"] if target and target != source else [])


def _said(then: Then) -> str:
    return f"moves to {then.state}" if then.state else f"is refused ({then.refused})"


def _step_view(pack: Pack, model: Workflow, step: ScenarioStep, source: str, actual: Then | None) -> dict[str, Any]:
    actor = next((a for a in pack.fixtures.actors if a.id == step.actor), None)
    view = {"actor": step.actor, "role": actor.role if actor else None, "action": step.action, "from": source,
            "expect": step.then.model_dump(exclude_none=True)}
    if actual is None:
        return view | {"status": "NOT_RUN", "cells": _cells(model, step.action, source, None)}
    ok = actual == step.then
    return view | {"status": "PASS" if ok else "FAIL", "actual": actual.model_dump(exclude_none=True),
                   "why": f"Expected it {_said(step.then)}; it {_said(actual)}." if not ok else _said(actual).capitalize() + ".",
                   "cells": _cells(model, step.action, source, actual.state)}


def run_scenario(pack: Pack, model: Workflow, scenario: Scenario) -> dict[str, Any]:
    """Run one scenario; it stops at the first step whose outcome differs from what it expects."""
    start = scenario.start or model.initial_state
    head = {"id": scenario.id, "title": scenario.title, "start": start}
    if start not in model.states:
        return head | {"status": "FAIL", "why": f"It starts in {start}, which this model does not have.",
                       "steps": [_step_view(pack, model, s, start, None) for s in scenario.steps], "failed_step": None}
    record, steps, failed = _Record(pack, model, start), [], None
    for index, step in enumerate(scenario.steps):
        source = record.state
        view = _step_view(pack, model, step, source, None if failed is not None else record.take(step.actor, step.action))
        if view["status"] == "FAIL":
            failed = index
        steps.append(view)
    status = "PASS" if failed is None else "FAIL"
    return head | {"status": status, "steps": steps, "failed_step": failed,
                   "why": f"Step {failed + 1}: {steps[failed]['why']}" if failed is not None else f"All {len(steps)} step(s) behave as written."}


def run_scenarios(pack: Pack, model: Workflow, scenarios: Scenarios) -> dict[str, Any]:
    """Every scenario run on `model`; a model the policy refuses runs none of them."""
    if model.id != pack.id or scenarios.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", "The model or the scenarios do not belong to this pack")
    head = {"format": FORMAT, "pack": pack.id, "model": model.semantic_hash, "scenarios_digest": scenarios.digest}
    refused = check_policy(model, pack)
    if refused:
        return head | {"status": "REFUSED", "policy": sorted(refused), "passed": 0, "failed": 0,
                       "scenarios": [{"id": s.id, "title": s.title, "status": "NOT_RUN"} for s in scenarios.scenarios]}
    results = [run_scenario(pack, model, s) for s in scenarios.scenarios]
    failed = sum(1 for r in results if r["status"] == "FAIL")
    status = "EMPTY" if not results else ("FAIL" if failed else "PASS")
    return head | {"status": status, "passed": len(results) - failed, "failed": failed, "scenarios": results}


def record_steps(pack: Pack, model: Workflow, start: str | None, steps: list[tuple[str, str]]) -> list[dict[str, Any]]:
    """What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.

    This is how a person adds a test: try the steps, read what happened, and keep it if it is what should happen."""
    state = start or model.initial_state
    if state not in model.states:
        raise DomainError("STATE_UNKNOWN", f"{state} is not a state of this model")
    record = _Record(pack, model, state)
    return [ScenarioStep(actor=actor, action=action, then=record.take(actor, action)).model_dump(mode="json", exclude_none=True)
            for actor, action in steps]
