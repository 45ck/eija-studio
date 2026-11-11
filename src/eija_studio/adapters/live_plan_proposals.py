"""Live plan proposer for the PlayIDE chat (ADR-0230): a model reads the request, the pack decides the steps.

Opt-in only. The offline proposer stays the default; this one is used for a request only when the Studio was
started with a networked provider and ``--allow-network``, and the person ticked consent for that request.

The model never writes steps. Exact phrases ("add state X after Y") are still read by the offline grammar, so a
precise request costs nothing and never leaves the machine. Anything else goes to the provider, whose first
alternative must be one of the pack's meanings; that meaning's own transactions become the plan, and the kernel
then checks it like any other. An unsafe meaning is planned as asked and refused by its law (issue #152), never
swapped for a safe one. A meaning with nothing to plan is refused with the model's explanation.
"""
from __future__ import annotations

from typing import Any

from eija_studio.application.ports import PlanProposer, ProposalProvider
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack


class LivePlanProposer:
    live = True

    def __init__(self, provider: ProposalProvider, offline: PlanProposer):
        self.provider, self.offline = provider, offline
        self.name = f"live:{provider.name}"

    def _offline_phrases(self, request: str, model: Workflow, pack: Pack, grows: bool) -> dict[str, Any] | None:
        """The offline reading when every clause is an exact phrase; None when the request needs a model."""
        try:
            plan = self.offline.propose(request, model, pack, grows=grows)
        except DomainError:
            return None
        return plan | {"answered_offline_by": self.offline.name} if plan.get("meaning") is None else None

    def propose(self, request: str, model: Workflow, pack: Pack, *, grows: bool = False) -> dict[str, Any]:
        exact = self._offline_phrases(request, model, pack, grows)
        if exact is not None:
            return exact
        reply = self.provider.propose(request, model).proposal
        first = reply.alternatives[0]
        meaning = pack.meaning(first.interpretation)
        if meaning is None or not meaning.transactions:
            raise DomainError("PLAN_REQUEST_UNSUPPORTED", f"The model read this as something the pack does not model: {first.explanation}"[:600])
        return {"summary": meaning.label, "meaning": meaning.id,
                "steps": [{"transaction": t.model_dump(mode="json"), "why": first.explanation} for t in meaning.transactions]}

    def follow_on(self, ripple: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any]:
        return self.offline.follow_on(ripple, model, pack)
