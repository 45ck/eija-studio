"""Independent executable reference for preview-instance execution.

Written from the specification text, not from ``application/runtime.py`` or the verifier oracle:

* docs/architecture/ARCHITECTURE.md, "Runtime commit sequence": inside one transaction, load candidate
  and instance; compare model identity; load trusted actor; check active/current role/assignment;
  check operation replay binding; check instance version and source state; update state; append
  required audit; enqueue required synthetic notification; record operation. "Replay rechecks current
  authority before returning original results and does not enqueue again."
* The ubiquitous language: "A changed candidate makes old instances stale; reset creates a new
  instance instead of silently migrating it." "Operations ... bind their full command and model identity."
* The protected policy's published consequences (``CANONICAL_OPTIONS["recommend_only"]``): only active,
  assigned teachers recommend; registrar approval and rejection initially require Recommended; the
  typed edit may move the rejection source between Submitted and Recommended.
* ADR-007 (reauthorise before replay) and ADR-011 (synthetic actors only).
* ADR-0148: every successful owner semantic edit appends its command and case-version provenance;
  refused edits append nothing. This authoring history is separate from runtime transition effects.

The specification does not say where "is the action modelled?" sits in the sequence. This model checks
it immediately before the actor, because role authority is only defined for a modelled action.

What this model establishes: a second, deliberately naive expression of the same rules, so that a
differential test can detect disagreement. What it does NOT establish: that the specification is right,
or independence of authorship. It shares the policy vocabulary (state, role and effect names) with the
kernel, and it was written in the same project; it is a differential oracle, not a blinded holdout.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# --- Specification tables (the protected excursion policy's vocabulary) -----------------------------

STATES = ("Draft", "Submitted", "Recommended", "Approved", "Rejected")
INITIAL_STATE = "Draft"
ROLES = ("Teacher", "Registrar", "Viewer")
ACTIONS = ("Submit", "Recommend", "Approve", "Reject", "Revise")
REJECTION_SOURCES = ("Recommended", "Submitted")


@dataclass(frozen=True)
class Rule:
    """One permitted move: who may do it, from where, to where, whether assignment is required and
    which effects it must queue."""

    role: str
    source: str
    target: str
    needs_assignment: bool
    effects: tuple[str, ...]


def rules(rejection_source: str) -> dict[str, Rule]:
    """The candidate model after the owner selected "teacher recommends; registrar decides"."""
    return {
        "Submit": Rule("Teacher", "Draft", "Submitted", False, ("Audit:ExcursionSubmitted",)),
        "Recommend": Rule("Teacher", "Submitted", "Recommended", True,
                          ("Audit:ExcursionRecommended", "Notification:RegistrarQueued")),
        "Approve": Rule("Registrar", "Recommended", "Approved", False, ("Audit:ExcursionApproved",)),
        "Reject": Rule("Registrar", rejection_source, "Rejected", False, ("Audit:ExcursionRejected",)),
        "Revise": Rule("Teacher", "Rejected", "Draft", False, ("Audit:ExcursionReopened",)),
    }


# The trusted synthetic directory shipped with the store (ADR-011): id -> (role, active, assigned).
FIXTURE_DIRECTORY = {
    "teacher-assigned": ("Teacher", True, True),
    "teacher-unassigned": ("Teacher", True, False),
    "teacher-revoked": ("Teacher", False, True),
    "registrar": ("Registrar", True, False),
    "viewer": ("Viewer", True, False),
}


# --- Outcomes ---------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Committed:
    """A newly committed transition: resulting state/version and the effects it queued."""

    state: str
    version: int
    effects: tuple[str, ...]


@dataclass(frozen=True)
class Replayed:
    """A duplicate of an earlier identical command: the original result, and no new effects."""

    original: Committed


@dataclass(frozen=True)
class Refused:
    """A rejected command or authoring call, identified by its stable error code; nothing changes."""

    code: str


Outcome = Committed | Replayed | Refused


@dataclass(frozen=True)
class Command:
    operation_id: str
    actor_id: str
    instance_id: str
    action: str
    expected_version: int


@dataclass
class Actor:
    role: str
    active: bool
    assigned: bool


@dataclass
class Instance:
    state: str
    version: int
    semantics: str  # the rejection source of the candidate the instance was created from


@dataclass
class ReferenceRuntime:
    """Mutable reference state for one Change Case holding one candidate model."""

    case_version: int
    rejection_source: str = "Recommended"
    actors: dict[str, Actor] = field(default_factory=lambda: {
        actor_id: Actor(*row) for actor_id, row in FIXTURE_DIRECTORY.items()})
    instances: dict[str, Instance] = field(default_factory=dict)
    operations: dict[str, tuple[tuple, Committed]] = field(default_factory=dict)
    audit: list[tuple[str, str, str, str]] = field(default_factory=list)  # (kind, operation, actor, instance)
    outbox: set[tuple[str, str]] = field(default_factory=set)  # (operation, kind)
    semantic_edits: list[tuple[int, int, str]] = field(default_factory=list)  # (from_version, to_version, source)

    # --- Execution ----------------------------------------------------------------------------------

    def predict(self, command: Command) -> Outcome:
        """The outcome the specification requires; does not change the reference state."""
        instance = self.instances.get(command.instance_id)
        if instance is None:
            return Refused("NOT_FOUND")
        if instance.semantics != self.rejection_source:
            return Refused("STALE_INSTANCE")
        rule = rules(self.rejection_source).get(command.action)
        if rule is None:
            return Refused("ACTION_DENIED")
        actor = self.actors.get(command.actor_id)
        if actor is None:
            return Refused("UNKNOWN_ACTOR")
        if not actor.active:
            return Refused("ACTOR_REVOKED")
        if actor.role != rule.role:
            return Refused("ROLE_DENIED")
        if rule.needs_assignment and not actor.assigned:
            return Refused("ASSIGNMENT_DENIED")
        prior = self.operations.get(command.operation_id)
        if prior is not None:
            binding, original = prior
            return Replayed(original) if binding == self._binding(command) else Refused("OPERATION_CONFLICT")
        if instance.version != command.expected_version:
            return Refused("STALE_VERSION")
        if instance.state != rule.source:
            return Refused("STATE_DENIED")
        return Committed(rule.target, instance.version + 1, rule.effects)

    def execute(self, command: Command) -> Outcome:
        """Predict, then apply a commit (state, audit, outbox, operation record) to the reference."""
        outcome = self.predict(command)
        if isinstance(outcome, Committed):
            instance = self.instances[command.instance_id]
            instance.state, instance.version = outcome.state, outcome.version
            for effect in outcome.effects:
                if effect.startswith("Audit:"):
                    self.audit.append((effect, command.operation_id, command.actor_id, command.instance_id))
                else:
                    self.outbox.add((command.operation_id, effect))
            self.operations[command.operation_id] = (self._binding(command), outcome)
        return outcome

    def _binding(self, command: Command) -> tuple:
        """Full command plus model identity; the operation id is the key it is bound under."""
        semantics = self.instances[command.instance_id].semantics
        return (command.actor_id, command.instance_id, command.action, command.expected_version, semantics)

    # --- Preview and authoring ----------------------------------------------------------------------

    def predict_reset(self, state: str | None, case_version: int) -> Refused | None:
        if case_version != self.case_version:
            return Refused("STALE_VERSION")
        if state and state not in STATES:
            return Refused("INVALID_STATE")
        return None

    def reset(self, instance_id: str, state: str | None) -> None:
        """Record the fresh isolated instance a successful reset created; nothing is migrated."""
        self.instances[instance_id] = Instance(state or INITIAL_STATE, 0, self.rejection_source)

    def predict_edit(self, case_version: int, can_edit: bool) -> Refused | None:
        """The typed semantic edit. Capability is checked before the case version."""
        if not can_edit:
            return Refused("AUTHORITY_REQUIRED")
        if case_version != self.case_version:
            return Refused("STALE_VERSION")
        return None

    def apply_edit(self, source: str) -> None:
        """Record an accepted edit. Instances of the previous model become stale unless the model is
        unchanged (their ``semantics`` no longer equals the case's)."""
        # Even a no-op semantic command is an accepted, versioned owner edit (ADR-0148).
        self.semantic_edits.append((self.case_version, self.case_version + 1, source))
        self.rejection_source = source
        self.case_version += 1

    # --- Trusted directory changes (outside the kernel's write API) ----------------------------------

    def set_actor(self, actor_id: str, column: str, value: object) -> None:
        setattr(self.actors[actor_id], column, value)

    # --- Views --------------------------------------------------------------------------------------

    def counts(self) -> dict[str, int]:
        return {"audit": len(self.audit), "outbox": len(self.outbox), "operations": len(self.operations)}

    def enabled_actions(self, instance_id: str) -> list[str]:
        """Actions whose source is the instance's state. Used only to bias generation, never as oracle."""
        instance = self.instances.get(instance_id)
        if instance is None:
            return []
        return [a for a, r in rules(self.rejection_source).items() if r.source == instance.state]

    def holders(self, action: str) -> list[str]:
        """Actor ids currently holding the action's role. Used only to bias generation."""
        rule = rules(self.rejection_source).get(action)
        return sorted(a for a, actor in self.actors.items() if rule is not None and actor.role == rule.role)
