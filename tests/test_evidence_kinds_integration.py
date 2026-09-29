"""Formal evidence through the adapters, the service, the review packet, the CLI and the Studio page (ADR-0145, ADR-0146)."""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess

import pytest
from eija_studio.adapters.formal import FormalReports
from eija_studio.application.compiler import compile_case, subject_for
from eija_studio.application.formal import what_if_model
from eija_studio.bootstrap import build_studio
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.evidence_kinds import KINDS
from eija_studio.domain.formal_smt import SOURCES as SMT_SOURCES
from eija_studio.domain.models import OWNER, DomainError, LayoutChange, SemanticTransaction, Workflow, fingerprint
from eija_studio.domain.policy import check_policy
from eija_studio.interfaces.cli import main as cli_main

from conftest import approve, harness_identity
from formal_support import (
    KIND_NAMES, ROOT, artifacts, attached, collect_all, leaves, make_checkout, not_run_artifact,
    receipt_of, smt_report, stub_all, with_change, workflows,
)

BASE, CANDIDATE = workflows()
ARTS = artifacts(BASE, CANDIDATE)
UNSAFE = ROOT / "examples" / "unsafe-teacher-final-approval.json"


def claims(studio, case):
    return studio.view(case["id"])["packet"]["technical_claims"]


def broken_bend():
    return with_change(ARTS["bend_proof"], ("proof", "laws", 0, "result"), "FAILED")


def unknown_bend():
    return with_change(ARTS["bend_proof"], ("negative_controls",), [])


# ------------------------------------------------------------------ the service attaches sealed receipts; the packet shows each claim

def test_verify_seals_formal_receipts_and_the_packet_lists_every_kind(studio, selected):
    studio.formal = stub_all(BASE, CANDIDATE)
    case = studio.verify(selected["id"], selected["version"])
    assert [r["kind"] for r in case["receipts"]] == ["integration_test", *KIND_NAMES]
    assert all(studio.signer.authentic(r) for r in case["receipts"])
    packet = studio.view(case["id"])["packet"]
    assert packet["eligible"] and packet["technical_claims"]["runtime_matrix"] == "PASS"
    assert {k: v for k, v in packet["technical_claims"].items() if k.startswith("formal_")} == {
        "formal_bend_proof": "PASS", "formal_smt_proof": "PASS", "formal_bounded_model_check": "PASS"}
    by_kind = {e["kind"]: e for e in packet["formal_evidence"]}
    assert set(by_kind) == set(KIND_NAMES)
    for kind, entry in by_kind.items():
        assert entry["does_not_establish"] and entry["assumptions"] and entry["bounds"] and entry["tool"]
        assert entry["evidence_level"] == "sealed_tool_verdict" and entry["receipt_id"]
        assert entry["establishes"] == KINDS[kind].establishes
    assert by_kind["bounded_model_check"]["bounds"]["depth"] >= 6
    assert {a["kind"]: a["status"] for a in packet["receipt_applicability"]}["bend_proof"] == "PASS"


def test_without_a_formal_source_the_kinds_stay_unknown_and_never_green(studio, verified):
    assert [r["kind"] for r in verified["receipts"]] == ["integration_test"]
    packet = studio.view(verified["id"])["packet"]
    assert {e["kind"]: e["status"] for e in packet["formal_evidence"]} == dict.fromkeys(KIND_NAMES, "UNKNOWN")
    assert packet["eligible"]  # UNKNOWN is visible, never blocking, never rounded up
    assert "no receipt" in packet["formal_evidence"][0]["reasons"][0]


def test_a_formal_fail_blocks_technical_eligibility_and_approval(studio, selected):
    studio.formal = stub_all(BASE, CANDIDATE, bend_proof=broken_bend())
    case = studio.verify(selected["id"], selected["version"])
    packet = studio.view(case["id"])["packet"]
    assert "FORMAL_EVIDENCE_FAIL:bend_proof" in packet["blockers"] and not packet["eligible"]
    assert packet["technical_claims"]["formal_bend_proof"] == "FAIL" and packet["technical_claims"]["runtime_matrix"] == "PASS"
    with pytest.raises(DomainError) as blocked:
        approve(studio, case)
    assert blocked.value.code == "GATE_BLOCKED" and "FORMAL_EVIDENCE_FAIL:bend_proof" in blocked.value.message


@pytest.mark.parametrize("label,replacement", [
    ("UNKNOWN", {"bend_proof": unknown_bend()}),
    ("NOT_RUN", {"bend_proof": not_run_artifact("bend_proof").artifact}),
])
def test_unknown_and_not_run_never_block_but_are_always_visible(studio, selected, label, replacement):
    studio.formal = stub_all(BASE, CANDIDATE, **replacement)
    case = studio.verify(selected["id"], selected["version"])
    packet = studio.view(case["id"])["packet"]
    assert packet["eligible"] and packet["blockers"] == []
    assert packet["technical_claims"]["formal_bend_proof"] == label
    entry = next(e for e in packet["formal_evidence"] if e["kind"] == "bend_proof")
    assert entry["status"] == label and entry["reasons"] and "assumptions" not in entry  # nothing carried is shown as admitted
    approve(studio, case)  # and the owner can still decide, with the UNKNOWN in front of them


def test_a_formal_conflict_between_two_authentic_receipts_blocks(studio, selected):
    studio.formal = stub_all(BASE, CANDIDATE)
    case = studio.verify(selected["id"], selected["version"])
    studio.formal = stub_all(BASE, CANDIDATE, bend_proof=broken_bend())
    case = studio.verify(case["id"], case["version"])
    packet = studio.view(case["id"])["packet"]
    assert packet["technical_claims"]["formal_bend_proof"] == "CONFLICT" and "FORMAL_EVIDENCE_CONFLICT:bend_proof" in packet["blockers"]


def test_repeating_verify_does_not_pile_up_identical_formal_receipts(studio, selected):
    studio.formal = stub_all(BASE, CANDIDATE)
    first = studio.verify(selected["id"], selected["version"])
    second = studio.verify(first["id"], first["version"])
    assert [r["kind"] for r in second["receipts"]].count("integration_test") == 2
    assert [r["kind"] for r in second["receipts"]].count("bend_proof") == 1


def test_a_layout_move_keeps_formal_evidence_but_a_semantic_edit_makes_the_model_bound_kinds_stale(studio, selected):
    studio.formal = stub_all(BASE, CANDIDATE)
    case = studio.verify(selected["id"], selected["version"])
    moved = studio.layout(case["id"], case["version"], LayoutChange(node="Submitted", x=5, y=6), OWNER)
    assert claims(studio, moved)["formal_bend_proof"] == "PASS"
    edited = studio.edit(moved["id"], moved["version"], SemanticTransaction(kind="set_rejection_source", rejection_source="Submitted"), OWNER)
    now = claims(studio, edited)
    # The semantic subject dimension moved, so every receipt made for the old candidate is STALE, whatever it proved.
    assert {k: v for k, v in now.items() if k.startswith("formal_")} == dict.fromkeys(
        ("formal_bend_proof", "formal_smt_proof", "formal_bounded_model_check"), "STALE")


def test_tampering_a_stored_formal_artifact_is_fail_and_blocks(studio, selected):
    studio.formal = stub_all(BASE, CANDIDATE)
    case = studio.verify(selected["id"], selected["version"])
    doc = copy.deepcopy(case)
    receipt = next(r for r in doc["receipts"] if r["kind"] == "smt_proof")
    receipt["artifact"]["invariants"][0]["status"] = "refuted"  # sealed bytes changed, seal and hash not updated
    tampered = ChangeCase.model_validate(doc)
    packet = compile_case(tampered, studio.identity_provider(), studio.signer.authentic, tampered.baseline_version)
    assert packet["technical_claims"]["formal_smt_proof"] == "FAIL" and not packet["eligible"]


# ------------------------------------------------------------------ the adapters: prerequisites, NOT_RUN, determinism

def test_a_missing_checkout_or_missing_reports_is_not_run_for_every_kind(tmp_path):
    for root in (tmp_path / "no-verification-dir", make_checkout(tmp_path / "x", smt=False, bmc=False, bend_snapshot=False)):
        root.mkdir(parents=True, exist_ok=True)
        items = collect_all(root, BASE, CANDIDATE)
        assert sorted(i.kind for i in items) == sorted(KIND_NAMES)
        assert all(set(i.artifact) == {"protocol", "not_run"} and i.artifact["not_run"]["reason"] for i in items)


def test_the_real_checkout_attaches_bend_and_reports_the_rest_as_not_run_or_evidence(tmp_path):
    items = collect_all(make_checkout(tmp_path, smt=False, bmc=False), BASE, CANDIDATE)
    by_kind = {i.kind: i for i in items}
    assert "not_run" not in by_kind["bend_proof"].artifact and "not_run" in by_kind["smt_proof"].artifact
    assert "not_run" in by_kind["bounded_model_check"].artifact and "z3" in by_kind["smt_proof"].artifact["not_run"]["reason"]


def _case_with(studio, receipts, candidate=None):
    base, cand = workflows()
    return ChangeCase(id="c1", version=0, stage="PREVIEW", request="synthetic", baseline_version=0, baseline=base,
                      candidate=candidate or cand, proposal=None, provider_run=None, selected_meaning="recommend_only",
                      selected_by="local-owner", transactions=(SemanticTransaction(kind="enable_recommendation"),), layout={},
                      receipts=tuple(receipts), decision=None, created_at="2026-01-01T00:00:00+00:00")


def _statuses(root, studio, candidate=CANDIDATE):
    identity = harness_identity()
    subject = subject_for(candidate, {}, identity)
    receipts = attached(collect_all(root, BASE, candidate), subject, studio.signer)
    packet = compile_case(_case_with(studio, receipts, candidate), identity, studio.signer.authentic, 0)
    return {e["kind"]: e["status"] for e in packet["formal_evidence"]}, packet


def test_a_complete_checkout_is_pass_and_each_change_makes_exactly_its_kind_stale(tmp_path, studio):
    root = make_checkout(tmp_path)
    statuses, packet = _statuses(root, studio)
    assert statuses == dict.fromkeys(KIND_NAMES, "PASS") and "FORMAL_EVIDENCE_PASS" not in packet["blockers"]
    (root / "verification" / "bend" / "LAWS.bend").write_bytes((root / "verification" / "bend" / "LAWS.bend").read_bytes() + b"\n# weakened\n")
    assert _statuses(root, studio)[0] == {"bend_proof": "STALE", "smt_proof": "PASS", "bounded_model_check": "PASS"}
    policy = root / "src" / "eija_studio" / "domain" / "policy.py"
    policy.write_bytes(policy.read_bytes() + b"\n# edited\n")
    assert _statuses(root, studio)[0] == {"bend_proof": "STALE", "smt_proof": "STALE", "bounded_model_check": "STALE"}


def test_a_checkout_with_a_different_line_ending_gives_byte_identical_artifacts(tmp_path):
    lf = make_checkout(tmp_path / "lf")
    crlf = make_checkout(tmp_path / "crlf")
    for path in [*(crlf / "verification" / "bend").glob("*.bend"), crlf / "verification" / "bend" / "bend_generate.py",
                 *(crlf / "src").rglob("*.py")]:
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    a = {i.kind: fingerprint(i.artifact) for i in collect_all(lf, BASE, CANDIDATE)}
    b = {i.kind: fingerprint(i.artifact) for i in collect_all(crlf, BASE, CANDIDATE)}
    assert a == b and len(a) == 3


def test_artifacts_are_deterministic_and_free_of_measurements(tmp_path):
    root = make_checkout(tmp_path)
    first = collect_all(root, BASE, CANDIDATE)
    report = json.loads((root / "reports" / "formal" / "smt.json").read_text(encoding="utf-8"))
    report["measurements"] = {"seconds_total": 999.0, "platform": "another-os", "python": "3.99"}
    (root / "reports" / "formal" / "smt.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    second = collect_all(root, BASE, CANDIDATE)
    assert [fingerprint(i.artifact) for i in first] == [fingerprint(i.artifact) for i in second]
    assert next(i for i in second if i.kind == "smt_proof").measurements["platform"] == "another-os"  # recorded beside, never hashed
    banned = {"created_at", "timestamp", "seconds", "seconds_total", "platform", "python", "measurements", "elapsed_seconds"}
    for item in second:
        assert not banned & {str(p[-1]) for p in leaves(item.artifact) if isinstance(p[-1], str)}
        assert "measurements" not in item.artifact


@pytest.mark.parametrize("damage", ["not json", "[1, 2]", '{"kind": "smt_proof", "schema": "eija.formal-report/v1"}',
                                    '{"kind": "smt_proof", "schema": "some-other-schema"}'])
def test_an_unreadable_or_unrecognised_report_is_not_run_not_a_crash_and_not_a_pass(tmp_path, damage):
    root = make_checkout(tmp_path)
    (root / "reports" / "formal" / "smt.json").write_text(damage, encoding="utf-8")
    item = next(i for i in collect_all(root, BASE, CANDIDATE) if i.kind == "smt_proof")
    assert set(item.artifact) == {"protocol", "not_run"}


def test_a_runner_that_reports_not_run_does_not_hide_the_committed_snapshot(tmp_path, studio):
    root = make_checkout(tmp_path)
    (root / "reports" / "formal" / "bend.json").write_text(
        json.dumps({"kind": "bend_proof", "status": "NOT_RUN", "reason": "docker daemon is not running"}), encoding="utf-8")
    items = [i for i in collect_all(root, BASE, CANDIDATE) if i.kind == "bend_proof"]
    assert [("not_run" in i.artifact) for i in items] == [True, False]
    assert "docker daemon is not running" in items[0].artifact["not_run"]["reason"]
    assert _statuses(root, studio)[0]["bend_proof"] == "PASS"  # NOT_RUN never beats the PASS of the snapshot, and is not silently dropped


def test_a_fresh_failing_report_conflicts_with_the_committed_pass(tmp_path, studio):
    root = make_checkout(tmp_path)
    report = json.loads((root / "verification" / "bend" / "evidence" / "bend.json").read_text(encoding="utf-8"))
    report["proof"]["laws"][0]["result"] = "FAILED"
    (root / "reports" / "formal" / "bend.json").write_text(json.dumps(report), encoding="utf-8")
    statuses, packet = _statuses(root, studio)
    assert statuses["bend_proof"] == "CONFLICT" and "FORMAL_EVIDENCE_CONFLICT:bend_proof" in packet["blockers"]


def test_an_extractor_copies_labels_but_the_kernel_recomputes(tmp_path, studio):
    root = make_checkout(tmp_path)
    report = json.loads((root / "reports" / "formal" / "smt.json").read_text(encoding="utf-8"))
    report["results"]["invariants"][0]["status"] = "refuted"
    (root / "reports" / "formal" / "smt.json").write_text(json.dumps(report), encoding="utf-8")
    assert report["verdict"] == "PASS"  # the report's own label still claims PASS
    assert _statuses(root, studio)[0]["smt_proof"] == "FAIL"


def test_the_source_named_by_the_report_is_compared_with_the_source_now(tmp_path):
    root = make_checkout(tmp_path)
    report = smt_report({"domain/policy.py": "0" * 64, "domain/models.py": "1" * 64})
    (root / "reports" / "formal" / "smt.json").write_text(json.dumps(report), encoding="utf-8")
    item = next(i for i in collect_all(root, BASE, CANDIDATE) if i.kind == "smt_proof")
    binding = item.artifact["binding"]
    assert binding["reported_sources_sha256_lf"] != binding["current_sources_sha256_lf"]
    assert set(binding["current_sources_sha256_lf"]) == set(SMT_SOURCES)


# ------------------------------------------------------------------ the unsafe teacher-approval scenario, end to end

def unsafe_workflow():
    return Workflow.model_validate_json(UNSAFE.read_text(encoding="utf-8"))


def test_unsafe_teacher_approval_is_stopped_by_policy_and_the_negative_control_counterexample_explains_it(studio):
    unsafe = unsafe_workflow()
    assert check_policy(unsafe) == ["PROTECTED_AUTHORITY:Approve"]
    # 1. through the front door the meaning is refused, never downgraded
    case = studio.create("Let teachers sign off excursions.")
    case = studio.propose(case["id"], case["version"])
    with pytest.raises(DomainError) as refused:
        studio.select(case["id"], case["version"], "final_approval", OWNER)
    assert refused.value.code == "MEANING_UNSUPPORTED"
    # 2. a candidate that reached the case some other way (a hand edit or an agent's proposal) is blocked by policy
    studio.formal = FormalReports()
    receipts = attached(FormalReports().collect(BASE, unsafe), subject_for(unsafe, {}, harness_identity()), studio.signer)
    packet = compile_case(_case_with(studio, receipts, unsafe), harness_identity(), studio.signer.authentic, 0)
    assert not packet["eligible"] and "POLICY_BLOCKED" in packet["blockers"] and packet["policy_errors"] == ["PROTECTED_AUTHORITY:Approve"]
    # 3. the Bend proof is about the shipped candidate, so it is honestly STALE for this model (not a pass, not a fail) ...
    assert packet["technical_claims"]["formal_bend_proof"] == "STALE"
    # 4. ... and the seeded negative control for exactly this fault is attached as the explanation, with its trace
    bend = next(x for x in packet["explanations"] if x["source"] == "bend_proof negative control")
    assert bend["control"] == "teacher_final_approval" and bend["policy_findings"] == ["PROTECTED_AUTHORITY:Approve"]
    assert bend["trace"] == [["teacher-assigned", "Submit"], ["teacher-assigned", "Recommend"], ["teacher-assigned", "Approve"]]
    assert bend["final_state"] == "Approved" and set(bend["laws_that_fail"]) == {"teacher_never_approves", "teacher_sequences_never_approve"}
    assert bend["positive_proof"] == "STALE" and "seeded" in bend["note"]


def test_unsafe_scenario_through_the_stored_case_and_the_owner_gate(studio):
    unsafe = unsafe_workflow()
    studio.formal = FormalReports()
    receipts = attached(FormalReports().collect(BASE, unsafe), subject_for(unsafe, {}, harness_identity()), studio.signer)
    body = _case_with(studio, receipts, unsafe).model_dump(mode="json")
    with studio.store.transaction() as u:
        u.insert_case(body)
    view = studio.view(body["id"])
    assert "POLICY_BLOCKED" in view["packet"]["blockers"] and view["packet"]["explanations"]
    with pytest.raises(DomainError) as blocked:
        studio.approve(body["id"], 0, view["packet"]["subject_hash"], {}, True, OWNER)
    assert blocked.value.code == "GATE_BLOCKED" and "POLICY_BLOCKED" in blocked.value.message


def test_smt_negative_controls_explain_policy_blocks_too(tmp_path, studio):
    unsafe = unsafe_workflow()
    subject = subject_for(unsafe, {}, harness_identity())
    receipts = attached(stub_all(BASE, CANDIDATE).collect(BASE, unsafe), subject, studio.signer)
    packet = compile_case(_case_with(studio, receipts, unsafe), harness_identity(), studio.signer.authentic, 0)
    smt = [x for x in packet["explanations"] if x["source"] == "smt_proof negative control"]
    assert smt and smt[0]["control"] == "PROTECTED_AUTHORITY:Approve/role" and smt[0]["violates"] == "INV-TEACHER-NOT-DECIDER"
    assert any(t["role"] == "Teacher" and t["action"] == "Approve" for t in smt[0]["witness"]["transitions"])


def test_explanations_come_only_from_authentic_intact_receipts(studio):
    unsafe = unsafe_workflow()
    subject = subject_for(unsafe, {}, harness_identity())
    unsealed = [receipt_of("bend_proof", ARTS["bend_proof"], subject)]
    packet = compile_case(_case_with(studio, unsealed, unsafe), harness_identity(), studio.signer.authentic, 0)
    assert packet["explanations"] == [] and packet["technical_claims"]["formal_bend_proof"] == "FAIL"


# ------------------------------------------------------------------ the CLI

@pytest.fixture
def cli_identity(monkeypatch):
    monkeypatch.setattr("eija_studio.bootstrap.identity", harness_identity)


def test_cli_verify_shows_each_formal_kind_and_no_formal_opts_out(cli_identity, tmp_path, capsys):
    ws = tmp_path / "ws"
    studio = build_studio(ws)
    studio.identity_provider = harness_identity
    case = studio.create("Let teachers sign off excursions.")
    case = studio.propose(case["id"], case["version"])
    case = studio.select(case["id"], case["version"], "recommend_only", OWNER)
    assert cli_main(["verify", case["id"], "--expected-version", str(case["version"]), "--workspace", str(ws)]) == 0
    captured = capsys.readouterr()
    packet = json.loads(captured.out)
    assert {e["kind"] for e in packet["formal_evidence"]} == set(KIND_NAMES)
    for kind in KIND_NAMES:
        assert re.search(rf"^\s+{kind}\s+(PASS|FAIL|STALE|UNKNOWN|NOT_RUN|CONFLICT)\s+sealed_tool_verdict", captured.err, re.MULTILINE)
    assert "never rounded up" in captured.err
    with build_studio(ws).store.transaction() as u:
        receipts = u.load_case(case["id"])["receipts"]
    assert "bend_proof" in {r["kind"] for r in receipts}
    # --no-formal: the same command leaves the case with the runtime receipt only.
    fresh = build_studio(tmp_path / "ws2")
    fresh.identity_provider = harness_identity
    other = fresh.create("Let teachers sign off excursions.")
    other = fresh.propose(other["id"], other["version"])
    other = fresh.select(other["id"], other["version"], "recommend_only", OWNER)
    assert cli_main(["verify", other["id"], "--expected-version", str(other["version"]), "--workspace", str(tmp_path / "ws2"), "--no-formal"]) == 0
    with build_studio(tmp_path / "ws2").store.transaction() as u:
        assert [r["kind"] for r in u.load_case(other["id"])["receipts"]] == ["integration_test"]


def test_cli_compile_of_the_unsafe_workflow_is_blocked_and_carries_the_explanation(cli_identity, tmp_path, capsys):
    code = cli_main(["compile", str(UNSAFE), "--out", str(tmp_path / "out"), "--workspace", str(tmp_path / "ws")])
    assert code == 2
    compiled = json.loads((tmp_path / "out" / "compiled.json").read_text(encoding="utf-8"))
    assert compiled["policy_errors"] == ["PROTECTED_AUTHORITY:Approve"]
    assert any(x["control"] == "teacher_final_approval" for x in compiled["formal_explanations"])
    assert "receipt" not in compiled  # a blocked model is never verified
    capsys.readouterr()


# ------------------------------------------------------------------ the Studio page

def test_the_studio_page_renders_formal_evidence_as_text_only():
    web = ROOT / "src" / "eija_studio" / "resources" / "web"
    html, script = (web / "index.html").read_text(encoding="utf-8"), (web / "app.js").read_text(encoding="utf-8")
    assert 'id="formal"' in html and "renderFormal(p)" in script
    body = script[script.index("function formalList"):script.index("async function load")]
    for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
        assert sink not in body


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_render_formal_builds_only_text_nodes_from_a_hostile_packet(tmp_path):
    script = (ROOT / "src" / "eija_studio" / "resources" / "web" / "app.js").read_text(encoding="utf-8")
    body = script[script.index("function formalList"):script.index("async function load")]
    harness = tmp_path / "render.js"
    harness.write_text(
        "const made=[];const mk=t=>({tag:t,text:'',cls:'',kids:[],append(...k){this.kids.push(...k)},replaceChildren(){this.kids=[]}});"
        "const el=(t,x,c)=>{const n=mk(t);if(x!==undefined)n.text=String(x);if(c)n.cls=c;made.push(n);return n;};"
        "const root=mk('div');const $=id=>root;\n" + body +
        "\nconst hostile='<img src=x onerror=alert(1)>';"
        "renderFormal({explanations:[{control:hostile,source:hostile,trace:[[hostile,'Approve']],final_state:hostile,note:hostile}],"
        "formal_evidence:[{kind:'bend_proof',status:'PASS',evidence_level:'sealed_tool_verdict',establishes:hostile,reasons:[hostile],"
        "does_not_establish:[hostile],assumptions:[hostile],bounds:{a:hostile},counterexamples:[{x:hostile}],prerequisites:hostile}]});"
        "if(!made.length||made.some(n=>n.html!==undefined||n.innerHTML!==undefined))process.exit(3);"
        "if(!made.some(n=>n.text.includes(hostile)))process.exit(4);console.log('ok '+made.length);", encoding="utf-8")
    done = subprocess.run(["node", str(harness)], capture_output=True, text=True, check=False)  # noqa: S603, S607
    assert done.returncode == 0 and done.stdout.startswith("ok"), done.stderr


# ------------------------------------------------------------------ hardening: hostile artifacts, failing sources, blocked meanings

def test_a_failing_evidence_source_is_not_run_for_every_kind_and_does_not_block_verify(studio, selected):
    class Broken:
        def collect(self, baseline, candidate):
            raise PermissionError("cannot read the reports directory")

    studio.formal = Broken()
    case = studio.verify(selected["id"], selected["version"])
    packet = studio.view(case["id"])["packet"]
    assert packet["eligible"]
    assert {e["kind"]: e["status"] for e in packet["formal_evidence"]} == dict.fromkeys(KIND_NAMES, "NOT_RUN")
    assert "PermissionError" in packet["formal_evidence"][0]["reasons"][0]


def test_tampered_bytes_are_never_displayed_as_evidence_details(studio, selected):
    studio.formal = stub_all(BASE, CANDIDATE)
    case = studio.verify(selected["id"], selected["version"])
    doc = copy.deepcopy(case)
    next(r for r in doc["receipts"] if r["kind"] == "bend_proof")["artifact"]["assumptions"] = ["<script>alert(1)</script>"]
    tampered = ChangeCase.model_validate(doc)
    packet = compile_case(tampered, studio.identity_provider(), studio.signer.authentic, tampered.baseline_version)
    entry = next(e for e in packet["formal_evidence"] if e["kind"] == "bend_proof")
    assert entry["status"] == "FAIL" and "assumptions" not in entry and "<script>" not in json.dumps(packet)


def test_the_unsafe_meaning_is_blocked_in_the_packet_with_the_counterexample_before_any_candidate_exists(studio):
    studio.formal = FormalReports()
    case = studio.create("Let teachers sign off excursions.")
    case = studio.propose(case["id"], case["version"])
    with pytest.raises(DomainError):
        studio.select(case["id"], case["version"], "final_approval", OWNER)
    packet = studio.view(case["id"])["packet"]
    assert packet["blockers"] == ["MEANING_REQUIRED"]
    blocked = {m["interpretation"]: m for m in packet["blocked_meanings"]}
    assert set(blocked) == {"final_approval"} and blocked["final_approval"]["policy_errors"] == ["PROTECTED_AUTHORITY:Approve"]
    trace = next(x for x in blocked["final_approval"]["explanations"] if x["source"] == "bend_proof negative control")
    assert trace["trace"][-1] == ["teacher-assigned", "Approve"] and trace["final_state"] == "Approved"
    # the what-if model is exactly the model the Bend lane seeded as its unsafe control
    assert what_if_model(BASE, "final_approval").semantic_hash == unsafe_workflow().semantic_hash
    assert what_if_model(BASE, "recommend_only") is None


def test_without_a_formal_source_no_meaning_is_explained(studio):
    case = studio.create("Let teachers sign off excursions.")
    case = studio.propose(case["id"], case["version"])
    assert studio.view(case["id"])["packet"]["blocked_meanings"] == []


def test_only_the_negative_controls_of_the_blocking_fault_class_are_offered_as_explanations(studio):
    unsafe = unsafe_workflow()
    subject = subject_for(unsafe, {}, harness_identity())
    receipts = attached(FormalReports().collect(BASE, unsafe), subject, studio.signer)
    packet = compile_case(_case_with(studio, receipts, unsafe), harness_identity(), studio.signer.authentic, 0)
    bend = [x["control"] for x in packet["explanations"] if x["source"] == "bend_proof negative control"]
    assert bend == ["teacher_final_approval"]  # not the five other seeded faults, which this candidate does not have


def test_blocked_meanings_disappear_once_a_supported_meaning_is_selected(studio):
    studio.formal = FormalReports()
    case = studio.create("Let teachers sign off excursions.")
    case = studio.propose(case["id"], case["version"])
    assert studio.view(case["id"])["packet"]["blocked_meanings"]
    case = studio.select(case["id"], case["version"], "recommend_only", OWNER)
    assert studio.view(case["id"])["packet"]["blocked_meanings"] == []
