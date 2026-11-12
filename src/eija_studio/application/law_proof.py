"""Prove a pack's laws over every run the kernel allows (ADR-0166).

The laws in `pack.json` (`domain/laws.py`) are the layer above the UML: what the model must never do, whatever is
drawn. The policy already judges them on the transition table. This module asks the stronger, runtime question for
any pack: is there ANY run, by ANY actor, from a new record, in which the kernel commits a step that breaks a law?

It explores the kernel's reachable configurations exhaustively. The kernel decides every step (`runtime.execute`
on an in-memory session); the laws are judged by `laws.evaluate_run` itself, so nothing here re-encodes either.

* Actors: every class the kernel can tell apart. `check_actor` reads only `active`, `role` and `assigned`, so one
  actor per role and per combination of the two flags, plus one actor holding a role the pack does not declare,
  stands for every possible actor.
* Configurations: the record's state plus the set of path-law waypoints (`path_requires.via`) it has passed and of
  the `path_requires_kind` laws whose kind of actor has already taken a step (ADR-0210), and the record's values
  where the model has guards over them: one search per combination its guards can tell apart (ADR-0234). Every other law kind is
  judged per step, so this product is complete for the current law kinds; `LAW_HANDLING` names
  how each kind is judged and a test fails if a new kind is not classified.
* Time events (`after(14 days)`, ADR-0237): time can always pass, so each step is tried once the longest of them is
  due. Waiting only makes more steps possible, never fewer, so this is every run the kernel allows.
* Linked objects (ADR-0241): a configuration also holds the state of each object the record links to, starting in its
  lifecycle's initial state, and a record's step carries its moves forward. Other records may link to the same object,
  so between steps an object may take any move of its lifecycle; that changes no step of this record's run.
* `can_reach_end` is about the runs a record could still take, not one run: it is judged on the steps the kernel
  committed during the search, so a record is stuck only where the kernel itself leaves no way to an end (ADR-0221).
* `distinct_actors` (separation of duties, ADR-0233) is about who acted, which the actor classes above do not track.
  It is judged by asking the kernel directly: wherever one of its actions can directly follow another on a reachable
  record, one actor takes the first, then holds the role of the second and tries it, and must be refused; a different
  actor must not be refused for separation.
* Each configuration is reached first by a shortest run, so a counterexample is the shortest run that breaks the law.
* A law about a state that is never reached, or an action that never commits, holds vacuously; that is reported.

Pure: no IO, no clock, no randomness. The same pack and model always give the same report.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from eija_studio.domain.laws import (LAW_KINDS, CanReachEnd, DistinctActors, PathRequires, PathRequiresKind, Step, applies,
                                     evaluate_run, evaluate_table, stuck_states)
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.linked import admitting, advance, drift
from eija_studio.domain.pack import Pack, PackError, parse_pack
from eija_studio.domain.policy import check_policy
from eija_studio.domain.value_guards import MAX_VALUATIONS, valuations
from . import runtime
from .memo import model_hash
from .simulation import MemorySession

FORMAT = "eija.law-proof.v1"
MAX_CONFIGURATIONS = 20_000
OUTSIDER = "(undeclared role)"
Passed = str | tuple[str, str]  # in a configuration: a waypoint state passed, or ("law", id) of a path_requires_kind law met
Objects = tuple[tuple[str, str], ...]  # each linked object's state, by link, sorted (ADR-0241); () without any
Node = tuple[str, frozenset[Passed], int, Objects]  # a configuration: state, what it has passed, which record values
# (index) and where its linked objects are
LAW_HANDLING = {  # how each law kind is judged here
    "closed_shape": "table", "action_requires_guard": "table",  # about the table, not a run (evaluate_run skips them)
    "requires_evidence": "evidence",  # judged by the evidence matrix of a review
    "can_reach_end": "reach",  # judged on every step the kernel committed in the search
    "distinct_actors": "kernel",  # judged by asking the kernel about one actor taking two of its actions
    "only_role_holds": "run", "role_never_holds": "run", "role_never_enters": "run", "state_only_via": "run",
    "action_target": "run", "action_source_in": "run", "forbidden_effects": "run", "state_final": "run",
    "path_requires": "run", "only_kind_holds": "run", "only_kind_enters": "run", "path_requires_kind": "run",
}
assert set(LAW_HANDLING) == set(LAW_KINDS), "classify every law kind"  # noqa: S101 - a module invariant
STOPPED = (f"The search stopped at its limit: {MAX_CONFIGURATIONS} configurations, or {MAX_VALUATIONS} combinations of "
           "record values for the value guards.")
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
         action: str, values: dict[str, Any], objects: dict[str, str] | None = None) -> Step | None:
    """What the kernel does when this actor takes this action on a record in this state holding these values, with its
    linked objects in these states: the step, or None if refused."""
    session = _session(pack, actors)
    session.create_instance({"id": "r", "case_id": "proof", "model_hash": model_hash(model), "state": state, "version": 0})
    session.record_values["r"] = dict(values)
    for link, at in (objects or {}).items():
        session.link("r", link, link, at)
    session.wait(model.longest_wait)  # time may always pass, so every time event is due (ADR-0237)
    command = ExecuteCommand(operation_id="op", actor_id=actor["id"], instance_id="r", action=action, expected_version=0)
    try:
        result = runtime.execute(session, "proof", model, command, pack=pack)  # type: ignore[arg-type]
    except DomainError:
        return None
    return Step(action=action, role=actor["role"], source=state, target=result["instance"]["state"],
                effects=tuple(result["effects"]))


def _subject(law: Any) -> list[str]:
    """The model elements a law is about: its state, its waypoint, its ends and its actions, where it names them."""
    refs = [f"state:{getattr(law, name)}" for name in ("state", "via") if isinstance(getattr(law, name, None), str)]
    refs += [f"state:{end}" for end in law.states] if isinstance(law, CanReachEnd) else []
    refs += [f"action:{a}" for a in law.actions] if isinstance(law, DistinctActors) else []
    return refs + ([f"action:{law.action}"] if isinstance(getattr(law, "action", None), str) else [])


def _step_view(step: Step) -> dict[str, Any]:
    view = {"action": step.action, "role": step.role, "from": step.source, "to": step.target, "effects": list(step.effects)}
    return view | ({"actor": step.actor} if step.actor else {})


@dataclass
class _Search:
    """What the breadth-first search found: configurations, what was reached and the first run breaking each law."""
    actors: int
    runs: dict[Node, list[Step]] = field(default_factory=dict)
    broken: dict[str, list[Step]] = field(default_factory=dict)
    valuations: list[dict[str, Any]] = field(default_factory=lambda: [{}])  # the record values tried (ADR-0234)
    broken_values: dict[str, int] = field(default_factory=dict)  # which record values each broken law's run held
    reached: set[str] = field(default_factory=set)
    committed: set[str] = field(default_factory=set)
    edges: dict[int, set[tuple[Any, Any]]] = field(default_factory=dict)  # per record values: (state, objects) moves
    complete: bool = True
    objects: Objects = ()  # where a new record's linked objects start (ADR-0241)


def _steps_from(pack: Pack, model: Workflow, actors: list[dict[str, Any]], state: str, values: dict[str, Any],
                objects: Objects = ()) -> list[tuple[Step, Objects]]:
    """Every step the kernel commits from this state, for a record holding these values with its linked objects in
    these states, over every action and actor class; each with where it leaves the objects (ADR-0241)."""
    found = []
    for action in sorted({t.action for t in model.transitions}):
        for actor in actors:
            step = _try(pack, model, actors, state, actor, action, values, dict(objects))
            after = advance(model, model.transition_for(action, state), dict(objects)) if step is not None else None
            if step is not None and after is not None:
                found.append((step, tuple(sorted(after.items()))))
    return list(dict.fromkeys(found))


def _passed(step: Step, waypoints: set[str], signers: list[PathRequiresKind]) -> set[Passed]:
    """What this step adds to a configuration: the waypoint (a state name) it enters, and a ("law", id) mark for each
    `path_requires_kind` law whose kind of actor took it."""
    marks: set[Passed] = {("law", law.id) for law in signers if law.counts(step.role)}
    return marks | ({step.target} & waypoints)


def _record(search: _Search, node: Node, step: Step, objects: Objects, laws: list[Any], model: Workflow,
            waypoints: set[str]) -> Node | None:
    """Judge the run that ends in `step`; return the configuration it leads to if it is new and may be explored."""
    search.committed.add(step.action)
    search.reached.add(step.target)
    run = [*search.runs[node], step]
    for violation in evaluate_run(laws, model.initial_state, run, {t.action for t in model.transitions}):
        if violation.law not in search.broken:
            search.broken[violation.law], search.broken_values[violation.law] = run, node[2]
    passed = node[1] | _passed(step, waypoints, [x for x in laws if isinstance(x, PathRequiresKind)])
    return _enter(search, node, (step.target, passed, node[2], objects), run)


def _enter(search: _Search, node: Node, following: Node, run: list[Step]) -> Node | None:
    """Note the move from `node` to `following`; return `following` if it is new and may be explored."""
    search.edges.setdefault(node[2], set()).add(((node[0], node[3]), (following[0], following[3])))
    if following in search.runs:
        return None
    if len(search.runs) >= MAX_CONFIGURATIONS:
        search.complete = False
        return None
    search.runs[following] = run
    return following


def _start(model: Workflow, waypoints: set[str], actors: int) -> _Search:
    """A search with one new record per combination of values (one with none for a model without value guards);
    stopped before it begins when there are too many combinations to try."""
    tried = valuations(model)
    passed = frozenset({model.initial_state} & waypoints)
    objects = tuple(sorted((o.link, o.initial) for o in model.objects))
    starts: list[Node] = [(model.initial_state, passed, i, objects) for i in range(len(tried or [{}]))]
    return _Search(actors=actors, runs={start: [] for start in starts}, reached={model.initial_state},
                   valuations=tried or [{}], complete=tried is not None, objects=objects)


def _explore(pack: Pack, model: Workflow) -> _Search:
    """Breadth-first over (state, waypoints passed, record values, linked objects' states), judging every committed run with the laws' own
    evaluator. A record's values never change, so each combination its value guards can tell apart starts a search."""
    laws = [law for law in pack.laws if LAW_HANDLING[law.kind] == "run"]
    waypoints = {law.via for law in laws if isinstance(law, PathRequires)}
    actors = actor_classes(pack, model)
    search = _start(model, waypoints, len(actors))
    queue = deque(search.runs)
    while queue and search.complete:
        node = queue.popleft()
        found = [_record(search, node, step, objects, laws, model, waypoints)
                 for step, objects in _steps_from(pack, model, actors, node[0], search.valuations[node[2]], node[3])]
        queue.extend(f for f in found + _drifted(search, node, model) if f is not None)
    return search


def _drifted(search: _Search, node: Node, model: Workflow) -> list[Node | None]:
    """Another record moves one of this record's shared objects: a new configuration, and this record's run is unchanged."""
    return [_enter(search, node, (node[0], node[1], node[2], tuple(sorted(moved.items()))), search.runs[node])
            for moved in drift(model, dict(node[3]))]


def _act(session: MemorySession, pack: Pack, model: Workflow, actor: dict[str, Any], action: str,
         n: int) -> tuple[Step | None, str]:
    """One step on the shared record `r` of `session`: the step, or None and the kernel's refusal code."""
    session.actors[actor["id"]] = dict(actor)
    session.wait(model.longest_wait)
    item = session.instances["r"]
    _ready(session, model, action, item["state"])
    command = ExecuteCommand(operation_id=f"op-{n}", actor_id=actor["id"], instance_id="r", action=action,
                             expected_version=item["version"])
    try:
        result = runtime.execute(session, "proof", model, command, pack=pack)  # type: ignore[arg-type]
    except DomainError as refused:
        return None, refused.code
    return Step(action=action, role=actor["role"], source=item["state"], target=result["instance"]["state"],
                effects=tuple(result["effects"]), actor=actor["id"]), ""


def _ready(session: MemorySession, model: Workflow, action: str, state: str) -> None:
    """Put the objects `action` moves from `state` where it can move them, so a pair of steps is judged on its actors."""
    for link, at in (admitting(model, model.transition_for(action, state)) or {}).items():
        session.link("r", link, link, at)


def _pair(pack: Pack, model: Workflow, first: Any, then: str, tried: list[dict[str, Any]]) -> tuple[list[Step], str, str]:
    """One actor takes `first`, is then given the role that takes `then` and tries it; then a different actor tries.
    The record holds values both transitions' value guards admit. Returns the steps committed and the two refusal
    codes ("" when the kernel committed)."""
    second = model.transition_for(then, first.to_state)
    values = next((v for v in tried if first.admits(v) is None and (second is None or second.admits(v) is None)), None)
    if values is None:
        return [], "", ""
    session = MemorySession(pack)
    session.create_instance({"id": "r", "case_id": "proof", "model_hash": model_hash(model), "state": first.from_state, "version": 0})
    session.record_values["r"] = dict(values)
    actor = {"id": "same", "role": first.role, "active": True, "assigned": True}
    step, _ = _act(session, pack, model, actor, first.action, 1)
    if step is None or second is None:
        return [], "", ""
    again, same_code = _act(session, pack, model, actor | {"role": second.role}, then, 2)
    if again is not None:
        return [step, again], "", ""
    _, other_code = _act(session, pack, model, {"id": "other", "role": second.role, "active": True, "assigned": True}, then, 3)
    return [step], same_code, other_code


def _following(model: Workflow, law: DistinctActors, reached: set[str]) -> list[tuple[Any, str]]:
    """Each transition of a listed action from a reached state, with each other listed action leaving where it ends."""
    follows = {(t.from_state, t.action) for t in model.transitions}
    return [(t, then) for t in model.transitions if t.action in law.actions and t.from_state in reached
            for then in law.actions if then != t.action and (t.to_state, then) in follows]


def _pair_breach(run: list[Step], other: str) -> dict[str, Any] | None:
    """What is wrong with one checked pair: the same actor let through, or a different actor refused for separation."""
    if len(run) == 2:
        return {"status": "BROKEN", "why": "The kernel let one actor take two of these actions on a record.",
                "counterexample": [_step_view(s) for s in run]}
    if other == "SEPARATION_DENIED":
        return {"status": "BROKEN", "why": "The kernel refused a different actor too.", "counterexample": [_step_view(s) for s in run]}
    return None


def _separation_verdict(pack: Pack, model: Workflow, law: DistinctActors, search: _Search) -> dict[str, Any]:
    """Every place one of the law's actions directly follows another on a record the kernel can reach."""
    checked = [(run, other) for t, then in _following(model, law, search.reached)
               for run, _same, other in [_pair(pack, model, t, then, search.valuations)] if run]
    breach = next((b for run, other in checked if (b := _pair_breach(run, other)) is not None), None)
    if breach is not None:
        return breach
    if not checked:
        return {"status": "VACUOUS", "why": "No reachable record lets one of these actions directly follow another."}
    return {"status": "HOLDS", "why": f"In each of {len(checked)} place(s) where one of these actions follows another, the "
            "kernel refused the same actor and did not refuse a different one for separation."}


def _kernel_verdicts(pack: Pack, model: Workflow, search: _Search | None) -> dict[str, dict[str, Any]]:
    """The verdict of each law judged by asking the kernel directly; none when the kernel refuses the model."""
    if search is None:
        return {}
    return {law.id: _separation_verdict(pack, model, law, search) for law in pack.laws if isinstance(law, DistinctActors)}


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
                "counterexample": [_step_view(s) for s in run]} | _values_view(search, search.broken_values[law.id])
    if not search.complete:
        return {"status": "UNKNOWN", "why": STOPPED}
    idle = _idle(subject, search)
    if idle:
        return {"status": "VACUOUS", "why": "Holds only because nothing reaches it: " + ", ".join(idle) + "."}
    return {"status": "HOLDS", "why": f"No run breaks it ({len(search.runs)} configurations searched)."}


def _values_view(search: _Search, index: int) -> dict[str, Any]:
    """The record values a counterexample ran on, shown only for a model with value guards."""
    return {"record_values": search.valuations[index]} if any(search.valuations) else {}


def _stuck(law: CanReachEnd, search: _Search, initial: str) -> tuple[list[str], int]:
    """Every state a record can be stuck in, under any of the record values tried, and the first values stuck in the
    first of them (0 when none is stuck)."""
    found = {i: _stuck_in(law, search, i, initial) for i in range(len(search.valuations))}
    stuck = sorted({s for states in found.values() for s in states})
    return stuck, next((i for i, states in found.items() if stuck and stuck[0] in states), 0)


def _stuck_in(law: CanReachEnd, search: _Search, index: int, initial: str) -> list[str]:
    """The states a record holding the `index`-th values can be stuck in. Without linked objects this is the laws' own
    `stuck_states`; with them, a record is stuck where no move of the record or of its objects leads to an end."""
    edges = search.edges.get(index, set())
    if not search.objects:
        return stuck_states(law, {(a[0], b[0]) for a, b in edges}, initial)
    reached = _closure(edges, [(initial, search.objects)])
    ending = _closure({(b, a) for a, b in edges}, [n for n in reached if n[0] in law.states])
    return sorted({n[0] for n in reached - ending})


def _closure(edges: set[tuple[Any, Any]], starts: list[Any]) -> set[Any]:
    """Every node reachable from `starts` along `edges`."""
    graph: dict[Any, set[Any]] = {}
    for source, target in edges:
        graph.setdefault(source, set()).add(target)
    seen, frontier = set(starts), list(starts)
    while frontier:
        for following in graph.get(frontier.pop(), set()) - seen:
            seen.add(following)
            frontier.append(following)
    return seen


def _reach_verdict(law: CanReachEnd, search: _Search, initial: str) -> dict[str, Any]:
    """Stuck states for each set of record values: values never change, so a record stuck with some values is stuck."""
    if not search.complete:
        return {"status": "UNKNOWN", "why": STOPPED}
    stuck, index = _stuck(law, search, initial)
    if not stuck:
        return {"status": "HOLDS", "why": f"From each of the {len(search.reached)} reachable states a run still reaches an end."}
    run = min((r for (state, _, i, _o), r in search.runs.items() if state == stuck[0] and i == index), key=len)
    return {"status": "BROKEN", "why": "A record can get stuck in " + ", ".join(stuck) + ": no step from there leads to an end.",
            "counterexample": [_step_view(s) for s in run], "stuck": stuck} | _values_view(search, index)


def _verdict(law: Any, table: set[str], search: _Search | None, actions: set[str], initial: str = "",
             kernel: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    entry: dict[str, Any] = {"id": law.id, "kind": law.kind, "code": law.code, "description": law.description,
                             "method": LAW_HANDLING[law.kind], "subject": _subject(law)}
    if not applies(law, actions):
        return entry | {"status": "INACTIVE", "why": f"Applies only {_when(law)}."}
    if entry["method"] == "evidence":
        return entry | {"status": "EVIDENCE", "why": "Judged by the evidence a review collects, not by runs."}
    if entry["method"] == "run" and search is not None:
        return entry | _run_verdict(law, entry["subject"], search)
    if entry["method"] == "reach" and search is not None:
        return entry | _reach_verdict(law, search, initial)
    if kernel and law.id in kernel:
        return entry | kernel[law.id]
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
    kernel = _kernel_verdicts(pack, model, search)
    verdicts = [_verdict(law, table, search, actions, model.initial_state, kernel) for law in pack.laws]
    report = {"format": FORMAT, "pack": pack.id, "model": model.semantic_hash, "status": _overall(refused, verdicts),
              "laws": verdicts, "search": _summary(model, search), "limits": list(LIMITS)}
    return report | ({"policy": sorted(refused)} if refused else {})


def with_laws(pack: Pack, laws: list[Any]) -> Pack:
    """The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.

    Nothing is saved: the draft is proved and shown, and the person decides whether to write it into `pack.json`."""
    document = pack.model_dump(mode="json") | {"laws": laws}
    try:
        return parse_pack(document)
    except PackError as error:
        raise DomainError("LAWS_INVALID", "; ".join(error.diagnostics), {"problems": list(error.diagnostics)}) from None


def compare_laws(before: Pack, after: Pack) -> dict[str, list[str]]:
    """Which laws a draft adds, removes or changes. Removing or changing a law can loosen what the kernel refuses."""
    old, new = {law.id: law for law in before.laws}, {law.id: law for law in after.laws}
    return {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new)),
            "changed": sorted(i for i in set(old) & set(new) if old[i] != new[i])}
