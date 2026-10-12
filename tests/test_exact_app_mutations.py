"""Behavioral controls for deliberately broken exact-app approval implementations.

Every oracle runs against both the real implementation and a private callable mutant.
A mutant counts as detected only after a specific unsafe acceptance or persisted state,
never because of an import error, source mismatch, unexpected exception or missing tool.
Owner authority and checker observations are explicit disposable test fixtures. These
tests run actual Studio/SQLite behavior, not an actual generated checker subprocess.
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
from types import MethodType

import pytest

from eija_studio.adapters.sqlite_store import Session
from eija_studio.application.compiler import compile_case
from eija_studio.application.generated_app import app_build_view
from eija_studio.application.service import Studio
from eija_studio.domain.generated_app import _execution_status, generated_receipt_status
from eija_studio.domain.models import OWNER, DomainError
from kernel_support import HARNESS_MARK, approve
from test_generated_app_approval import command, observation, payload, snapshot
from verification.selfdogfood.mutants import _clone, _RemoveGuard


class _RemoveCall(ast.NodeTransformer):
    def __init__(self, expression):
        self.expression, self.removed = expression, 0

    def visit_Expr(self, node):
        if ast.unparse(node.value) == self.expression:
            self.removed += 1
            return None
        return self.generic_visit(node)


class _RemoveDecisionCaseID(ast.NodeTransformer):
    def __init__(self):
        self.removed = 0

    def visit_Dict(self, node):
        for index, key in enumerate(node.keys):
            if isinstance(key, ast.Constant) and key.value == "case_id":
                del node.keys[index]
                del node.values[index]
                self.removed += 1
                break
        return self.generic_visit(node)


def _method_mutant(monkeypatch, instance, method, transform):
    variant, _ = _clone(getattr(type(instance), method), transform)
    monkeypatch.setattr(instance, method, MethodType(variant, instance))


def _detect(broken, oracle):
    if broken:
        with pytest.raises(AssertionError, match="UNSAFE EXACT APP:"):
            oracle()
    else:
        oracle()


@pytest.fixture
def exact_case(studio, monkeypatch):
    assert studio.identity_provider()["identity_source"] == HARNESS_MARK
    monkeypatch.setattr(studio.generated_apps, "verify", lambda binding, provider: observation(binding))
    return studio.from_plan(command(studio), OWNER)


def _wrong_subject_oracle(studio, request):
    before = snapshot(studio)
    try:
        case = studio.from_plan(request, OWNER)
    except DomainError as error:
        assert error.code == "APP_BUILD_CHANGED"
        assert snapshot(studio) == before
        return
    with studio.store.transaction() as session:
        persisted = session.load_case(case["id"])
    assert persisted["app_build"] == case["app_build"]
    assert persisted["app_build"]["subject"]["digest"] == request.expected_build_digest, (
        "UNSAFE EXACT APP: persisted a generated app different from the inspected subject"
    )


@pytest.mark.parametrize("broken", [False, True], ids=["real-refuses", "missing-subject-check-detected"])
def test_wrong_inspected_app_is_not_selected(studio, monkeypatch, broken):
    request = command(studio).model_copy(update={"expected_build_digest": "0" * 64})
    if broken:
        _method_mutant(monkeypatch, studio.generated_apps, "capture",
                       _RemoveGuard("binding.subject.digest != expected_digest"))
    _detect(broken, lambda: _wrong_subject_oracle(studio, request))


def _runner_failure_mutant(studio, monkeypatch):
    execution, _ = _clone(_execution_status, _RemoveGuard("observations != (0, False, 6)"))
    status, _ = _clone(generated_receipt_status, globals_override={"_execution_status": execution})
    view, _ = _clone(app_build_view, globals_override={"generated_receipt_status": status})
    compiler, _ = _clone(compile_case, globals_override={"app_build_view": view})
    compile_method, _ = _clone(Studio._compile, globals_override={"compile_case": compiler})
    monkeypatch.setattr(studio, "_compile", MethodType(compile_method, studio))


def _failed_checker_oracle(studio, case):
    checked = studio.verify(case["id"], case["version"])
    receipt = next(r for r in checked["receipts"] if r["claim"] == "generated_app_conformance")
    assert studio.signer.authentic(receipt)
    assert receipt["artifact"]["returncode"] == 1
    assert studio.view(case["id"])["packet"]["technical_claims"]["runtime_matrix"] == "PASS"
    before = snapshot(studio)
    try:
        approved = approve(studio, checked)
    except DomainError as error:
        assert error.code == "GATE_BLOCKED"
        assert snapshot(studio) == before
        return
    applied = studio.apply(approved["id"], approved["version"], OWNER)
    with studio.store.transaction() as session:
        assert session.active()["version"] == case["baseline_version"] + 1
    assert applied["stage"] == "APPLIED"
    assert receipt["artifact"]["returncode"] == 0, (
        "UNSAFE EXACT APP: activated a generated app whose authentic checker observation failed"
    )


@pytest.mark.parametrize("broken", [False, True], ids=["real-refuses", "missing-runner-check-detected"])
def test_failed_generated_checker_cannot_authorize_activation(studio, exact_case, monkeypatch, broken):
    monkeypatch.setattr(studio.generated_apps, "verify",
                        lambda binding, provider: observation(binding) | {"returncode": 1})
    if broken:
        _runner_failure_mutant(studio, monkeypatch)
    _detect(broken, lambda: _failed_checker_oracle(studio, exact_case))


def _foreign_decision_oracle(studio, first):
    other = studio.from_plan(command(studio), OWNER)
    approved = approve(studio, studio.verify(first["id"], first["version"]))
    checked = studio.verify(other["id"], other["version"])
    assert studio.view(first["id"])["packet"]["subject_hash"] == studio.view(other["id"])["packet"]["subject_hash"]
    with studio.store.transaction() as session:
        substituted = checked | {"stage": "APPROVED", "decision": approved["decision"]}
        session.save_case(substituted, checked["version"])
    before = snapshot(studio)
    try:
        applied = studio.apply(substituted["id"], substituted["version"], OWNER)
    except DomainError as error:
        assert error.code == "STALE_DECISION"
        assert snapshot(studio) == before
        return
    with studio.store.transaction() as session:
        persisted = session.load_case(applied["id"])
        assert session.active()["app_build"]["case_id"] == other["id"]
    assert persisted["stage"] == "APPLIED" and studio.signer.authentic(persisted["decision"])
    assert persisted["decision"]["case_id"] == persisted["id"], (
        "UNSAFE EXACT APP: activated one case using another case's authentic owner decision"
    )


@pytest.mark.parametrize("broken", [False, True], ids=["real-refuses", "missing-case-binding-detected"])
def test_foreign_signed_decision_cannot_be_replayed(studio, exact_case, monkeypatch, broken):
    if broken:
        _method_mutant(monkeypatch, studio, "_decision_matches", _RemoveDecisionCaseID())
    _detect(broken, lambda: _foreign_decision_oracle(studio, exact_case))


def _change_during_seal(studio, case, monkeypatch, change):
    target, identity = payload(studio, case), studio.identity_provider
    original_bytes, original_identity = target.read_bytes(), identity()
    seal = studio.signer.seal

    def seal_then_change(value):
        result = seal(value)
        if value.get("kind") == "local-owner-acknowledgement":
            if change == "payload":
                target.write_bytes(original_bytes + b"\n<!-- changed after decision sealing -->")
            else:
                monkeypatch.setattr(studio, "identity_provider", lambda: identity() | {"implementation": "0" * 64})
        return result

    monkeypatch.setattr(studio.signer, "seal", seal_then_change)
    return lambda: target.read_bytes() == original_bytes and studio.identity_provider() == original_identity


def _post_seal_oracle(studio, checked, unchanged):
    before = snapshot(studio)
    try:
        approved = approve(studio, checked)
    except DomainError as error:
        assert error.code in {"APP_BUILD_CHANGED", "SUBJECT_CHANGED"}
        assert snapshot(studio) == before
        assert not unchanged()
        return
    with studio.store.transaction() as session:
        persisted = session.load_case(approved["id"])
    assert persisted["stage"] == "APPROVED" and studio.signer.authentic(persisted["decision"])
    assert unchanged(), "UNSAFE EXACT APP: committed approval after the measured subject changed during sealing"


@pytest.mark.parametrize("change", ["payload", "measured-implementation"])
@pytest.mark.parametrize("broken", [False, True], ids=["real-refuses", "missing-final-measurement-detected"])
def test_change_during_sealing_cannot_commit_approval(studio, exact_case, monkeypatch, broken, change):
    checked = studio.verify(exact_case["id"], exact_case["version"])
    unchanged = _change_during_seal(studio, exact_case, monkeypatch, change)
    if broken:
        _method_mutant(monkeypatch, studio, "approve", _RemoveCall("self._assert_packet_current(case, packet)"))
    _detect(broken, lambda: _post_seal_oracle(studio, checked, unchanged))


def _lost_association_mutant(studio):
    set_active, _ = _clone(Session.set_active, _RemoveGuard("app_build is not None"))
    session_type = type("SyntheticLostExactAppSession", (Session,), {"set_active": set_active})

    class LostExactAppStore(type(studio.store)):
        @contextmanager
        def transaction(self):
            with super().transaction() as session:
                session.__class__ = session_type
                yield session

    studio.store.__class__ = LostExactAppStore


def _association_oracle(studio, case, open_studio):
    approved = approve(studio, studio.verify(case["id"], case["version"]))
    applied = studio.apply(approved["id"], approved["version"], OWNER)
    reopened = open_studio(studio.store.directory)
    with reopened.store.transaction() as session:
        active = session.active()
        persisted = session.load_case(case["id"])
    assert persisted["stage"] == applied["stage"] == "APPLIED"
    assert active["version"] == case["baseline_version"] + 1
    assert active["model"] == case["candidate"]
    association = active.get("app_build")
    assert association is not None and association["binding"] == case["app_build"], (
        "UNSAFE EXACT APP: committed the active model but lost its approved generated-app association"
    )
    assert association["case_id"] == case["id"]
    assert reopened.active_app_build()["freshness"] == "CURRENT"


@pytest.mark.parametrize("broken", [False, True], ids=["real-persists", "missing-association-write-detected"])
def test_generated_app_association_survives_atomic_application(studio, exact_case, open_studio, broken):
    if broken:
        _lost_association_mutant(studio)
    _detect(broken, lambda: _association_oracle(studio, exact_case, open_studio))


def _tampered_payload_oracle(studio, checked):
    before = snapshot(studio)
    try:
        approved = approve(studio, checked)
    except DomainError as error:
        assert error.code == "GATE_BLOCKED"
        assert snapshot(studio) == before
        return
    applied = studio.apply(approved["id"], approved["version"], OWNER)
    with studio.store.transaction() as session:
        assert session.active()["app_build"]["case_id"] == checked["id"]
    assert applied["stage"] == "APPLIED"
    assert b"UNREVIEWED PAYLOAD" not in payload(studio, checked).read_bytes(), (
        "UNSAFE EXACT APP: activated an artifact whose retained bytes no longer match the approved bundle"
    )


@pytest.mark.parametrize("broken", [False, True], ids=["real-refuses", "missing-payload-check-detected"])
def test_retained_artifact_must_be_remeasured(studio, exact_case, monkeypatch, broken):
    checked = studio.verify(exact_case["id"], exact_case["version"])
    target = payload(studio, checked)
    target.write_bytes(target.read_bytes() + b"\n<!-- UNREVIEWED PAYLOAD -->")
    if broken:
        # This private adapter loses exactly its payload validation; model generation,
        # receipt policy, owner approval, CAS and persistence remain the real services.
        monkeypatch.setattr(studio.generated_apps, "_check_payload", lambda binding, provider: None)
    _detect(broken, lambda: _tampered_payload_oracle(studio, checked))
