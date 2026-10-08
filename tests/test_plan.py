"""Plan mode (ADR-0156): the chat's AI proposes typed steps; each is re-checked, and only accepted ones are previewed."""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.adapters.plan_proposals import OfflinePlanProposer
from eija_studio.application.plan import preview_plan, propose_plan
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.domain.transactions import parse_transaction

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
TWO_STEPS = "add state Lost after Overdue then add Renew from Overdue to Lost for Librarian"


def plan(request: str, proposer=None) -> dict:
    return propose_plan(request, LOAN.model, LOAN, proposer or OfflinePlanProposer())


def transactions(result: dict) -> list:
    return [parse_transaction(s["transaction"]) for s in result["steps"]]


def test_a_request_becomes_numbered_typed_steps_previewed_through_the_policy():
    result = plan(TWO_STEPS)
    assert result["trust"] == "UNTRUSTED_PROPOSAL" and result["live"] is False
    assert [s["text"] for s in result["steps"]] == ["Add state Lost after Overdue", "Add Renew: Overdue → Lost, by Librarian"]
    assert result["steps"][1]["transaction"]["id"] == "TR-RENEW"
    preview = result["preview"]
    assert preview["legal"] and preview["diff"]["added_states"] == ["Lost"] and preview["diff"]["added_actions"] == ["Renew"]
    assert "Lost" in preview["candidate"]["states"]


def test_rejecting_a_step_that_another_needs_says_so():
    preview = preview_plan(LOAN.model, LOAN, transactions(plan(TWO_STEPS)), [False, True])
    assert [s["status"] for s in preview["steps"]] == ["rejected", "does_not_apply"]
    assert not preview["legal"] and preview["codes"] == ["PLAN_STEP_DOES_NOT_APPLY"] and preview["candidate"] is None
    nothing = preview_plan(LOAN.model, LOAN, transactions(plan(TWO_STEPS)), [False, False])
    assert nothing["accepted"] == 0 and nothing["candidate"] is None and nothing["codes"] == []


def test_the_policy_still_decides():
    preview = plan("allow Member to CheckOut")["preview"]  # a protected authority: proposing it does not make it allowed
    assert not preview["legal"] and any(code.startswith("PROTECTED_AUTHORITY") for code in preview["codes"])


def test_a_described_change_the_pack_models_becomes_its_meanings_steps():
    result = plan("Members should be able to renew a loan")
    assert result["meaning"] == "allow_renewal" and result["preview"]["legal"]
    assert [s["transaction"]["kind"] for s in result["steps"]] == ["add_transition"]


@pytest.mark.parametrize(("request_text", "code"), [
    ("make it better", "PLAN_REQUEST_UNSUPPORTED"),
    ("add state Lost then frobnicate", "PLAN_REQUEST_UNSUPPORTED"),
    ("remove state Nowhere", "PLAN_UNKNOWN_NAME"),
    ("add Teleport from OnLoan to Returned for Librarian", "PLAN_UNKNOWN_NAME"),
    ("   ", "PLAN_REQUEST_INVALID"),
])
def test_requests_it_cannot_read_are_refused(request_text, code):
    with pytest.raises(DomainError) as error:
        plan(request_text)
    assert error.value.code == code


class Rogue:
    """A proposer that tries to slip something past the plan checks."""
    name, live = "rogue", False

    def __init__(self, document):
        self.document = document

    def propose(self, request, model, pack):
        return self.document


@pytest.mark.parametrize("document", [
    {"steps": []},
    {"steps": [{"transaction": {"kind": "approve_case"}}]},
    {"steps": [{"transaction": {"kind": "add_state", "state": "X"}}] * 13},
    {"summary": "no steps"},
    ["not", "a", "plan"],
])
def test_an_untrusted_plan_is_rechecked(document):
    with pytest.raises(DomainError) as error:
        plan("anything", Rogue(document))
    assert error.value.code in {"PLAN_INVALID", "EDIT_INVALID"}


def test_a_proposer_cannot_name_a_meaning_the_pack_lacks():
    result = plan("x", Rogue({"meaning": "approve_everything", "steps": [{"transaction": {"kind": "add_state", "state": "X"}}]}))
    assert result["meaning"] is None
