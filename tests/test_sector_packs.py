"""The sector packs: realistic systems from five sectors, shipped as templates a new system can start from.

Each pack is a real-world workflow (healthcare referral, card payment, parcel delivery, SaaS subscription, building
permit) with laws, scenarios, a data model and screens. The tests pin what makes each one worth shipping: its
scenarios pass and its laws hold on the kernel, its supported change is allowed and its unsafe change is refused by
the law that forbids it, and it appears as a template. What the model cannot yet say about each sector is recorded
in the pack's `fixtures.proposals.unknowns` and in docs/sector-packs.md.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.application.law_proof import prove_laws
from eija_studio.application.scenario_run import run_scenarios
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.scenarios import scenarios_for
from eija_studio.domain.screens import check_screens, load_screens
from eija_studio.interfaces.play_systems import templates

ROOT = Path(__file__).resolve().parents[1]
# pack id -> (the supported meaning, the unsafe meaning, a law that refuses the unsafe one)
SECTORS = {
    "specialist-referral": ("advice_and_guidance", "patient_self_booking", "law:patient-never-books"),
    "card-payment": ("withdraw_refund_request", "support_issues_refunds", "law:finance-approves-refunds"),
    "parcel-delivery": ("safe_place", "hub_clears_customs", "law:customs-clears"),
    "saas-subscription": ("downgrade_to_free", "owner_unsuspends", "law:success-reactivates"),
    "building-permit": ("permit_lapse", "fast_track_minor_works", "law:approval-after-review"),
}


@pytest.mark.parametrize("pack_id", SECTORS)
def test_scenarios_pass_and_cover_every_kind_of_refusal(pack_id):
    pack = load_pack(ROOT / "packs" / pack_id)
    scenarios = scenarios_for(pack)
    report = run_scenarios(pack, pack.model, scenarios)
    assert report["status"] == "PASS" and report["failed"] == 0 and len(scenarios.scenarios) >= 7
    refusals = {step.then.refused for s in scenarios.scenarios for step in s.steps if step.then.refused}
    assert refusals >= {"ROLE_DENIED", "ASSIGNMENT_DENIED", "ACTOR_REVOKED", "STATE_DENIED"}


@pytest.mark.parametrize("pack_id", SECTORS)
def test_laws_hold_on_every_run_the_kernel_allows(pack_id):
    pack = load_pack(ROOT / "packs" / pack_id)
    assert prove_laws(pack)["status"] == "HOLDS"
    kinds = {law.kind for law in pack.laws}
    assert {"path_requires", "only_role_holds", "action_requires_guard", "state_final", "forbidden_effects"} <= kinds


@pytest.mark.parametrize("pack_id", SECTORS)
def test_the_supported_change_is_allowed_and_the_unsafe_one_is_refused_by_its_law(pack_id):
    supported, unsafe, law = SECTORS[pack_id]
    pack = load_pack(ROOT / "packs" / pack_id)
    assert pack.meaning(supported).supported and not pack.meaning(unsafe).supported
    apply_transactions(pack.model, pack.meaning(supported).transactions, pack)
    with pytest.raises(DomainError) as refused:
        apply_transactions(pack.model, pack.meaning(unsafe).transactions, pack)
    assert refused.value.code == "POLICY_BLOCKED" and law in refused.value.details["refs"]


@pytest.mark.parametrize("pack_id", SECTORS)
def test_every_use_case_has_an_authored_screen_that_passes_the_design_check(pack_id):
    pack = load_pack(ROOT / "packs" / pack_id)
    data, screens = data_for(pack), load_screens(ROOT / "packs" / pack_id, pack_id)
    assert data is not None and screens is not None
    assert {t.action for t in pack.model.transitions} <= {s.use_case for s in screens.screens}
    assert check_screens(screens, pack.model, data) == []


def test_each_sector_is_offered_as_a_template():
    assert set(SECTORS) <= {t["id"] for t in templates()}
