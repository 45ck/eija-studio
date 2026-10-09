"""What's missing (ADR-0216): one list across every model and view of what is not ready yet, so a system built in
chat or on the canvas says what it still lacks instead of the person having to look in each tab.

Each view gets a row: ready, or the things it is missing, each in words with where to fix it. Nothing here decides
anything new. Every item restates a check the IDE already has: the screens' design check, the scenarios run by the
kernel, the laws proved by the kernel, reachability on the state machine, and who can take what. A view with no law or
no test is "missing", not failing: an empty file proves nothing, and the list says so rather than showing green.
"""
from __future__ import annotations

from typing import Any

from eija_studio.domain.data import DataModel
from eija_studio.domain.laws import reachable
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.scenarios import Scenarios
from eija_studio.domain.screens import Screens, check_screens

from .law_proof import prove_laws
from .scenario_run import run_scenarios

VIEWS = (("states", "State machine"), ("classes", "Class diagram"), ("usecases", "Use cases and permissions"),
         ("screens", "Screens"), ("tests", "Tests and sequences"), ("laws", "Laws"))


def _item(text: str, fix: str, kind: str = "missing") -> dict[str, str]:
    return {"kind": kind, "text": text, "fix": fix}


def _states(model: Workflow) -> list[dict[str, str]]:
    edges = [(t.from_state, t.to_state) for t in model.transitions]
    reach = reachable(edges, model.initial_state)
    return [_item(f"{s} cannot be reached from {model.initial_state}", f"Add a transition into {s}, or remove it", "problem")
            for s in model.states if s not in reach]


def _classes(data: DataModel | None) -> list[dict[str, str]]:
    if data is None:
        return [_item("There is no class diagram, so records have only a title", "Start the system from a sketch or a description")]
    record = data.entity(data.record)
    if [a.name for a in record.attributes] == ["title"]:
        return [_item(f"{record.name} has only a title, so the app's form has one field",
                      "Ask in chat: add field <name> as text|number|date|boolean|choice <A>, <B>")]
    return []


def _use_cases(pack: Pack, model: Workflow) -> list[dict[str, str]]:
    takers = {t.role for t in model.transitions}
    idle = [r.id for r in pack.roles if r.id not in takers]
    return [_item(f"{role} takes no action", f"Allow {role} to take an action, or leave it out") for role in idle]


def _screens(screens: Screens, model: Workflow, data: DataModel | None) -> list[dict[str, str]]:
    return [_item(p["text"], "Fix it in Screens, or accept the follow-on the Changes view suggests", "problem")
            for p in check_screens(screens, model, data)]


def _tests(pack: Pack, model: Workflow, scenarios: Scenarios) -> list[dict[str, str]]:
    if not scenarios.scenarios:
        return [_item("No test cases, so no sequence diagram and nothing pins down what the kernel does",
                      "Record one in Tests: try the steps, keep what should happen")]
    run = run_scenarios(pack, model, scenarios)
    items = [_item(f"Test “{s['title']}” fails: {s.get('why') or 'a step does something else now'}",
                   "Open Tests: change the model back, or record what should happen now", "problem")
             for s in run["scenarios"] if s["status"] == "FAIL"]
    tested = {step.action for s in scenarios.scenarios for step in s.steps}
    return items + [_item(f"No test takes {action}", f"Record a test in Tests that takes {action}")
                    for action in dict.fromkeys(t.action for t in model.transitions) if action not in tested]


def _laws(pack: Pack, model: Workflow) -> list[dict[str, str]]:
    if not pack.laws:
        end = next((s for s in model.states if s not in {t.from_state for t in model.transitions}), None)
        example = f" (for example: {end} is final)" if end else ""
        return [_item("No laws, so nothing is proved about this system", f"Write one in Laws{example}; laws are yours to set, never the AI's")]
    proof = prove_laws(pack, model)
    return [_item(f"Law {v['id']} is {v['status'].lower()}: {v['why']}", "Open Laws to see why", "problem")
            for v in proof["laws"] if v["status"] in ("BROKEN", "UNKNOWN")]


def missing(pack: Pack, model: Workflow, data: DataModel | None, screens: Screens, scenarios: Scenarios) -> dict[str, Any]:
    """Every view's row: what it is missing or what is wrong with it, or nothing when it is ready."""
    found: dict[str, list[dict[str, str]]] = {"states": _states(model), "classes": _classes(data), "usecases": _use_cases(pack, model),
             "screens": _screens(screens, model, data), "tests": _tests(pack, model, scenarios), "laws": _laws(pack, model)}
    views = [{"view": key, "label": label, "ready": not found[key], "items": found[key]} for key, label in VIEWS]
    return {"views": views, "ready": sum(not found[key] for key, _ in VIEWS), "of": len(views),
            "count": sum(len(items) for items in found.values())}
