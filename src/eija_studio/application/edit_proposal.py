"""A read-only offline proposal over one captured candidate; owner edits keep their existing boundary."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from eija_studio.domain.affordance import affordances
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.models import Contract, DomainError
from eija_studio.domain.pack import Pack
from eija_studio.domain.transactions import parse_transaction

from .edit_preview import EditPreview, preview_edit
from .history import replay
from .ports import EditProposer


class EditProposalPack(Contract):
    id: str
    digest: str


class TypedEditProposal(Contract):
    scope: Literal["typed-edit-proposal"] = "typed-edit-proposal"
    provider: Literal["offline"] = "offline"
    model: Literal["typed-edit-fixture-v1"] = "typed-edit-fixture-v1"
    live: Literal[False] = False
    trust: Literal["UNTRUSTED_PROPOSAL"] = "UNTRUSTED_PROPOSAL"
    request: str = Field(min_length=1, max_length=6000)
    pack: EditProposalPack
    preview: EditPreview


def propose_edit(case: ChangeCase, request: str, pack: Pack, proposer: EditProposer | None) -> TypedEditProposal:
    """No persistence or evidence: resolve one request, then use the existing policy-checked projection."""
    if proposer is None:
        raise DomainError("EDIT_PROPOSER_UNAVAILABLE", "No offline typed-edit proposer is configured")
    if not isinstance(request, str) or not request.strip() or len(request) > 6000:
        raise DomainError("INVALID_REQUEST", "Provide 1-6000 characters of synthetic edit request text")
    case.require_editable()
    model = case.executable()
    replay(case, pack)
    choices = tuple(parse_transaction(entry["transaction"]) for entry in affordances(model, pack))
    raw = proposer.propose(request, model, choices)
    try:
        transaction = parse_transaction(raw)
    except DomainError:
        raise DomainError("EDIT_PROPOSAL_INVALID", "The edit proposer returned an invalid transaction; no model was changed.") from None
    if transaction not in choices:
        raise DomainError("EDIT_PROPOSAL_INVALID", "The proposed transaction is outside this captured model's edit choices.")
    return TypedEditProposal(request=request, pack=EditProposalPack(id=pack.id, digest=pack.digest),
                             preview=preview_edit(case, transaction, pack))
