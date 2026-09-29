"""Per-kind admissibility of formal evidence (ADR-0145, ADR-0146): the kernel recomputes every verdict.

Each test names the attack it defends against: a tampered artifact byte, a forged green label, a stale model,
missing negative controls, a bound below the declared minimum, a missing prerequisite.
"""
from __future__ import annotations

import copy

import pytest
from eija_studio.adapters.receipts import ReceiptSigner
from eija_studio.domain.evidence import (
    aggregate_formal, assess_formal_receipt, assess_receipt, combine, intact_artifact,
)
from eija_studio.domain.evidence_kinds import KINDS
from eija_studio.domain.formal import Context
from eija_studio.domain.formal_bend import CONTROLS as BEND_CONTROLS, LAWS as BEND_LAWS
from eija_studio.domain.formal_bmc import MIN_DEPTH, MUTANTS
from eija_studio.domain.formal_smt import INVARIANTS, MIN_DIFFERENTIAL_CANDIDATES, NAMED_CONTROLS
from eija_studio.domain.models import fingerprint

from formal_support import (
    KIND_NAMES, artifacts, at, context_of, flipped, leaves, not_run_artifact, receipt_of, subject_of, with_change, workflows,
)

BASE, CANDIDATE = workflows()
SUBJECT = subject_of(CANDIDATE)
CONTEXT = context_of(BASE, CANDIDATE)
ARTIFACTS = artifacts(BASE, CANDIDATE)


def verdict(kind, artifact, *, rehash=True, subject=SUBJECT, context=CONTEXT, **overrides):
    receipt = receipt_of(kind, artifact, SUBJECT, rehash=rehash, **overrides)
    return assess_formal_receipt(receipt, subject, KINDS[kind].claim, kind, context)


def law(name):
    return ("proof", "laws", BEND_LAWS.index(name), "result")


def control_index(artifact, name):
    return next(i for i, c in enumerate(artifact["negative_controls"]) if c["name"] == name)


# ------------------------------------------------------------------ baseline: real evidence is admitted

@pytest.mark.parametrize("kind", KIND_NAMES)
def test_real_artifacts_are_admitted_as_pass(kind):
    a = verdict(kind, ARTIFACTS[kind])
    assert a.status == "PASS" and a.reasons == (), a.reasons


@pytest.mark.parametrize("kind", KIND_NAMES)
def test_every_kind_declares_what_it_does_not_establish_and_its_level(kind):
    spec = KINDS[kind]
    assert spec.does_not_establish and all(spec.does_not_establish) and spec.establishes and spec.prerequisites
    assert spec.level == "sealed_tool_verdict"  # none of these has a kernel-checkable certificate yet


def test_kinds_without_a_rule_are_unknown_by_construction():
    receipt = receipt_of("bend_proof", ARTIFACTS["bend_proof"], SUBJECT, kind="tlc_model_check", claim="protocol_model")
    assert assess_receipt(receipt, SUBJECT, "protocol_model", "tlc_model_check") == "UNKNOWN"
    assert assess_receipt(receipt_of("bend_proof", ARTIFACTS["bend_proof"], SUBJECT), SUBJECT, "runtime_matrix", "integration_test") == "UNKNOWN"


# ------------------------------------------------------------------ tamper: any artifact byte

@pytest.mark.parametrize("kind", KIND_NAMES)
def test_tampering_any_single_artifact_value_without_rehashing_is_fail(kind):
    artifact = ARTIFACTS[kind]
    paths = leaves(artifact)
    assert len(paths) > 40
    for path in paths:
        tampered = with_change(artifact, path, flipped(at(artifact, path)))
        assert verdict(kind, tampered, rehash=False).status == "FAIL", path
    # A stale hash on the ORIGINAL bytes is also a FAIL: the raw artifact must hash to what was sealed.
    assert verdict(kind, artifact, rehash=False).status == "FAIL"


@pytest.mark.parametrize("kind", KIND_NAMES)
def test_an_unknown_extra_or_missing_top_level_field_is_a_fail(kind):
    extra = {**copy.deepcopy(ARTIFACTS[kind]), "status": "PASS"}
    assert verdict(kind, extra).status == "FAIL"
    missing = {k: v for k, v in ARTIFACTS[kind].items() if k != "assumptions"}
    assert verdict(kind, missing).status == "FAIL"


def test_a_receipt_for_another_subject_is_stale_before_its_bytes_are_judged():
    other = dict(SUBJECT, implementation="someone-elses")
    receipt = receipt_of("bend_proof", ARTIFACTS["bend_proof"], other, rehash=False)
    assert assess_formal_receipt(receipt, SUBJECT, KINDS["bend_proof"].claim, "bend_proof", CONTEXT).status == "STALE"


@pytest.mark.parametrize("override", [{"producer": "someone"}, {"method": "other-v9"}])
def test_unrecognised_producer_or_method_is_unknown(override):
    assert verdict("bend_proof", ARTIFACTS["bend_proof"], **override).status == "UNKNOWN"


def test_an_unrecognised_protocol_version_is_unknown_not_fail():
    assert verdict("smt_proof", {**ARTIFACTS["smt_proof"], "protocol": "eija.formal.smt-proof/v2"}).status == "UNKNOWN"


# ------------------------------------------------------------------ forged labels

def test_a_forged_green_label_cannot_hide_a_failing_law():
    artifact = with_change(ARTIFACTS["bend_proof"], law("teacher_never_approves"), "FAILED")
    assert artifact["reported"]["verdict"] == "PASS"  # the label still says PASS
    a = verdict("bend_proof", artifact, status="PASS", admissible=True)
    assert a.status == "FAIL" and any("teacher_never_approves" in r for r in a.reasons)


def test_forged_receipt_level_labels_are_never_read():
    a = verdict("bend_proof", with_change(ARTIFACTS["bend_proof"], law("forbidden_effects_never_emitted"), "FAILED"),
                status="PASS", admissible=True, verdict="PASS", summary={"proof": "PASS"})
    assert a.status == "FAIL"


@pytest.mark.parametrize("kind", KIND_NAMES)
def test_a_tools_own_fail_label_lowers_the_status_even_when_the_content_looks_perfect(kind):
    artifact = with_change(ARTIFACTS[kind], ("reported", "verdict"), "FAIL")
    assert verdict(kind, artifact).status == "FAIL"
    incomplete = with_change(ARTIFACTS[kind], ("reported", "verdict"), "PARTIAL")
    assert verdict(kind, incomplete).status == "UNKNOWN"


@pytest.mark.parametrize("kind", KIND_NAMES)
def test_a_pass_label_alone_cannot_raise_an_artifact_whose_content_fails(kind):
    breakers = {"bend_proof": (law("approved_only_from_recommended"), "FAILED"),
                "smt_proof": (("invariants", 0, "status"), "refuted"),
                "bounded_model_check": (("counterexamples", "baseline"), [{"invariant": "X", "length": 2, "trace": ["a"]}])}
    path, bad = breakers[kind]
    artifact = with_change(ARTIFACTS[kind], path, bad)
    assert artifact["reported"]["verdict"] == "PASS"
    assert verdict(kind, artifact).status == "FAIL"


# ------------------------------------------------------------------ Bend: recomputed verdict

def test_bend_missing_law_is_unknown_and_a_law_without_proof_is_unknown():
    a = copy.deepcopy(ARTIFACTS["bend_proof"])
    a["proof"]["laws"] = [x for x in a["proof"]["laws"] if x["name"] != "teacher_never_approves"]
    assert verdict("bend_proof", a).status == "UNKNOWN"
    b = with_change(ARTIFACTS["bend_proof"], ("proof", "laws_without_proof"), ["forbidden_effects_never_emitted"])
    assert verdict("bend_proof", b).status == "UNKNOWN"


def test_bend_without_the_proof_kernel_recheck_or_in_quick_mode_is_unknown():
    assert verdict("bend_proof", with_change(ARTIFACTS["bend_proof"], ("proof", "command"), "bend PROOF.bend")).status == "UNKNOWN"
    assert verdict("bend_proof", with_change(ARTIFACTS["bend_proof"], ("mode",), "quick")).status == "UNKNOWN"


def test_bend_unaccepted_tool_version_is_unknown():
    assert verdict("bend_proof", with_change(ARTIFACTS["bend_proof"], ("tool", "bend_version"), "9.9.9")).status == "UNKNOWN"
    assert verdict("bend_proof", with_change(ARTIFACTS["bend_proof"], ("tool", "base_image"), "ubuntu:24.04")).status == "UNKNOWN"


@pytest.mark.parametrize("name", sorted(BEND_CONTROLS))
def test_bend_a_missing_negative_control_is_unknown_never_pass(name):
    a = copy.deepcopy(ARTIFACTS["bend_proof"])
    del a["negative_controls"][control_index(a, name)]
    result = verdict("bend_proof", a)
    assert result.status == "UNKNOWN" and any(name in r for r in result.reasons)


def test_bend_no_negative_controls_at_all_is_unknown():
    assert verdict("bend_proof", with_change(ARTIFACTS["bend_proof"], ("negative_controls",), [])).status == "UNKNOWN"


@pytest.mark.parametrize("name", sorted(BEND_CONTROLS))
def test_bend_a_control_the_proof_did_not_reject_is_fail(name):
    a = copy.deepcopy(ARTIFACTS["bend_proof"])
    c = a["negative_controls"][control_index(a, name)]
    c["full_run"]["result"] = "PROVEN"
    result = verdict("bend_proof", a)
    assert result.status == "FAIL" and any("insensitive" in r for r in result.reasons)


def test_bend_a_control_that_breaks_the_wrong_laws_is_fail():
    a = copy.deepcopy(ARTIFACTS["bend_proof"])
    c = a["negative_controls"][control_index(a, "teacher_final_approval")]
    c["failing_laws"], c["passing_laws"] = c["failing_laws"][:1], c["passing_laws"] + c["failing_laws"][1:]
    assert verdict("bend_proof", a).status == "FAIL"


def test_bend_a_control_without_a_confirmed_counterexample_is_fail():
    a = copy.deepcopy(ARTIFACTS["bend_proof"])
    a["negative_controls"][control_index(a, "teacher_final_approval")]["counterexample"]["confirmed"] = False
    assert verdict("bend_proof", a).status == "FAIL"
    b = copy.deepcopy(ARTIFACTS["bend_proof"])
    b["negative_controls"][control_index(b, "payment_effect_emitted")]["effect_probe"]["emitted"] = ["Audit_ExcursionApproved"]
    assert verdict("bend_proof", b).status == "FAIL"


def test_bend_conformance_below_the_declared_minimum_is_unknown_and_disagreement_is_fail():
    a = copy.deepcopy(ARTIFACTS["bend_proof"])
    a["conformance"]["matrix"].update(cells=100, agree=100)
    assert verdict("bend_proof", a).status == "UNKNOWN"
    b = with_change(ARTIFACTS["bend_proof"], ("conformance", "matrix", "agree"), 224)
    assert verdict("bend_proof", b).status == "FAIL"
    c = with_change(ARTIFACTS["bend_proof"], ("conformance", "witnesses", 0, "python_final_state"), "Rejected")
    assert verdict("bend_proof", c).status == "FAIL"


# ------------------------------------------------------------------ stale model: the receipt is about another workflow

def test_bend_a_changed_candidate_makes_the_receipt_stale():
    base, edited = workflows("Submitted")
    subject = subject_of(edited)
    receipt = receipt_of("bend_proof", ARTIFACTS["bend_proof"], subject)
    a = assess_formal_receipt(receipt, subject, KINDS["bend_proof"].claim, "bend_proof", context_of(base, edited))
    assert a.status == "STALE" and any("Candidate" in r for r in a.reasons)


def test_bend_a_changed_baseline_is_stale():
    other_baseline = workflows("Submitted")[1]  # any workflow whose hash differs from the proved Baseline
    ctx = context_of(other_baseline, CANDIDATE)
    receipt = receipt_of("bend_proof", ARTIFACTS["bend_proof"], SUBJECT)
    assert assess_formal_receipt(receipt, SUBJECT, KINDS["bend_proof"].claim, "bend_proof", ctx).status == "STALE"


def test_bend_without_a_baseline_hash_cannot_bind_and_is_unknown():
    receipt = receipt_of("bend_proof", ARTIFACTS["bend_proof"], SUBJECT)
    ctx = Context(candidate_semantic=CANDIDATE.semantic_hash)
    assert assess_formal_receipt(receipt, SUBJECT, KINDS["bend_proof"].claim, "bend_proof", ctx).status == "UNKNOWN"


@pytest.mark.parametrize("file", ["main.bend", "LAWS.bend", "PROOF.bend", "bend_generate.py"])
def test_bend_a_changed_model_file_or_law_file_makes_the_proof_stale(file):
    a = with_change(ARTIFACTS["bend_proof"], ("binding", "current_files_sha256", file), "0" * 64)
    assert verdict("bend_proof", a).status == "STALE"


def test_bend_regenerated_model_text_must_equal_the_proved_text():
    assert verdict("bend_proof", with_change(ARTIFACTS["bend_proof"], ("binding", "regenerated_main_bend_sha256"), "0" * 64)).status == "STALE"
    assert verdict("bend_proof", with_change(ARTIFACTS["bend_proof"], ("binding", "regenerated_main_bend_sha256"), None)).status == "UNKNOWN"


def test_smt_the_proof_binds_to_the_admitted_set_not_to_one_workflow():
    for source in ("Recommended", "Submitted"):
        base, cand = workflows(source)
        subject = subject_of(cand)
        r = receipt_of("smt_proof", ARTIFACTS["smt_proof"], subject)
        assert assess_formal_receipt(r, subject, KINDS["smt_proof"].claim, "smt_proof", context_of(base, cand)).status == "PASS"
    dropped = with_change(ARTIFACTS["smt_proof"], ("accepted_set", "semantic_hashes"), ["0" * 64])
    dropped["accepted_set"]["count"] = 1
    assert verdict("smt_proof", dropped).status == "STALE"


def test_smt_and_bmc_source_changes_are_stale():
    smt = with_change(ARTIFACTS["smt_proof"], ("binding", "current_sources_sha256_lf", "domain/policy.py"), "0" * 64)
    assert verdict("smt_proof", smt).status == "STALE"
    bmc = with_change(ARTIFACTS["bounded_model_check"], ("binding", "current_sources_sha256_lf", "application/runtime.py"), "0" * 64)
    assert verdict("bounded_model_check", bmc).status == "STALE"
    unobserved = copy.deepcopy(ARTIFACTS["bounded_model_check"])
    del unobserved["binding"]["current_sources_sha256_lf"]["application/runtime.py"]
    assert verdict("bounded_model_check", unobserved).status == "UNKNOWN"


def test_bmc_a_candidate_the_search_did_not_explore_is_stale():
    base, edited = workflows("Submitted")  # the full tier explores only reject-from-Recommended
    subject = subject_of(edited)
    r = receipt_of("bounded_model_check", ARTIFACTS["bounded_model_check"], subject)
    a = assess_formal_receipt(r, subject, KINDS["bounded_model_check"].claim, "bounded_model_check", context_of(base, edited))
    assert a.status == "STALE"


# ------------------------------------------------------------------ SMT

@pytest.mark.parametrize("name", INVARIANTS)
def test_smt_every_required_invariant_matters(name):
    index = next(i for i, x in enumerate(ARTIFACTS["smt_proof"]["invariants"]) if x["id"] == name)
    assert verdict("smt_proof", with_change(ARTIFACTS["smt_proof"], ("invariants", index, "status"), "refuted")).status == "FAIL"
    assert verdict("smt_proof", with_change(ARTIFACTS["smt_proof"], ("invariants", index, "status"), "unknown")).status == "UNKNOWN"
    dropped = copy.deepcopy(ARTIFACTS["smt_proof"])
    del dropped["invariants"][index]
    assert verdict("smt_proof", dropped).status == "UNKNOWN"


@pytest.mark.parametrize("clause", sorted(NAMED_CONTROLS))
def test_smt_negative_controls_are_part_of_admissibility(clause):
    a = copy.deepcopy(ARTIFACTS["smt_proof"])
    index = next(i for i, c in enumerate(a["negative_controls"]["named"]) if c["remove"] == clause)
    assert verdict("smt_proof", with_change(a, ("negative_controls", "named", index, "counterexample_found"), False)).status == "FAIL"
    del a["negative_controls"]["named"][index]
    assert verdict("smt_proof", a).status == "UNKNOWN"


def test_smt_thin_or_unfaithful_differential_evidence():
    thin = with_change(ARTIFACTS["smt_proof"], ("differential", "candidates"), MIN_DIFFERENTIAL_CANDIDATES - 1)
    assert verdict("smt_proof", thin).status == "UNKNOWN"
    unfaithful = with_change(ARTIFACTS["smt_proof"], ("differential", "code_disagreements"), [{"candidate": 1}])
    assert verdict("smt_proof", unfaithful).status == "FAIL"
    vacuous = with_change(ARTIFACTS["smt_proof"], ("differential", "clauses_never_fired"), ["GUARD_POLICY:Recommend"])
    assert verdict("smt_proof", vacuous).status == "UNKNOWN"


def test_smt_vacuous_or_incompletely_enumerated_proofs_are_unknown():
    assert verdict("smt_proof", with_change(ARTIFACTS["smt_proof"], ("non_vacuity", "policy_admits_some_candidate"), False)).status == "UNKNOWN"
    assert verdict("smt_proof", with_change(ARTIFACTS["smt_proof"], ("accepted_set", "enumeration_complete"), False)).status == "UNKNOWN"
    narrower = with_change(ARTIFACTS["smt_proof"], ("bounds", "unknown_action_slot"), False)
    assert verdict("smt_proof", narrower).status == "UNKNOWN"


def test_smt_an_unfaithful_encoding_or_unknown_solver_version():
    bad = with_change(ARTIFACTS["smt_proof"], ("accepted_set", "inconsistent_models"), [{"candidate": {}}])
    assert verdict("smt_proof", bad).status == "FAIL"
    assert verdict("smt_proof", with_change(ARTIFACTS["smt_proof"], ("tool", "package_version"), "0.0.1")).status == "UNKNOWN"
    assert verdict("smt_proof", with_change(ARTIFACTS["smt_proof"], ("subject_function",), "eija_studio.domain.models.fingerprint")).status == "UNKNOWN"


# ------------------------------------------------------------------ bounded model check: bounded means bounded

def test_bmc_a_bound_smaller_than_the_declared_minimum_is_unknown():
    shallow = with_change(ARTIFACTS["bounded_model_check"], ("bounds", "depth"), MIN_DEPTH - 1)
    result = verdict("bounded_model_check", shallow)
    assert result.status == "UNKNOWN" and any("minimum" in r for r in result.reasons)


def test_bmc_a_counterexample_is_fail_and_names_the_invariant():
    a = copy.deepcopy(ARTIFACTS["bounded_model_check"])
    a["counterexamples"]["baseline"] = [{"invariant": "AUTHORITY-ON-COMMIT", "length": 3, "trace": ["t1", "t2", "t3"], "detail": "d"}]
    result = verdict("bounded_model_check", a)
    assert result.status == "FAIL" and any("AUTHORITY-ON-COMMIT" in r for r in result.reasons)


def test_bmc_inconclusive_or_vacuous_searches_are_unknown():
    a = copy.deepcopy(ARTIFACTS["bounded_model_check"])
    model = next(iter(a["models"]))
    assert verdict("bounded_model_check", with_change(a, ("models", model, "truncated"), True)).status == "UNKNOWN"
    assert verdict("bounded_model_check", with_change(a, ("models", model, "invariant_checks"), 0)).status == "UNKNOWN"
    assert verdict("bounded_model_check", with_change(a, ("models", model, "expected_outcomes_unreached"), ["duplicate"])).status == "UNKNOWN"
    assert verdict("bounded_model_check", with_change(a, ("models", model, "max_depth"), 2)).status == "UNKNOWN"


@pytest.mark.parametrize("mutant", MUTANTS)
def test_bmc_the_self_test_is_the_negative_control(mutant):
    a = copy.deepcopy(ARTIFACTS["bounded_model_check"])
    index = next(i for i, r in enumerate(a["mutation_self_test"]) if r["mutant"] == mutant)
    assert verdict("bounded_model_check", with_change(a, ("mutation_self_test", index, "detected"), False)).status == "FAIL"
    del a["mutation_self_test"][index]
    assert verdict("bounded_model_check", a).status == "UNKNOWN"
    assert verdict("bounded_model_check", with_change(ARTIFACTS["bounded_model_check"], ("mutation_self_test",), [])).status == "UNKNOWN"


# ------------------------------------------------------------------ NOT_RUN

@pytest.mark.parametrize("kind", KIND_NAMES)
def test_a_missing_prerequisite_is_not_run_never_pass(kind):
    item = not_run_artifact(kind)
    result = verdict(kind, item.artifact)
    assert result.status == "NOT_RUN" and "the tool is not installed" in result.reasons[0]


def test_not_run_artifacts_have_exactly_one_shape_and_cannot_carry_content():
    padded = {**ARTIFACTS["bend_proof"], "not_run": {"reason": "no docker", "prerequisite": "docker"}}
    assert verdict("bend_proof", padded).status == "FAIL"
    extra = {"protocol": KINDS["smt_proof"].protocol, "not_run": {"reason": "r", "prerequisite": "p", "note": "n"}}
    assert verdict("smt_proof", extra).status == "FAIL"
    empty_reason = {"protocol": KINDS["smt_proof"].protocol, "not_run": {"reason": "", "prerequisite": "p"}}
    assert verdict("smt_proof", empty_reason).status == "FAIL"


# ------------------------------------------------------------------ aggregation

def sealed(tmp_path):
    return ReceiptSigner(tmp_path)


def agg(kind, receipts, signer, context=CONTEXT):
    return aggregate_formal(kind, receipts, SUBJECT, signer.authentic, context)


def test_absence_is_unknown_and_visible(tmp_path):
    v = agg("smt_proof", [], sealed(tmp_path))
    assert v.status == "UNKNOWN" and v.receipts == 0 and v.reasons


def test_authenticated_pass_and_fail_do_not_average(tmp_path):
    signer = sealed(tmp_path)
    good = signer.seal(receipt_of("bend_proof", ARTIFACTS["bend_proof"], SUBJECT, id="good"))
    bad_art = with_change(ARTIFACTS["bend_proof"], law("teacher_never_approves"), "FAILED")
    bad = signer.seal(receipt_of("bend_proof", bad_art, SUBJECT, id="bad"))
    v = agg("bend_proof", [good, bad], signer)
    assert v.status == "CONFLICT" and v.receipt["id"] == "bad"
    assert agg("bend_proof", [good], signer).status == "PASS"


def test_not_run_never_beats_a_pass_and_never_hides_a_fail(tmp_path):
    signer = sealed(tmp_path)
    good = signer.seal(receipt_of("bend_proof", ARTIFACTS["bend_proof"], SUBJECT, id="good"))
    gone = signer.seal(receipt_of("bend_proof", not_run_artifact("bend_proof").artifact, SUBJECT, id="gone"))
    bad = signer.seal(receipt_of("bend_proof", with_change(ARTIFACTS["bend_proof"], law("teacher_never_approves"), "FAILED"), SUBJECT, id="bad"))
    assert agg("bend_proof", [good, gone], signer).status == "PASS"
    assert agg("bend_proof", [gone], signer).status == "NOT_RUN"
    assert agg("bend_proof", [bad, gone], signer).status == "FAIL"


def test_an_unsealed_or_resealed_wrong_receipt_is_fail(tmp_path):
    signer = sealed(tmp_path)
    unsealed = receipt_of("smt_proof", ARTIFACTS["smt_proof"], SUBJECT)
    assert agg("smt_proof", [unsealed], signer).status == "FAIL"
    forged = {**signer.seal(unsealed), "artifact_hash": fingerprint({"other": 1})}
    assert agg("smt_proof", [forged], signer).status == "FAIL"


def test_a_stale_receipt_is_stale_not_fail_and_a_newer_pass_wins(tmp_path):
    signer = sealed(tmp_path)
    old = signer.seal(receipt_of("smt_proof", ARTIFACTS["smt_proof"], dict(SUBJECT, semantic="old-model")))
    assert agg("smt_proof", [old], signer).status == "STALE"
    new = signer.seal(receipt_of("smt_proof", ARTIFACTS["smt_proof"], SUBJECT))
    assert agg("smt_proof", [old, new], signer).status == "PASS"


@pytest.mark.parametrize("statuses,expected", [
    (["PASS"], "PASS"), (["PASS", "FAIL"], "CONFLICT"), (["FAIL", "STALE"], "FAIL"), (["STALE", "NOT_RUN"], "STALE"),
    (["NOT_RUN", "UNKNOWN"], "NOT_RUN"), (["UNKNOWN"], "UNKNOWN"), ([], "UNKNOWN"), (["PASS", "NOT_RUN", "UNKNOWN", "STALE"], "PASS"),
])
def test_status_algebra(statuses, expected):
    assert combine(statuses) == expected


def test_intact_artifact_needs_seal_hash_and_known_protocol(tmp_path):
    signer = sealed(tmp_path)
    receipt = signer.seal(receipt_of("bend_proof", ARTIFACTS["bend_proof"], SUBJECT))
    assert intact_artifact(receipt, "bend_proof", signer.authentic) == ARTIFACTS["bend_proof"]
    assert intact_artifact({**receipt, "artifact_hash": "0" * 64}, "bend_proof", signer.authentic) is None
    assert intact_artifact(receipt_of("bend_proof", ARTIFACTS["bend_proof"], SUBJECT), "bend_proof", signer.authentic) is None
    gone = signer.seal(receipt_of("bend_proof", not_run_artifact("bend_proof").artifact, SUBJECT))
    assert intact_artifact(gone, "bend_proof", signer.authentic) is None
