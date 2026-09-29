"""Exact-oracle tests of the runtime verifier (`application/verifier.py`), added by the mutation lane (ADR-0033).

The verifier turns the runtime into a 5 actors x states x 5 actions matrix and compares each observation
with a hand-authored oracle. The accepted cells below are derived from the policy in
docs/SECURITY_AND_TRUST.md (who may do what, from which state), *not* from the verifier's own tables, so a
wrong actor flag, a wrong role or a wrong rejection source cannot hide inside a self-consistent matrix.
A negative control shows the matrix really does detect a runtime that stops enforcing authority.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

import pytest

from eija_studio.adapters.sqlite_store import SQLiteStore
from eija_studio.application import runtime, verifier
from eija_studio.domain.evidence import assess_receipt
from eija_studio.domain.models import SemanticTransaction, Workflow, fingerprint
from eija_studio.domain.policy import apply_transaction, baseline

SUBJECT = {"semantic": "s", "implementation": "i", "policy": "p", "environment": "e", "harness": "h"}


def make_sandbox(root):
    opened = []

    @contextmanager
    def factory():
        store = SQLiteStore(root / f"sb{len(opened)}", durability="ephemeral")
        opened.append("open")
        try:
            yield store
        finally:
            opened.append("closed")

    factory.log = opened
    return factory


@pytest.fixture
def sandbox(tmp_path):
    return make_sandbox(tmp_path)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One verification per model, shared by the read-only shape tests (a verification is ~1 s)."""
    root = tmp_path_factory.mktemp("verifier")
    factory = make_sandbox(root)
    return {name: verifier.verify_runtime(model, SUBJECT, factory)
            for name, model in (("candidate", candidate()), ("widened", candidate("Submitted")), ("baseline", baseline()))}


def candidate(rejection_source: str = "Recommended") -> Workflow:
    model = apply_transaction(baseline(), SemanticTransaction(kind="enable_recommendation"))
    if rejection_source != "Recommended":
        model = apply_transaction(model, SemanticTransaction(kind="set_rejection_source", rejection_source=rejection_source))
    return model


def accepted(receipt: dict) -> set[tuple[str, str, str]]:
    return {(c["actor"], c["state"], c["action"]) for c in receipt["artifact"]["cells"] if c["actual"]["accepted"]}


# Independent oracle: (actor, state, action) cells that must be accepted, per policy.
COMMON = {("teacher-assigned", "Draft", "Submit"), ("teacher-unassigned", "Draft", "Submit"),
          ("teacher-assigned", "Rejected", "Revise"), ("teacher-unassigned", "Rejected", "Revise")}
CANDIDATE_ONLY = {("teacher-assigned", "Submitted", "Recommend"),
                  ("registrar", "Recommended", "Approve"), ("registrar", "Recommended", "Reject")}


def test_candidate_matrix_accepts_exactly_the_policy_cells(built):
    receipt = built["candidate"]
    assert accepted(receipt) == COMMON | CANDIDATE_ONLY
    assert all(c["expected"] == c["actual"] for c in receipt["artifact"]["cells"])


def test_candidate_with_widened_rejection_source_accepts_rejection_from_submitted(built):
    receipt = built["widened"]
    assert accepted(receipt) == COMMON | {("teacher-assigned", "Submitted", "Recommend"), ("registrar", "Recommended", "Approve"),
                                          ("registrar", "Submitted", "Reject")}
    assert all(c["expected"] == c["actual"] for c in receipt["artifact"]["cells"])


def test_baseline_matrix_has_no_recommendation_and_registrar_decides_from_submitted(built):
    receipt = built["baseline"]
    assert accepted(receipt) == COMMON | {("registrar", "Submitted", "Approve"), ("registrar", "Submitted", "Reject")}
    assert receipt["artifact"]["matrix"]["states"] == ["Draft", "Submitted", "Approved", "Rejected"]
    assert receipt["artifact"]["expected_cells"] == 100 == len(receipt["artifact"]["cells"])
    assert all(c["expected"] == c["actual"] for c in receipt["artifact"]["cells"])
    assert not any(c["actual"]["accepted"] for c in receipt["artifact"]["cells"] if c["action"] == "Recommend")


def test_expected_observations_are_derived_from_the_rule_not_copied_from_actual(built):
    receipt = built["candidate"]
    by_key = {(c["actor"], c["state"], c["action"]): c for c in receipt["artifact"]["cells"]}
    ok = by_key[("teacher-assigned", "Submitted", "Recommend")]["expected"]
    assert ok == {"accepted": True, "state": "Recommended", "version": 1, "audit": 1, "outbox": 1, "operations": 1}
    approve = by_key[("registrar", "Recommended", "Approve")]["expected"]
    assert approve == {"accepted": True, "state": "Approved", "version": 1, "audit": 1, "outbox": 0, "operations": 1}
    denied = by_key[("viewer", "Draft", "Submit")]["expected"]
    assert denied == {"accepted": False, "state": "Draft", "version": 0, "audit": 0, "outbox": 0, "operations": 0}
    assert by_key[("teacher-revoked", "Submitted", "Recommend")]["actual"]["accepted"] is False  # revoked beats assigned
    assert by_key[("teacher-unassigned", "Submitted", "Recommend")]["actual"]["accepted"] is False  # assignment is required


def test_receipt_envelope_and_artifact_are_exactly_as_documented(built):
    receipt = built["candidate"]
    assert set(receipt) == {"id", "claim", "kind", "subject", "producer", "method", "created_at", "artifact_hash", "artifact"}
    assert UUID(receipt["id"]).hex == receipt["id"]
    assert (receipt["claim"], receipt["kind"], receipt["subject"]) == ("runtime_matrix", "integration_test", SUBJECT)
    assert (receipt["producer"], receipt["method"]) == ("eija-local-verifier", "bounded-runtime-matrix-v1")
    assert datetime.fromisoformat(receipt["created_at"]).utcoffset().total_seconds() == 0
    artifact = receipt["artifact"]
    assert receipt["artifact_hash"] == fingerprint(artifact)
    assert set(artifact) == {"protocol", "expected_cells", "matrix", "cells", "limitations"}
    assert artifact["protocol"] == "bounded-runtime-matrix-v1"
    assert artifact["expected_cells"] == 125 == len(artifact["cells"])
    assert artifact["matrix"] == {
        "actors": ["teacher-assigned", "teacher-unassigned", "teacher-revoked", "registrar", "viewer"],
        "states": ["Draft", "Submitted", "Recommended", "Approved", "Rejected"],
        "actions": ["Submit", "Recommend", "Approve", "Reject", "Revise"]}
    assert artifact["limitations"] == [
        "Synthetic fixture directory; no real SSO", "No human-outcome measurement",
        "One-step state/action matrix, not exhaustive arbitrary sequences", "Same-author oracle, not an independent holdout",
        "Disposable non-durable sandbox: observes transaction semantics, not crash durability"]
    assert all(set(c) == {"actor", "state", "action", "expected", "actual"} for c in artifact["cells"])
    assert assess_receipt(receipt, SUBJECT, "runtime_matrix", "integration_test") == "PASS"


def test_ids_are_fresh_per_verification_and_the_artifact_is_reproducible(built, sandbox):
    again = verifier.verify_runtime(baseline(), SUBJECT, sandbox)
    assert again["id"] != built["baseline"]["id"] and again["artifact_hash"] == built["baseline"]["artifact_hash"]


def test_the_sandbox_is_opened_once_and_always_closed(sandbox):
    verifier.verify_runtime(baseline(), SUBJECT, sandbox)
    assert sandbox.log == ["open", "closed"]


def test_a_runtime_that_stops_enforcing_authority_is_detected(sandbox, monkeypatch):
    """Negative control: with the actor check removed the matrix must disagree with the oracle and the receipt must FAIL."""
    monkeypatch.setattr(runtime, "check_actor", lambda actor, transition, command: None)
    receipt = verifier.verify_runtime(candidate(), SUBJECT, sandbox)
    mismatched = [c for c in receipt["artifact"]["cells"] if c["expected"] != c["actual"]]
    assert {c["actor"] for c in mismatched} >= {"viewer", "teacher-revoked", "teacher-unassigned"}
    assert assess_receipt(receipt, SUBJECT, "runtime_matrix", "integration_test") == "FAIL"
