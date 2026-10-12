"""Synthetic owner/unit fixtures for exact app authority. Process execution has a separate integration check."""
from __future__ import annotations

import copy
import os
import py_compile
import pytest

from eija_studio.adapters.sqlite_store import Session
from eija_studio.domain.change_case import ChangeCase, OwnerPlanRequest
from eija_studio.domain.generated_app import GeneratedAppBinding, generated_receipt_status
from eija_studio.domain.models import AGENT, OWNER, DomainError, Workflow, canonical, fingerprint
from eija_studio.domain.policy import apply_transactions
from eija_studio.interfaces.app_build import app_files, conformance
from kernel_support import approve


def command(studio):
    active = studio.workbench()
    model = Workflow.model_validate(active["model"])
    steps = studio.pack.meaning("recommend_only").transactions
    candidate = apply_transactions(model, steps, studio.pack)
    _, manifest = app_files(studio.pack, candidate, identity_provider=studio.identity_provider)
    return OwnerPlanRequest.model_validate({"request": "Check this exact generated app", "pack_id": studio.pack.id,
        "expected_pack_digest": studio.pack.digest, "expected_baseline_version": active["baseline_version"],
        "expected_baseline_semantic_hash": model.semantic_hash, "expected_candidate_semantic_hash": candidate.semantic_hash,
        "expected_build_digest": manifest["subject"]["digest"],
        "steps": [{"transaction": step.model_dump(mode="json"), "author": "you", "round": 1, "request": "Exact edit"}
                  for step in steps]})


def observation(binding):
    """Explicit fake process observation: these unit tests do not assert an actual subprocess ran."""
    return {"binding_digest": binding.digest, "subject_digest": binding.subject.digest,
            "checker": binding.checker.model_dump(mode="json"), "configuration": binding.configuration.model_dump(mode="json"),
            "before": binding.subject.digest, "after": binding.subject.digest,
            "returncode": 0, "timed_out": False, "tests_run": 6, "stdout": "", "stderr": "Synthetic checker fixture"}


@pytest.fixture
def bound(studio, monkeypatch):
    monkeypatch.setattr(studio.generated_apps, "verify", lambda binding, provider: observation(binding))
    return studio.from_plan(command(studio), OWNER)


def payload(studio, case):
    return studio.store.directory / "generated-reviews" / case["app_build"]["digest"] / "app/web/index.html"


def snapshot(studio):
    with studio.store.transaction() as u:
        return u.active(), studio.store.list_cases(), u.effect_counts()


def test_exact_capture_refuses_unknown_build_without_case_or_audit(studio):
    request = command(studio).model_copy(update={"expected_build_digest": "0" * 64})
    before = snapshot(studio)
    with pytest.raises(DomainError, match="differs from the inspected build"):
        studio.from_plan(request, OWNER)
    assert snapshot(studio) == before


def test_bound_packet_starts_without_generated_evidence_and_preserves_source_gate(studio, bound):
    packet = studio.view(bound["id"])["packet"]
    assert packet["app_build"]["freshness"] == "CURRENT"
    assert packet["app_build"]["conformance"]["status"] == "NOT_RUN"
    assert packet["subject"]["generated_app"] == bound["app_build"]["digest"]
    assert packet["identity_source"] == "pytest-harness"
    original = studio.identity_provider
    studio.identity_provider = lambda: original() | {"trusted_fixture": False}
    assert "SOURCE_REVIEW_REQUIRED" in studio.view(bound["id"])["packet"]["blockers"]
    with pytest.raises(DomainError) as error:
        studio.verify(bound["id"], bound["version"])
    assert error.value.code == "SOURCE_REVIEW_REQUIRED"


@pytest.mark.parametrize("operation", ["select", "approve", "apply"])
def test_exact_app_owner_authority_cannot_be_borrowed(studio, bound, operation):
    with pytest.raises(DomainError) as error:
        if operation == "select":
            studio.from_plan(command(studio), AGENT)
        elif operation == "approve":
            studio.approve(bound["id"], bound["version"], "0" * 64, {}, True, AGENT)
        else:
            studio.apply(bound["id"], bound["version"], AGENT)
    assert error.value.code == "AUTHORITY_REQUIRED"


def test_exact_activation_and_reopen_keep_bundle_and_separate_workflow_claim(studio, bound, open_studio):
    checked = studio.verify(bound["id"], bound["version"])
    packet = studio.view(bound["id"])["packet"]
    assert packet["technical_claims"]["runtime_matrix"] == "PASS"
    assert packet["app_build"]["conformance"]["status"] == "PASS"
    approved = approve(studio, checked)
    applied = studio.apply(approved["id"], approved["version"], OWNER)
    reopened = open_studio(studio.store.directory)
    active = reopened.active_app_build()
    assert active["freshness"] == "CURRENT" and active["case_id"] == applied["id"]
    assert active["binding"] == bound["app_build"]
    assert reopened.build_approval(active["subject"])["status"] == "ACTIVE_APPROVED"
    other = active["subject"] | {"digest": "0" * 64}
    assert reopened.build_approval(other)["status"] == "UNREVIEWED"
    before = snapshot(reopened)
    with pytest.raises(DomainError):
        reopened.apply(applied["id"], applied["version"], OWNER)
    assert snapshot(reopened) == before


@pytest.mark.parametrize("moment", ["before_verify", "before_approve", "before_apply", "after_apply"])
def test_retained_payload_tampering_never_inherits_approval(studio, bound, moment):
    case = bound
    if moment != "before_verify":
        case = studio.verify(case["id"], case["version"])
    if moment in {"before_apply", "after_apply"}:
        case = approve(studio, case)
    if moment == "after_apply":
        case = studio.apply(case["id"], case["version"], OWNER)
    target = payload(studio, case)
    target.write_bytes(target.read_bytes() + b"\n<!-- replaced payload -->")
    before = snapshot(studio)
    assert studio.view(case["id"])["packet"]["app_build"]["freshness"] == "STALE"
    if moment == "after_apply":
        assert studio.active_app_build()["freshness"] == "STALE"
        assert studio.build_approval(case["app_build"]["subject"])["status"] == "STALE"
    else:
        with pytest.raises(DomainError):
            if moment == "before_verify":
                studio.verify(case["id"], case["version"])
            elif moment == "before_approve":
                approve(studio, case)
            else:
                studio.apply(case["id"], case["version"], OWNER)
    assert snapshot(studio) == before


def test_checker_failure_cannot_borrow_kernel_pass(studio, bound, monkeypatch):
    monkeypatch.setattr(studio.generated_apps, "verify", lambda binding, provider: observation(binding) | {"returncode": 1})
    checked = studio.verify(bound["id"], bound["version"])
    packet = studio.view(checked["id"])["packet"]
    assert packet["technical_claims"]["runtime_matrix"] == "PASS"
    assert packet["app_build"]["conformance"]["status"] == "FAIL"
    assert "APP_CONFORMANCE_FAIL" in packet["blockers"]


def test_rerun_preserves_failure_conflict_and_new_review_can_recover(studio, bound, monkeypatch):
    monkeypatch.setattr(studio.generated_apps, "verify", lambda binding, provider: observation(binding) | {"returncode": 1})
    failed = studio.verify(bound["id"], bound["version"])
    monkeypatch.setattr(studio.generated_apps, "verify", lambda binding, provider: observation(binding))
    retried = studio.verify(failed["id"], failed["version"])
    packet = studio.view(retried["id"])["packet"]
    assert packet["app_build"]["conformance"]["status"] == "CONFLICT"
    assert "APP_CONFORMANCE_CONFLICT" in packet["blockers"]
    with pytest.raises(DomainError):
        approve(studio, retried)
    fresh = studio.from_plan(command(studio), OWNER)
    checked = studio.verify(fresh["id"], fresh["version"])
    assert studio.view(checked["id"])["packet"]["app_build"]["conformance"]["status"] == "PASS"
    assert studio.view(retried["id"])["packet"]["app_build"]["conformance"]["status"] == "CONFLICT"


def test_verification_race_discards_unpublished_receipts(studio, bound, monkeypatch):
    def check_then_change(binding, provider):
        target = payload(studio, bound)
        target.write_bytes(target.read_bytes() + b"changed after checker")
        return observation(binding)
    monkeypatch.setattr(studio.generated_apps, "verify", check_then_change)
    before = snapshot(studio)
    with pytest.raises(DomainError):
        studio.verify(bound["id"], bound["version"])
    assert snapshot(studio) == before


def test_atomic_application_rolls_back_bundle_with_model_and_case(studio, bound, monkeypatch):
    checked = studio.verify(bound["id"], bound["version"])
    approved = approve(studio, checked)
    before = snapshot(studio)
    original = Session.save_case
    def fail_applied(self, body, expected):
        if body["stage"] == "APPLIED":
            raise RuntimeError("Synthetic storage failure")
        return original(self, body, expected)
    monkeypatch.setattr(Session, "save_case", fail_applied)
    with pytest.raises(RuntimeError):
        studio.apply(approved["id"], approved["version"], OWNER)
    assert snapshot(studio) == before and studio.active_app_build() is None


def test_foreign_case_decision_cannot_authorize_identical_app(studio, bound):
    other = studio.from_plan(command(studio), OWNER)
    approved = approve(studio, studio.verify(bound["id"], bound["version"]))
    checked = studio.verify(other["id"], other["version"])
    with studio.store.transaction() as u:
        forged = dict(checked) | {"stage": "APPROVED", "decision": approved["decision"]}
        u.save_case(forged, checked["version"])
    before = snapshot(studio)
    with pytest.raises(DomainError) as error:
        studio.apply(forged["id"], forged["version"], OWNER)
    assert error.value.code == "STALE_DECISION" and snapshot(studio) == before


def test_competing_valid_case_cannot_replace_the_new_active_bundle(studio, bound):
    other = studio.from_plan(command(studio), OWNER)
    first = approve(studio, studio.verify(bound["id"], bound["version"]))
    second = approve(studio, studio.verify(other["id"], other["version"]))
    studio.apply(first["id"], first["version"], OWNER)
    before = snapshot(studio)
    with pytest.raises(DomainError) as error:
        studio.apply(second["id"], second["version"], OWNER)
    assert error.value.code == "GATE_BLOCKED" and snapshot(studio) == before
    assert studio.active_app_build()["case_id"] == first["id"]


def test_payload_changed_while_decision_was_sealed_cannot_commit(studio, bound, monkeypatch):
    checked = studio.verify(bound["id"], bound["version"])
    seal = studio.signer.seal
    def changed_after_seal(value):
        result = seal(value)
        if value.get("kind") == "local-owner-acknowledgement":
            target = payload(studio, bound)
            target.write_bytes(target.read_bytes() + b"changed while approving")
        return result
    monkeypatch.setattr(studio.signer, "seal", changed_after_seal)
    before = snapshot(studio)
    with pytest.raises(DomainError):
        approve(studio, checked)
    assert snapshot(studio) == before


def test_source_trust_removed_while_sealing_cannot_commit(studio, bound, monkeypatch):
    checked = studio.verify(bound["id"], bound["version"])
    seal, identity = studio.signer.seal, studio.identity_provider
    def source_review_removed(value):
        result = seal(value)
        if value.get("kind") == "local-owner-acknowledgement":
            monkeypatch.setattr(studio, "identity_provider", lambda: identity() | {"trusted_fixture": False})
        return result
    monkeypatch.setattr(studio.signer, "seal", source_review_removed)
    before = snapshot(studio)
    with pytest.raises(DomainError) as error:
        approve(studio, checked)
    assert error.value.code == "SOURCE_REVIEW_REQUIRED" and snapshot(studio) == before


@pytest.mark.parametrize("corruption", ["missing", "unselected", "wrong-id"])
def test_unavailable_active_case_does_not_crash_workbench_or_borrow_approval(studio, bound, corruption):
    approved = approve(studio, studio.verify(bound["id"], bound["version"]))
    applied = studio.apply(approved["id"], approved["version"], OWNER)
    with studio.store.transaction() as u:
        if corruption == "missing":
            u.db.execute("DELETE FROM cases WHERE id=?", (applied["id"],))
        else:
            changes = {"candidate": None} if corruption == "unselected" else {"id": "wrong-row-id"}
            body = dict(applied) | changes
            u.db.execute("UPDATE cases SET body=? WHERE id=?", (canonical(body), applied["id"]))
    assert studio.workbench()["active_app_build"]["freshness"] == "UNAVAILABLE"
    assert studio.build_approval(bound["app_build"]["subject"])["status"] == "UNREVIEWED"


def test_workflow_only_signed_decision_cannot_borrow_generated_app_review(studio, bound, selected):
    approved = approve(studio, studio.verify(selected["id"], selected["version"]))
    checked = studio.verify(bound["id"], bound["version"])
    with studio.store.transaction() as u:
        substituted = dict(checked) | {"stage": "APPROVED", "decision": approved["decision"]}
        u.save_case(substituted, checked["version"])
    with pytest.raises(DomainError) as error:
        studio.apply(substituted["id"], substituted["version"], OWNER)
    assert error.value.code == "STALE_DECISION" and studio.active_app_build() is None


def test_real_generated_checker_runs_the_retained_selected_artifact(studio):
    """Actual subprocess, scoped to the generated tests; owner capability remains synthetic."""
    case = studio.from_plan(command(studio), OWNER)
    retained = payload(studio, case).parents[1] / "service.py"
    original, stamp = retained.read_bytes(), retained.stat()
    # A real timestamp/size-valid bytecode cache containing different code must not be imported as the selected source.
    retained.write_bytes(b"raise RuntimeError('stale cache executed')\n".ljust(len(original), b" "))
    os.utime(retained, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    py_compile.compile(str(retained), doraise=True, invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    retained.write_bytes(original)
    os.utime(retained, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    assert conformance(retained.parents[1])["status"] == "PASS"
    checked = studio.verify(case["id"], case["version"])
    generated = next(r for r in checked["receipts"] if r["claim"] == "generated_app_conformance")
    assert generated["artifact"]["returncode"] == 0
    assert generated["artifact"]["tests_run"] == 6
    assert "Ran 6 tests" in generated["artifact"]["stderr"]
    assert studio.view(case["id"])["packet"]["app_build"]["conformance"]["status"] == "PASS"


def test_legacy_case_keeps_workflow_only_review(studio, selected):
    assert selected["app_build"] is None
    packet = studio.view(selected["id"])["packet"]
    assert "generated_app" not in packet["subject"]
    assert packet["app_build"]["freshness"] == "UNBOUND"


def test_historical_case_without_app_binding_preserves_receipts_and_subject(studio, selected):
    checked = studio.verify(selected["id"], selected["version"])
    before = studio.view(checked["id"])["packet"]
    historical = {key: value for key, value in checked.items() if key != "app_build"}
    assert ChangeCase.model_validate(historical).app_build is None
    with studio.store.transaction() as u:
        u.db.execute("UPDATE cases SET body=? WHERE id=?", (canonical(historical), checked["id"]))
    reopened = studio.view(checked["id"])
    assert reopened["case"]["receipts"] == checked["receipts"]
    assert reopened["packet"]["subject_hash"] == before["subject_hash"]
    assert reopened["packet"]["app_build"]["freshness"] == "UNBOUND"


@pytest.mark.parametrize("mutation", ["claimed_status", "checker", "configuration", "zero_tests", "wrong_payload"])
def test_generated_receipt_policy_uses_actual_scoped_observation(studio, bound, mutation):
    binding = GeneratedAppBinding.model_validate(bound["app_build"])
    artifact = observation(binding)
    if mutation == "checker":
        artifact["checker"] = artifact["checker"] | {"digest": "0" * 64}
    elif mutation == "configuration":
        artifact["configuration"] = artifact["configuration"] | {"timeout_seconds": 1}
    elif mutation == "zero_tests":
        artifact["tests_run"] = 0
    elif mutation == "wrong_payload":
        artifact["after"] = "0" * 64
    else:
        artifact["returncode"] = 1
    receipt = {"claim": "generated_app_conformance", "kind": "generated_app_execution", "producer": "eija-generated-app-verifier",
        "method": binding.checker.id, "subject": {"generated_app": binding.digest}, "status": "PASS",
        "artifact": artifact, "artifact_hash": fingerprint(artifact)}
    assert generated_receipt_status(copy.deepcopy(receipt), binding, True) != "PASS"
