"""Template-only changes stale real review gates without rewriting historical receipts.

Authority is the existing synthetic kernel harness. The measured source copy is
disposable; neither owner source-review fixtures nor production templates change.
"""
from __future__ import annotations

import pytest

import eija_studio.adapters.identity as measured
from eija_studio.domain.models import OWNER, DomainError
from kernel_support import approve


def copy_measured_source(destination):
    for relative in measured.implementation_files():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((measured.PACKAGE / relative).read_bytes())


def test_template_only_change_stales_evidence_and_approval_but_preserves_history(
        studio, selected, tmp_path, monkeypatch, open_studio):
    source = tmp_path / "measured-source"
    copy_measured_source(source)
    monkeypatch.setattr(measured, "PACKAGE", source)
    files_before = measured.implementation_files()
    verified = studio.verify(selected["id"], selected["version"])
    original_packet = studio.view(verified["id"])["packet"]
    assert original_packet["technical_claims"]["runtime_matrix"] == "PASS"
    approved = approve(studio, verified)
    with studio.store.transaction() as unit:
        active_before = unit.active()

    template = source / "resources/appgen/web/app.css.tmpl"
    template.write_bytes(template.read_bytes() + b"\n/* changed template in isolated test source */\n")
    files_after = measured.implementation_files()
    assert {path for path in files_before if files_before[path] != files_after[path]} == {
        "resources/appgen/web/app.css.tmpl"}
    current = studio.view(approved["id"])
    assert current["packet"]["subject"]["implementation"] != original_packet["subject"]["implementation"]
    assert current["packet"]["technical_claims"]["runtime_matrix"] == "STALE"
    assert not current["packet"]["eligible"]
    answers = {question["id"]: question["expected"] for question in original_packet["questions"]}
    with pytest.raises(DomainError) as refused_approval:
        studio.approve(approved["id"], approved["version"], original_packet["subject_hash"], answers, True, OWNER)
    assert refused_approval.value.code == "GATE_BLOCKED"
    with pytest.raises(DomainError) as refused_apply:
        studio.apply(approved["id"], approved["version"], OWNER)
    assert refused_apply.value.code == "GATE_BLOCKED"
    with studio.store.transaction() as unit:
        assert unit.active() == active_before

    reopened = open_studio(studio.store.directory)
    history = reopened.view(approved["id"])
    assert history["case"]["receipts"] == approved["receipts"]
    assert history["case"]["decision"] == approved["decision"]
    assert all(reopened.signer.authentic(receipt) for receipt in history["case"]["receipts"])
    assert reopened.signer.authentic(history["case"]["decision"])
    assert history["packet"]["technical_claims"]["runtime_matrix"] == "STALE"
    assert reopened.export(approved["id"])["payload"]["case"]["receipts"] == approved["receipts"]
