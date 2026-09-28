"""Does the real runtime agree with the TLA+ model? Two independent measurements.

1. State-graph comparison (exhaustive within a bound). TLC prints, for every reachable state of the
   spec, the outcome code of every command and the successor of every committing command and every
   environment step. Python explores the same bounded space by driving the REAL `application.runtime.execute`
   against an ephemeral SQLite sandbox from the real initial state, abstracts every result with
   `Harness.abstract`, and the two tables are compared cell by cell.
2. Trace validation. Sequences (scripted scenarios, shortest paths to every reachable state with
   replay/cross-actor probes, and seeded random walks with revocation and assignment changes) are
   executed on the real runtime with real commits; each step's observed outcome and post-state are
   handed to TLC, which checks that the spec produces the same outcome and the same state.

What agreement establishes: within the bound and the abstraction (see abstraction.py), the spec's
decision procedure and the runtime's produce the same outcome codes and state changes. What it does
not: behaviour beyond the bound, concurrency across connections, crashes (tested elsewhere), fields
outside the abstraction, or that either side is right about the intended policy.
"""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

from eija_studio.domain.models import DomainError, Workflow

from .abstraction import Harness, Key
from .model import (MUTABLE_ACTORS, UNKNOWN_ACTORS, action_universe, command_sequence, directory,
                    environment_sequence)
from .tlc import top_level_values

Sandbox = Callable[[], Any]


class _Discard(Exception):
    """Raised inside a scratch transaction to roll it back."""


@dataclass
class Node:
    outcomes: tuple[str, ...]
    succ: tuple[Key | None, ...]
    env: tuple[Key, ...]


@dataclass
class Graph:
    initial: Key
    nodes: dict[Key, Node]
    cmds: list[dict[str, Any]]
    envs: list[dict[str, Any]]
    executions: int = 0
    defects: list[dict[str, Any]] = field(default_factory=list)  # runtime-side findings that are not spec diffs


# ------------------------------------------------------------------------------------ python side

def explore(workflow: Workflow, ops: int, sandbox: Sandbox) -> Graph:
    """Breadth-first exploration of the bounded state space through the real runtime."""
    harness = Harness(workflow, ops)
    cmds, envs = command_sequence(ops), environment_sequence()
    graph = Graph(initial=(), nodes={}, cmds=cmds, envs=envs)
    with sandbox() as store:
        with store.transaction() as u:
            graph.initial = harness.start(u)
        frontier: deque[Key] = deque([graph.initial])
        while frontier:
            key = frontier.popleft()
            if key in graph.nodes:
                continue
            try:
                with store.transaction() as u:
                    graph.nodes[key] = _expand(harness, u, key, graph)
                    raise _Discard
            except _Discard:
                pass
            node = graph.nodes[key]
            frontier.extend(k for k in (*node.succ, *node.env) if k is not None and k not in graph.nodes)
    return graph


def _expand(h: Harness, u: Any, key: Key, graph: Graph) -> Node:
    h.concretise(u, key)
    if h.abstract(u) != key:
        graph.defects.append({"kind": "concretise_roundtrip", "key": key})
    before = h.light(u)
    outcomes: list[str] = []
    succ: list[Key | None] = []
    for cmd in graph.cmds:
        u.db.execute("SAVEPOINT probe")
        code, result = h.run(u, cmd)
        graph.executions += 1
        if code == "COMMITTED":
            succ.append(h.abstract(u))
        else:
            succ.append(None)
            if code != "DUPLICATE":
                u.db.execute("ROLLBACK TO probe")  # the real transaction rolls back on every raised error
            if h.light(u) != before:
                graph.defects.append({"kind": "state_changed_without_commit", "key": key, "cmd": cmd, "outcome": code})
            if code == "DUPLICATE":
                _check_replay_result(h, key, cmd, result, graph)
        u.db.execute("ROLLBACK TO probe")
        u.db.execute("RELEASE probe")
        outcomes.append(code)
    env_next: list[Key] = []
    for env in graph.envs:
        u.db.execute("SAVEPOINT probe")
        h.environment(u, env)
        env_next.append(h.abstract(u))
        u.db.execute("ROLLBACK TO probe")
        u.db.execute("RELEASE probe")
    return Node(tuple(outcomes), tuple(succ), tuple(env_next))


def _check_replay_result(h: Harness, key: Key, cmd: dict[str, Any], result: dict | None, graph: Graph) -> None:
    """A replay must hand back the ORIGINAL result, not a recomputed one."""
    stored = key[3][h.ops.index(cmd["op"])]
    original = (result or {}).get("original_result", {}).get("instance", {})
    if not stored or (original.get("state"), original.get("version")) != (stored[3], stored[4]):
        graph.defects.append({"kind": "replay_result_differs", "key": key, "cmd": cmd})


# ---------------------------------------------------------------------------------------- TLC side

def parse_dump(path: Path) -> Graph:
    """Read the states TLC printed with the dump configuration (Emit in Excursion.tla)."""
    header: tuple | None = None
    nodes: dict[Key, Node] = {}
    initial: Key = ()
    with path.open(encoding="utf-8", errors="replace") as handle:
        for value in top_level_values(handle):
            if value[0] == "HEADER":
                header = value
            elif value[0] == "STATE":
                _, key, outcomes, succ, env = value
                if not nodes:
                    initial = key  # TLC prints the initial state first
                nodes[key] = Node(tuple(outcomes), tuple(k if k != () else None for k in succ), tuple(env))
    if header is None or not nodes:
        raise ValueError("TLC output has no HEADER/STATE lines (dump configuration did not run)")
    cmds = [{"op": o, "actor": a, "action": act, "ver": v} for (o, a, act, v) in header[1]]
    envs = [{"actor": a, "kind": k, "val": bool(v)} for (a, k, v) in header[2]]
    return Graph(initial=initial, nodes=nodes, cmds=cmds, envs=envs)


def compare(python: Graph, tlc: Graph, *, sample: int = 5) -> dict[str, Any]:
    """Cell-by-cell comparison; every disagreement is counted, the first few are described."""
    problems: dict[str, Any] = {}
    if python.cmds != tlc.cmds or python.envs != tlc.envs:
        return {"agree": False, "reason": "command/environment orderings differ between Python and the spec"}
    only_py, only_tlc = sorted(set(python.nodes) - set(tlc.nodes)), sorted(set(tlc.nodes) - set(python.nodes))
    outcome_diffs: list[dict[str, Any]] = []
    succ_diffs = env_diffs = compared = committed = 0
    for key in sorted(set(python.nodes) & set(tlc.nodes)):
        a, b = python.nodes[key], tlc.nodes[key]
        for i, (x, y) in enumerate(zip(a.outcomes, b.outcomes)):
            compared += 1
            committed += x == "COMMITTED"
            if x != y:
                outcome_diffs.append({"state": key, "command": python.cmds[i], "runtime": x, "spec": y})
            elif a.succ[i] != b.succ[i]:
                succ_diffs += 1
        env_diffs += sum(1 for x, y in zip(a.env, b.env) if x != y)
    problems.update({
        "states_runtime": len(python.nodes), "states_spec": len(tlc.nodes), "states_common": len(set(python.nodes) & set(tlc.nodes)),
        "initial_states_equal": python.initial == tlc.initial,
        "only_in_runtime": len(only_py), "only_in_spec": len(only_tlc),
        "state_command_cells_compared": compared, "committing_cells": committed,
        "outcome_disagreements": len(outcome_diffs), "successor_disagreements": succ_diffs,
        "environment_successor_disagreements": env_diffs,
        "runtime_executions": python.executions, "runtime_side_defects": len(python.defects),
        "examples": {"outcome": outcome_diffs[:sample], "only_in_runtime": [list(k) for k in only_py[:sample]],
                     "only_in_spec": [list(k) for k in only_tlc[:sample]], "defects": python.defects[:sample]},
    })
    problems["agree"] = (not only_py and not only_tlc and not outcome_diffs and not succ_diffs and not env_diffs
                         and python.initial == tlc.initial and not python.defects)
    return problems


# -------------------------------------------------------------------------------------------- traces

Step = tuple  # ("X", op, actor, action, ver, outcome, post) | ("E", actor, kind, val, 0, "ENV", post)


class TraceRecorder:
    """Executes one trace on the real runtime with real commits, recording each step as observed."""

    def __init__(self, workflow: Workflow, ops: int, sandbox: Sandbox):
        self.harness = Harness(workflow, ops)
        self._sandbox = sandbox
        self.steps: list[Step] = []

    def __enter__(self) -> "TraceRecorder":
        self._context = self._sandbox()
        self.store = self._context.__enter__()
        with self.store.transaction() as u:
            self.initial = self.harness.start(u)
        self.key = self.initial
        return self

    def __exit__(self, *exc: object) -> None:
        self._context.__exit__(*exc)

    def execute(self, op: str, actor: str, action: str, ver: int) -> str:
        cmd = {"op": op, "actor": actor, "action": action, "ver": ver}
        try:
            with self.store.transaction() as u:  # an exception rolls the whole transaction back
                result = self.harness.execute_command(u, cmd)
            code = "DUPLICATE" if result["duplicate"] else "COMMITTED"
        except DomainError as exc:
            code = exc.code
        except Exception as exc:  # noqa: BLE001
            code = "EXC:" + type(exc).__name__
        self._observe(("X", op, actor, action, ver, code))
        return code

    def environment(self, actor: str, kind: str, value: int) -> None:
        with self.store.transaction() as u:
            self.harness.environment(u, {"actor": actor, "kind": kind, "val": value})
        self._observe(("E", actor, kind, value, 0, "ENV"))

    def _observe(self, head: tuple) -> None:
        with self.store.transaction() as u:
            self.key = self.harness.abstract(u)
        self.steps.append((*head, self.key))


def scenario_suite() -> list[tuple[str, list[tuple]]]:
    """Named, scripted sequences aimed at replay, revocation and binding. `cur` = current version."""
    T, T2, TR, R, V, G = "teacher-assigned", "teacher-unassigned", "teacher-revoked", "registrar", "viewer", "ghost"
    X = lambda op, actor, action, ver="cur": ("X", op, actor, action, ver)  # noqa: E731
    E = lambda actor, kind, val: ("E", actor, kind, val)  # noqa: E731
    return [
        ("happy_path", [X("op1", T, "Submit"), X("op2", T, "Recommend"), X("op3", R, "Approve")]),
        ("baseline_approve_from_submitted", [X("op1", T, "Submit"), X("op2", R, "Approve"), X("op3", T, "Recommend")]),
        ("replay_identical", [X("op1", T, "Submit"), X("op1", T, "Submit", 0), X("op1", T, "Submit", 0)]),
        ("replay_after_actor_revoked", [X("op1", T, "Submit"), E(T, "active", 0), X("op1", T, "Submit", 0),
                                        E(T, "active", 1), X("op1", T, "Submit", 0)]),
        ("replay_after_assignment_lost", [X("op1", T, "Submit"), X("op2", T, "Recommend"), E(T, "assigned", 0),
                                          X("op2", T, "Recommend", 1), E(T, "assigned", 1), X("op2", T, "Recommend", 1)]),
        ("replay_after_registrar_revoked", [X("op1", T, "Submit"), X("op2", T, "Recommend"), X("op3", R, "Approve"),
                                            E(R, "active", 0), X("op3", R, "Approve", 2), X("op4", R, "Reject"),
                                            E(R, "active", 1), X("op3", R, "Approve", 2)]),
        ("cross_actor_replay", [X("op1", T, "Submit"), X("op1", R, "Submit", 0), X("op1", T2, "Submit", 0),
                                X("op1", V, "Submit", 0), X("op1", G, "Submit", 0), X("op1", TR, "Submit", 0)]),
        ("op_id_reuse_other_binding", [X("op1", T, "Submit"), X("op1", T, "Recommend", 1), X("op1", T, "Submit", 1),
                                       X("op1", T, "Revise", 0)]),
        ("stale_and_state_denied", [X("op1", T, "Submit", 3), X("op1", T, "Submit", 0), X("op2", T, "Submit", 0),
                                    X("op3", R, "Approve", 1), X("op4", T, "Revise", 1), X("op5", R, "Reject", 1)]),
        ("unknown_and_unmodelled", [X("op1", G, "Submit", 0), X("op2", T, "Recommend", 0), X("op3", T2, "Recommend", 0),
                                    X("op4", TR, "Submit", 0), X("op5", V, "Approve", 0)]),
        ("reject_revise_cycle", [X("op1", T, "Submit"), X("op2", T, "Recommend"), X("op3", R, "Reject"), X("op4", T, "Revise"),
                                 X("op5", T, "Submit"), X("op6", T, "Recommend"), X("op1", T, "Submit", 0)]),
        ("unassigned_then_assigned", [E(T, "assigned", 0), X("op1", T, "Submit"), X("op2", T, "Recommend"),
                                      E(T, "assigned", 1), X("op2", T, "Recommend"), X("op3", R, "Approve")]),
        ("environment_chatter", [E(T, "active", 0), E(R, "assigned", 0), E(T, "active", 1), X("op1", T, "Submit"),
                                 E(R, "active", 0), E(R, "active", 1), X("op2", T, "Recommend"), E(T, "assigned", 0),
                                 E(T, "assigned", 1)]),
    ]


def run_scenario(recorder: TraceRecorder, script: list[tuple]) -> None:
    for item in script:
        if item[0] == "E":
            recorder.environment(item[1], item[2], item[3])
        else:
            _, op, actor, action, ver = item
            recorder.execute(op, actor, action, recorder.key[1] if ver == "cur" else ver)


def random_walk(recorder: TraceRecorder, rng: random.Random, length: int) -> None:
    """Seeded random steps, biased toward meaningful commands, replays, conflicts and revocations."""
    h = recorder.harness
    actors = h.actor_ids + UNKNOWN_ACTORS
    role_of = {a[0]: a[1] for a in directory()}
    for _ in range(length):
        state, version, _audit, sigs, _outbox, _dirs = recorder.key
        if rng.random() < 0.24:
            recorder.environment(rng.choice(MUTABLE_ACTORS), rng.choice(("active", "assigned")), rng.choice((0, 1)))
            continue
        used = [op for op, sig in zip(h.ops, sigs) if sig]
        fresh = [op for op, sig in zip(h.ops, sigs) if not sig]
        mode = rng.choices(("progress", "replay", "conflict", "noise"), (48, 22, 12, 18))[0]
        if mode in ("replay", "conflict") and not used:
            mode = "progress"
        if mode == "replay":
            op = rng.choice(used)
            actor, action, ver = sigs[h.ops.index(op)][:3]
            recorder.execute(op, actor, action, ver)
        elif mode == "conflict":
            op = rng.choice(used)
            actor, action, ver = sigs[h.ops.index(op)][:3]
            field_ = rng.choice(("actor", "action", "ver"))
            actor = rng.choice(actors) if field_ == "actor" else actor
            action = rng.choice(action_universe()) if field_ == "action" else action
            ver = rng.randint(0, h.max_ver) if field_ == "ver" else ver
            recorder.execute(op, actor, action, ver)
        elif mode == "progress":
            legal = [a for a, e in h.table.items() if e["src"] == state] or list(action_universe())
            action = rng.choice(legal)
            role = h.table.get(action, {}).get("role")
            pool = [a for a in h.actor_ids if role_of[a] == role] if role and rng.random() < 0.85 else list(actors)
            op = rng.choice(fresh) if fresh else rng.choice(h.ops)
            ver = version if rng.random() < 0.85 else rng.randint(0, h.max_ver)
            recorder.execute(op, rng.choice(pool or list(actors)), action, ver)
        else:
            recorder.execute(rng.choice(h.ops), rng.choice(actors), rng.choice(action_universe()), rng.randint(0, h.max_ver))


def path_probe_traces(graph: Graph, limit: int) -> list[tuple[Key, tuple[Any, ...]]]:
    """A shortest path (found in `graph`) to reachable states plus replay and cross-actor probes.

    Every reachable state is a candidate; when there are more than `limit`, a deterministic stride over
    the sorted states is used (and the caller reports the sample size)."""
    parents: dict[Key, tuple[Key, tuple[Any, ...]] | None] = {graph.initial: None}
    queue: deque[Key] = deque([graph.initial])
    while queue:
        key = queue.popleft()
        node = graph.nodes[key]
        for i, nxt in enumerate(node.succ):
            if nxt is not None and nxt not in parents:
                parents[nxt] = (key, ("X", graph.cmds[i]))
                queue.append(nxt)
        for i, nxt in enumerate(node.env):
            if nxt != key and nxt not in parents:
                parents[nxt] = (key, ("E", graph.envs[i]))
                queue.append(nxt)
    out = []
    targets = sorted(parents)
    if len(targets) > limit:
        targets = targets[:: -(-len(targets) // limit)]
    for key in targets:
        path = []
        cursor = key
        while parents[cursor] is not None:
            cursor, step = parents[cursor]  # type: ignore[misc]
            path.append(step)
        out.append((key, tuple(reversed(path))))
    return out


def replay_path(recorder: TraceRecorder, path: Iterable[tuple[Any, ...]]) -> None:
    last: dict[str, Any] | None = None
    for kind, item in path:
        if kind == "E":
            recorder.environment(item["actor"], item["kind"], int(item["val"]))
        else:
            recorder.execute(item["op"], item["actor"], item["action"], item["ver"])
            last = item
    if last is not None:  # probes: replay the last command, then every actor asking for the same binding
        recorder.execute(last["op"], last["actor"], last["action"], last["ver"])
        for actor in recorder.harness.actor_ids + UNKNOWN_ACTORS:
            recorder.execute(last["op"], actor, last["action"], last["ver"])


def build_traces(workflow: Workflow, ops: int, sandbox: Sandbox, graph: Graph | None, *, seed: str, random_count: int,
                 probe_limit: int = 100) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Run every trace kind on the real runtime; returns traces and counts per kind."""
    traces: list[dict[str, Any]] = []
    counts = {"scenario": 0, "path_probe": 0, "random": 0}

    def record(kind: str, action: Callable[[TraceRecorder], None]) -> None:
        with TraceRecorder(workflow, ops, sandbox) as rec:
            action(rec)
            traces.append({"kind": kind, "init": rec.initial, "steps": list(rec.steps)})
        counts[kind] += 1

    for _name, script in scenario_suite():
        record("scenario", lambda rec, s=script: run_scenario(rec, s))
    if graph is not None:
        for _key, path in path_probe_traces(graph, probe_limit):
            record("path_probe", lambda rec, p=path: replay_path(rec, p))
    for i in range(random_count):
        rng = random.Random(f"{seed}:{i}")
        length = rng.randint(8, 20)
        record("random", lambda rec, r=rng, n=length: random_walk(rec, r, n))
    return traces, counts


def trace_steps_total(traces: list[dict[str, Any]]) -> int:
    return sum(len(t["steps"]) for t in traces)
