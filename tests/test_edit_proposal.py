"""Offline typed requests remain proposals until the owner commits the captured edit.

Normal source identity, disposable SQLite, no live provider, approval, apply or stamping.
Expected candidate changes are expressed directly rather than by calling the edit engine.
"""
from __future__ import annotations

import copy
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.edit_proposals import OfflineEditProposer
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import AGENT, OWNER, DomainError, LayoutChange, Workflow
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.domain.transactions import RetargetTransition, parse_transaction
from eija_studio.interfaces.http import create_app

SYNTHETIC_SESSION = "synthetic-edit-proposal-test"
HEADERS = {"Authorization": "Bearer " + SYNTHETIC_SESSION, "Origin": "http://127.0.0.1:8765"}
MOVE = {"kind": "retarget_transition", "transition": "TR-VERIFY", "end": "source", "state": "SAVED"}
ROLE = {"kind": "set_role", "transition": "TR-SAVE", "role": "Agent"}


class NeverMeaningProvider:
    name = "must-not-call-meaning-provider"
    networked = True

    def propose(self, *args, **kwargs):
        raise AssertionError("A typed edit must not invoke the original meaning provider")


def selected_studio(tmp_path, name="eija-review-slice", meaning="show_saved_path"):
    studio = build_studio(tmp_path / name, pack=load_pack(PACKS_ROOT / name))
    case = studio.create(studio.pack.fixtures.demo_request)
    case = studio.propose(case["id"], case["version"])
    case = studio.select(case["id"], case["version"], meaning, OWNER)
    studio.provider = NeverMeaningProvider()
    return studio, case


@pytest.fixture
def selected_edit(tmp_path):
    return selected_studio(tmp_path)


def database(studio):
    """Includes every case, baseline, receipt, history/audit row and runtime/outbox row."""
    with studio.store.connection() as connection:
        return tuple(connection.iterdump())


def client(studio):
    return TestClient(create_app(studio, SYNTHETIC_SESSION), base_url=HEADERS["Origin"])


def endpoint(case):
    return f"/api/cases/{case['id']}/edit/propose"


def expected_candidate(case, transaction):
    candidate = copy.deepcopy(case["candidate"])
    transition = next(row for row in candidate["transitions"] if row["id"] == transaction["transition"])
    if transaction["kind"] == "set_role":
        transition["role"] = transaction["role"]
    else:
        field = {"source": "from_state", "target": "to_state"}[transaction["end"]]
        transition[field] = transaction["state"]
    return candidate


def expected_proposal(studio, case, request, transaction):
    candidate = expected_candidate(case, transaction)
    return {
        "scope": "typed-edit-proposal", "provider": "offline", "model": "typed-edit-fixture-v1",
        "live": False, "trust": "UNTRUSTED_PROPOSAL", "request": request,
        "pack": {"id": studio.pack.id, "digest": studio.pack.digest},
        "preview": {
            "legal": True, "codes": [], "refs": [], "case_id": case["id"], "version": case["version"],
            "stage": case["stage"], "semantic_hash": Workflow.model_validate(case["candidate"]).semantic_hash,
            "transaction": transaction, "current": case["candidate"], "candidate": candidate,
            "candidate_semantic_hash": Workflow.model_validate(candidate).semantic_hash,
            "applied": False, "persisted": False, "scope": "semantic-edit-preview",
        },
    }


@pytest.mark.parametrize("edit_request,transaction", [
    ("Move Verify source to SAVED", MOVE),
    ("  mOvE\ttr-verify   SOURCE to saved.  ", MOVE),
    ("Allow Agent to Save", ROLE),
    ("Set TR-SAVE role to Agent.", ROLE),
    ("Move Save target to PREVIEW", {
        "kind": "retarget_transition", "transition": "TR-SAVE", "end": "target", "state": "PREVIEW"}),
])
def test_complete_request_returns_exact_uncommitted_candidate(selected_edit, edit_request, transaction):
    studio, case = selected_edit
    before = database(studio)
    result = studio.propose_edit(case["id"], case["version"], edit_request)
    assert result == expected_proposal(studio, case, edit_request, transaction)
    assert database(studio) == before


def test_proposal_cannot_write_even_with_layout_and_pending_redo(selected_edit, monkeypatch):
    studio, case = selected_edit
    edited = studio.edit(case["id"], case["version"], parse_transaction(ROLE), OWNER)
    undone = studio.undo(case["id"], edited["version"], OWNER)
    case = studio.layout(case["id"], undone["version"], LayoutChange(node="PREVIEW", x=80, y=120), OWNER)
    before, history = database(studio), studio.history(case["id"])
    assert history["can_redo"] and case["layout"]
    connect, attempted = studio.store._connect, []

    def readonly_connection():
        connection = connect()

        def authorize(operation, argument, _second, _database, _trigger):
            if operation in {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE}:
                attempted.append((operation, argument))
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        connection.set_authorizer(authorize)
        return connection

    monkeypatch.setattr(studio.store, "_connect", readonly_connection)
    result = studio.propose_edit(case["id"], case["version"], "Move Verify source to SAVED")
    assert result == expected_proposal(studio, case, "Move Verify source to SAVED", MOVE)
    assert not attempted and database(studio) == before
    assert studio.history(case["id"]) == history
    assert studio.view(case["id"])["case"]["receipts"] == case["receipts"]


def test_protected_role_is_returned_as_a_refused_preview_without_writes(selected_edit):
    studio, case = selected_edit
    before = database(studio)
    response = client(studio).post(endpoint(case), headers=HEADERS,
                                   json={"expected_version": case["version"], "request": "Allow Agent to Approve"})
    assert response.status_code == 200
    result = response.json()
    assert result["trust"] == "UNTRUSTED_PROPOSAL" and result["live"] is False
    preview = result["preview"]
    assert preview["transaction"] == {"kind": "set_role", "transition": "TR-APPROVE", "role": "Agent"}
    assert not preview["legal"] and preview["codes"] == ["REFERENCE_AUTHORITY:Approve"]
    assert "law:approve-owner" in preview["refs"] and "transition:TR-APPROVE" in preview["refs"]
    assert preview["candidate"] is preview["candidate_semantic_hash"] is None
    assert not preview["applied"] and not preview["persisted"]
    assert preview["current"] == case["candidate"] and database(studio) == before


@pytest.mark.parametrize("edit_request,code", [
    ("Make verification easier", "EDIT_REQUEST_UNSUPPORTED"),
    ("Do not move Verify source to SAVED", "EDIT_REQUEST_UNSUPPORTED"),
    ("Move Verify source to SAVED and Allow Agent to Save", "EDIT_REQUEST_UNSUPPORTED"),
    ("Move Verify source to SAVED. Allow Agent to Save.", "EDIT_REQUEST_UNSUPPORTED"),
    ("Move Verify source to SAVED..", "EDIT_REQUEST_UNSUPPORTED"),
    ("Please Move Verify source to SAVED", "EDIT_REQUEST_UNSUPPORTED"),
    ("Move Missing source to SAVED", "EDIT_REQUEST_UNSUPPORTED"),
    ("Move Verify source to UNKNOWN", "EDIT_REQUEST_UNSUPPORTED"),
    ("Allow UnknownRole to Save", "EDIT_REQUEST_UNSUPPORTED"),
    ("Move Verify source to PREVIEW", "EDIT_REQUEST_NO_CHANGE"),
    ("Allow Owner to Save", "EDIT_REQUEST_NO_CHANGE"),
])
def test_unsupported_negated_multiple_and_noop_requests_are_not_guessed(selected_edit, edit_request, code):
    studio, case = selected_edit
    before = database(studio)
    response = client(studio).post(endpoint(case), headers=HEADERS,
                                   json={"expected_version": case["version"], "request": edit_request})
    assert response.status_code == 409 and response.json()["code"] == code
    assert database(studio) == before


@pytest.mark.parametrize("collision", ["casefold-state", "action-versus-id"])
def test_ambiguous_model_names_are_refused_instead_of_picked(selected_edit, collision):
    _, case = selected_edit
    value = copy.deepcopy(case["candidate"])
    choices = [parse_transaction(MOVE)]
    if collision == "casefold-state":
        value["states"].append("saved")
        choices.append(RetargetTransition(kind="retarget_transition", transition="TR-VERIFY", end="source", state="saved"))
    else:
        next(row for row in value["transitions"] if row["id"] == "TR-SAVE")["action"] = "TR-VERIFY"
        choices.append(RetargetTransition(kind="retarget_transition", transition="TR-SAVE", end="source", state="SAVED"))
    model = Workflow.model_validate(value)
    with pytest.raises(DomainError) as caught:
        OfflineEditProposer().propose("Move TR-VERIFY source to SAVED", model, tuple(choices))
    assert caught.value.code == "EDIT_REQUEST_AMBIGUOUS"


@pytest.mark.parametrize("raw", [
    None, [], {"kind": "unknown"}, MOVE | {"approved": True},
    {"transaction": MOVE, "trust": "TRUSTED", "applied": True},
    {"kind": "add_state", "state": "Invented"}, MOVE | {"state": "Invented"}, ROLE | {"role": "Invented"},
])
def test_untrusted_adapter_output_cannot_escape_captured_choices(selected_edit, raw):
    studio, case = selected_edit

    class MaliciousProposer:
        def propose(self, request, model, choices):
            assert request == "Move Verify source to SAVED"
            assert model.model_dump(mode="json") == case["candidate"] and isinstance(choices, tuple)
            return raw

    studio.edit_proposer = MaliciousProposer()
    before = database(studio)
    with pytest.raises(DomainError) as caught:
        studio.propose_edit(case["id"], case["version"], "Move Verify source to SAVED")
    assert caught.value.code == "EDIT_PROPOSAL_INVALID" and database(studio) == before


@pytest.mark.parametrize("state,code", [
    ("draft", "MEANING_REQUIRED"),
    ("discarded", "CASE_CLOSED"),
    ("inconsistent_history", "HISTORY_INCONSISTENT"),
])
def test_invalid_case_preconditions_refuse_before_the_proposer(selected_edit, state, code):
    studio, case = selected_edit
    if state == "draft":
        case = studio.create("Synthetic draft without an owner-selected meaning")
    elif state == "discarded":
        case = studio.discard(case["id"], case["version"])
    else:
        # Synthetic corruption: remove an initial meaning transaction without repairing its candidate.
        damaged = copy.deepcopy(case)
        damaged["transactions"].pop(0)
        with studio.store.transaction() as unit:
            unit.db.execute("UPDATE cases SET body=? WHERE id=?", (json.dumps(damaged), case["id"]))
    studio.edit_proposer = NeverMeaningProvider()
    before = database(studio)
    with pytest.raises(DomainError) as caught:
        studio.propose_edit(case["id"], case["version"], "Move Verify source to SAVED")
    assert caught.value.code == code and database(studio) == before


@pytest.mark.parametrize("edit_request,configured,code", [
    (" \t\n ", True, "INVALID_REQUEST"),
    ("Move Verify source to SAVED", False, "EDIT_PROPOSER_UNAVAILABLE"),
    (" \t\n ", False, "EDIT_PROPOSER_UNAVAILABLE"),
])
def test_request_and_configuration_preconditions_do_not_mutate(selected_edit, edit_request, configured, code):
    studio, case = selected_edit
    studio.edit_proposer = NeverMeaningProvider() if configured else None
    before = database(studio)
    with pytest.raises(DomainError) as caught:
        studio.propose_edit(case["id"], case["version"], edit_request)
    assert caught.value.code == code and database(studio) == before


@pytest.mark.parametrize("change", ["semantic", "layout"])
def test_stale_request_is_refused_before_invoking_the_proposer(selected_edit, change):
    studio, case = selected_edit
    if change == "semantic":
        studio.edit(case["id"], case["version"], parse_transaction(ROLE), OWNER)
    else:
        studio.layout(case["id"], case["version"], LayoutChange(node="PREVIEW", x=30, y=40), OWNER)
    studio.edit_proposer = NeverMeaningProvider()
    before = database(studio)
    with pytest.raises(DomainError) as caught:
        studio.propose_edit(case["id"], case["version"], "Move Verify source to SAVED")
    assert caught.value.code == "STALE_VERSION" and database(studio) == before


@pytest.mark.parametrize("change", ["semantic", "layout"])
def test_change_during_proposal_cannot_publish_a_stale_preview(selected_edit, change):
    studio, case = selected_edit
    captured = {}

    class RacingProposer:
        def propose(self, request, model, choices):
            assert model.model_dump(mode="json") == case["candidate"]
            if change == "semantic":
                studio.edit(case["id"], case["version"], parse_transaction(ROLE), OWNER)
            else:
                studio.layout(case["id"], case["version"], LayoutChange(node="PREVIEW", x=30, y=40), OWNER)
            captured["database"] = database(studio)
            return MOVE

    studio.edit_proposer = RacingProposer()
    with pytest.raises(DomainError) as caught:
        studio.propose_edit(case["id"], case["version"], "Move Verify source to SAVED")
    assert caught.value.code == "STALE_VERSION"
    assert database(studio) == captured["database"]


@pytest.mark.parametrize("change", ["semantic", "layout"])
def test_later_change_blocks_owner_commit_of_the_captured_proposal(selected_edit, change):
    studio, case = selected_edit
    preview = studio.propose_edit(case["id"], case["version"], "Move Verify source to SAVED")["preview"]
    if change == "semantic":
        studio.edit(case["id"], case["version"], parse_transaction(ROLE), OWNER)
    else:
        updated = studio.layout(case["id"], case["version"], LayoutChange(node="PREVIEW", x=30, y=40), OWNER)
        assert Workflow.model_validate(updated["candidate"]).semantic_hash == preview["semantic_hash"]
    before = database(studio)
    response = client(studio).post(f"/api/cases/{case['id']}/edit", headers=HEADERS,
                                   json={"expected_version": preview["version"], "transaction": preview["transaction"]})
    assert response.status_code == 409 and response.json()["code"] == "STALE_VERSION"
    assert database(studio) == before


def test_only_owner_can_commit_the_exact_proposal_and_undo_it(selected_edit):
    studio, case = selected_edit
    preview = studio.propose_edit(case["id"], case["version"], "Move Verify source to SAVED")["preview"]
    before = database(studio)
    with pytest.raises(DomainError) as caught:
        studio.edit(case["id"], preview["version"], parse_transaction(preview["transaction"]), AGENT)
    assert caught.value.code == "AUTHORITY_REQUIRED" and database(studio) == before
    response = client(studio).post(f"/api/cases/{case['id']}/edit", headers=HEADERS,
                                   json={"expected_version": preview["version"], "transaction": preview["transaction"]})
    assert response.status_code == 200
    edited = response.json()
    assert edited["candidate"] == preview["candidate"] and edited["version"] == case["version"] + 1
    assert edited["selected_meaning"] == case["selected_meaning"]
    assert edited["decision"] is None and edited["baseline"] == case["baseline"]
    undone = studio.undo(case["id"], edited["version"], OWNER)
    assert undone["candidate"] == case["candidate"] and undone["receipts"] == case["receipts"]
    assert undone["baseline_version"] == case["baseline_version"] and undone["decision"] is None


@pytest.mark.parametrize("edit_request,transaction", [
    ("Move Return source to Overdue", {"kind": "retarget_transition", "transition": "TR-RETURN", "end": "source", "state": "Overdue"}),
    ("Set Cancel role to Clerk", {"kind": "set_role", "transition": "TR-CANCEL", "role": "Clerk"}),
])
def test_other_pack_uses_its_own_names_and_exact_model(tmp_path, edit_request, transaction):
    studio, case = selected_studio(tmp_path, "library-loan", "allow_renewal")
    transition = next(row for row in case["candidate"]["transitions"] if row["id"] == transaction["transition"])
    if transaction["kind"] == "set_role":
        assert transition["role"] == "Member" and transaction["role"] == "Clerk"
    assert expected_candidate(case, transaction) != case["candidate"]
    before = database(studio)
    assert studio.propose_edit(case["id"], case["version"], edit_request) == expected_proposal(studio, case, edit_request, transaction)
    assert database(studio) == before


@pytest.mark.parametrize("payload", [
    {}, {"request": "Move Verify source to SAVED"}, {"expected_version": 2},
    {"request": "", "expected_version": 2}, {"request": None, "expected_version": 2},
    {"request": "x" * 6001, "expected_version": 2},
    {"request": "Move Verify source to SAVED", "expected_version": True},
    {"request": "Move Verify source to SAVED", "expected_version": 2, "principal": "owner"},
    {"request": "Move Verify source to SAVED", "expected_version": 2, "transaction": MOVE},
])
def test_http_rejects_malformed_or_smuggled_contract_fields(selected_edit, payload):
    studio, case = selected_edit
    before = database(studio)
    response = client(studio).post(endpoint(case), headers=HEADERS, json=payload)
    assert response.status_code == 422 and response.json()["code"] == "CONTRACT_REJECTED"
    assert database(studio) == before


def test_http_proposal_needs_the_session_and_same_origin(selected_edit):
    studio, case = selected_edit
    before = database(studio)
    payload = {"request": "Move Verify source to SAVED", "expected_version": case["version"]}
    http = client(studio)
    assert http.post(endpoint(case), headers={"Origin": HEADERS["Origin"]}, json=payload).status_code == 401
    assert http.post(endpoint(case), headers=HEADERS | {"Origin": "https://invalid.example"}, json=payload).status_code == 403
    response = http.post(endpoint(case), headers=HEADERS, json=payload)
    assert response.status_code == 200 and response.json() == expected_proposal(studio, case, payload["request"], MOVE)
    assert database(studio) == before
