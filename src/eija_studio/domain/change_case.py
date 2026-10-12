from __future__ import annotations
from typing import Annotated, Any, Literal
from pydantic import Field
from .models import Contract, Workflow, Proposal, DomainError
from .transactions import Transaction
from .generated_app import GeneratedAppBinding


class OwnerPlanStep(Contract):
    """Reported proposal provenance, never a capability or an owner decision."""
    transaction: Transaction
    author: Literal["you", "ai"]
    round: int = Field(ge=1, strict=True)
    request: str = Field(max_length=6000)


class OwnerPlanRequest(Contract):
    """Exact accepted workflow commands and the identities of their reviewed preview."""
    request: str = Field(min_length=1, max_length=6000)
    pack_id: str = Field(min_length=1, max_length=40)
    expected_pack_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_baseline_version: int = Field(ge=0, strict=True)
    expected_baseline_semantic_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_candidate_semantic_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    steps: tuple[OwnerPlanStep, ...] = Field(min_length=1, max_length=64)
    expected_build_digest: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


class PackMeaningSelection(Contract):
    kind: Literal["pack_meaning"]
    meaning: str


class OwnerPlanSelection(Contract):
    kind: Literal["owner_plan"]
    pack_id: str
    pack_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    baseline_semantic_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    candidate_semantic_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    steps: tuple[OwnerPlanStep, ...] = Field(min_length=1, max_length=64)


Selection = Annotated[PackMeaningSelection | OwnerPlanSelection, Field(discriminator="kind")]


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
    provider_run: dict[str, Any] | None
    selected_meaning: str | None
    selected_by: str | None
    selection: Selection | None = None  # legacy cases retain their selected_meaning without rewriting history
    transactions: tuple[Transaction, ...]
    redo_transactions: tuple[Transaction, ...] = ()  # stack: next redo is last; initial meaning never enters it
    layout: dict[str, dict[str, int]]
    receipts: tuple[dict[str, Any], ...]
    decision: dict[str, Any] | None
    app_build: GeneratedAppBinding | None = None
    created_at: str

    def require_editable(self) -> None:
        if self.stage in {"APPLIED", "DISCARDED"}:
            raise DomainError("CASE_CLOSED", "Create a new Change Case; this case is closed")

    def at_version(self, expected: int) -> None:
        if self.version != expected:
            raise DomainError("STALE_VERSION", "Case changed; reload before acting")

    def executable(self) -> Workflow:
        if self.candidate is None or (self.selected_meaning is None and self.selection is None):
            raise DomainError("MEANING_REQUIRED", "An explicit supported meaning must be selected first")
        return self.candidate
