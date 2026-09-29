"""Model configurations derived from the executable Python workflow.

Everything the TLA+ specification needs that is *data* (transition table, actor directory, forbidden
effects, action universe) is read from the kernel here, never retyped. `generate.py` renders these
values into `generated/MC_*.tla`; `conformance.py` uses the same ordering to compare the runtime with
the specification.

What this module does NOT establish: that the TLA+ decision procedure (`Decide` in Excursion.tla)
matches `application/runtime.py`. That is what conformance checking measures.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from eija_studio.domain.models import SemanticTransaction, Workflow
from eija_studio.domain.policy import apply_transaction, baseline, check_policy
from verification.excursion_pack import EFFECTS, FIXTURE_ACTORS

UNKNOWN_ACTORS: tuple[str, ...] = ("ghost",)  # ids that are deliberately absent from the directory
MUTABLE_ACTORS: tuple[str, ...] = ("teacher-assigned", "registrar")  # the environment may change these
INVARIANTS: tuple[str, ...] = (
    "TypeOK", "NoTeacherApproval", "ApprovalRequiresRecommendation", "OutboxAtMostOncePerOperation",
    "AtomicCommit", "ReplayNeverBypassesCurrentAuthority", "ForbiddenEffectsNeverEmitted",
)
PROPERTIES: tuple[str, ...] = ("VersionMonotonic",)
MUTATIONS: tuple[str, ...] = ("none", "replay_before_auth", "replay_reemits", "emit_unadapted")
EFFECT_KINDS = (("Audit:", "audit"), ("Notification:", "notify"))  # mirrors runtime.execute's dispatch


@dataclass(frozen=True)
class TlaConfig:
    """One model-checking configuration: a workflow, bounds and an expected verdict."""

    name: str
    workflow: Workflow
    description: str
    check_ops: int = 4  # operation ids in the model-checking run
    dump_ops: int = 2  # operation ids in the exhaustive conformance run
    mutation: str = "none"
    expect: str = "holds"  # "holds", or the invariant that TLC must report violated
    policy_errors: tuple[str, ...] = ()  # what protected policy says about this workflow
    note: str = ""  # for a negative control: why the counterexample violates the invariant

    @property
    def negative_control(self) -> bool:
        return self.expect != "holds"


def _replace_transition(workflow: Workflow, action: str, **changes: Any) -> Workflow:
    # model_copy skips validation on purpose: these are hostile tables that escaped contract checks.
    moved = tuple(t.model_copy(update=changes) if t.action == action else t for t in workflow.transitions)
    return workflow.model_copy(update={"transitions": moved})


def configs() -> tuple[TlaConfig, ...]:
    """All configurations, in a fixed order. Safe ones pass protected policy; controls do not."""
    base = baseline()
    cand = apply_transaction(base, SemanticTransaction(kind="enable_recommendation"))
    cand_sub = apply_transaction(cand, SemanticTransaction(kind="set_rejection_source", rejection_source="Submitted"))
    teacher = _replace_transition(cand, "Approve", role="Teacher")
    payment = _replace_transition(cand, "Approve", required_effects=("Audit:ExcursionApproved", "PaymentCaptured"))
    made = (
        TlaConfig("baseline", base, "Baseline: no recommendation; registrar decides from Submitted"),
        TlaConfig("candidate", cand, "Candidate: teacher recommends, registrar approves or rejects from Recommended", dump_ops=3),
        TlaConfig("candidate_reject_submitted", cand_sub, "Candidate with registrar rejection allowed from Submitted"),
        TlaConfig("nc_teacher_approval", teacher, "NEGATIVE CONTROL: Approve granted to the Teacher role",
                  mutation="none", expect="NoTeacherApproval",
                  note="With Approve assigned to the Teacher role the assigned teacher can walk Submit, Recommend, Approve. "
                       "Protected policy rejects this workflow (PROTECTED_AUTHORITY:Approve), so the kernel never runs it."),
        TlaConfig("nc_replay_before_auth", cand, "NEGATIVE CONTROL: operation replay looked up BEFORE authority",
                  mutation="replay_before_auth", expect="ReplayNeverBypassesCurrentAuthority",
                  note="ReplayNeverBypassesCurrentAuthority is a predicate over every command in the last state. Once op1 is recorded, "
                       "the seeded spec answers OPERATION_CONFLICT (or DUPLICATE) to an actor that is not authorised now, for example "
                       "teacher-revoked (inactive in the fixture directory) reusing op1, instead of ACTOR_REVOKED."),
        TlaConfig("nc_replay_reemits", cand, "NEGATIVE CONTROL: a replay re-queues its notification effects",
                  mutation="replay_reemits", expect="OutboxAtMostOncePerOperation",
                  note="Replaying the committed Recommend (op2) with the same binding queues its notification a second time."),
        TlaConfig("nc_forbidden_effect", payment, "NEGATIVE CONTROL: unadapted forbidden effect emitted instead of rejected",
                  mutation="emit_unadapted", expect="ForbiddenEffectsNeverEmitted",
                  note="Approve requires PaymentCaptured, which has no adapter. The real runtime raises EFFECT_DENIED and rolls back; "
                       "the seeded spec emits it instead. Protected policy also rejects this workflow (EFFECT_POLICY:Approve)."),
    )
    return tuple(_with_policy(c) for c in made)


def _with_policy(config: TlaConfig) -> TlaConfig:
    errors = tuple(check_policy(config.workflow))
    hostile = config.name in {"nc_teacher_approval", "nc_forbidden_effect"}
    if hostile and not errors:
        raise AssertionError(f"{config.name}: control workflow must be blocked by protected policy")
    if not hostile and errors:
        raise AssertionError(f"{config.name}: safe workflow blocked by protected policy: {errors}")
    return replace(config, policy_errors=errors)


# ----------------------------------------------------------------------------- derived data

def action_universe() -> tuple[str, ...]:
    """Every action a command may name (the kernel's effect table is the source)."""
    return tuple(sorted(EFFECTS))


def forbidden_effects(workflow: Workflow) -> tuple[str, ...]:
    return tuple(sorted({e for t in workflow.transitions for e in t.forbidden_effects}))


def transition_table(workflow: Workflow) -> dict[str, dict[str, Any]]:
    """action -> transition facts, classifying effects as `runtime.execute` does."""
    table: dict[str, dict[str, Any]] = {}
    for t in sorted(workflow.transitions, key=lambda x: x.action):
        kinds: dict[str, list[str]] = {"audit": [], "notify": [], "other": []}
        for effect in t.required_effects:
            kind = next((k for prefix, k in EFFECT_KINDS if effect.startswith(prefix)), "other")
            kinds[kind].append(effect)
        table[t.action] = {"src": t.from_state, "dst": t.to_state, "role": t.role,
                           "needsAssigned": "actor_assigned" in t.guards, "audit": tuple(kinds["audit"]),
                           "notify": tuple(kinds["notify"]), "other": tuple(kinds["other"])}
    return table


def directory() -> tuple[tuple[str, str, int, int], ...]:
    """The trusted fixture directory in its declared order: (id, role, active, assigned)."""
    return tuple(FIXTURE_ACTORS)


def op_ids(count: int) -> tuple[str, ...]:
    return tuple(f"op{i}" for i in range(1, count + 1))


def command_sequence(ops: int) -> list[dict[str, Any]]:
    """The command ordering Excursion.tla's `CmdSeq` uses: op, actor, action, version (innermost)."""
    actors = tuple(a[0] for a in directory()) + UNKNOWN_ACTORS
    return [{"op": op, "actor": actor, "action": action, "ver": ver}
            for op in op_ids(ops) for actor in actors for action in action_universe() for ver in range(ops + 1)]


def environment_sequence() -> list[dict[str, Any]]:
    """The environment-step ordering `EnvSeq` uses: mutable actor, kind (active, assigned), value."""
    return [{"actor": actor, "kind": kind, "val": bool(val)}
            for actor in MUTABLE_ACTORS for kind in ("active", "assigned") for val in (0, 1)]
