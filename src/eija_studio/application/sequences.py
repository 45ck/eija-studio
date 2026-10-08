"""The pack's scenarios drawn as UML sequence diagrams the kernel checks (ADR-0185).

There is one source of scenarios: `scenarios.json` (`domain.scenarios`, ADR-0177), run by `scenario_run`. A sequence
diagram is a view of one scenario: the actors and the record are lifelines, each step is a call from its actor to the
record, a step that expects a move shows the record's state after it as a UML state invariant, and a step that
expects a refusal is a `neg` combined fragment, the UML for a trace that must not happen. Each message's verdict is
the kernel's own answer for that step:

* OK: the kernel did what the step expects; the record moved to the state it names.
* HOLDS: a `neg` step the kernel refused, with the code the step names.
* BROKEN: the kernel did something else. The step's sentence and the kernel's reason say what.
* NOT_REACHED: an earlier step was broken, so the scenario stopped there.

A sequence is PRODUCIBLE when no step is BROKEN. With `base`, the model in force, every scenario is also run on it, so
a change shows which scenarios it breaks or fixes, and each message carries its action's status in the change
(`ghost_diff`, ADR-0176). `sequence_layout` places the result, so the page only draws boxes and arrows at the
coordinates it is given. What this does NOT establish: that a scenario is the right one, or anything about actors
the pack does not list; scenarios are examples, the laws (ADR-0166) are the universal claims.
"""
from __future__ import annotations

import re
from typing import Any

from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.scenarios import Scenario, Scenarios
from .ghost_diff import ghost_diff
from .scenario_run import run_scenario
from .sequence_layout import export, place

FORMAT = "eija.sequence-check.v1"
WHY = {
    "ACTION_DENIED": "{action} is not in the model",
    "STATE_DENIED": "{action} does not leave {state}",
    "ROLE_DENIED": "{actor} is a {role}; {action} is for a {needs}",
    "ASSIGNMENT_DENIED": "{actor} is not assigned, and {action} needs an assigned {needs}",
    "ACTOR_REVOKED": "{actor} is not active",
    "UNKNOWN_ACTOR": "{actor} is not one of the pack's actors",
}
LIMITS = ["Each sequence is a scenario from the pack's scenarios.json (the Tests tab's test cases), run by the pack's fixture actors on one record.",
          "A step that expects a refusal is drawn as a neg fragment. Scenarios have no opt, alt or loop yet, so neither do these diagrams."]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:24] or "record"


def record_name(pack: Pack) -> tuple[str, str]:
    """The record lifeline's name and its class: `loan : Loan` when the pack has a data model."""
    data = data_for(pack)
    return ("record", "Record") if data is None else (_slug(data.record), data.record)


def _reason(pack: Pack, model: Workflow, step: dict[str, Any]) -> str:
    """The kernel's refusal of a step in words, from its code, the actor's role and the transition's."""
    actor = next((a for a in pack.fixtures.actors if a.id == step["actor"]), None)
    t = next((t for t in model.transitions if t.action == step["action"]), None)
    code = step["actual"]["refused"]
    template = WHY.get(code, "the kernel refused it with {code}")
    return template.format(action=step["action"], state=step["from"], actor=step["actor"], role=actor.role if actor else "?",
                           needs=t.role if t else "?", code=code)


def _verdict(pack: Pack, model: Workflow, step: dict[str, Any]) -> dict[str, Any]:
    """One step's verdict from what `scenario_run` reported for it."""
    if step["status"] == "NOT_RUN":
        return {"verdict": "NOT_REACHED", "code": None, "states": [], "why": "Not reached: an earlier step did not do what the scenario says"}
    actual = step["actual"]
    out = {"code": actual.get("refused"), "states": [actual["state"]] if "state" in actual else []}
    if step["status"] == "PASS":
        neg = "refused" in step["expect"]
        why = f"The kernel refused it with {actual['refused']}, as the scenario expects" if neg else f"The kernel committed {step['action']}; the record is {actual['state']}"
        return out | {"verdict": "HOLDS" if neg else "OK", "why": why}
    reason = f": {_reason(pack, model, step)}" if "refused" in actual else ""
    return out | {"verdict": "BROKEN", "why": step["why"].rstrip(".") + reason}


def _effects(model: Workflow, step: dict[str, Any]) -> list[str]:
    """The effects the model requires of the transition a committed step took."""
    t = next((t for t in model.transitions if t.action == step["action"] and t.from_state == step["from"]), None)
    return list(t.required_effects) if t and "state" in step.get("actual", {}) else []


def _status(ghost: dict[str, Any] | None, action: str) -> str:
    """The action's status in the change (ADR-0176): same, added, removed, changed or moved."""
    if ghost is None:
        return "same"
    edge = next((e for e in ghost["transitions"] if e["action"] == action and not e["key"].startswith("was:")), None)
    return str(edge["status"]) if edge else "same"


def _producible(run: dict[str, Any]) -> str:
    return "PRODUCIBLE" if run["status"] == "PASS" else "BROKEN"


def _compare(pack: Pack, placed: dict[str, Any], base: Workflow | None, scenario: Scenario, ghost: dict[str, Any] | None) -> dict[str, Any] | None:
    """Each message's action status in the change and, on the model in force, its verdict there; returns that run."""
    was = run_scenario(pack, base, scenario) if base is not None else None
    for m in placed["messages"]:
        m["change"] = _status(ghost, m["action"])
        if was is not None and base is not None:
            m["was"] = _verdict(pack, base, was["steps"][int(m["ref"])])["verdict"]
    return was


def _one(pack: Pack, model: Workflow, scenario: Scenario, base: Workflow | None, ghost: dict[str, Any] | None, record: tuple[str, str]) -> dict[str, Any]:
    run = run_scenario(pack, model, scenario)
    steps = [_verdict(pack, model, s) | {"step": s, "effects": _effects(model, s)} for s in run["steps"]]
    placed = place(pack, scenario, run["start"], steps, record)
    was = _compare(pack, placed, base, scenario, ghost)
    broken = [m for m in placed["messages"] if m["verdict"] == "BROKEN"]
    first = broken[0]["why"] if broken else (run["why"] if run["status"] == "FAIL" else None)
    out = {"id": scenario.id, "title": scenario.title, "verdict": _producible(run), "first_problem": first, "broken": len(broken),
           "steps": len(placed["messages"]), **placed, "export": export(scenario.title, placed)}
    if was is not None:
        before, after = _producible(was), out["verdict"]
        out |= {"was": before, "change": "same" if before == after else "breaks" if after == "BROKEN" else "fixes"}
    return out


def _vocabulary(pack: Pack, model: Workflow) -> dict[str, Any]:
    """What the editor offers: the fixture actors, every action the model or the pack names, and the model's states."""
    return {"actors": [{"id": a.id, "role": a.role, "active": a.active, "assigned": a.assigned} for a in pack.fixtures.actors],
            "actions": sorted({t.action for t in model.transitions} | {a.id for a in pack.actions}),
            "states": list(model.states), "initial": model.initial_state}


def check_sequences(pack: Pack, model: Workflow, scenarios: Scenarios, base: Workflow | None = None) -> dict[str, Any]:
    """Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also
    on it, for the change."""
    if scenarios.id != pack.id:
        raise DomainError("SCENARIOS_PACK_MISMATCH", "The scenarios belong to a different pack")
    before = base if base is not None and base.semantic_hash != model.semantic_hash else None
    ghost = ghost_diff(before, model) if before is not None else None
    record = record_name(pack)
    checked = [_one(pack, model, s, before, ghost, record) for s in scenarios.scenarios]
    broken = sum(s["verdict"] == "BROKEN" for s in checked)
    return {"format": FORMAT, "model": model.semantic_hash, "base": (base or model).semantic_hash, "changed": before is not None,
            "document": scenarios.model_dump(mode="json", exclude_none=True), "digest": scenarios.digest,
            "status": "BROKEN" if broken else "PRODUCIBLE", "counts": {"producible": len(checked) - broken, "broken": broken},
            "sequences": checked, "limits": LIMITS, **_vocabulary(pack, model)}
