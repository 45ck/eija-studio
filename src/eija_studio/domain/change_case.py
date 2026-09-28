from __future__ import annotations
from typing import Literal
from .models import Contract, Workflow, Proposal, SemanticTransaction, DomainError


class ChangeCase(Contract):
    """Aggregate boundary: transitions are mediated by the application and CAS store."""
    id: str
    version: int
    stage: Literal["DRAFT", "PROPOSED", "PREVIEW", "SAVED", "VERIFIED", "APPROVED", "APPLIED", "DISCARDED"]
    request: str
    baseline_version: int
    baseline: Workflow
    candidate: Workflow | None
    proposal: Proposal | None
    provider_run: dict | None
    selected_meaning: str | None
    selected_by: str | None
    transactions: tuple[SemanticTransaction, ...]
    layout: dict[str, dict[str, int]]
    receipts: tuple[dict, ...]
    decision: dict | None
    created_at: str

    def require_editable(self) -> None:
        if self.stage in {"APPLIED", "DISCARDED"}:
            raise DomainError("CASE_CLOSED", "Create a new Change Case; this case is closed")

    def at_version(self, expected: int) -> None:
        if self.version != expected:
            raise DomainError("STALE_VERSION", "Case changed; reload before acting")

    def executable(self) -> Workflow:
        if self.candidate is None or self.selected_meaning is None:
            raise DomainError("MEANING_REQUIRED", "An explicit supported meaning must be selected first")
        return self.candidate
