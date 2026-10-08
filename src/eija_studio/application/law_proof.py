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
from dataclasses import dataclass, field
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


@dataclass
class _Search:
    """What the breadth-first search found: configurations, what was reached and the first run breaking each law."""
    actors: int
    runs: dict[tuple[str, frozenset[str]], list[Step]] = field(default_factory=dict)
    broken: dict[str, list[Step]] = field(default_factory=dict)
    reached: set[str] = field(default_factory=set)
    committed: set[str] = field(default_factory=set)
    complete: bool = True


def _steps_from(pack: Pack, model: Workflow, actors: list[dict[str, Any]], state: str) -> list[Step]:
    """Every step the kernel commits from this state, over every action and actor class."""
    tried = (_try(pack, model, actors, state, actor, action)
             for action in sorted({t.action for t in model.transitions}) for actor in actors)
    return [step for step in tried if step is not None]


def _record(search: _Search, node: tuple[str, frozenset[str]], step: Step, laws: list[Any], model: Workflow,
            waypoints: set[str]) -> tuple[str, frozenset[str]] | None:
    """Judge the run that ends in `step`; return the configuration it leads to if it is new and may be explored."""
    search.committed.add(step.action)
    search.reached.add(step.target)
    run = [*search.runs[node], step]
    for violation in evaluate_run(laws, model.initial_state, run, {t.action for t in model.transitions}):
        search.broken.setdefault(violation.law, run)
    following = (step.target, node[1] | ({step.target} & waypoints))
    if following in search.runs:
        return None
    if len(search.runs) >= MAX_CONFIGURATIONS:
        search.complete = False
        return None
    search.runs[following] = run
    return following


def _explore(pack: Pack, model: Workflow) -> _Search:
    """Breadth-first over (state, waypoints passed), judging every committed run with the laws' own evaluator."""
    laws = [law for law in pack.laws if LAW_HANDLING[law.kind] == "run"]
    waypoints = {law.via for law in laws if isinstance(law, PathRequires)}
    actors = actor_classes(pack, model)
    start = (model.initial_state, frozenset({model.initial_state} & waypoints))
    search = _Search(actors=len(actors), runs={start: []}, reached={model.initial_state})
    queue = deque([start])
    while queue and search.complete:
        node = queue.popleft()
        for step in _steps_from(pack, model, actors, node[0]):
            following = _record(search, node, step, laws, model, waypoints)
            if following is not None:
                queue.append(following)
    return search


def _when(law: Any) -> str:
    when = law.when
    return (f"when {when.action_present} is modelled" if when.action_present else "") + \
        (" and " if when.action_present and when.action_absent else "") + \
        (f"when {when.action_absent} is not modelled" if when.action_absent else "")


def _idle(subject: list[str], search: _Search) -> list[str]:
    """The law's states never reached and actions never committed."""
    return [r for r in subject if (r.startswith("state:") and r[6:] not in search.reached)
            or (r.startswith("action:") and r[7:] not in search.committed)]


def _run_verdict(law: Any, subject: list[str], search: _Search) -> dict[str, Any]:
    if law.id in search.broken:
        run = search.broken[law.id]
        return {"status": "BROKEN", "why": f"A run of {len(run)} step(s) breaks it.",
                "counterexample": [_step_view(s) for s in run]}
    if not search.complete:
        return {"status": "UNKNOWN", "why": f"The search stopped at {MAX_CONFIGURATIONS} configurations."}
    idle = _idle(subject, search)
    if idle:
        return {"status": "VACUOUS", "why": "Holds only because nothing reaches it: " + ", ".join(idle) + "."}
    return {"status": "HOLDS", "why": f"No run breaks it ({len(search.runs)} configurations searched)."}


def _verdict(law: Any, table: set[str], search: _Search | None, actions: set[str]) -> dict[str, Any]:
    entry: dict[str, Any] = {"id": law.id, "kind": law.kind, "code": law.code, "description": law.description,
                             "method": LAW_HANDLING[law.kind], "subject": _subject(law)}
    if not applies(law, actions):
        return entry | {"status": "INACTIVE", "why": f"Applies only {_when(law)}."}
    if entry["method"] == "evidence":
        return entry | {"status": "EVIDENCE", "why": "Judged by the evidence a review collects, not by runs."}
    if entry["method"] == "run" and search is not None:
        return entry | _run_verdict(law, entry["subject"], search)
    if law.id in table:
        return entry | {"status": "BROKEN", "why": "The transition table breaks it."}
    return entry | {"status": "HOLDS", "why": "Checked on the transition table."}


def _overall(refused: list[str], verdicts: list[dict[str, Any]]) -> str:
    statuses = {v["status"] for v in verdicts}
    return next((s for s in ("BROKEN", "UNKNOWN") if s in statuses), "HOLDS") if not refused else "REFUSED"


def _summary(model: Workflow, search: _Search | None) -> dict[str, Any]:
    if search is None:
        return {"status": "NOT_RUN", "why": "The kernel refuses this model, so nothing runs."}
    return {"status": "COMPLETE" if search.complete else "STOPPED", "configurations": len(search.runs),
            "actor_classes": search.actors, "reached": sorted(search.reached),
            "unreached": sorted(set(model.states) - search.reached),
            "never_committed": sorted({t.action for t in model.transitions} - search.committed)}


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
    report = {"format": FORMAT, "pack": pack.id, "model": model.semantic_hash, "status": _overall(refused, verdicts),
              "laws": verdicts, "search": _summary(model, search), "limits": list(LIMITS)}
    return report | ({"policy": sorted(refused)} if refused else {})
