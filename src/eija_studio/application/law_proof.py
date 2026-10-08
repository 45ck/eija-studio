"""Prove a pack's laws over every run the kernel allows (ADR-0166).

The laws in `pack.json` (`domain/laws.py`) are the layer above the UML: what the model must never do, whatever is
drawn. The policy already judges them on the transition table. This module asks the stronger, runtime question for
any pack: is there ANY run, by ANY actor, from a new record, in which the kernel commits a step that breaks a law?

It explores the kernel's reachable configurations exhaustively. The kernel decides every step (`runtime.execute`
on an in-memory session); the laws are judged by `laws.evaluate_run` itself, so nothing here re-encodes either.

* Actors: every class the kernel can tell apart. `check_actor` reads only `active`, `role` and `assigned`, so one
  actor per role and per combination of the two flags, plus one actor holding a role the pack does not declare,
  stands for every possible actor.
* Configurations: the record's state plus the set of path-law waypoints (`path_requires.via`) it has passed. Every
  other law kind is judged per step, so this product is complete for the current law kinds; `LAW_HANDLING` names
  how each kind is judged and a test fails if a new kind is not classified.
* Each configuration is reached first by a shortest run, so a counterexample is the shortest run that breaks the law.
* A law about a state that is never reached, or an action that never commits, holds vacuously; that is reported.

Pure: no IO, no clock, no randomness. The same pack and model always give the same report.
"""
from __future__ import annotations

from collections import deque
from typing import Any

from eija_studio.domain.laws import LAW_KINDS, PathRequires, Step, applies, evaluate_run, evaluate_table
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import check_policy
from . import runtime
from .simulation import MemorySession

FORMAT = "eija.law-proof.v1"
MAX_CONFIGURATIONS = 20_000
OUTSIDER = "(undeclared role)"
LAW_HANDLING = {  # how each law kind is judged here
    "closed_shape": "table", "action_requires_guard": "table",  # about the table, not a run (evaluate_run skips them)
    "requires_evidence": "evidence",  # judged by the evidence matrix of a review
    "only_role_holds": "run", "role_never_holds": "run", "role_never_enters": "run", "state_only_via": "run",
    "action_target": "run", "action_source_in": "run", "forbidden_effects": "run", "state_final": "run",
    "path_requires": "run",
}
assert set(LAW_HANDLING) == set(LAW_KINDS), "classify every law kind"  # noqa: S101 - a module invariant
LIMITS = (
    "Exhaustive over every configuration a new record can reach and every class of actor the kernel distinguishes. "
    "It is about one record at a time; nothing here relates two records.",
    "The kernel decides each step on an in-memory session. Storage, transactions and replays are checked by the "
    "built app's conformance run, not here.",
)


def actor_classes(pack: Pack, model: Workflow) -> list[dict[str, Any]]:
    """One actor per role (declared or used) and per combination of `active` and `assigned`, and an outsider."""
    roles = sorted({r.id for r in pack.roles} | {t.role for t in model.transitions})
    outsider = OUTSIDER if OUTSIDER not in roles else OUTSIDER + "*"
    return [{"id": f"{role}|{'active' if active else 'inactive'}|{'assigned' if assigned else 'unassigned'}",
             "role": role, "active": active, "assigned": assigned}
            for role in [*roles, outsider] for active in (True, False) for assigned in (True, False)]


def _session(pack: Pack, actors: list[dict[str, Any]]) -> MemorySession:
    session = MemorySession(pack)
    session.actors = {a["id"]: a for a in actors}
    return session


def _try(pack: Pack, model: Workflow, actors: list[dict[str, Any]], state: str, actor: dict[str, Any],
         action: str) -> Step | None:
    """What the kernel does when this actor takes this action on a record in this state: the step, or None if refused."""
    session = _session(pack, actors)
    session.create_instance({"id": "r", "case_id": "proof", "model_hash": model.semantic_hash, "state": state, "version": 0})
    command = ExecuteCommand(operation_id="op", actor_id=actor["id"], instance_id="r", action=action, expected_version=0)
    try:
        result = runtime.execute(session, "proof", model, command, pack=pack)  # type: ignore[arg-type]
    except DomainError:
        return None
    return Step(action=action, role=actor["role"], source=state, target=result["instance"]["state"],
                effects=tuple(result["effects"]))


def _subject(law: Any) -> list[str]:
    """The model elements a law is about: its state, its waypoint and its action, where it names them."""
    refs = [f"state:{getattr(law, name)}" for name in ("state", "via") if isinstance(getattr(law, name, None), str)]
    return refs + ([f"action:{law.action}"] if isinstance(getattr(law, "action", None), str) else [])


def _step_view(step: Step) -> dict[str, Any]:
    return {"action": step.action, "role": step.role, "from": step.source, "to": step.target, "effects": list(step.effects)}


def _explore(pack: Pack, model: Workflow) -> dict[str, Any]:
    """Breadth-first over (state, waypoints passed); returns the steps found and the first run breaking each law."""
    laws = [law for law in pack.laws if LAW_HANDLING[law.kind] == "run"]
    waypoints = {law.via for law in laws if isinstance(law, PathRequires)}
    actions = {t.action for t in model.transitions}
    actors = actor_classes(pack, model)
    start = (model.initial_state, frozenset({model.initial_state} & waypoints))
    runs: dict[tuple[str, frozenset[str]], list[Step]] = {start: []}
    queue, committed, reached = deque([start]), set(), {model.initial_state}
    broken: dict[str, list[Step]] = {}
    while queue:
        node = queue.popleft()
        state, passed = node
        for action in sorted(actions):
            for actor in actors:
                step = _try(pack, model, actors, state, actor, action)
                if step is None:
                    continue
                committed.add(action)
                reached.add(step.target)
                run = [*runs[node], step]
                for violation in evaluate_run(laws, model.initial_state, run, actions):
                    broken.setdefault(violation.law, run)
                following = (step.target, passed | ({step.target} & waypoints))
                if following not in runs:
                    if len(runs) >= MAX_CONFIGURATIONS:
                        return {"complete": False, "configurations": len(runs), "broken": broken, "reached": reached,
                                "committed": committed, "actors": len(actors)}
                    runs[following] = run
                    queue.append(following)
    return {"complete": True, "configurations": len(runs), "broken": broken, "reached": reached, "committed": committed,
            "actors": len(actors)}


def _when(law: Any) -> str:
    when = law.when
    return (f"when {when.action_present} is modelled" if when.action_present else "") + \
        (" and " if when.action_present and when.action_absent else "") + \
        (f"when {when.action_absent} is not modelled" if when.action_absent else "")


def _verdict(law: Any, table: set[str], search: dict[str, Any] | None, actions: set[str]) -> dict[str, Any]:
    entry: dict[str, Any] = {"id": law.id, "kind": law.kind, "code": law.code, "description": law.description,
                             "method": LAW_HANDLING[law.kind], "subject": _subject(law)}
    if not applies(law, actions):
        return entry | {"status": "INACTIVE", "why": f"Applies only {_when(law)}."}
    if entry["method"] == "evidence":
        return entry | {"status": "EVIDENCE", "why": "Judged by the evidence a review collects, not by runs."}
    if entry["method"] == "table" or search is None:
        holds = law.id not in table
        return entry | {"status": "HOLDS" if holds else "BROKEN",
                        "why": "Checked on the transition table." if holds else "The transition table breaks it."}
    if law.id in search["broken"]:
        run = search["broken"][law.id]
        return entry | {"status": "BROKEN", "why": f"A run of {len(run)} step(s) breaks it.",
                        "counterexample": [_step_view(s) for s in run]}
    if not search["complete"]:
        return entry | {"status": "UNKNOWN", "why": f"The search stopped at {MAX_CONFIGURATIONS} configurations."}
    idle = [r for r in entry["subject"] if (r.startswith("state:") and r[6:] not in search["reached"])
            or (r.startswith("action:") and r[7:] not in search["committed"])]
    if idle:
        return entry | {"status": "VACUOUS", "why": "Holds only because nothing reaches it: " + ", ".join(idle) + "."}
    return entry | {"status": "HOLDS", "why": f"No run breaks it ({search['configurations']} configurations searched)."}


def prove_laws(pack: Pack, model: Workflow | None = None) -> dict[str, Any]:
    """Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict."""
    model = model if model is not None else pack.model
    if model.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", f"Workflow {model.id!r} does not belong to pack {pack.id!r}")
    table = {v.law for v in evaluate_table(pack.laws, model)}
    refused = check_policy(model, pack)
    search = None if refused else _explore(pack, model)
    actions = {t.action for t in model.transitions}
    verdicts = [_verdict(law, table, search, actions) for law in pack.laws]
    statuses = {v["status"] for v in verdicts}
    overall = ("REFUSED" if refused else "BROKEN" if "BROKEN" in statuses else "UNKNOWN" if "UNKNOWN" in statuses
               else "HOLDS")
    report: dict[str, Any] = {"format": FORMAT, "pack": pack.id, "model": model.semantic_hash, "status": overall,
                              "laws": verdicts, "limits": list(LIMITS)}
    if refused:
        return report | {"policy": sorted(refused),
                         "search": {"status": "NOT_RUN", "why": "The kernel refuses this model, so nothing runs."}}
    assert search is not None  # noqa: S101 - set whenever the policy accepts the model
    return report | {"search": {"status": "COMPLETE" if search["complete"] else "STOPPED",
                                "configurations": search["configurations"], "actor_classes": search["actors"],
                                "reached": sorted(search["reached"]),
                                "unreached": sorted(set(model.states) - search["reached"]),
                                "never_committed": sorted({t.action for t in model.transitions} - search["committed"])}}
