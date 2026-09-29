"""Frozen copy of the hand-written excursion policy as it was before domain packs (commit 1540f46).

A test ORACLE only: the pack-driven policy (``domain.policy.check_policy`` with the excursion pack) must return
exactly these codes on every model (tests/test_pack.py). Never imported by the kernel."""
from __future__ import annotations

from typing import Any

from eija_studio.domain.models import BASE_GUARDS, Workflow

FORBIDDEN = ("PaymentCaptured", "ParentDataExported")
EFFECTS = {
    "Submit": ("Audit:ExcursionSubmitted",),
    "Recommend": ("Audit:ExcursionRecommended", "Notification:RegistrarQueued"),
    "Approve": ("Audit:ExcursionApproved",),
    "Reject": ("Audit:ExcursionRejected",),
    "Revise": ("Audit:ExcursionReopened",),
}
CANONICAL_OPTIONS: dict[str, dict[str, Any]] = {
    "recommend_only": {"label": "Teacher recommends; registrar decides", "supported": True,
        "consequences": ["Only active, assigned teachers recommend.", "Registrar approval AND rejection initially require Recommended.", "Teachers do not receive final approval authority."]},
    "final_approval": {"label": "Teacher grants final approval", "supported": False,
        "consequences": ["Expands protected authority; blocked by this POC's policy."]},
    "confirm_only": {"label": "Teacher confirms a completed section", "supported": False,
        "consequences": ["A different domain operation; not implemented by this bounded POC."]},
    "unsupported": {"label": "Outside the modelled scope", "supported": False,
        "consequences": ["Requires domain and source-level engineering; no automatic application."]},
}


def check_policy(model: Workflow) -> list[str]:
    errors: list[str] = []
    by = {t.action: t for t in model.transitions}
    candidate = "Recommend" in by
    expected_actions = {"Submit", "Approve", "Reject", "Revise"} | ({"Recommend"} if candidate else set())
    expected_states = {"Draft", "Submitted", "Approved", "Rejected"} | ({"Recommended"} if candidate else set())
    if set(by) != expected_actions or set(model.states) != expected_states or model.initial_state != "Draft":
        errors.append("UNSUPPORTED_WORKFLOW_SHAPE")
    expected = {
        "Submit": ("Teacher", "Draft", "Submitted"),
        "Revise": ("Teacher", "Rejected", "Draft"),
        "Approve": ("Registrar", "Recommended" if candidate else "Submitted", "Approved"),
        "Reject": ("Registrar", None if candidate else "Submitted", "Rejected"),
        "Recommend": ("Teacher", "Submitted", "Recommended"),
    }
    for action, t in by.items():
        if action not in expected:
            errors.append("UNSUPPORTED_ACTION"); continue
        role, source, target = expected[action]
        if t.role != role:
            errors.append("PROTECTED_AUTHORITY:" + action)
        if t.to_state != target or (source is not None and t.from_state != source):
            errors.append("PROTECTED_STATE:" + action)
        if action == "Reject" and t.from_state not in {"Recommended", "Submitted"}:
            errors.append("UNSUPPORTED_REJECTION_SOURCE")
        expected_guards = set(BASE_GUARDS) | ({"actor_assigned"} if action == "Recommend" else set())
        if set(t.guards) != expected_guards:
            errors.append("GUARD_POLICY:" + action)
        if set(t.required_effects) != set(EFFECTS[action]) or not set(FORBIDDEN).issubset(t.forbidden_effects):
            errors.append("EFFECT_POLICY:" + action)
    return sorted(set(errors))
