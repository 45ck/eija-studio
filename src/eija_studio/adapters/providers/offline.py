"""Deterministic offline fixture. It is not an LLM and never touches the network. Its answers come from the pack."""
from __future__ import annotations
from eija_studio.domain.models import Proposal, Workflow
from eija_studio.domain.pack import Pack, ProposalRule, default_pack
from eija_studio.application.ports import ProviderResult


def matches_rule(rule: ProposalRule, text: str) -> bool:
    """The rule's reading of a request: the lower-cased text contains every ``all`` word and one ``any`` word (so a
    plural or a longer word still counts). The chat's plan proposer reads the same rules the same way."""
    text = text.lower()
    return all(w in text for w in rule.all) and (not rule.any or any(w in text for w in rule.any))


class OfflineProvider:
    name, networked = "offline", False

    def __init__(self, pack: Pack | None = None):
        self.pack = pack if pack is not None else default_pack()

    def doctor(self) -> dict:
        return {"provider": self.name, "ready": True, "live_test": "NOT_APPLICABLE", "note": "Deterministic demo fixture, not an LLM"}

    def propose(self, request: str, model: Workflow) -> ProviderResult:
        fixture, text = self.pack.fixtures.proposals, request.lower()
        rule = next((r for r in fixture.rules if matches_rule(r, text)), None)
        alternatives = rule.alternatives if rule is not None else fixture.fallback
        return ProviderResult(Proposal(summary=fixture.summary, alternatives=alternatives, unknowns=fixture.unknowns),
                              self.name, "fixture-v1", {}, False)
