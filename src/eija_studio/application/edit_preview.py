"""Read-only edit projection over one captured case, using the same interpreter as owner edits."""
from __future__ import annotations

from typing import Literal

from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.models import Contract, DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_transaction
from eija_studio.domain.transactions import Transaction

from .history import replay


class EditPreview(Contract):
    """An uncommitted candidate bound to a captured case revision; no evidence or edit authority."""

    legal: bool
    codes: list[str]
    refs: list[str]
    case_id: str
    version: int
    stage: str
    semantic_hash: str
    transaction: Transaction
    current: Workflow
    candidate: Workflow | None
    candidate_semantic_hash: str | None
    applied: Literal[False] = False
    persisted: Literal[False] = False
    scope: Literal["semantic-edit-preview"] = "semantic-edit-preview"


def preview_edit(case: ChangeCase, transaction: Transaction, pack: Pack) -> EditPreview:
    """The candidate edit would produce from this snapshot, or its refusal without a guessed model."""
    current = case.candidate if case.candidate is not None else case.baseline
    candidate = None
    codes: list[str] = []
    refs: list[str] = []
    try:
        case.require_editable()
        replay(case, pack)
        candidate = apply_transaction(case.executable(), transaction, pack)
    except DomainError as error:
        details = error.details or {}
        codes = list(details.get("codes") or [error.code])
        refs = list(details.get("refs") or [])
    return EditPreview(
        legal=candidate is not None, codes=codes, refs=refs, case_id=case.id, version=case.version,
        stage=case.stage, semantic_hash=current.semantic_hash, transaction=transaction, current=current,
        candidate=candidate, candidate_semantic_hash=candidate.semantic_hash if candidate is not None else None,
    )
