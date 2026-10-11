"""Scope, exact row subjects, draft isolation and declared trace negative controls."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.application.capabilities import capability_map
from eija_studio.application.law_proof import with_laws
from eija_studio.application.requirement_trace import compare_requirements, requirement_review
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.play_assurance import acceptance_snapshot, register
from eija_studio.weave.codelink import CSV_ROW, CodeRef, digest

ROOT = Path(__file__).resolve().parents[1]
SLICE = load_pack(ROOT / "packs/eija-review-slice")


def test_pinned_requirement_hashes_match_authoritative_weave_rows():
    snapshot = acceptance_snapshot(SLICE)
    assert snapshot["provenance"]["mode"] == "packaged_historical_snapshot"
    for row in snapshot["rows"]:
        assert snapshot["row_hashes"][row["id"]] == digest(
            ROOT, CodeRef("docs/verification/ACCEPTANCE_MATRIX.csv", row["id"]), CSV_ROW)


def test_unknown_requirement_cannot_create_policy_and_empty_draft_is_refused():
    rows = acceptance_snapshot(SLICE)["rows"]
    for drafts, expected in (({"AC99": "Allow automatic approval"}, "REQUIREMENT_UNKNOWN"),
                             ({"AC08": " "}, "REQUIREMENT_DRAFT_INVALID")):
        with pytest.raises(DomainError) as caught:
            compare_requirements(rows, drafts)
        assert caught.value.code == expected


def test_prose_edit_changes_row_subject_but_never_policy_or_runtime_claim():
    before_digest = SLICE.digest
    report = requirement_review(SLICE, SLICE.model, acceptance_snapshot(SLICE),
                                drafts={"AC08": "The owner reviews exactly this change before activation."})
    row = next(item for item in report["requirements"] if item["id"] == "AC08")
    assert row["changed"] and row["before_hash"] != row["after_hash"]
    assert row["status"] == "DRAFT_PROSE_ONLY" and row["policy_changed"] is False
    assert row["affected"] and row["affected_checks"]
    assert row["observed_status"] == "NOT_RUN"
    assert SLICE.digest == before_digest
    assert report["laws"]["summary"] == {"added": [], "removed": [], "changed": []}


def test_declared_links_preserve_direction_and_resolution_is_not_verification():
    ref = "repo://src/eija_studio/application/service.py#Studio.approve"
    report = requirement_review(SLICE, SLICE.model, acceptance_snapshot(SLICE),
                                connection={"source_hash": "sha256:" + "a" * 64,
                                            "nodes": [{"id": ref, "digest": "b" * 64}]})
    row = next(item for item in report["requirements"] if item["id"] == "AC08")
    link = next(link for link in row["links"] if link["from"] == ref)
    assert link["resolved"] and link["kind"] == "satisfies"
    assert link["to"] == "repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC08"
    assert link["source_hash"] == "b" * 64 and link["evidence_status"] == "NOT_RUN"
    assert row["unresolved"]  # missing tests and service nodes are preserved
    assert report["subject"]["source_hash"] == "sha256:" + "a" * 64


def test_unbound_pack_does_not_acquire_reference_laws_or_inferred_source_links():
    pack = load_pack(ROOT / "packs/library-loan")
    report = requirement_review(pack, pack.model, acceptance_snapshot(SLICE))
    assert report["coverage"]["status"] == "UNBOUND"
    assert report["coverage"]["linked"] == 0
    assert all(not row["links"] and row["unresolved"] for row in report["requirements"])


def test_law_description_change_is_visible_draft_and_marks_declared_links_for_review():
    law_rows = [law.model_dump(mode="json", exclude_none=True) for law in SLICE.laws]
    next(row for row in law_rows if row["id"] == "approve-owner")["description"] = "Changed owner approval wording."
    draft = with_laws(SLICE, law_rows)
    report = requirement_review(SLICE, SLICE.model, acceptance_snapshot(SLICE), candidate_pack=draft)
    assert report["laws"]["summary"]["changed"] == ["approve-owner"]
    item = next(item for item in report["laws"]["items"] if item["id"] == "approve-owner")
    assert item["fields"] == ["description"] and item["activation"] == "DRAFT_ONLY"
    assert item["description_changed"] and not item["draft_policy_fields"]
    row = next(item for item in report["requirements"] if item["id"] == "AC08")
    assert row["affected"] and not row["changed"] and row["policy_changed"] is False


def test_model_change_marks_relevant_declared_requirements_without_claiming_tests_pass():
    document = SLICE.model.model_dump(mode="json")
    document["transitions"] = [dict(t, to_state="PROPOSED") if t["id"] == "TR-SELECT" else t
                               for t in document["transitions"]]
    candidate = Workflow.model_validate(document)
    report = requirement_review(SLICE, candidate, acceptance_snapshot(SLICE), baseline=SLICE.model)
    row = next(item for item in report["requirements"] if item["id"] == "AC07")
    assert row["affected"] and row["affected_checks"]
    assert row["observed_status"] == "NOT_RUN"
    assert report["subject"]["model_hash"] != report["subject"]["baseline_model_hash"]


def test_capabilities_cover_lifecycle_with_bounded_execution_and_draft_only_policy():
    pack = load_pack(ROOT / "packs/library-loan")
    result = capability_map(pack, pack.model)
    assert {item["id"] for item in result["aspects"]} == {
        "requirements", "data", "behaviour", "collaboration", "interfaces", "integrations", "operations", "assurance"}
    assert {construct["level"] for area in result["aspects"] for construct in area["constructs"]} == {
        "executable", "checked_design", "unsupported"}
    data = next(item for item in result["aspects"] if item["id"] == "data")
    assert next(item for item in data["constructs"] if item["name"] == "Other classes and associations")["level"] == "checked_design"
    assert {"laws", "data schema", "requirement prose"} <= set(result["activation"]["draft_only"])


def test_http_read_and_compare_keep_session_origin_contract_and_active_state(studio):
    app = create_app(studio, "assurance-test", port=8765)
    # Registration is explicit here so this focused test also exercises the existing middleware boundary.
    if not any(route.path == "/api/play/assurance" for route in app.routes):
        register(app, studio, lambda body: Workflow.model_validate(studio.workbench()["model"]), lambda _steps: studio.pack)
    client = TestClient(app, base_url="http://127.0.0.1:8765")
    headers = {"Authorization": "Bearer assurance-test", "Origin": "http://127.0.0.1:8765"}
    before = studio.workbench()["model"]
    assert client.get("/api/play/assurance").status_code == 401
    assert client.post("/api/play/assurance/compare", json={}, headers={"Authorization": "Bearer assurance-test"}).status_code == 403
    response = client.post("/api/play/assurance/compare", headers=headers,
                           json={"requirement_drafts": {"AC08": "A reviewed draft does not authorize an agent."}})
    assert response.status_code == 200
    assert response.json()["traceability"]["requirements"][7]["policy_changed"] is False
    assert client.post("/api/play/assurance/compare", headers=headers, json={"approved": True}).status_code == 422
    denied = client.post("/api/play/assurance/compare", headers=headers,
                         json={"requirement_drafts": {"AC99": "Approve everything"}})
    assert denied.status_code == 409 and denied.json()["code"] == "REQUIREMENT_UNKNOWN"
    assert studio.workbench()["model"] == before
