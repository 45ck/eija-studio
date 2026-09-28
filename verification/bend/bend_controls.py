"""Negative controls: deliberately unsafe models the committed proofs must REJECT.

A proof that also "proves" an unsafe model is worthless, so trust in ``PROOF.bend`` rests on these
controls as much as on the passing run. Each control is a variant of the shipped models, generated
through the same ``render_main`` path, and names the laws it is designed to break. The runner runs the
unchanged ``LAWS.bend`` / ``PROOF.bend`` against each one and requires the proof to fail, exactly the
named laws to fail, and a concrete counterexample (a trace or an emitted effect) to confirm that the
property really is violated in the unsafe model.

Model-level controls change the Python ``Workflow`` (what a provider or a careless edit could
produce); the kernel's own ``check_policy`` independently rejects each of them, which the report
records next to Bend's verdict. The engine-level control changes the fixed part of the Bend program
(the guard evaluator) to show the revocation law is sensitive to the semantics and not only to the
tables; it has no ``Workflow`` form.

What this establishes: the proofs are sensitive to the seeded faults. What it does NOT establish:
that no *other* fault escapes them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from bend_generate import UNSAFE_EXAMPLE, ModelError, default_models, load_workflow, render_main
from eija_studio.domain.models import Workflow
from eija_studio.domain.policy import check_policy

_LIVE = "def live(a: Actor) -> Bool:\n  Actor{role, active, assigned} = a\n  active\n"


@dataclass(frozen=True)
class Control:
    name: str
    description: str
    expected_failing_laws: tuple[str, ...]
    # A concrete trace on the Candidate slot showing the fault is real (the law is false here, not
    # merely unproven): (actor id, action) steps and the state Bend must reach when replaying them.
    witness_steps: tuple[tuple[str, str], ...] = ()
    witness_state: str = ""
    # For a fault about emitted effects: (actor id, action, state) and the effect that step must emit.
    probe: tuple[str, str, str] | None = None
    probe_effect: str = ""
    candidate: Callable[[], Workflow] | None = None  # model-level control: the mutated Candidate workflow
    engine_edit: tuple[str, str] | None = None  # engine-level control: (text to replace, replacement)

    def workflow(self) -> Workflow | None:
        return self.candidate() if self.candidate else None

    def build(self) -> str:
        """Text of the mutated ``main.bend``."""
        models = default_models()
        if self.candidate is not None:
            models["Candidate"] = self.candidate()
        text = render_main(models)
        if self.engine_edit is not None:
            old, new = self.engine_edit
            if old not in text:
                raise ModelError("engine template changed: update the engine control")
            text = text.replace(old, new)
        return text

    def kernel_policy_findings(self) -> list[str] | None:
        """What the kernel's own protected policy reports for the mutated workflow (None: not a Workflow fault)."""
        workflow = self.workflow()
        return None if workflow is None else check_policy(workflow)


def _candidate() -> Workflow:
    return default_models()["Candidate"]


def _mutate(workflow: Workflow, action: str, **changes: object) -> Workflow:
    """Copy of the workflow with one transition changed (Workflow re-validates on construction)."""
    data = workflow.model_dump(mode="json")
    hit = [t for t in data["transitions"] if t["action"] == action]
    if len(hit) != 1:
        raise ModelError(f"expected exactly one {action} transition")
    hit[0].update({k: list(v) if isinstance(v, tuple) else v for k, v in changes.items()})
    return Workflow.model_validate(data)


def _transition(workflow: Workflow, action: str):
    return next(t for t in workflow.transitions if t.action == action)


def _approve_skips_recommendation() -> Workflow:
    return _mutate(_candidate(), "Approve", from_state="Submitted")


def _unassigned_may_recommend() -> Workflow:
    guards = tuple(g for g in _transition(_candidate(), "Recommend").guards if g != "actor_assigned")
    return _mutate(_candidate(), "Recommend", guards=guards)


def _reject_from_draft() -> Workflow:
    return _mutate(_candidate(), "Reject", from_state="Draft")


def _payment_effect_emitted() -> Workflow:
    effects = (*_transition(_candidate(), "Approve").required_effects, "PaymentCaptured")
    return _mutate(_candidate(), "Approve", required_effects=effects, forbidden_effects=())


CONTROLS: tuple[Control, ...] = (
    Control("teacher_final_approval",
            "examples/unsafe-teacher-final-approval.json: the candidate lets a Teacher perform Approve "
            "(the excursion the kernel's policy blocks as PROTECTED_AUTHORITY:Approve)",
            ("teacher_never_approves", "teacher_sequences_never_approve"),
            (("teacher-assigned", "Submit"), ("teacher-assigned", "Recommend"), ("teacher-assigned", "Approve")), "Approved",
            candidate=lambda: load_workflow(UNSAFE_EXAMPLE)),
    Control("approve_skips_recommendation",
            "the candidate's Approve fires from Submitted, so Approved is reachable without Recommended",
            ("approved_only_from_recommended", "every_path_to_approved_passes_recommended"),
            (("teacher-assigned", "Submit"), ("registrar", "Approve")), "Approved",
            candidate=_approve_skips_recommendation),
    Control("unassigned_may_recommend",
            "the candidate's Recommend drops the actor_assigned guard",
            ("unassigned_teacher_cannot_recommend",),
            (("teacher-assigned", "Submit"), ("teacher-unassigned", "Recommend")), "Recommended",
            candidate=_unassigned_may_recommend),
    Control("reject_from_draft",
            "the candidate's Reject fires from Draft instead of the declared rejection source",
            ("reject_only_from_declared_source",),
            (("registrar", "Reject"),), "Rejected",
            candidate=_reject_from_draft),
    Control("payment_effect_emitted",
            "the candidate's Approve declares the forbidden effect PaymentCaptured and drops its forbidden list",
            ("forbidden_effects_never_emitted",),
            probe=("registrar", "Approve", "Recommended"), probe_effect="PaymentCaptured",
            candidate=_payment_effect_emitted),
    Control("engine_ignores_revocation",
            "the guard evaluator ignores whether the actor is still active (a revoked actor keeps authority)",
            ("revoked_teacher_cannot_recommend",),
            (("teacher-revoked", "Submit"), ("teacher-revoked", "Recommend")), "Recommended",
            engine_edit=(_LIVE, _LIVE.replace("  active\n", "  True{}\n"))),
)
