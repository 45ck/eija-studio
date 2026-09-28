"""Deterministic offline fixture. It is not an LLM and never touches the network."""
from __future__ import annotations
from eija_studio.domain.models import Proposal, Alternative, Workflow
from eija_studio.application.ports import ProviderResult


class OfflineProvider:
    name, networked = "offline", False
    def doctor(self) -> dict:
        return {"provider": self.name, "ready": True, "live_test": "NOT_APPLICABLE", "note": "Deterministic demo fixture, not an LLM"}
    def propose(self, request: str, model: Workflow) -> ProviderResult:
        related = "excursion" in request.lower() and any(x in request.lower() for x in ("teacher", "recommend", "sign"))
        alternatives = (
            Alternative(interpretation="recommend_only", explanation="Teachers recommend; registrar approval and rejection initially require Recommended."),
            Alternative(interpretation="final_approval", explanation="Would expand final approval authority. Protected policy blocks this."),
            Alternative(interpretation="confirm_only", explanation="Would confirm a section rather than recommend the excursion. Not implemented."),
        ) if related else (Alternative(interpretation="unsupported", explanation="This offline fixture only demonstrates teacher sign-off for excursions."),)
        return ProviderResult(Proposal(summary="Deterministic demonstration; no model inference was used.", alternatives=alternatives,
            unknowns=("Actual school policy is unknown.", "Reviewer comprehension has not been measured.")), self.name, "fixture-v1", {}, False)
