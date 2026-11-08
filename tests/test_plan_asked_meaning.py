"""The offline chat plans the change a request asked for, safe or not (issue #152).

It used to skip a matching unsupported meaning and plan the next supported one, so "let support agents issue
refunds" was answered with "customers can take back a refund request" and a green "the policy allows it". Now the
unsafe change is planned as asked, and the policy refuses it and names the law; a safe request still plans its own
meaning, and every pack's chat example is a plan the policy allows.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.adapters.plan_proposals import OfflinePlanProposer
from eija_studio.application.plan import example_passes, propose_plan
from eija_studio.domain.pack import load_pack

ROOT = Path(__file__).resolve().parents[1]
# pack -> (a plain request for the unsafe change, its meaning, a law the policy names when it refuses it)
UNSAFE = {
    "card-payment": ("Let support agents issue refunds themselves", "support_issues_refunds", "law:finance-approves-refunds"),
    "refund-desk": ("Let the support agent approve refunds itself", "agent_auto_approve", "law:only-people-approve"),
    "ai-ops": ("Let the ops agent ship green builds itself", "agent_self_deploy", None),
    "building-permit": ("Put an application on hold", "hold_application", "law:no-application-stuck"),
    "parcel-delivery": ("Let the hub clear customs", "hub_clears_customs", "law:customs-clears"),
    "saas-subscription": ("Let owners lift their own suspension", "owner_unsuspends", "law:success-reactivates"),
    "specialist-referral": ("Let a patient book their own appointment", "patient_self_booking", "law:patient-never-books"),
}


def plan(pack_id: str, request: str):
    pack = load_pack(ROOT / "packs" / pack_id)
    return pack, propose_plan(request, pack.model, pack, OfflinePlanProposer())


@pytest.mark.parametrize("pack_id", UNSAFE)
def test_an_unsafe_request_is_planned_as_asked_and_refused_by_its_law(pack_id):
    request, meaning, law = UNSAFE[pack_id]
    pack, result = plan(pack_id, request)
    assert result["meaning"] == meaning and not pack.meaning(meaning).supported
    assert not result["preview"]["legal"] and result["preview"]["codes"]
    if law is not None:
        assert law in result["preview"]["refs"]


@pytest.mark.parametrize("pack_id", [*UNSAFE, "library-loan", "excursion", "eija-review-slice"])
def test_the_chat_example_is_a_plan_the_policy_allows(pack_id):
    pack = load_pack(ROOT / "packs" / pack_id)
    result = propose_plan(pack.fixtures.demo_request, pack.model, pack, OfflinePlanProposer())
    assert result["meaning"] is not None and pack.meaning(result["meaning"]).supported
    assert example_passes(pack.fixtures.demo_request, pack.model, pack, OfflinePlanProposer())
