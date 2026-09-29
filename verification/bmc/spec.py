"""The reference model and safety invariants the search checks against the real runtime.

Two kinds of check, both computed only from observed database snapshots and the workflow model:

* step properties   (pre-state, command, outcome, post-state): authority is checked before replay,
                    commits only when every guard holds, rejected/replayed commands leave no trace,
                    a commit changes exactly state + version + operation + declared effects.
* state properties  (any reached state): version counts commits, the audit trail is a valid run of the
                    model, the pack's laws hold on the recorded run (``PACK-LAWS-HOLD-ON-RUN``: the run is rebuilt
                    from the audit and outbox rows and judged by ``domain.laws.evaluate_run``, the kernel's own law
                    evaluator, so there is no second encoding of the laws here; the pack's forbidden effects are one
                    more ``forbidden_effects`` law), outbox rows correspond to committed notification effects.

The reference model is a small independent re-statement of the intended semantics, written by the
same authors as the runtime and verifier. It is a same-author oracle, not an independent one.
It is precedence-agnostic about WHICH denial code wins when several apply, and strict about the class
of outcome (commit / replay / reject) and about every side effect.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from eija_studio.domain.laws import ForbiddenEffects, Step, evaluate_run
from eija_studio.domain.models import Transition, Workflow
from eija_studio.domain.pack import Pack, default_pack

from .snapshot import Snapshot

CASE = "bmc"
UNKNOWN_ACTOR = "ghost"
UNMODELLED_ACTION = "Bogus"
LAWS_ON_RUN = "PACK-LAWS-HOLD-ON-RUN"


@dataclass(frozen=True)
class Command:
    actor: str
    action: str
    expected_version: int
    op_id: str

    def label(self) -> str:
        return f"{self.actor} {self.action} v={self.expected_version} op={self.op_id}"


@dataclass(frozen=True)
class Outcome:
    kind: str                      # committed | duplicate | rejected | crashed
    code: str | None = None
    result: dict[str, Any] | None = None
    detail: str = ""


@dataclass(frozen=True)
class Violation:
    invariant: str
    detail: str


@dataclass(frozen=True)
class Expectation:
    kind: str                      # commit | duplicate | reject
    allowed_codes: frozenset[str] = frozenset()
    authorised: bool = False
    transition: Transition | None = None
    reasons: frozenset[str] = frozenset()


def transition_of(model: Workflow, action: str) -> Transition | None:
    return next((t for t in model.transitions if t.action == action), None)


def expectation(model: Workflow, pre: Snapshot, recorded: dict[str, Command], cmd: Command) -> Expectation:
    """What the intended semantics allow for `cmd` from `pre` (see module docstring for precedence)."""
    t = transition_of(model, cmd.action)
    actors = pre.actor_table()
    if t is None:
        unknown = {"UNKNOWN_ACTOR"} if cmd.actor not in actors else set()
        return Expectation("reject", frozenset({"ACTION_DENIED"} | unknown))
    if cmd.actor not in actors:
        return Expectation("reject", frozenset({"UNKNOWN_ACTOR"}), transition=t)
    role, active, assigned = actors[cmd.actor]
    denied = set()
    if not active:
        denied.add("ACTOR_REVOKED")
    if role != t.role:
        denied.add("ROLE_DENIED")
    if "actor_assigned" in t.guards and not assigned:
        denied.add("ASSIGNMENT_DENIED")
    if denied:
        return Expectation("reject", frozenset(denied), False, t, frozenset(denied))
    prior = recorded.get(cmd.op_id)
    if prior is not None:
        if prior == cmd:
            return Expectation("duplicate", authorised=True, transition=t)
        return Expectation("reject", frozenset({"OPERATION_CONFLICT"}), True, t, frozenset({"OPERATION_CONFLICT"}))
    blocked = set()
    if cmd.expected_version != pre.version:
        blocked.add("STALE_VERSION")
    if pre.state != t.from_state:
        blocked.add("STATE_DENIED")
    if blocked:
        return Expectation("reject", frozenset(blocked), True, t, frozenset(blocked))
    return Expectation("commit", authorised=True, transition=t)


# ------------------------------------------------------------------------------------------------
# Step properties
# ------------------------------------------------------------------------------------------------

def check_step(model: Workflow, pre: Snapshot, recorded: dict[str, Command], cmd: Command,
               outcome: Outcome, post: Snapshot) -> list[Violation]:
    exp = expectation(model, pre, recorded, cmd)
    out: list[Violation] = []

    def bad(invariant: str, detail: str) -> None:
        out.append(Violation(invariant, detail))

    if outcome.kind == "crashed":
        bad("NO-UNEXPECTED-EXCEPTION", outcome.detail)
        return out
    if outcome.kind == "committed":
        if exp.kind != "commit":
            if not exp.authorised:
                reasons = sorted(exp.reasons) or "unknown actor or unmodelled action"
                bad("AUTHORITY-ON-COMMIT", f"committed though the actor is not authorised ({reasons})")
            elif exp.kind == "duplicate":
                bad("EXACTLY-ONCE-OPERATION", "committed a second time under an already-recorded operation id")
            elif "OPERATION_CONFLICT" in exp.reasons:
                bad("OPERATION-BINDING", "committed under an operation id bound to a different request")
            elif "STALE_VERSION" in exp.reasons:
                bad("CAS-ON-COMMIT", f"committed with expected_version={cmd.expected_version} but version was {pre.version}")
            else:
                bad("STATE-GUARD-ON-COMMIT", f"committed from {pre.state}, transition requires {exp.transition.from_state}")
        else:
            out.extend(_commit_effects(pre, cmd, exp.transition, outcome, post))
    elif outcome.kind == "duplicate":
        if exp.kind != "duplicate":
            if not exp.authorised:
                bad("AUTHORITY-BEFORE-REPLAY", f"replay served to an actor who is not currently authorised ({sorted(exp.reasons)})")
            else:
                bad("OPERATION-BINDING", "replay served for a request different from the one recorded")
        if post != pre:
            bad("REPLAY-HAS-NO-EFFECT", "a replayed operation changed the database")
        result = outcome.result or {}
        if result.get("committed") or result.get("effects"):
            bad("REPLAY-HAS-NO-EFFECT", "replay result claims a commit or new effects")
    else:  # rejected
        if exp.kind != "reject":
            bad("NO-SPURIOUS-DENIAL", f"denied ({outcome.code}) but the reference model allows a {exp.kind}")
        elif outcome.code not in exp.allowed_codes:
            bad("DENIAL-REASON", f"denied with {outcome.code}; applicable reasons: {sorted(exp.allowed_codes)}")
        if post != pre:
            bad("REJECTION-LEAVES-NO-TRACE", "a rejected command changed the database")
    return out


def _commit_effects(pre: Snapshot, cmd: Command, t: Transition, outcome: Outcome, post: Snapshot) -> list[Violation]:
    """A commit changes exactly: state, version, one operation row, the declared audit and outbox rows."""
    audit_effects = [e for e in t.required_effects if e.startswith("Audit:")]
    notifications = [e for e in t.required_effects if e.startswith("Notification:")]
    wanted_instance = (pre.instance[0], pre.instance[1], pre.instance[2], t.to_state, pre.version + 1)
    problems = []
    if post.instances != (wanted_instance,):
        problems.append(f"instance {post.instances} != {(wanted_instance,)}")
    if post.actors != pre.actors:
        problems.append("actors table changed")
    if len(post.operations) != len(pre.operations) + 1 or {o[0] for o in post.operations} != {o[0] for o in pre.operations} | {cmd.op_id}:
        problems.append("operation table did not gain exactly the command's operation id")
    if post.audit[:len(pre.audit)] != pre.audit or len(post.audit) != len(pre.audit) + len(audit_effects):
        problems.append("audit log did not grow by exactly the declared audit effects")
    else:
        for (kind, body), effect in zip(post.audit[len(pre.audit):], audit_effects, strict=True):
            b = json.loads(body)
            if kind != effect or (b.get("case_id"), b.get("operation_id"), b.get("actor_id")) != (CASE, cmd.op_id, cmd.actor):
                problems.append(f"audit entry {kind} does not record the committed command")
    wanted_ids = {f"{cmd.op_id}:{e}" for e in notifications}
    gained = [r for r in post.outbox if r not in pre.outbox]
    if {r[0] for r in gained} != wanted_ids or len(gained) != len(wanted_ids) or len(post.outbox) != len(pre.outbox) + len(gained):
        problems.append("outbox did not gain exactly the declared notification intents")
    result = outcome.result or {}
    if not result.get("committed") or result.get("duplicate") or result.get("effects") != list(t.required_effects):
        problems.append("returned result does not describe the commit")
    return [Violation("COMMIT-EFFECTS-EXACT", "; ".join(problems))] if problems else []


# ------------------------------------------------------------------------------------------------
# State properties
# ------------------------------------------------------------------------------------------------

def _effect_names(kind: str) -> tuple[str, ...]:
    """A recorded effect row by its id and by its bare name (``Audit:X`` is also ``X``), so a namespaced row of a
    forbidden effect matches the pack's bare forbidden id."""
    bare = kind.rsplit(":", 1)[-1]
    return (kind,) if bare == kind else (kind, bare)


def _rows_by_operation(snap: Snapshot) -> tuple[list[str], dict[str, list[tuple[str, str | None, bool]]]]:
    """Audit and outbox rows grouped by operation id, operations in audit (commit) order, outbox-only ones last:
    (kind, recording actor's role or None, is an audit row)."""
    roles = {a[0]: a[1] for a in snap.actors}
    rows: dict[str, list[tuple[str, str | None, bool]]] = {}
    for kind, body in snap.audit:
        b = json.loads(body)
        rows.setdefault(str(b.get("operation_id")), []).append((kind, roles.get(b.get("actor_id")), True))
    for row in snap.outbox:
        rows.setdefault(str(row[2]), []).append((row[3], None, False))
    return list(rows), rows


def recorded_run(model: Workflow, snap: Snapshot) -> list[Step]:
    """The run the database records: one step per operation, its transition named by its AUDIT rows (the outbox only
    adds effects), with the recording actor's role and the state the replayed trail was in. An operation whose rows
    name no model transition becomes a step with no action and no states, which only effect laws can judge."""
    audit_of = {e: t for t in model.transitions for e in t.required_effects}
    order, rows = _rows_by_operation(snap)
    steps, state = [], model.initial_state
    for op in order:
        role = next((r for _, r, _ in rows[op] if r is not None), "")
        t = next((audit_of[k] for k, _, audit in rows[op] if audit and k in audit_of), None)
        effects = tuple(n for k, _, _ in rows[op] for n in _effect_names(k))
        if t is None:
            steps.append(Step(action="", role=role, source="", target="", effects=effects))
            continue
        steps.append(Step(action=t.action, role=role, source=state, target=t.to_state, effects=effects))
        state = t.to_state
    return steps


def law_violations_on_run(model: Workflow, snap: Snapshot, pack: Pack | None = None) -> list[Violation]:
    """``PACK-LAWS-HOLD-ON-RUN``: ``evaluate_run`` over the recorded run, with the pack's forbidden effects as one more law."""
    p = pack if pack is not None else default_pack()
    laws = [*p.laws]
    if p.effects.forbidden:
        laws.append(ForbiddenEffects(kind="forbidden_effects", id="pack-forbidden-effects", code="EFFECT_POLICY",
                                     effects=p.effects.forbidden))
    actions = {t.action for t in model.transitions}
    found = evaluate_run(laws, model.initial_state, recorded_run(model, snap), actions)
    return [Violation(LAWS_ON_RUN, f"law {v.law} ({v.code}) at {', '.join(v.refs[1:])}") for v in found]


def check_state(model: Workflow, snap: Snapshot, pack: Pack | None = None) -> list[Violation]:
    out: list[Violation] = []

    def bad(invariant: str, detail: str) -> None:
        out.append(Violation(invariant, detail))

    if len(snap.instances) != 1:
        bad("ONE-INSTANCE", f"{len(snap.instances)} instances")
        return out
    roles = {a[0]: a[1] for a in snap.actors}
    audit_actions = {e: t for t in model.transitions for e in t.required_effects if e.startswith("Audit:")}
    events = [(kind, json.loads(body)) for kind, body in snap.audit]
    if snap.state not in model.states:
        bad("STATE-IN-MODEL", snap.state)
    if snap.version != len(snap.operations):
        bad("VERSION-COUNTS-COMMITS", f"version {snap.version} but {len(snap.operations)} recorded operations")
    allowed_outbox = {e for t in model.transitions for e in t.required_effects if e.startswith("Notification:")}
    if any(k not in audit_actions for k, _ in events) or any(r[3] not in allowed_outbox for r in snap.outbox):
        bad("EFFECTS-DECLARED-BY-MODEL", "an audit/outbox kind outside the model's declared effects")
    # The audit trail must be a valid run of the model that ends where the instance is.
    state = model.initial_state
    for kind, _ in events:
        t = audit_actions.get(kind)
        if t is None:
            continue
        if state != t.from_state:
            bad("AUDIT-TRAIL-IS-A-VALID-RUN", f"{t.action} recorded while the run was in {state}, needs {t.from_state}")
            break
        state = t.to_state
    else:
        if state != snap.state:
            bad("AUDIT-TRAIL-IS-A-VALID-RUN", f"trail ends in {state} but the instance is {snap.state}")
    # Authority in the record: the recording actor holds the transition's role, and the pack's laws hold on the run.
    for kind, body in events:
        t = audit_actions.get(kind)
        actor_role = roles.get(body.get("actor_id"))
        if t is not None and actor_role != t.role:
            bad("AUDIT-ACTOR-HOLDS-TRANSITION-ROLE", f"{kind} recorded for {body.get('actor_id')} ({actor_role}), needs {t.role}")
    out.extend(law_violations_on_run(model, snap, pack))
    out.extend(_outbox_matches(model, events, snap))
    if {e[1].get("operation_id") for e in events} - {o[0] for o in snap.operations}:
        bad("AUDIT-REFERENCES-RECORDED-OPERATION", "audit entry for an operation that was never recorded")
    return out


def _outbox_matches(model: Workflow, events: list[tuple[str, dict[str, Any]]], snap: Snapshot) -> list[Violation]:
    """The outbox holds exactly the declared notification effects of the committed operations, one row each."""
    audit_actions = {e: t for t in model.transitions for e in t.required_effects if e.startswith("Audit:")}
    committed = {str(b.get("operation_id")): audit_actions[k] for k, b in events if k in audit_actions}
    want = sorted((op, e) for op, t in committed.items() for e in t.required_effects if e.startswith("Notification:"))
    got = sorted((str(r[2]), str(r[3])) for r in snap.outbox)
    if got == want:
        return []
    return [Violation("OUTBOX-MATCHES-COMMITTED-NOTIFICATIONS", f"{len(got)} outbox rows for {len(want)} declared notifications")]


@dataclass
class Findings:
    """First (shortest, because the search is breadth-first) counterexample per invariant."""
    first: dict[str, dict[str, Any]] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)

    def record(self, v: Violation, trace: list[str]) -> None:
        self.counts[v.invariant] = self.counts.get(v.invariant, 0) + 1
        self.first.setdefault(v.invariant, {"invariant": v.invariant, "detail": v.detail, "length": len(trace), "trace": trace})
