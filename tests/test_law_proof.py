"""Laws proved over every run the kernel allows (ADR-0166).

Each negative control breaks the kernel or the model one way and requires the proof to find the law it breaks, with a
shortest counterexample run, so a HOLDS verdict is not vacuous.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.application import law_proof, runtime
from eija_studio.application.law_proof import LAW_HANDLING, actor_classes, prove_laws
from eija_studio.domain.laws import LAW_KINDS
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.domain.policy import demo_candidate
from eija_studio.interfaces.cli import main

ROOT = Path(__file__).resolve().parents[1]
PACKS = ("excursion", "library-loan", "eija-review-slice")
LOAN = load_pack(ROOT / "packs" / "library-loan")
EXCURSION = load_pack(ROOT / "packs" / "excursion")


def verdict(report, law_id):
    return next(v for v in report["laws"] if v["id"] == law_id)


def test_every_law_kind_is_classified():
    assert set(LAW_HANDLING) == set(LAW_KINDS)


@pytest.mark.parametrize("pack", PACKS)
def test_the_shipped_models_keep_their_laws(pack):
    report = prove_laws(load_pack(ROOT / "packs" / pack))
    assert report["status"] == "HOLDS"
    assert report["search"]["status"] == "COMPLETE" and report["search"]["unreached"] == []
    assert report == prove_laws(load_pack(ROOT / "packs" / pack))  # deterministic


def test_actor_classes_cover_every_flag_combination_and_an_outsider():
    classes = actor_classes(LOAN, LOAN.model)
    roles = {r.id for r in LOAN.roles}
    assert len(classes) == 4 * (len(roles) + 1)
    assert {(a["active"], a["assigned"]) for a in classes} == {(True, True), (True, False), (False, True), (False, False)}
    assert any(a["role"] not in roles for a in classes)


def test_candidate_laws_are_inactive_or_vacuous_on_the_baseline_and_hold_on_the_candidate():
    baseline = prove_laws(EXCURSION)
    assert verdict(baseline, "approve-requires-recommended")["status"] == "INACTIVE"
    assert verdict(baseline, "recommend-ends-recommended")["status"] == "VACUOUS"
    candidate = prove_laws(EXCURSION, demo_candidate(EXCURSION))
    assert candidate["status"] == "HOLDS"
    assert verdict(candidate, "approve-requires-recommended")["status"] == "HOLDS"


def test_evidence_and_table_laws_say_how_they_were_judged():
    report = prove_laws(LOAN)
    assert verdict(report, "runtime-evidence")["status"] == "EVIDENCE"
    assert verdict(report, "checkout-needs-assignment")["method"] == "table"


def test_a_refused_model_is_not_run_and_names_the_broken_laws():
    data = LOAN.model.model_dump(mode="json")
    cancel = next(t for t in data["transitions"] if t["action"] == "Cancel")
    cancel["from_state"] = "OnLoan"
    report = prove_laws(LOAN, Workflow.model_validate(data))
    assert report["status"] == "REFUSED" and report["search"]["status"] == "NOT_RUN"
    assert verdict(report, "cancel-from-requested")["status"] == "BROKEN"


def test_refuses_another_packs_model():
    with pytest.raises(DomainError) as refused:
        prove_laws(LOAN, EXCURSION.model)
    assert refused.value.code == "WORKFLOW_PACK_MISMATCH"


# ---- negative controls ------------------------------------------------------------------------------------------

def test_negative_control_a_kernel_that_ignores_roles_breaks_authority_laws(monkeypatch):
    monkeypatch.setattr(runtime, "check_actor", lambda actor, transition, command: None)
    report = prove_laws(LOAN)
    assert report["status"] == "BROKEN"
    broken = verdict(report, "checkout-held-by-librarian")
    assert broken["status"] == "BROKEN"
    assert len(broken["counterexample"]) == 1 and broken["counterexample"][0]["role"] != "Librarian"


def test_negative_control_without_the_policy_a_shortcut_breaks_the_path_law(monkeypatch):
    """The kernel refuses a law-breaking model. Switch that off and the proof must still find the broken run."""
    monkeypatch.setattr(runtime, "ensure_policy", lambda model, pack=None: None)
    monkeypatch.setattr(law_proof, "check_policy", lambda model, pack=None: [])
    data = LOAN.model.model_dump(mode="json")
    returned = next(t for t in data["transitions"] if t["action"] == "Return")
    returned["from_state"] = "Requested"
    report = prove_laws(LOAN, Workflow.model_validate(data))
    path = verdict(report, "returned-requires-loan")
    assert path["status"] == "BROKEN"
    assert [s["action"] for s in path["counterexample"]] == ["Return"]


def test_negative_control_a_final_state_left_is_found_on_a_longer_run(monkeypatch):
    monkeypatch.setattr(runtime, "ensure_policy", lambda model, pack=None: None)
    monkeypatch.setattr(law_proof, "check_policy", lambda model, pack=None: [])
    data = LOAN.model.model_dump(mode="json")
    cancel = next(t for t in data["transitions"] if t["action"] == "Cancel")
    cancel["from_state"] = "Returned"
    report = prove_laws(LOAN, Workflow.model_validate(data))
    final = verdict(report, "returned-final")
    assert final["status"] == "BROKEN"
    assert [s["action"] for s in final["counterexample"]] == ["CheckOut", "Return", "Cancel"]


def test_cli_prints_the_proof(capsys):
    assert main(["laws", "--pack", str(ROOT / "packs" / "library-loan")]) == 0
    assert '"status": "HOLDS"' in capsys.readouterr().out
