"""Exact plan transfer uses the real interpreter/UOW; approval fixtures are synthetic kernel tests."""
from __future__ import annotations

import copy

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from eija_studio.adapters.sqlite_store import Session
from eija_studio.application.history import replay
from eija_studio.application.plan import preview_plan
from eija_studio.domain.change_case import ChangeCase, OwnerPlanRequest
from eija_studio.domain.models import AGENT, OWNER, DomainError, Workflow
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.transactions import AddState
from eija_studio.interfaces.http import create_app
from kernel_support import approve, reject_from


HEADERS = {"Authorization": "Bearer plan-test", "Origin": "http://127.0.0.1:8765"}


def command(studio, transactions=None):
    transactions = transactions or studio.pack.meaning("recommend_only").transactions
    with studio.store.transaction() as u:
        active = u.active()
    baseline = Workflow.model_validate(active["model"])
    candidate = apply_transactions(baseline, transactions, studio.pack)
    return OwnerPlanRequest.model_validate({
        "request": "Keep precisely the reviewed commands",
        "pack_id": studio.pack.id, "expected_pack_digest": studio.pack.digest,
        "expected_baseline_version": active["version"],
        "expected_baseline_semantic_hash": baseline.semantic_hash,
        "expected_candidate_semantic_hash": candidate.semantic_hash,
        "steps": [{"transaction": tx.model_dump(mode="json"), "author": "you" if i % 2 else "ai",
                   "round": i + 1, "request": f"Round {i + 1}"} for i, tx in enumerate(transactions)],
    })


def snapshot(studio):
    with studio.store.transaction() as u:
        return studio.store.list_cases(), u.active(), u.effect_counts()


def test_exact_atomic_batch_and_reported_provenance_are_retained_without_provider_call(studio, monkeypatch):
    transactions = (*studio.pack.meaning("recommend_only").transactions, reject_from("Submitted"))
    request = command(studio, transactions)
    before = snapshot(studio)
    monkeypatch.setattr(studio.provider, "propose", lambda *_: pytest.fail("No proposal provider call is permitted"))
    case = studio.from_plan(request, OWNER)
    assert case["stage"] == "PREVIEW" and case["version"] == 0
    assert case["selected_by"] == OWNER.id and case["selected_meaning"] is None
    assert case["selection"]["kind"] == "owner_plan"
    assert case["selection"]["steps"] == request.model_dump(mode="json")["steps"]
    assert case["transactions"] == [tx.model_dump(mode="json") for tx in transactions]
    assert Workflow.model_validate(case["candidate"]).semantic_hash == request.expected_candidate_semantic_hash
    assert case["receipts"] == [] and case["decision"] is None
    assert snapshot(studio)[1] == before[1]
    with studio.store.transaction() as u:
        events = u.observations(case["id"])["events"]
    assert [event["kind"] for event in events] == ["CaseCreated", "OwnerPlanSelected"]
    assert events[-1]["body"]["by"] == OWNER.id


def test_agent_cannot_select_owner_plan(studio):
    request, before = command(studio), snapshot(studio)
    with pytest.raises(DomainError) as error:
        studio.from_plan(request, AGENT)
    assert error.value.code == "AUTHORITY_REQUIRED" and snapshot(studio) == before


@pytest.mark.parametrize("field,value,code", [
    ("expected_baseline_version", 9, "STALE_BASELINE"),
    ("expected_baseline_semantic_hash", "0" * 64, "STALE_BASELINE"),
    ("pack_id", "another-pack", "PACK_CHANGED"),
    ("expected_pack_digest", "0" * 64, "PACK_CHANGED"),
    ("expected_candidate_semantic_hash", "0" * 64, "CANDIDATE_CHANGED"),
])
def test_identity_mismatches_leave_no_case_or_audit(studio, field, value, code):
    request = OwnerPlanRequest.model_validate(command(studio).model_dump(mode="json") | {field: value})
    before = snapshot(studio)
    with pytest.raises(DomainError) as error:
        studio.from_plan(request, OWNER)
    assert error.value.code == code and snapshot(studio) == before


@pytest.mark.parametrize("transaction,code", [
    ({"kind": "set_role", "transition": "TR-APPROVE", "role": "Teacher"}, "POLICY_BLOCKED"),
    ({"kind": "add_state", "state": "Draft"}, "EDIT_INVALID"),
    ({"kind": "set_role", "transition": "TR-APPROVE", "role": "Undeclared"}, "POLICY_BLOCKED"),
])
def test_untrusted_commands_are_recomputed_and_refused_without_effects(studio, transaction, code):
    body = command(studio).model_dump(mode="json")
    body["steps"] = [{"transaction": transaction, "author": "ai", "round": 1, "request": "unsafe proposal"}]
    before = snapshot(studio)
    with pytest.raises(DomainError) as error:
        studio.from_plan(OwnerPlanRequest.model_validate(body), OWNER)
    assert error.value.code == code and snapshot(studio) == before


def test_selection_insert_and_audit_share_one_transaction(studio, monkeypatch):
    request, before = command(studio), snapshot(studio)
    original = Session.event

    def fail_selection(session, kind, body):
        if kind == "OwnerPlanSelected":
            raise RuntimeError("Injected audit failure")
        original(session, kind, body)

    monkeypatch.setattr(Session, "event", fail_selection)
    with pytest.raises(RuntimeError, match="Injected audit failure"):
        studio.from_plan(request, OWNER)
    assert snapshot(studio) == before


def test_owner_plan_prefix_is_protected_and_later_edits_use_normal_history(studio, open_studio):
    case = studio.from_plan(command(studio), OWNER)
    initial = studio.history(case["id"])
    assert initial["selection"]["kind"] == "owner_plan" and initial["selection"]["model"] == case["candidate"]
    assert initial["selection"]["provenance"] == case["selection"]
    assert not initial["can_undo"]
    with pytest.raises(DomainError) as error:
        studio.undo(case["id"], case["version"], OWNER)
    assert error.value.code == "NOTHING_TO_UNDO"
    changed = studio.edit(case["id"], case["version"], reject_from("Submitted"), OWNER)
    undone = studio.undo(changed["id"], changed["version"], OWNER)
    assert undone["candidate"] == case["candidate"] and undone["selection"] == case["selection"]
    reopened = open_studio(studio.store.directory)
    assert reopened.history(case["id"])["redo"][0]["model"] == changed["candidate"]
    assert reopened.redo(undone["id"], undone["version"], OWNER)["candidate"] == changed["candidate"]


@pytest.mark.parametrize("mutation", ["prefix", "pack", "baseline", "candidate"])
def test_owner_plan_replay_refuses_corrupted_selection(studio, mutation):
    body = studio.from_plan(command(studio), OWNER)
    if mutation == "prefix":
        body["transactions"][0] = AddState(kind="add_state", state="Tampered").model_dump(mode="json")
    else:
        field = {"pack": "pack_digest", "baseline": "baseline_semantic_hash", "candidate": "candidate_semantic_hash"}[mutation]
        body["selection"][field] = "0" * 64
    with pytest.raises(DomainError) as error:
        replay(ChangeCase.model_validate(body), studio.pack)
    assert error.value.code == "HISTORY_INCONSISTENT"


def test_legacy_pack_meaning_cases_replay_without_rewriting_audit(studio, selected):
    body = copy.deepcopy(selected)
    body.pop("selection")
    with studio.store.transaction() as u:
        u.save_case(body, selected["version"])
    before = snapshot(studio)
    history = studio.history(body["id"])
    assert history["selection"]["kind"] == "pack_meaning"
    assert history["selection"]["meaning"] == selected["selected_meaning"]
    assert history["selection"]["model"] == selected["candidate"]
    assert snapshot(studio) == before


def test_owner_plan_activation_persists_and_old_plan_is_stale(studio, open_studio):
    request = command(studio)
    case = studio.from_plan(request, OWNER)
    case = studio.verify(case["id"], case["version"])
    case = approve(studio, case)
    case = studio.apply(case["id"], case["version"], OWNER)
    reopened = open_studio(studio.store.directory)
    assert reopened.workbench()["model"] == case["candidate"]
    assert reopened.workbench()["baseline_version"] == 1
    assert reopened.view(case["id"])["case"]["stage"] == "APPLIED"
    with pytest.raises(DomainError) as error:
        reopened.from_plan(request, OWNER)
    assert error.value.code == "STALE_BASELINE"
    before = snapshot(reopened)
    with pytest.raises(DomainError) as error:
        reopened.apply(case["id"], case["version"], OWNER)
    assert error.value.code == "CASE_CLOSED" and snapshot(reopened) == before


def test_changed_source_still_blocks_plan_verification_and_approval(studio):
    case = studio.from_plan(command(studio), OWNER)
    identity = studio.identity_provider()
    studio.identity_provider = lambda: identity | {"trusted_fixture": False}
    assert "SOURCE_REVIEW_REQUIRED" in studio.view(case["id"])["packet"]["blockers"]
    before = snapshot(studio)
    with pytest.raises(DomainError) as error:
        studio.verify(case["id"], case["version"])
    assert error.value.code == "SOURCE_REVIEW_REQUIRED" and snapshot(studio) == before


def test_http_exact_transfer_security_boundaries_and_authoritative_identity(studio):
    body = command(studio).model_dump(mode="json")
    with TestClient(create_app(studio, "plan-test"), base_url="http://127.0.0.1:8765") as client:
        status = client.get("/api/status", headers=HEADERS).json()
        assert status["baseline_semantic_hash"] == body["expected_baseline_semantic_hash"]
        assert status["pack"]["digest"] == body["expected_pack_digest"]
        assert client.post("/api/cases/from-plan", json=body).status_code == 401
        assert client.post("/api/cases/from-plan", json=body, headers=HEADERS | {"Origin": "https://evil.invalid"}).status_code == 403
        case = client.post("/api/cases/from-plan", json=body, headers=HEADERS)
        assert case.status_code == 200 and case.json()["selection"]["steps"] == body["steps"]


@pytest.mark.parametrize("mutation", ["candidate", "extra", "data", "vocabulary", "law", "screen", "scenario", "empty", "invalid_round"])
def test_http_rejects_nonworkflow_and_malformed_plan_fields(studio, mutation):
    body = command(studio).model_dump(mode="json")
    if mutation in {"candidate", "extra"}:
        body[mutation] = True
    elif mutation == "empty":
        body["steps"] = []
    elif mutation == "invalid_round":
        body["steps"][0]["round"] = True
    else:
        body["steps"][0]["transaction"] = {"kind": {"data": "set_required", "vocabulary": "rename_term",
            "law": "change_law", "screen": "screen", "scenario": "scenario"}[mutation]}
    before = snapshot(studio)
    with TestClient(create_app(studio, "plan-test"), base_url="http://127.0.0.1:8765") as client:
        response = client.post("/api/cases/from-plan", json=body, headers=HEADERS)
    assert response.status_code == 422 and response.json()["code"] == "CONTRACT_REJECTED"
    assert snapshot(studio) == before


def test_preview_candidate_identity_is_the_one_promoted(studio):
    request = command(studio)
    model = Workflow.model_validate(studio.workbench()["model"])
    transactions = [step.transaction for step in request.steps]
    preview = preview_plan(model, studio.pack, transactions, [True] * len(transactions))
    assert preview["before_semantic_hash"] == request.expected_baseline_semantic_hash
    assert preview["candidate_semantic_hash"] == request.expected_candidate_semantic_hash
    assert studio.from_plan(request, OWNER)["candidate"] == preview["candidate"]


def test_selection_contract_rejects_client_authority(studio):
    body = command(studio).model_dump(mode="json")
    body["steps"][0]["approved"] = True
    with pytest.raises(ValidationError):
        OwnerPlanRequest.model_validate(body)


def review_case(studio, operation, origin="owner_plan"):
    # This persistence probe holds one explicitly synthetic kernel-test identity;
    # source freshness is covered separately and is not the fault under test here.
    measured = studio.identity_provider()
    studio.identity_provider = lambda: measured
    if origin == "owner_plan":
        case = studio.from_plan(command(studio), OWNER)
    else:
        case = studio.create("Let teachers sign off excursions.")
        case = studio.propose(case["id"], case["version"])
        case = studio.select(case["id"], case["version"], "recommend_only", OWNER)
        case.pop("selection")
        with studio.store.transaction() as u:
            u.save_case(case, case["version"])
    if operation != "verify":
        case = studio.verify(case["id"], case["version"])
    if operation == "apply":
        case = approve(studio, case)
    return case


def refuse_corrupt_review(studio, case, operation):
    # Direct adapter persistence represents corrupt retained metadata. It bypasses
    # authoring on purpose so the review boundaries must independently refuse it.
    with studio.store.transaction() as u:
        u.save_case(case, case["version"])
    before = snapshot(studio)
    with pytest.raises(DomainError) as error:
        if operation == "approve":
            packet = studio.view(case["id"])["packet"]
            studio.approve(case["id"], case["version"], packet["subject_hash"],
                {q["id"]: q["expected"] for q in packet["questions"]}, True, OWNER)
        elif operation == "apply":
            studio.apply(case["id"], case["version"], OWNER)
        else:
            studio.verify(case["id"], case["version"])
    assert error.value.code == "HISTORY_INCONSISTENT"
    assert snapshot(studio) == before


@pytest.mark.parametrize("operation", ["verify", "approve", "apply"])
def test_review_boundaries_refuse_corrupt_plan_identity_without_writes(studio, operation):
    case = review_case(studio, operation)
    case["selection"]["pack_digest"] = "0" * 64
    refuse_corrupt_review(studio, case, operation)


@pytest.mark.parametrize("operation", ["verify", "approve", "apply"])
@pytest.mark.parametrize("origin", ["owner_plan", "legacy_pack_meaning"])
def test_review_boundaries_protect_initial_prefix_for_new_and_legacy_cases(studio, operation, origin):
    case = review_case(studio, operation, origin)
    case["transactions"][0] = AddState(kind="add_state", state="CorruptPrefix").model_dump(mode="json")
    refuse_corrupt_review(studio, case, operation)
