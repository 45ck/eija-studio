"""Live plan proposer for the PlayIDE chat (ADR-0230): a model reads the request, the pack decides the steps.

Opt-in only. The offline proposer stays the default; this one is used for a request only when the Studio was
started with a networked provider and ``--allow-network``, and the person ticked consent for that request.

The model never writes steps. Exact phrases ("add state X after Y") are still read by the offline grammar, so a
precise request costs nothing and never leaves the machine. Anything else goes to the provider, whose first
alternative must be one of the pack's meanings; that meaning's own transactions become the plan, and the kernel
then checks it like any other. An unsafe meaning is planned as asked and refused by its law (issue #152), never
swapped for a safe one. A meaning with nothing to plan is refused with the model's explanation.

A request that is partly exact phrases and partly prose is refused before anything is sent: the model plans one
meaning, so the clauses the grammar read would be dropped from the plan without a word. One call runs at a time;
a second while one is in flight is refused with PROVIDER_BUSY, so a double send is never billed twice.
A request shaped like an exact phrase but naming something the model lacks ("add state X after Nowhere") gets the
phrase reader's answer and is not sent: the model would read it as some meaning and plan that instead.
Every call that leaves the machine is written to the audit log, as `Studio.propose` writes its own: started, then
received or not accepted, with a hash of the request and never the request itself.
"""
from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import Any
from uuid import uuid4

from .plan_proposals import clauses_read
from eija_studio.application.ports import PlanProposer, ProposalProvider
from eija_studio.domain.models import DomainError, Workflow, fingerprint
from eija_studio.domain.pack import Pack


class LivePlanProposer:
    live = True

    def __init__(self, provider: ProposalProvider, offline: PlanProposer):
        self.provider, self.offline = provider, offline
        self.name = f"live:{provider.name}"
        self._calling = Lock()
        self.audit: Callable[[str, dict[str, Any]], None] | None = None  # the studio's audit log, wired by bootstrap

    def _record(self, kind: str, body: dict[str, Any]) -> None:
        if self.audit is not None:
            self.audit(kind, body)

    def _offline_phrases(self, request: str, model: Workflow, pack: Pack, grows: bool) -> dict[str, Any] | None:
        """The offline reading when every clause is an exact phrase; None when the request needs a model."""
        try:
            plan = self.offline.propose(request, model, pack, grows=grows)
        except DomainError as error:
            if error.code in ("PLAN_UNKNOWN_NAME", "PLAN_LIMIT_UNSUPPORTED"):  # its answer, not the model's: a phrase naming
                # what the model lacks, or a limit no plan step can hold
                raise
            read, clauses = clauses_read(request, model, pack, grows=grows)
            if 0 < read < clauses:
                raise DomainError("PLAN_REQUEST_MIXED", "This request mixes exact changes with a description. The model plans "
                                  "one meaning and would drop the exact changes, so send them as a separate request.") from None
            return None
        return plan | {"answered_offline_by": self.offline.name} if plan.get("meaning") is None else None

    def propose(self, request: str, model: Workflow, pack: Pack, *, grows: bool = False) -> dict[str, Any]:
        exact = self._offline_phrases(request, model, pack, grows)
        if exact is not None:
            return exact
        if not self._calling.acquire(blocking=False):
            raise DomainError("PROVIDER_BUSY", "One live request is already running; no duplicate call was made")
        attempt = uuid4().hex
        try:
            self._record("PlanProviderCallStarted", {"attempt_id": attempt, "provider": self.provider.name,
                                                     "request_hash": fingerprint(request), "egress": True})
            try:
                reply = self.provider.propose(request, model).proposal
            except DomainError as error:
                self._record("PlanProviderCallNotAccepted", {"attempt_id": attempt, "error_code": error.code,
                                                             "billing": "UNKNOWN for a started network request"})  # vocab-ok: provider cost field of an event payload, not a pack actor
                raise
            self._record("PlanProposalReceived", {"attempt_id": attempt, "provider": self.provider.name,
                                                  "meaning": reply.alternatives[0].interpretation})
        finally:
            self._calling.release()
        first = reply.alternatives[0]
        meaning = pack.meaning(first.interpretation)
        if meaning is None or not meaning.transactions:
            raise DomainError("PLAN_REQUEST_UNSUPPORTED", f"The model read this as something the pack does not model: {first.explanation}"[:600])
        return {"summary": meaning.label, "meaning": meaning.id,
                "steps": [{"transaction": t.model_dump(mode="json"), "why": first.explanation} for t in meaning.transactions]}

    def follow_on(self, ripple: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any]:
        return self.offline.follow_on(ripple, model, pack)
