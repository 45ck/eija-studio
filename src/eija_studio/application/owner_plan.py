"""Exact owner-plan case construction; authority and atomic storage remain in Studio.

This adapter checks the submitted subjects and reuses the existing typed transaction
interpreter. It neither selects on behalf of a principal nor persists a case or audit.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

from eija_studio.domain.change_case import ChangeCase, OwnerPlanRequest, OwnerPlanSelection
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_transactions


def _owner_plan_case(command: OwnerPlanRequest, selected_by: str, active: dict[str, Any],
                     pack: Pack, timestamp: Callable[[], str]) -> tuple[ChangeCase, dict[str, Any]]:
    """Recompute exactly one accepted batch and prepare its case and audit payload."""
    baseline = Workflow.model_validate(active["model"])
    if command.pack_id != pack.id or command.expected_pack_digest != pack.digest:
        raise DomainError("PACK_CHANGED", "The domain pack changed; review a new preview")
    if (command.expected_baseline_version != active["version"]
            or command.expected_baseline_semantic_hash != baseline.semantic_hash):
        raise DomainError("STALE_BASELINE", "The model in force changed; review a new preview")
    transactions = tuple(step.transaction for step in command.steps)
    candidate = apply_transactions(baseline, transactions, pack)
    if candidate.semantic_hash != command.expected_candidate_semantic_hash:
        raise DomainError("CANDIDATE_CHANGED", "The exact commands do not reproduce the reviewed candidate")
    selection = OwnerPlanSelection(kind="owner_plan", pack_id=pack.id, pack_digest=pack.digest,
        baseline_semantic_hash=baseline.semantic_hash, candidate_semantic_hash=candidate.semantic_hash,
        steps=command.steps)
    case = ChangeCase(id=uuid4().hex, version=0, stage="PREVIEW", request=command.request,
        baseline_version=active["version"], baseline=baseline, candidate=candidate,
        proposal=None, provider_run=None, selected_meaning=None, selected_by=selected_by,
        selection=selection, transactions=transactions, layout={}, receipts=(), decision=None, created_at=timestamp())
    event = {"case_id": case.id, "by": selected_by,
        "selection": selection.model_dump(mode="json"), "baseline_version": active["version"],
        "provenance_note": "Step authorship is reported proposal provenance, not authenticated authority"}
    return case, event
