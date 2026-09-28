"""Breadth-first explicit-state search over the REAL `application.runtime.execute`.

State  = the complete observable database of an ephemeral sandbox store (`bootstrap.sandbox_factory`
         semantics): instance, actors table, operation table, audit log, outbox.
Moves  = (a) every (actor, action, expected_version, operation id) command drawn from the alphabet,
         including replays of a recorded operation id (identical, other actor, other action) and stale
         versions, and (b) environment moves that flip an actor's `active` / `assigned` flag.
Search = BFS to depth k with state de-duplication, checking the step and state invariants of `spec.py`
         at every transition and every newly reached state. The first counterexample per invariant is
         therefore a shortest one.

The exploration is bounded and explicit-state: "no violation found" means none is reachable within the
declared alphabet and depth, not that none exists. The runtime is executed, not modelled, so this
observes the implementation's behaviour (including its SQLite transaction semantics) but says nothing
about interleavings of concurrent writers, crash points, or actors outside the fixture directory.
"""
from __future__ import annotations

import hashlib
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

from eija_studio.adapters.sqlite_store import FIXTURE_ACTORS, SQLiteStore
from eija_studio.application import runtime
from eija_studio.application.ports import SandboxFactory
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow

from . import spec
from .snapshot import Observer, Snapshot
from .spec import CASE, Command, Findings, Outcome

ExecuteFn = Callable[..., dict]
FIXTURE_ACTOR_IDS: tuple[str, ...] = tuple(a[0] for a in FIXTURE_ACTORS)
ACTIONS: tuple[str, ...] = ("Submit", "Recommend", "Approve", "Reject", "Revise")


CORE_TOGGLES = (("teacher-assigned", "active"), ("teacher-assigned", "assigned"), ("registrar", "active"))
ALL_TOGGLES = (*CORE_TOGGLES, ("teacher-unassigned", "assigned"), ("teacher-revoked", "active"))


@dataclass(frozen=True)
class Config:
    """Bounds and alphabet. Every field is echoed into the evidence report."""
    depth: int = 6
    actors: tuple[str, ...] = (*FIXTURE_ACTOR_IDS, spec.UNKNOWN_ACTOR)
    actions: tuple[str, ...] = (*ACTIONS, spec.UNMODELLED_ACTION)
    # (actor, column): flipped by an environment move. Column is `active` (revocation) or `assigned`.
    toggles: tuple[tuple[str, str], ...] = CORE_TOGGLES
    stale_versions: bool = True        # also try expected_version = version-1 (or version+1 at version 0)
    replay_conflicts: bool = True      # replay a recorded operation id with another actor / another action
    max_seconds: float | None = None   # wall-clock cap; hitting it makes the run INCONCLUSIVE, never PASS
    stop_when_found: tuple[str, ...] = ()  # finish the BFS level in which one of these invariants first fails, then stop (mutant runs)

    def describe(self) -> dict[str, Any]:
        return {"depth": self.depth, "actors": list(self.actors), "actions": list(self.actions),
                "environment_toggles": [list(t) for t in self.toggles], "stale_versions": self.stale_versions,
                "replay_conflicts": self.replay_conflicts, "max_seconds": self.max_seconds,
                "stop_when_found": list(self.stop_when_found)}


@dataclass
class Node:
    id: int
    snap: Snapshot
    recorded: tuple[Command, ...]
    depth: int


@dataclass
class Result:
    model: str
    config: Config
    findings: Findings
    per_depth: list[dict[str, int]] = field(default_factory=list)
    outcomes: dict[str, int] = field(default_factory=dict)
    states: int = 1
    transitions: int = 0
    max_depth: int = 0
    exhausted: bool = False           # the frontier emptied: every reachable state (in the alphabet) was seen
    truncated: bool = False           # stopped by max_seconds
    seconds: float = 0.0
    invariant_checks: int = 0

    @property
    def verdict(self) -> str:
        if self.findings.first:
            return "FAIL"
        return "INCONCLUSIVE" if self.truncated else "PASS"


def _digest(snap: Snapshot) -> bytes:
    return hashlib.blake2b(repr(snap).encode("utf-8"), digest_size=16).digest()


def run_command(store: SQLiteStore, model: Workflow, instance_id: str, cmd: Command, execute_fn: ExecuteFn) -> Outcome:
    command = ExecuteCommand(operation_id=cmd.op_id, actor_id=cmd.actor, instance_id=instance_id,
                             action=cmd.action, expected_version=cmd.expected_version)
    try:
        with store.transaction() as unit:
            result = execute_fn(unit, CASE, model, command)
    except DomainError as e:
        return Outcome("rejected", e.code)
    except Exception as e:  # an unexpected failure of the runtime is itself a finding
        return Outcome("crashed", detail=f"{type(e).__name__}: {e}")
    return Outcome("duplicate" if result["duplicate"] else "committed", result=result)


def _moves(cfg: Config, node: Node) -> Iterator[tuple[str, Any]]:
    """Deterministically ordered moves from a node: ("env", (actor, column, value)) or ("cmd", Command)."""
    version = node.snap.version
    versions = (version, version - 1 if version > 0 else version + 1) if cfg.stale_versions else (version,)
    fresh = f"op{len(node.recorded)}"
    for actor in cfg.actors:
        for action in cfg.actions:
            for v in versions:
                yield "cmd", Command(actor, action, v, fresh)
    for rec in node.recorded:
        yield "cmd", rec                                         # identical replay
        if cfg.replay_conflicts:
            for actor in cfg.actors:
                if actor != rec.actor:
                    yield "cmd", Command(actor, rec.action, rec.expected_version, rec.op_id)
            for action in cfg.actions:
                if action != rec.action:
                    yield "cmd", Command(rec.actor, action, rec.expected_version, rec.op_id)
    table = node.snap.actor_table()
    for actor, column in cfg.toggles:
        _role, active, assigned = table[actor]
        current = active if column == "active" else assigned
        yield "env", (actor, column, 0 if current else 1)


def explore(name: str, model: Workflow, cfg: Config, sandbox: SandboxFactory, execute_fn: ExecuteFn = runtime.execute) -> Result:
    started = time.perf_counter()
    findings = Findings()
    result = Result(model=name, config=cfg, findings=findings)
    with sandbox() as store:
        obs = Observer(store)
        try:
            with store.transaction() as unit:
                instance = runtime.initialise(unit, CASE, model)
            root_snap = obs.read()
            for v in spec.check_state(model, root_snap):
                findings.record(v, [])
            seen = {_digest(root_snap): 0}
            parents: list[tuple[int, str]] = [(-1, "")]
            frontier = [Node(0, root_snap, (), 0)]
            live = root_snap                                       # what the sandbox database currently holds

            def trace(node_id: int) -> list[str]:
                out: list[str] = []
                while node_id > 0:
                    node_id, label = parents[node_id]
                    out.append(label)
                return out[::-1]

            for depth in range(1, cfg.depth + 1):
                stats = {"depth": depth, "frontier": len(frontier), "transitions": 0, "new_states": 0}
                nxt: list[Node] = []
                for node in frontier:
                    if live != node.snap:
                        obs.restore(node.snap)
                        live = node.snap
                    recorded = {c.op_id: c for c in node.recorded}
                    for kind, payload in _moves(cfg, node):
                        if cfg.max_seconds is not None and time.perf_counter() - started > cfg.max_seconds:
                            result.truncated = True
                            break
                        pre = node.snap
                        if kind == "env":
                            actor, column, value = payload
                            label = f"env: {actor}.{column} := {value}"
                            obs.set_actor_flag(actor, column, value)
                            outcome, violations = Outcome("env"), []
                            post = obs.read()
                            counter = f"env:{column}={value}"
                            new_recorded = node.recorded
                        else:
                            cmd: Command = payload
                            label = cmd.label()
                            outcome = run_command(store, model, instance["id"], cmd, execute_fn)
                            post = obs.read()
                            violations = spec.check_step(model, pre, recorded, cmd, outcome, post)
                            counter = outcome.kind + (f":{cmd.action}" if outcome.kind == "committed" else "") + \
                                (f":{outcome.code}" if outcome.code else "")
                            new_recorded = (*node.recorded, cmd) if outcome.kind == "committed" else node.recorded
                        stats["transitions"] += 1
                        result.invariant_checks += 1
                        result.transitions += 1
                        result.outcomes[counter] = result.outcomes.get(counter, 0) + 1
                        step_trace = [*trace(node.id), label]
                        for v in violations:
                            findings.record(v, step_trace)
                        if post == pre:
                            continue
                        obs.restore(pre)                                # next move starts from `pre` again
                        live = pre
                        key = _digest(post)
                        if key in seen or violations:
                            continue
                        seen[key] = len(parents)
                        parents.append((node.id, label))
                        state_violations = spec.check_state(model, post)
                        result.invariant_checks += 1
                        for v in state_violations:
                            findings.record(v, step_trace)
                        stats["new_states"] += 1
                        result.states += 1
                        result.max_depth = depth
                        if not state_violations:
                            nxt.append(Node(seen[key], post, new_recorded, depth))
                    if result.truncated:
                        break
                result.per_depth.append(stats)
                frontier = nxt
                if result.truncated or (cfg.stop_when_found and any(i in findings.first for i in cfg.stop_when_found)):
                    break
                if not frontier:
                    result.exhausted = True
                    break
        finally:
            obs.close()
    result.seconds = time.perf_counter() - started
    return result
