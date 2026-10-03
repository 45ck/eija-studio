"""Synthetic adapter oracles: inspection preserves exact records and cannot confer evidence or authority."""
from __future__ import annotations

import copy
import json
import sqlite3

import pytest
from pydantic import ValidationError

from eija_studio.application.compiler import compile_case, subject_for
from eija_studio.application.formal import packet_view
from eija_studio.application.witness_inspection import InspectionContext, WitnessInspection
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.evidence import aggregate_formal
from eija_studio.domain.formal import Context
from eija_studio.domain.models import LayoutChange, OWNER, Workflow, canonical, fingerprint
from formal_support import golden, not_run_artifact, receipt_of


KIND = "bounded_model_check"


def row(view, kind=KIND):
    return next(item for item in view["packet"]["formal_evidence"] if item["kind"] == kind)


def receipt(studio, case, artifact, kind=KIND, **overrides):
    subject = subject_for(Workflow.model_validate(case["candidate"]), case["layout"], studio.identity_provider())
    return studio.signer.seal(receipt_of(kind, artifact, subject, **overrides))


def stored_case(studio, case, receipts):
    """Install explicitly synthetic sealed fixtures; never run an owner approval or live verifier."""
    body = copy.deepcopy(case) | {"receipts": receipts}
    with studio.store.transaction() as unit:
        unit.db.execute("UPDATE cases SET body=? WHERE id=?", (json.dumps(body), case["id"]))
    return body


def database(studio):
    with studio.store.connection() as connection:
        return tuple(connection.iterdump())


def failed_bmc():
    artifact = golden("bmc")
    slot = "candidate-reject-from-Recommended"
    artifact["counterexamples"][slot] = [{"invariant": "AUTHORITY-ON-COMMIT", "detail": "synthetic revoked actor committed",
                                        "length": 2, "trace": ["revoke teacher", "teacher Recommend"]}]
    return artifact


def test_view_inspects_exact_failed_record_without_writes_or_verdict_changes(studio, selected, monkeypatch):
    artifact = failed_bmc()
    sealed = receipt(studio, selected, artifact)
    stored = stored_case(studio, selected, [sealed])
    before = database(studio)
    attempts = []
    connect = studio.store._connect

    def readonly():
        connection = connect()

        def authorize(operation, argument, _second, _database, _trigger):
            if operation in {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE}:
                attempts.append((operation, argument))
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        connection.set_authorizer(authorize)
        return connection

    monkeypatch.setattr(studio.store, "_connect", readonly)
    view = studio.view(selected["id"])
    entry, packet = row(view), view["packet"]
    inspect = entry["inspection"]
    assert entry["status"] == inspect["status"] == "FAIL"
    assert "FORMAL_EVIDENCE_FAIL:bounded_model_check" in packet["blockers"]
    assert inspect["reasons"] == entry["reasons"]
    assert inspect["availability"] == "available" and inspect["availability_reasons"] == []
    assert json.loads(inspect["artifact_json"]) == artifact
    assert inspect["review"] == {
        "case_id": selected["id"], "case_version": selected["version"], "scope": "local-demo",
        "subject_json": canonical(packet["subject"]), "subject_hash": packet["subject_hash"],
        "candidate_semantic_hash": Workflow.model_validate(selected["candidate"]).semantic_hash,
        "pack_id": studio.pack.id, "pack_digest": studio.pack.digest,
    }
    assert inspect["receipt"] == {"id": sealed["id"], "subject_json": canonical(sealed["subject"]),
        "artifact_hash": sealed["artifact_hash"], "producer": sealed["producer"], "method": sealed["method"],
        "subject_matches_review": True}
    witness = inspect["records"][0]
    assert witness["artifact_path"] == "/counterexamples/candidate-reject-from-Recommended/0"
    assert witness["origin"] == "counterexample" and witness["invariant"] == "AUTHORITY-ON-COMMIT"
    assert [step["text"] for step in witness["steps"]] == ["revoke teacher", "teacher Recommend"]
    assert witness["model"]["availability"] == "not_provided"
    assert witness["model"]["supplied_semantic_hash"] == packet["subject"]["semantic"]
    assert witness["navigation"]["current_model"] is witness["navigation"]["source"] is None
    assert "seal" not in inspect["receipt"]
    assert view["case"] == stored and not attempts and database(studio) == before
    assert studio.view(selected["id"]) == view


def test_deciding_failure_not_newest_receipt_drives_inspection_even_with_duplicate_id(studio, selected):
    fail = receipt(studio, selected, failed_bmc(), id="same-id")
    passing = receipt(studio, selected, golden("bmc"), id="same-id")
    stored_case(studio, selected, [fail, passing])
    entry = row(studio.view(selected["id"]))
    assert entry["status"] == entry["inspection"]["status"] == "CONFLICT"
    assert entry["inspection"]["receipt"]["artifact_hash"] == fail["artifact_hash"] != passing["artifact_hash"]
    assert json.loads(entry["inspection"]["artifact_json"]) == fail["artifact"]


@pytest.mark.parametrize("mode,expected", [("absent", "NO_DECIDING_RECEIPT"),
                                         ("not-run", "INTACT_ARTIFACT_UNAVAILABLE"),
                                         ("tampered", "INTACT_ARTIFACT_UNAVAILABLE"),
                                         ("protocol", "INTACT_ARTIFACT_UNAVAILABLE")])
def test_missing_or_untrusted_artifact_has_no_fabricated_witness(studio, selected, mode, expected):
    artifact = not_run_artifact(KIND).artifact if mode == "not-run" else golden("bmc")
    if mode == "protocol":
        artifact["protocol"] += "-unrecognised"
    sealed = receipt(studio, selected, artifact)
    if mode == "tampered":
        sealed["artifact"]["counterexamples"]["baseline"] = [{"trace": ["forged"]}]
    stored_case(studio, selected, [] if mode == "absent" else [sealed])
    entry = row(studio.view(selected["id"]))
    inspect = entry["inspection"]
    assert inspect["availability"] == "unavailable" and expected in inspect["availability_reasons"]
    assert inspect["artifact_json"] is inspect["receipt"] is None
    assert inspect["records"] == [] and inspect["record_count"] == 0
    assert inspect["status"] == entry["status"] and inspect["reasons"] == entry["reasons"]


def test_authentic_unknown_retains_diagnostics_without_becoming_a_pass(studio, selected):
    artifact = golden("bmc")
    artifact["bounds"]["depth"] = 1
    sealed = receipt(studio, selected, artifact)
    stored_case(studio, selected, [sealed])
    entry = row(studio.view(selected["id"]))
    inspect = entry["inspection"]
    assert entry["status"] == inspect["status"] == "UNKNOWN"
    assert inspect["availability"] == "available"
    assert json.loads(inspect["artifact_json"])["bounds"]["depth"] == 1
    assert all(record["origin"] == "negative_control" for record in inspect["records"])
    assert all(record["steps"] == [] for record in inspect["records"])
    assert "bounds" not in entry  # the existing admitted-details gate remains unchanged


def test_old_receipt_and_witness_model_remain_distinct_from_current_review(studio, selected):
    artifact = failed_bmc()
    artifact["models"]["candidate-reject-from-Recommended"]["semantic_hash"] = "2" * 64
    old_subject = {"semantic": "1" * 64, "presentation": "old-layout"}
    sealed = receipt(studio, selected, artifact, subject=old_subject)
    stored_case(studio, selected, [sealed])
    inspect = row(studio.view(selected["id"]))["inspection"]
    assert inspect["status"] == "STALE" and inspect["availability"] == "available"
    assert json.loads(inspect["receipt"]["subject_json"]) == old_subject
    assert not inspect["receipt"]["subject_matches_review"]
    assert inspect["review"]["candidate_semantic_hash"] not in {"1" * 64, "2" * 64}
    assert inspect["records"][0]["model"]["supplied_semantic_hash"] == "2" * 64
    assert inspect["records"][0]["navigation"]["current_model"] is None


@pytest.mark.parametrize("invalid", [False, True])
def test_smt_actual_specimen_is_validated_without_repair_or_borrowing_subject_identity(studio, selected, invalid):
    artifact = golden("smt")
    specimen = copy.deepcopy(selected["candidate"])
    if invalid:
        specimen["transitions"][0]["guards"] = []
    artifact["invariants"][0] |= {"status": "refuted", "counterexample": {
        "candidate": specimen, "passes_pydantic_validators": not invalid, "real_check_policy": []}}
    sealed = receipt(studio, selected, artifact, kind="smt_proof")
    stored_case(studio, selected, [sealed])
    inspect = row(studio.view(selected["id"]), "smt_proof")["inspection"]
    actual, *controls = inspect["records"]
    assert actual["origin"] == "counterexample" and actual["artifact_path"] == "/invariants/0"
    assert json.loads(actual["model"]["raw_json"]) == specimen
    assert actual["model"]["supplied_semantic_hash"] is None
    assert all(item["origin"] == "negative_control" and item["model"]["availability"] == "not_provided"
               for item in controls)
    if invalid:
        assert actual["model"]["availability"] == "raw_invalid"
        assert actual["model"]["workflow"] is actual["model"]["computed_semantic_hash"] is None
        assert any("Mandatory guards" in error for error in actual["model"]["validation_errors"])
    else:
        assert actual["model"]["availability"] == "valid_workflow"
        assert actual["model"]["workflow"] == specimen
        assert actual["model"]["computed_semantic_hash"] == Workflow.model_validate(specimen).semantic_hash
    assert all(item["navigation"]["current_model"] is item["navigation"]["source"] is None
               for item in inspect["records"])


def test_all_bmc_slots_and_indices_survive_without_truncation_or_action_inference(studio, selected):
    artifact = failed_bmc()
    raw = artifact["counterexamples"]["candidate-reject-from-Recommended"][0]
    artifact["counterexamples"] = {"same/~slot": [raw] * 7, "other": [raw]}
    artifact["models"]["same/~slot"] = {"semantic_hash": "a" * 64}
    artifact["models"]["other"] = {"semantic_hash": "b" * 64}
    stored_case(studio, selected, [receipt(studio, selected, artifact)])
    inspect = row(studio.view(selected["id"]))["inspection"]
    witnesses = [record for record in inspect["records"] if record["origin"] == "counterexample"]
    assert len(witnesses) == 8
    assert {record["artifact_path"] for record in witnesses} == {
        "/counterexamples/other/0", *(f"/counterexamples/same~1~0slot/{i}" for i in range(7))}
    assert {record["model"]["supplied_semantic_hash"] for record in witnesses} == {"a" * 64, "b" * 64}
    assert all(record["model"]["workflow"] is None and record["navigation"]["current_model"] is None
               for record in witnesses)
    assert inspect["record_count"] == len(inspect["records"])


@pytest.mark.parametrize("malformed", [
    {"id": 17, "status": "refuted", "counterexample": []},
    {"id": 17, "status": "proved"},
    {"id": "", "status": "proved"},
    {"id": "INV-TEACHER-NOT-DECIDER", "status": {"claimed": "proved"}},
    {"id": "INV-TEACHER-NOT-DECIDER", "status": "invented"},
    "not an invariant object",
])
def test_malformed_smt_invariant_cannot_be_a_counterexample_or_hidden_as_proved(studio, selected, malformed):
    artifact = golden("smt")
    artifact["invariants"][0] = malformed
    stored_case(studio, selected, [receipt(studio, selected, artifact, kind="smt_proof")])
    entry = row(studio.view(selected["id"]), "smt_proof")
    inspect = entry["inspection"]
    record = next(item for item in inspect["records"] if item["artifact_path"] == "/invariants/0")
    assert record["origin"] == "diagnostic" and json.loads(record["raw_json"]) == malformed
    assert record["model"]["availability"] == "not_provided" and record["steps"] == []
    assert any("MALFORMED_INVARIANT_RECORD: /invariants/0" in note for note in inspect["projection_reasons"])
    assert entry["status"] == inspect["status"] == "FAIL"
    assert entry["reasons"] == inspect["reasons"]
    assert json.loads(inspect["artifact_json"]) == artifact


@pytest.mark.parametrize("counterexample", [None, [], {}, {"candidate": None}])
def test_smt_refutation_without_a_specimen_remains_diagnostic(studio, selected, counterexample):
    artifact = golden("smt")
    artifact["invariants"][0] |= {"status": "refuted", "counterexample": counterexample}
    stored_case(studio, selected, [receipt(studio, selected, artifact, kind="smt_proof")])
    inspect = row(studio.view(selected["id"]), "smt_proof")["inspection"]
    record = next(item for item in inspect["records"] if item["artifact_path"] == "/invariants/0")
    assert record["origin"] == "diagnostic" and record["model"]["availability"] == "not_provided"
    assert json.loads(record["raw_json"])["counterexample"] == counterexample
    assert any("RECORDED_SPECIMEN_UNAVAILABLE: /invariants/0" in note for note in inspect["projection_reasons"])
    assert inspect["status"] == "FAIL"


@pytest.mark.parametrize("artifact", [
    {"protocol": "eija.formal.bounded-model-check/v1", "counterexamples": ["wrong-container"]},
    {"protocol": "eija.formal.bounded-model-check/v1", "counterexamples": {"x": [None, "not-an-object"]}},
])
def test_intact_malformed_nested_data_preserves_raw_failure_without_crashing_packet(studio, selected, artifact):
    stored_case(studio, selected, [receipt(studio, selected, artifact)])
    entry = row(studio.view(selected["id"]))
    assert entry["status"] == "FAIL" and entry["inspection"]["availability"] == "available"
    assert json.loads(entry["inspection"]["artifact_json"]) == artifact
    assert entry["inspection"]["reasons"] == entry["reasons"]
    assert entry["inspection"]["projection_reasons"]
    assert all(record["origin"] == "diagnostic" and record["model"]["supplied_semantic_hash"] is None
               for record in entry["inspection"]["records"])


def test_partly_malformed_collection_is_visible_beside_valid_witness(studio, selected):
    artifact = failed_bmc()
    artifact["counterexamples"]["malformed-slot"] = {"invariant": "wrong container"}
    stored_case(studio, selected, [receipt(studio, selected, artifact)])
    inspect = row(studio.view(selected["id"]))["inspection"]
    assert any(record["origin"] == "counterexample" for record in inspect["records"])
    assert any("/counterexamples/malformed-slot" in reason for reason in inspect["projection_reasons"])
    assert json.loads(inspect["artifact_json"])["counterexamples"]["malformed-slot"] == {"invariant": "wrong container"}


@pytest.mark.parametrize("mode", ["PASS", "FAIL", "CONFLICT", "STALE", "UNKNOWN", "NOT_RUN"])
def test_inspection_does_not_change_existing_deciding_receipt_or_status_serialization(studio, selected, mode):
    artifact = failed_bmc() if mode in {"FAIL", "CONFLICT"} else golden("bmc")
    if mode == "UNKNOWN":
        artifact["bounds"]["depth"] = 1
    if mode == "NOT_RUN":
        artifact = not_run_artifact(KIND).artifact
    first = receipt(studio, selected, artifact)
    if mode == "STALE":
        first = receipt(studio, selected, artifact, subject=first["subject"] | {"implementation": "old"})
    receipts = [first]
    if mode == "CONFLICT":
        receipts.append(receipt(studio, selected, golden("bmc"), id="newer-pass"))
    stored_case(studio, selected, receipts)
    current = subject_for(Workflow.model_validate(selected["candidate"]), selected["layout"], studio.identity_provider())
    kernel = aggregate_formal(KIND, receipts, current, studio.signer.authentic, Context(current["semantic"]))
    entry = row(studio.view(selected["id"]))
    assert kernel.status == mode
    assert {key: entry[key] for key in ("status", "receipt_id", "reasons", "receipts")} == {
        "status": kernel.status, "receipt_id": kernel.receipt["id"],
        "reasons": list(kernel.reasons), "receipts": kernel.receipts}
    assert entry["inspection"]["status"] == kernel.status
    assert entry["inspection"]["reasons"] == list(kernel.reasons)


def test_bend_control_does_not_borrow_positive_model_identity_or_invent_trace(studio, selected):
    model_hash = Workflow.model_validate(selected["candidate"]).semantic_hash
    artifact = {"protocol": "eija.formal.bend-proof/v1", "model": {"semantic_hash": {"Candidate": model_hash}},
        "proof": {"laws": [{"name": "law-failed", "result": "FAILED"}]},
        "negative_controls": [{"name": "unsafe", "counterexample": {"steps": ["Approve"]}},
                              {"name": "effect", "effect_probe": {"step": "Pay", "emitted": ["PaymentCaptured"]}}]}
    stored_case(studio, selected, [receipt(studio, selected, artifact, kind="bend_proof")])
    records = row(studio.view(selected["id"]), "bend_proof")["inspection"]["records"]
    assert [item["origin"] for item in records] == ["diagnostic", "negative_control", "negative_control"]
    assert all(item["model"]["supplied_semantic_hash"] is None for item in records)
    assert records[1]["steps"][0]["text"] == "Approve" and records[2]["steps"] == []
    assert json.loads(records[2]["raw_json"])["effect_probe"]["step"] == "Pay"


def test_layout_revision_is_captured_but_does_not_change_formal_verdict_or_original_receipt(studio, selected):
    sealed = receipt(studio, selected, golden("bmc"))
    stored_case(studio, selected, [sealed])
    before = row(studio.view(selected["id"]))["inspection"]
    moved = studio.layout(selected["id"], selected["version"], LayoutChange(node="Submitted", x=8, y=10), OWNER)
    after = row(studio.view(selected["id"]))["inspection"]
    assert before["status"] == after["status"] == "PASS"
    assert after["review"]["case_version"] == moved["version"] != before["review"]["case_version"]
    assert after["review"]["subject_hash"] != before["review"]["subject_hash"]
    assert after["receipt"]["subject_json"] == before["receipt"]["subject_json"]
    assert not after["receipt"]["subject_matches_review"]


def test_contextless_packet_preserves_existing_verdict_and_explicitly_disables_inspection(studio, selected):
    sealed = receipt(studio, selected, golden("bmc"))
    result = packet_view([sealed], sealed["subject"], studio.signer.authentic,
                         Context(sealed["subject"]["semantic"]), [], studio.pack)
    entry = next(item for item in result["evidence"] if item["kind"] == KIND)
    assert entry["status"] == "PASS"
    assert entry["inspection"]["availability"] == "unavailable"
    assert entry["inspection"]["availability_reasons"] == ["REVIEW_CONTEXT_UNAVAILABLE"]
    assert entry["inspection"]["review"]["case_id"] is None


def test_typed_projection_is_immutable_and_detached_from_raw_receipt(studio, selected):
    artifact = failed_bmc()
    sealed = receipt(studio, selected, artifact)
    case = ChangeCase.model_validate(selected | {"receipts": [sealed]})
    packet = compile_case(case, studio.identity_provider(), studio.signer.authentic, case.baseline_version)
    inspect = WitnessInspection.model_validate(next(item for item in packet["formal_evidence"] if item["kind"] == KIND)["inspection"])
    before = inspect.model_dump_json()
    artifact["counterexamples"] = {}
    sealed["subject"]["semantic"] = "changed"
    assert inspect.model_dump_json() == before
    with pytest.raises(ValidationError, match="frozen"):
        inspect.status = "PASS"
    with pytest.raises(ValidationError, match="frozen"):
        inspect.records[0].model.slot = "other"
    assert fingerprint(json.loads(inspect.artifact_json)) == inspect.receipt.artifact_hash
    assert InspectionContext(case_id="case", case_version=1, scope="scope").case_version == 1
