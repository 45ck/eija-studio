"""An edit preview is an exact uncommitted model, never a write, receipt or edit capability."""
from __future__ import annotations

import copy
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.sqlite_store import Session
from eija_studio.application import service
from eija_studio.domain.models import AGENT, OWNER, DomainError, LayoutChange, Workflow
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.domain.transactions import RetargetTransition, parse_transaction
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.mcp_server import AgentSurface, StudioAgentPort
from kernel_support import harness_studio, reject_from

HEADERS = {"Authorization": "Bearer synthetic-preview-test", "Origin": "http://127.0.0.1:8765"}


def database(studio):
    """All persisted rows, including audit, operations, outbox, active baseline and other cases."""
    with studio.store.connection() as connection:
        return tuple(connection.iterdump())


def api(studio):
    return TestClient(create_app(studio, "synthetic-preview-test"), base_url=HEADERS["Origin"])


def preview_url(case):
    return f"/api/cases/{case['id']}/edit/preview"


def expected_retarget(case, transition, state):
    """Concrete independent oracle: only this transition's source changes in the returned model."""
    model = copy.deepcopy(case["candidate"])
    next(item for item in model["transitions"] if item["id"] == transition)["from_state"] = state
    return model


def stored_fixture(studio, case, **changes):
    """Inject a labelled synthetic persisted case without running verification or owner approval."""
    changed = copy.deepcopy(case) | changes
    with studio.store.transaction() as unit:
        unit.db.execute("UPDATE cases SET body=? WHERE id=?", (json.dumps(changed), case["id"]))
    return changed


def test_legal_preview_is_exact_and_sqlite_denies_any_attempted_write(studio, selected, monkeypatch):
    before = database(studio)
    attempted_writes = []
    connect = studio.store._connect

    def readonly_connection():
        connection = connect()

        def authorize(operation, argument, _second, _database, _trigger):
            if operation in {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE}:
                attempted_writes.append((operation, argument))
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        connection.set_authorizer(authorize)
        return connection

    monkeypatch.setattr(studio.store, "_connect", readonly_connection)
    tx = reject_from("Submitted")
    preview = studio.edit_preview(selected["id"], tx)
    expected = expected_retarget(selected, "TR-REJECT", "Submitted")
    assert preview == {
        "legal": True, "codes": [], "refs": [], "case_id": selected["id"],
        "version": selected["version"], "stage": "PREVIEW",
        "semantic_hash": Workflow.model_validate(selected["candidate"]).semantic_hash,
        "transaction": tx.model_dump(mode="json"), "current": selected["candidate"],
        "candidate": expected, "candidate_semantic_hash": Workflow.model_validate(expected).semantic_hash,
        "applied": False, "persisted": False, "scope": "semantic-edit-preview",
    }
    assert studio.edit_preview(selected["id"], tx) == preview
    assert not attempted_writes and database(studio) == before


def test_preview_keeps_pending_redo_layout_receipts_and_decision(studio, selected):
    changed = studio.edit(selected["id"], selected["version"], reject_from("Submitted"), OWNER)
    undone = studio.undo(changed["id"], changed["version"], OWNER)
    case = stored_fixture(studio, undone, stage="APPROVED", layout={"Submitted": {"x": 100, "y": 80}},
                          receipts=[{"synthetic_history_marker": "immutable receipt"}],
                          decision={"synthetic_history_marker": "existing decision"})
    before = database(studio)
    preview = studio.edit_preview(case["id"], reject_from("Submitted"))
    assert preview["legal"] and preview["stage"] == "APPROVED"
    assert preview["candidate"] == changed["candidate"]
    assert database(studio) == before


def test_policy_refusal_has_exact_codes_refs_and_no_candidate(studio, selected):
    before = database(studio)
    tx = reject_from("Draft")
    preview = studio.edit_preview(selected["id"], tx)
    assert not preview["legal"]
    assert preview["codes"] == ["UNSUPPORTED_REJECTION_SOURCE"]
    assert preview["refs"] == ["law:reject-source-bounded", "transition:TR-REJECT"]
    assert preview["candidate"] is preview["candidate_semantic_hash"] is None
    assert preview["current"] == selected["candidate"]
    with pytest.raises(DomainError) as caught:
        studio.edit(selected["id"], selected["version"], tx, OWNER)
    assert caught.value.code == "POLICY_BLOCKED"
    assert caught.value.details == {"codes": preview["codes"], "refs": preview["refs"]}
    assert database(studio) == before


def test_structural_refusal_has_exact_reference_and_no_guessed_candidate(studio, selected):
    before = database(studio)
    tx = RetargetTransition(kind="retarget_transition", transition="TR-MISSING", end="source", state="Submitted")
    preview = studio.edit_preview(selected["id"], tx)
    assert not preview["legal"] and preview["codes"] == ["EDIT_INVALID"]
    assert preview["refs"] == ["transition:TR-MISSING"]
    assert preview["candidate"] is preview["candidate_semantic_hash"] is None
    assert database(studio) == before


@pytest.mark.parametrize("proposed", [False, True])
def test_missing_owner_meaning_refuses_even_a_structurally_valid_edit(studio, proposed):
    case = studio.create("Let teachers sign off excursions.")
    if proposed:
        case = studio.propose(case["id"], case["version"])
    before = database(studio)
    preview = studio.edit_preview(case["id"], reject_from("Submitted"))
    assert not preview["legal"] and preview["codes"] == ["MEANING_REQUIRED"] and preview["refs"] == []
    assert preview["current"] == case["baseline"]
    assert preview["candidate"] is preview["candidate_semantic_hash"] is None
    assert database(studio) == before


@pytest.mark.parametrize("stage", ["APPLIED", "DISCARDED"])
def test_closed_case_refuses_preview_and_edit_without_mutation(studio, selected, stage):
    case = stored_fixture(studio, selected, stage=stage)
    before = database(studio)
    preview = studio.edit_preview(case["id"], reject_from("Submitted"))
    assert not preview["legal"] and preview["codes"] == ["CASE_CLOSED"]
    assert preview["stage"] == stage and preview["candidate"] is None
    with pytest.raises(DomainError) as caught:
        studio.edit(case["id"], case["version"], reject_from("Submitted"), OWNER)
    assert caught.value.code == "CASE_CLOSED" and database(studio) == before


def test_unexplained_candidate_refuses_preview_without_repair(studio, selected):
    stored_fixture(studio, selected, candidate=expected_retarget(selected, "TR-REJECT", "Submitted"))
    before = database(studio)
    preview = studio.edit_preview(selected["id"], reject_from("Recommended"))
    assert not preview["legal"] and preview["codes"] == ["HISTORY_INCONSISTENT"]
    assert preview["candidate"] is None and database(studio) == before


@pytest.mark.parametrize("concurrent_change", ["semantic", "layout"])
def test_apply_captured_version_rejects_stale_preview_even_if_semantics_match(studio, selected, concurrent_change):
    preview = studio.edit_preview(selected["id"], reject_from("Submitted"))
    if concurrent_change == "semantic":
        current = studio.edit(selected["id"], selected["version"], reject_from("Submitted"), OWNER)
    else:
        current = studio.layout(selected["id"], selected["version"], LayoutChange(node="Submitted", x=70, y=80), OWNER)
        assert Workflow.model_validate(current["candidate"]).semantic_hash == preview["semantic_hash"]
    assert current["version"] > preview["version"]
    before = database(studio)
    response = api(studio).post(f"/api/cases/{selected['id']}/edit", headers=HEADERS,
                                json={"expected_version": preview["version"], "transaction": preview["transaction"]})
    assert response.status_code == 409 and response.json()["code"] == "STALE_VERSION"
    assert database(studio) == before


def test_apply_fresh_preview_matches_exactly_and_remains_owner_only(studio, selected):
    preview = studio.edit_preview(selected["id"], reject_from("Submitted"))
    tx = parse_transaction(preview["transaction"])
    before = database(studio)
    with pytest.raises(DomainError) as caught:
        studio.edit(selected["id"], preview["version"], tx, AGENT)
    assert caught.value.code == "AUTHORITY_REQUIRED" and database(studio) == before
    applied = studio.edit(selected["id"], preview["version"], tx, OWNER)
    assert applied["candidate"] == preview["candidate"]
    assert applied["version"] == preview["version"] + 1


def test_preview_reads_case_once_and_returns_that_coherent_snapshot(studio, selected, monkeypatch):
    loads = []
    load = Session.load_case

    def counted_load(unit, case_id):
        loads.append(case_id)
        return load(unit, case_id)

    monkeypatch.setattr(Session, "load_case", counted_load)
    preview = studio.edit_preview(selected["id"], reject_from("Submitted"))
    assert loads == [selected["id"]]
    assert (preview["version"], preview["current"]) == (selected["version"], selected["candidate"])


def test_revision_after_capture_cannot_mix_new_identity_with_old_candidate(studio, selected, monkeypatch):
    project = service.preview_edit

    def change_after_capture(case, transaction, pack):
        studio.layout(case.id, case.version, LayoutChange(node="Submitted", x=10, y=20), OWNER)
        return project(case, transaction, pack)

    monkeypatch.setattr(service, "preview_edit", change_after_capture)
    preview = studio.edit_preview(selected["id"], reject_from("Submitted"))
    assert preview["version"] == selected["version"] and preview["current"] == selected["candidate"]
    with studio.store.transaction() as unit:
        assert unit.load_case(selected["id"])["version"] == selected["version"] + 1


@pytest.mark.parametrize("transaction", [
    {"kind": "unknown"},
    {"kind": "retarget_transition", "transition": "TR-REJECT", "end": "elsewhere", "state": "Submitted"},
    {"kind": "retarget_transition", "transition": "TR-REJECT", "end": "source", "state": "Submitted", "approved": True},
])
def test_malformed_http_and_agent_transactions_are_rejected_without_writes(studio, selected, transaction):
    before = database(studio)
    response = api(studio).post(preview_url(selected), headers=HEADERS, json={"transaction": transaction})
    assert response.status_code == 422 and response.json()["code"] == "CONTRACT_REJECTED"
    with pytest.raises(DomainError) as caught:
        AgentSurface(StudioAgentPort(studio)).edit_check(selected["id"], transaction)
    assert caught.value.code == "EDIT_INVALID" and database(studio) == before


def test_http_preview_has_full_model_while_agent_check_contract_is_unchanged(studio, selected):
    tx = reject_from("Submitted").model_dump(mode="json")
    before = database(studio)
    response = api(studio).post(preview_url(selected), headers=HEADERS, json={"transaction": tx})
    assert response.status_code == 200 and response.json()["candidate"] is not None
    agent = AgentSurface(StudioAgentPort(studio)).edit_check(selected["id"], tx)
    assert agent == {
        "legal": True, "codes": [], "refs": [], "trust": "UNTRUSTED_PROPOSAL", "applied": False,
        "persisted": False, "boundary": "Dry-run only; the local owner must choose and perform any model edit.",
    }
    assert database(studio) == before


def test_old_check_keeps_policy_only_semantics_for_draft_and_closed_cases(studio, selected):
    draft = studio.create("Let teachers sign off excursions.")
    closed = studio.discard(selected["id"], selected["version"])
    before = database(studio)
    tx = reject_from("Submitted")
    for case, code in ((draft, "MEANING_REQUIRED"), (closed, "CASE_CLOSED")):
        response = api(studio).post(f"/api/cases/{case['id']}/edit/check", headers=HEADERS,
                                    json={"transaction": tx.model_dump(mode="json")})
        assert response.status_code == 200 and response.json() == {"legal": True, "codes": [], "refs": []}
        preview = studio.edit_preview(case["id"], tx)
        assert not preview["legal"] and preview["codes"] == [code]
    assert database(studio) == before


def test_http_preview_still_requires_local_session_and_origin(studio, selected):
    before = database(studio)
    payload = {"transaction": reject_from("Submitted").model_dump(mode="json")}
    client = api(studio)
    assert client.post(preview_url(selected), headers={"Origin": HEADERS["Origin"]}, json=payload).status_code == 401
    assert client.post(preview_url(selected), headers=HEADERS | {"Origin": "https://invalid.example"}, json=payload).status_code == 403
    assert database(studio) == before


def test_preview_is_pack_agnostic_and_refuses_library_sequence_bypass(tmp_path):
    pack = load_pack(PACKS_ROOT / "library-loan")
    studio = harness_studio(tmp_path / "library", pack)
    case = studio.create(pack.fixtures.demo_request)
    case = studio.propose(case["id"], case["version"])
    case = studio.select(case["id"], case["version"], "allow_renewal", OWNER)
    before = database(studio)
    tx = RetargetTransition(kind="retarget_transition", transition="TR-RENEW", end="source", state="OnLoan")
    preview = studio.edit_preview(case["id"], tx)
    assert preview["legal"] and preview["candidate"] == expected_retarget(case, "TR-RENEW", "OnLoan")
    bypass = RetargetTransition(kind="retarget_transition", transition="TR-RETURN", end="source", state="Requested")
    refused = studio.edit_preview(case["id"], bypass)
    assert not refused["legal"] and refused["candidate"] is None
    assert refused["codes"] == ["LOAN_RETURN_WITHOUT_CHECKOUT"]
    assert database(studio) == before
