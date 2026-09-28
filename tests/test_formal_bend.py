"""Bend lane: the generated model, the laws/proofs pairing, the negative controls and the runner logic.

Everything here runs without Docker and states what it checks. The tests that need the pinned Bend
container are skipped (reported as skipped, never as passed) when Docker is not available; the full
proof gate is the nox session ``formal_bend``.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BEND = ROOT / "verification" / "bend"
sys.path.insert(0, str(BEND))

import bend_conformance as conformance  # noqa: E402
import bend_controls  # noqa: E402
import bend_generate as gen  # noqa: E402
import bend_runner as runner  # noqa: E402
import bend_slicing as slicing  # noqa: E402
from eija_studio.domain.policy import check_policy  # noqa: E402

LAWS = (BEND / "LAWS.bend").read_text(encoding="utf-8")
PROOF = (BEND / "PROOF.bend").read_text(encoding="utf-8")
MAIN = (BEND / "main.bend").read_text(encoding="utf-8")
EXPECTED_LAWS = [
    "teacher_never_approves", "teacher_sequences_never_approve", "approved_only_from_recommended",
    "every_path_to_approved_passes_recommended", "revoked_teacher_cannot_recommend",
    "unassigned_teacher_cannot_recommend", "reject_only_from_declared_source", "forbidden_effects_never_emitted",
]


def docker_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        return subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"], capture_output=True, timeout=20).returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


needs_docker = pytest.mark.skipif(not docker_ready(), reason="Docker daemon not available: Bend proofs need the pinned container (NOT_RUN)")


# --- generation ---------------------------------------------------------------------------------

def test_generation_is_deterministic_and_the_committed_model_is_current():
    first, second = gen.render_main(gen.default_models()), gen.render_main(gen.default_models())
    assert first == second
    assert MAIN == first, "main.bend is stale: run python verification/bend/bend_generate.py"
    for name in ("main.bend", "LAWS.bend", "PROOF.bend", "bend_generate.py", "Dockerfile"):
        assert b"\r" not in (BEND / name).read_bytes(), f"{name} must use LF line endings"


def test_drift_check_fails_on_a_stale_or_missing_model_and_passes_on_a_fresh_one(tmp_path):
    fresh, stale = tmp_path / "fresh.bend", tmp_path / "stale.bend"
    fresh.write_bytes(MAIN.encode("utf-8"))
    stale.write_bytes(MAIN.replace("Recommend{}", "Recomend{}", 1).encode("utf-8"))
    assert gen.main(["--check", "--out", str(fresh)]) == 0
    assert gen.main(["--check", "--out", str(stale)]) == 1
    assert gen.main(["--check", "--out", str(tmp_path / "missing.bend")]) == 1


def test_slots_are_the_executable_workflows_and_the_header_names_their_hashes():
    models = gen.default_models()
    assert models["Candidate"].semantic_hash == gen.load_workflow(gen.CANDIDATE_EXAMPLE).semantic_hash
    for slot, workflow in models.items():
        assert f"#   {slot}: {workflow.semantic_hash}" in MAIN
    assert check_policy(models["Baseline"]) == [] and check_policy(models["Candidate"]) == []


def test_every_transition_of_each_workflow_becomes_exactly_one_rule():
    for slot, workflow in gen.default_models().items():
        block = MAIN.split(f"    case {slot}{{}}:\n      match act:\n")[1].split("\n    case ")[0]
        rules = re.findall(r"Some\{Rule\{(\w+)\{\}, (\w+)\{\}, (\w+)\{\}, (True|False)\{\}, \[(.*?)\]\}\}", block)
        assert len(rules) == len(workflow.transitions)
        for t in workflow.transitions:
            effects = ", ".join(f"{e.replace(':', '_')}{{}}" for e in sorted(t.required_effects))
            needs = "True" if "actor_assigned" in t.guards else "False"
            assert (t.from_state, t.to_state, t.role, needs, effects) in rules


def test_generation_refuses_names_it_cannot_represent_faithfully():
    data = gen.default_models()["Candidate"].model_dump(mode="json")
    data["states"] = [s if s != "Rejected" else "Actor" for s in data["states"]]
    for t in data["transitions"]:
        t["to_state"] = "Actor" if t["to_state"] == "Rejected" else t["to_state"]
        t["from_state"] = "Actor" if t["from_state"] == "Rejected" else t["from_state"]
    clash = gen.Workflow.model_validate(data)
    with pytest.raises(gen.ModelError):
        gen.render_main({"Baseline": gen.default_models()["Baseline"], "Candidate": clash})
    with pytest.raises(gen.ModelError):
        gen.render_main({"Candidate": clash})


def test_effect_names_cover_the_policys_forbidden_effects():
    assert "PaymentCaptured{}" in MAIN and "ParentDataExported{}" in MAIN


# --- laws and proofs ----------------------------------------------------------------------------

def test_every_law_has_a_proof_and_no_proof_is_orphaned():
    assert slicing.law_names(LAWS) == EXPECTED_LAWS
    assert slicing.proof_names(PROOF) == set(EXPECTED_LAWS)


def test_no_escape_hatches_in_the_bend_sources():
    for name, text in (("main", MAIN), ("LAWS", LAWS), ("PROOF", PROOF)):
        code = "\n".join(ln.split("#", 1)[0] for ln in text.splitlines())
        assert "@unsafe" not in code and "?TODO" not in code, name
        assert not re.search(r'^\s*import\s+"', code, re.MULTILINE), f"{name}: foreign code import"
        assert not re.search(r"\bdef\s+\w[\w.]*\?", code), f"{name}: def f? is the @unsafe sugar"
        assert not re.search(r"^import\s+(0x|\S+@)", code, re.MULTILINE), f"{name}: remote package import"


def test_docs_name_every_law():
    doc = (ROOT / "docs" / "formal" / "bend.md").read_text(encoding="utf-8")
    for law in EXPECTED_LAWS:
        assert f"`{law}`" in doc, law


def test_slicing_keeps_only_the_law_and_the_lemmas_it_uses():
    laws, proof = slicing.slice_for_law(LAWS, PROOF, "revoked_teacher_cannot_recommend")
    assert slicing.law_names(laws) == ["revoked_teacher_cannot_recommend"]
    assert slicing.proof_names(proof) == {"revoked_teacher_cannot_recommend"}
    assert "cert_teacher" not in proof and "replay_sound" not in proof
    _, teacher = slicing.slice_for_law(LAWS, PROOF, "teacher_never_approves")
    assert "def cert_teacher" in teacher and "def step_prop" in teacher and "replay_sound" not in teacher
    # slicing never rewrites a proof: every kept definition appears verbatim in the original
    originals = {i.name: i.text for i in slicing.parse_items(PROOF)}
    for item in slicing.parse_items(teacher):
        assert originals[item.name] == item.text
    with pytest.raises(KeyError):
        slicing.slice_for_law(LAWS, PROOF, "no_such_law")


def test_law_comments_are_the_human_statements():
    comments = slicing.law_comments(LAWS)
    assert comments["teacher_never_approves"].startswith("LAW 1:") and set(comments) == set(EXPECTED_LAWS)


# --- negative controls --------------------------------------------------------------------------

def test_each_control_generates_a_different_model_from_the_shipped_one():
    texts = {c.name: c.build() for c in bend_controls.CONTROLS}
    assert all(text != MAIN for text in texts.values())
    assert len(set(texts.values())) == len(texts)
    assert {c.name for c in bend_controls.CONTROLS} >= {"teacher_final_approval"}


def test_teacher_control_is_the_kernels_own_unsafe_example():
    control = next(c for c in bend_controls.CONTROLS if c.name == "teacher_final_approval")
    assert control.workflow() == gen.load_workflow(gen.UNSAFE_EXAMPLE)
    assert control.kernel_policy_findings() == ["PROTECTED_AUTHORITY:Approve"]


def test_the_kernel_policy_independently_blocks_every_model_level_control():
    for control in bend_controls.CONTROLS:
        findings = control.kernel_policy_findings()
        if control.candidate is not None:
            assert findings, f"{control.name}: the kernel policy should reject this model"
        else:
            assert findings is None


def test_every_law_is_targeted_by_some_control():
    targeted = {law for c in bend_controls.CONTROLS for law in c.expected_failing_laws}
    assert targeted == set(EXPECTED_LAWS), "a law that no control can break has no demonstrated sensitivity"


def test_control_witnesses_and_probes_reference_real_actors_and_actions():
    for c in bend_controls.CONTROLS:
        for actor, action in c.witness_steps:
            assert actor in conformance.ACTOR_ID and action in {"Submit", "Recommend", "Approve", "Reject", "Revise"}
        assert bool(c.witness_steps) != bool(c.probe)


# --- conformance (the Python side runs without Docker) -----------------------------------------

def test_witness_expectations_hold_in_the_real_python_runtime(tmp_path):
    models = gen.default_models()
    for w in conformance.GOOD_WITNESSES:
        assert conformance.python_witness(models[w.slot], w.steps, tmp_path) == w.final_state, w.name


def test_matrix_programs_cover_every_cell_of_the_runtime_matrix():
    programs = conformance.matrix_programs(gen.default_models())
    assert len(programs) == 2 * len(conformance.ACTORS)
    cells = sum(text.count('show("') for text in programs.values())
    assert cells == 4 * 5 * 5 + 5 * 5 * 5  # Baseline has 4 states, Candidate 5; 5 actors x 5 actions each


def test_parse_and_compare_matrix_detect_a_disagreement():
    record = "Candidate|teacher-assigned|Submitted|Recommend|T|Recommended|Audit_ExcursionRecommended,Notification_RegistrarQueued,;"
    bend = conformance.parse_matrix('"' + record + '"')
    key = ("Candidate", "teacher-assigned", "Submitted", "Recommend")
    assert bend[key] == conformance.BendCell(True, "Recommended", 1, 1)
    agree = conformance.compare_matrices(bend, dict(bend))
    assert agree["mismatches"] == [] and agree["agree"] == 1
    flipped = {key: conformance.BendCell(False, "Submitted", 0, 0)}  # negative control: a runtime that denied it
    assert len(conformance.compare_matrices(bend, flipped)["mismatches"]) == 1
    assert conformance.compare_matrices(bend, {})["unmatched_cells"]
    with pytest.raises(ValueError):
        conformance.parse_matrix("not a quoted string")


# --- runner honesty -----------------------------------------------------------------------------

def test_classify_only_calls_a_clean_verdict_a_proof():
    ok = runner.Result(0, "ALL PROOFS CHECK\n")
    assert runner.classify(ok)["result"] == "PROVEN"
    assert runner.classify(runner.Result(1, "ALL PROOFS CHECK\n"))["result"] == "FAILED"  # exit code wins
    assert runner.classify(runner.Result(0, "Use --verdict for mathematical validity.\n"))["result"] == "FAILED"
    failed = runner.classify(runner.Result(1, "SOME PROOFS FAIL\nError:\n- expected : a\nLocation: Laws.x\n"))
    assert failed["result"] == "FAILED" and failed["location"] == "Laws.x"
    assert runner.classify(runner.Result(0, "SOME PROOFS FAIL\nALL PROOFS CHECK"))["result"] == "FAILED"


def test_a_missing_job_marker_is_a_failure_never_a_success():
    text = "@@@BEGIN 0\nALL PROOFS CHECK\n@@@END 0 0\n@@@BEGIN 1\nALL PROOFS CHECK\n"
    results = runner.parse_jobs(text, 3)
    assert [r.code for r in results] == [0, 255, 255]
    assert [runner.classify(r)["result"] for r in results] == ["PROVEN", "FAILED", "FAILED"]


def test_a_missing_docker_is_not_run_never_pass(monkeypatch):
    def no_docker(*args, **kwargs):
        raise FileNotFoundError("docker")
    monkeypatch.setattr(subprocess, "run", no_docker)
    with pytest.raises(runner.NotRun):
        runner.Checker().prerequisites()
    report = runner.build_report()
    assert report["status"] == "NOT_RUN" and "docker" in report["reason"]
    assert "proof" not in report and report["kind"] == "bend_proof"


def test_a_stopped_daemon_is_not_run(monkeypatch):
    def daemon_down(*args, **kwargs):
        return subprocess.CompletedProcess(args, 1, "", "Cannot connect to the Docker daemon")
    monkeypatch.setattr(subprocess, "run", daemon_down)
    assert runner.build_report(controls=False, conformance_check=False)["status"] == "NOT_RUN"


def test_the_dockerfile_pins_everything_that_decides_a_verdict():
    text = (BEND / "Dockerfile").read_text(encoding="utf-8")
    assert re.search(r"^FROM ubuntu:24\.04@sha256:[0-9a-f]{64}", text, re.MULTILINE)
    assert len(re.findall(r"--checksum=sha256:[0-9a-f]{64}", text)) == 2  # Bend archive and Lean archive
    assert "releases/download/v2.0.32/" in text and "BEND_COMMIT=573002f01ec6c52416d44489543f69a9625facf8" in text
    assert "latest" not in re.sub(r"#.*", "", text)


def test_the_committed_evidence_snapshot_describes_the_committed_proofs():
    snapshot = json.loads((BEND / "evidence" / "bend.json").read_text(encoding="utf-8"))
    assert snapshot["kind"] == "bend_proof" and snapshot["status"] == "PASS" and snapshot["mode"] == "complete"
    assert snapshot["platform"] and snapshot["tool"]["bend_version"] == "2.0.32"
    assert snapshot["tool"]["bend_commit"] == "573002f01ec6c52416d44489543f69a9625facf8"
    for name in ("main.bend", "LAWS.bend", "PROOF.bend"):
        assert snapshot["model"]["files"][name] == runner.sha256_file(BEND / name), f"{name} changed since the snapshot: rerun the gate with --snapshot"
    assert snapshot["model"]["semantic_hash"] == {slot: w.semantic_hash for slot, w in gen.default_models().items()}
    assert [law["name"] for law in snapshot["proof"]["laws"]] == EXPECTED_LAWS
    assert all(law["result"] == "PROVEN" for law in snapshot["proof"]["laws"])
    assert snapshot["proof"]["full_run"]["result"] == "PROVEN"
    assert [c["name"] for c in snapshot["negative_controls"]] == [c.name for c in bend_controls.CONTROLS]
    assert all(c["result"] == "PROOF_FAILS_AS_EXPECTED" and c["failing_laws"] == c["expected_failing_laws"]
               for c in snapshot["negative_controls"])
    assert snapshot["conformance"]["status"] == "PASS" and snapshot["conformance"]["matrix"]["mismatches"] == []
    assert snapshot["limits"], "the limits travel with the evidence"


# --- with Docker --------------------------------------------------------------------------------

@needs_docker
def test_the_committed_proofs_check_and_a_seeded_fault_fails_them():
    checker = runner.Checker()
    checker.prerequisites()
    verdicts, _ = runner.prove_directory(checker, "pytest-committed", MAIN, LAWS, PROOF, {}, attribute=False)
    assert verdicts["model_check"]["result"] == "PROVEN"
    assert verdicts["full_run"]["result"] == "PROVEN"
    control = next(c for c in bend_controls.CONTROLS if c.name == "teacher_final_approval")
    unsafe, _ = runner.prove_directory(checker, "pytest-unsafe", control.build(), LAWS, PROOF, {}, attribute=False)
    assert unsafe["model_check"]["result"] == "PROVEN", "the unsafe model is well-formed Bend"
    assert unsafe["full_run"]["result"] == "FAILED", "the same proofs must NOT check against the unsafe model"
