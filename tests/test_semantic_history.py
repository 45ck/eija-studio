"""History must reuse semantic interpretation without reopening authority or rewriting evidence."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.sqlite_store import Session
from eija_studio.application.history import replay
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.models import AGENT, OWNER, DomainError, LayoutChange
from eija_studio.domain.pack import PACKS_ROOT, Pack, load_pack
from eija_studio.domain.policy import apply_transaction
from eija_studio.domain.transactions import (
    AddState,
    RemoveTransition,
    RenameState,
    SetGuards,
    SetRole,
)
from eija_studio.interfaces.http import create_app
from kernel_support import approve, harness_studio, reject_from


def snapshot(studio, case_id):
    with studio.store.transaction() as u:
        return u.load_case(case_id), u.active(), u.observations(case_id), u.effect_counts()


def edit(studio, case, tx):
    return studio.edit(case["id"], case["version"], tx, OWNER)


def navigate(studio, case, operation):
    return getattr(studio, operation)(case["id"], case["version"], OWNER)


def test_initial_meaning_is_atomic_and_never_partially_undone(studio, selected):
    initial = studio.pack.meaning(selected["selected_meaning"]).transactions
    assert len(initial) > 1
    with pytest.raises(DomainError):
        apply_transaction(ChangeCase.model_validate(selected).baseline, initial[0], studio.pack)
    before = snapshot(studio, selected["id"])
    history = studio.history(selected["id"])
    assert history["selection"]["transaction_count"] == len(initial)
    assert history["selection"]["model"] == selected["candidate"]
    assert history["edits"] == history["redo"] == []
    assert not history["can_undo"] and not history["can_redo"]
    with pytest.raises(DomainError, match="original meaning") as error:
        navigate(studio, selected, "undo")
    assert error.value.code == "NOTHING_TO_UNDO"
    assert snapshot(studio, selected["id"]) == before


def test_two_edits_undo_redo_are_exact_and_ordered(studio, selected):
    first = edit(studio, selected, reject_from("Submitted"))
    second = edit(studio, first, reject_from("Recommended"))
    case = navigate(studio, second, "undo")
    assert case["candidate"] == first["candidate"]
    case = navigate(studio, case, "undo")
    assert case["candidate"] == selected["candidate"]
    assert case["transactions"] == selected["transactions"]
    history = studio.history(case["id"])
    assert [item["index"] for item in history["redo"]] == [1, 2]
    assert [item["model"] for item in history["redo"]] == [first["candidate"], second["candidate"]]
    assert history["cursor"] == 0 and not history["can_undo"] and history["can_redo"]
    case = navigate(studio, case, "redo")
    assert case["candidate"] == first["candidate"]
    case = navigate(studio, case, "redo")
    assert case["candidate"] == second["candidate"] and not case["redo_transactions"]
    assert case["version"] == second["version"] + 4
    assert [item["kind"] for item in studio.history(case["id"])["events"]] == [
        "SemanticEdited", "SemanticEdited", "SemanticUndone", "SemanticUndone", "SemanticRedone", "SemanticRedone",
    ]


def test_branching_clears_redo_but_preserves_original_command_audit(studio, selected):
    first = edit(studio, selected, reject_from("Submitted"))
    undone = navigate(studio, first, "undo")
    original_events = snapshot(studio, undone["id"])[2]["events"]
    branch = edit(studio, undone, reject_from("Recommended"))
    history = studio.history(branch["id"])
    assert not history["redo"] and not branch["redo_transactions"]
    assert snapshot(studio, branch["id"])[2]["events"][:len(original_events)] == original_events
    assert history["events"][-1]["body"]["discarded_redo"] == [reject_from("Submitted").model_dump(mode="json")]
    before = snapshot(studio, branch["id"])
    with pytest.raises(DomainError) as error:
        navigate(studio, branch, "redo")
    assert error.value.code == "NOTHING_TO_REDO"
    assert snapshot(studio, branch["id"]) == before


def test_restart_preserves_pending_redo_and_chronology(studio, selected, open_studio):
    first = edit(studio, selected, reject_from("Submitted"))
    undone = navigate(studio, first, "undo")
    history = studio.history(undone["id"])
    reopened = open_studio(studio.store.directory)
    assert reopened.history(undone["id"]) == history
    restored = navigate(reopened, undone, "redo")
    assert restored["candidate"] == first["candidate"]
    body = reopened.history(restored["id"])["events"][-1]["body"]
    assert body["by"] == OWNER.id and body["time"]
    assert body["from_version"] == undone["version"] and body["to_version"] == restored["version"]


def test_undo_preserves_receipts_and_baseline_but_invalidates_decision(studio, selected):
    changed = edit(studio, selected, reject_from("Submitted"))
    verified = studio.verify(changed["id"], changed["version"])
    approved = approve(studio, verified)
    baseline = snapshot(studio, approved["id"])[1]
    undone = navigate(studio, approved, "undo")
    assert undone["stage"] == "PREVIEW" and undone["decision"] is None
    assert undone["receipts"] == approved["receipts"]
    assert undone["baseline"] == approved["baseline"] and undone["baseline_version"] == approved["baseline_version"]
    assert snapshot(studio, undone["id"])[1] == baseline
    audit = snapshot(studio, undone["id"])[2]["events"]
    invalidation = next(item["body"] for item in audit if item["kind"] == "DecisionInvalidated")
    assert invalidation["old_decision"] == approved["decision"] and invalidation["reason"] == "semantic undo"
    redone = navigate(studio, undone, "redo")
    assert redone["decision"] is None and redone["receipts"] == approved["receipts"]
    assert studio.view(redone["id"])["packet"]["eligible"]
    with pytest.raises(DomainError) as error:
        studio.apply(redone["id"], redone["version"], OWNER)
    assert error.value.code == "GATE_BLOCKED"
    assert "seal" not in json.dumps(studio.history(redone["id"])["events"])


def test_history_is_read_only_and_semantic_undo_keeps_layout(studio, selected):
    changed = edit(studio, selected, reject_from("Submitted"))
    positioned = studio.layout(changed["id"], changed["version"], LayoutChange(node="Submitted", x=450, y=90), OWNER)
    before = snapshot(studio, positioned["id"])
    history = studio.history(positioned["id"])
    assert history["scope"] == "semantic" and len(history["edits"]) == 1
    assert snapshot(studio, positioned["id"]) == before
    undone = navigate(studio, positioned, "undo")
    assert undone["layout"] == positioned["layout"] and undone["selected_by"] == selected["selected_by"]


def test_failed_audit_append_rolls_back_candidate_version_and_stacks(studio, selected, monkeypatch):
    case = edit(studio, selected, reject_from("Submitted"))
    before = snapshot(studio, case["id"])
    original_event = Session.event

    def fail_command_event(session, kind, body):
        if kind == "SemanticUndone":
            raise RuntimeError("synthetic audit write failure")
        original_event(session, kind, body)

    monkeypatch.setattr(Session, "event", fail_command_event)
    with pytest.raises(RuntimeError, match="synthetic audit write failure"):
        navigate(studio, case, "undo")
    assert snapshot(studio, case["id"]) == before


def test_redo_invalidates_current_decision_and_applied_cases_are_closed(studio, selected):
    case = navigate(studio, edit(studio, selected, reject_from("Submitted")), "undo")
    case = studio.verify(case["id"], case["version"])
    approved = approve(studio, case)
    redone = navigate(studio, approved, "redo")
    assert redone["decision"] is None and redone["receipts"] == approved["receipts"]
    audit = snapshot(studio, case["id"])[2]["events"]
    assert any(item["kind"] == "DecisionInvalidated" and item["body"]["reason"] == "semantic redo" for item in audit)
    undone = navigate(studio, redone, "undo")
    approved_again = approve(studio, undone)
    applied = studio.apply(approved_again["id"], approved_again["version"], OWNER)
    before = snapshot(studio, applied["id"])
    for operation in ("undo", "redo"):
        with pytest.raises(DomainError) as error:
            navigate(studio, applied, operation)
        assert error.value.code == "CASE_CLOSED"
    assert snapshot(studio, applied["id"]) == before
    assert not studio.history(applied["id"])["can_redo"]


@pytest.mark.parametrize("operation", ["undo", "redo"])
def test_agent_stale_and_closed_commands_do_not_mutate(studio, selected, operation):
    case = edit(studio, selected, reject_from("Submitted"))
    if operation == "redo":
        case = navigate(studio, case, "undo")
    before = snapshot(studio, case["id"])
    for principal, version, code in ((AGENT, case["version"], "AUTHORITY_REQUIRED"),
                                     (OWNER, case["version"] - 1, "STALE_VERSION")):
        with pytest.raises(DomainError) as error:
            getattr(studio, operation)(case["id"], version, principal)
        assert error.value.code == code
        assert snapshot(studio, case["id"]) == before
    case = studio.discard(case["id"], case["version"])
    before = snapshot(studio, case["id"])
    with pytest.raises(DomainError) as error:
        navigate(studio, case, operation)
    assert error.value.code == "CASE_CLOSED"
    assert snapshot(studio, case["id"]) == before
    history = studio.history(case["id"])
    assert not history["can_undo"] and not history["can_redo"]


def test_refused_edit_keeps_redo_and_all_audit(studio, selected):
    case = navigate(studio, edit(studio, selected, reject_from("Submitted")), "undo")
    before = snapshot(studio, case["id"])
    with pytest.raises(DomainError):
        edit(studio, case, SetRole(kind="set_role", transition="TR-APPROVE", role="Teacher"))
    assert snapshot(studio, case["id"]) == before
    assert studio.history(case["id"])["can_redo"]


@pytest.mark.parametrize("corruption", ["prefix", "candidate", "unsupported", "redo"])
def test_inconsistent_history_refuses_without_repair(studio, selected, corruption):
    case = edit(studio, selected, reject_from("Submitted"))
    damaged = copy.deepcopy(case)
    if corruption == "prefix":
        damaged["transactions"].pop(0)
    elif corruption == "candidate":
        damaged["candidate"] = selected["candidate"]
    elif corruption == "unsupported":
        damaged["selected_meaning"] = "final_approval"
    else:
        damaged["redo_transactions"] = [SetRole(kind="set_role", transition="TR-APPROVE", role="Teacher").model_dump(mode="json")]
    with studio.store.transaction() as u:
        u.save_case(damaged, case["version"])
    before = snapshot(studio, case["id"])
    for operation in ("undo", "redo"):
        with pytest.raises(DomainError) as error:
            navigate(studio, damaged, operation)
        assert error.value.code == "HISTORY_INCONSISTENT"
    with pytest.raises(DomainError):
        studio.history(case["id"])
    assert snapshot(studio, case["id"]) == before


def test_draft_has_no_semantic_history_and_commands_require_selection(studio):
    case = studio.create("Synthetic request")
    before = snapshot(studio, case["id"])
    history = studio.history(case["id"])
    assert history["status"] == "meaning_required" and history["selection"] is None
    for operation in ("undo", "redo"):
        with pytest.raises(DomainError) as error:
            navigate(studio, case, operation)
        assert error.value.code == "MEANING_REQUIRED"
    assert snapshot(studio, case["id"]) == before


def test_legacy_case_without_redo_field_can_reconstruct(studio, selected):
    legacy = copy.deepcopy(selected)
    legacy.pop("redo_transactions")
    with studio.store.transaction() as u:
        u.save_case(legacy, legacy["version"])
    history = studio.history(legacy["id"])
    assert history["selection"]["model"] == selected["candidate"] and history["events"] == []
    assert ChangeCase.model_validate(legacy).redo_transactions == ()


def test_removal_restores_exact_transition_and_renames_roundtrip_on_other_pack(tmp_path):
    pack = load_pack(PACKS_ROOT / "library-loan")
    studio = harness_studio(tmp_path / "loan", pack=pack)
    case = studio.create(pack.fixtures.demo_request)
    case = studio.propose(case["id"], case["version"])
    case = studio.select(case["id"], case["version"], "allow_renewal", OWNER)
    case = edit(studio, case, SetRole(kind="set_role", transition="TR-RENEW", role="Clerk"))
    transition = next(item for item in case["candidate"]["transitions"] if item["id"] == "TR-RENEW")
    case = edit(studio, case, SetGuards(kind="set_guards", transition="TR-RENEW", guards=tuple(reversed(transition["guards"]))))
    prior = case["candidate"]
    case = edit(studio, case, RemoveTransition(kind="remove_transition", transition="TR-RENEW"))
    case = navigate(studio, case, "undo")
    assert case["candidate"] == prior
    case = edit(studio, case, AddState(kind="add_state", state="Paused"))
    before_rename = case["candidate"]
    case = edit(studio, case, RenameState(kind="rename_state", state="Paused", to="OnHold"))
    renamed = case["candidate"]
    case = navigate(studio, case, "undo")
    assert case["candidate"] == before_rename
    case = navigate(studio, case, "redo")
    assert case["candidate"] == renamed


def test_empty_supported_meaning_still_protects_selection(selected):
    data = load_pack(PACKS_ROOT / "excursion").model_dump(mode="json")
    data["meanings"].append({"id": "keep_baseline", "label": "Keep baseline", "supported": True,
                             "consequences": ["No semantic change"], "transactions": []})
    pack = Pack.model_validate(data)
    case = ChangeCase.model_validate(selected | {"selected_meaning": "keep_baseline", "candidate": selected["baseline"],
                                               "transactions": [], "redo_transactions": []})
    history = replay(case, pack)
    assert history.initial_count == 0 and history.models == (case.baseline,)


def test_new_routes_keep_session_origin_contract_and_cas_guards(studio, selected):
    case = edit(studio, selected, reject_from("Submitted"))
    prefix = "/api/cases/" + case["id"]
    headers = {"Authorization": "Bearer history-test-token", "Origin": "http://127.0.0.1:8765"}
    before = snapshot(studio, case["id"])
    with TestClient(create_app(studio, "history-test-token"), base_url="http://127.0.0.1:8765") as http:
        assert http.get(prefix + "/history").status_code == 401
        assert http.get(prefix + "/history", headers=headers).json()["can_undo"]
        for operation in ("undo", "redo"):
            path = prefix + "/" + operation
            body = {"expected_version": case["version"]}
            assert http.post(path, json=body).status_code == 401
            assert http.post(path, json=body, headers=headers | {"Origin": "https://invalid.test"}).status_code == 403
            assert http.post(path, json=body | {"expected_version": True}, headers=headers).status_code == 422
            assert http.post(path, json=body | {"transaction": {}}, headers=headers).status_code == 422
            stale = http.post(path, json={"expected_version": case["version"] - 1}, headers=headers)
            assert stale.status_code == 409 and stale.json()["code"] == "STALE_VERSION"
        assert snapshot(studio, case["id"]) == before
        undone = http.post(prefix + "/undo", json={"expected_version": case["version"]}, headers=headers).json()
        restored = http.post(prefix + "/redo", json={"expected_version": undone["version"]}, headers=headers).json()
        assert restored["candidate"] == case["candidate"]


def test_committed_change_case_schema_includes_typed_redo():
    path = Path(__file__).resolve().parents[1] / "contracts" / "change-case.schema.json"
    assert json.loads(path.read_text(encoding="utf-8")) == ChangeCase.model_json_schema()
