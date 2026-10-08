"""Property tests (Hypothesis): the kernel never raises a status from labels, and the algebra is order-free."""
from __future__ import annotations

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, settings, strategies as st  # noqa: E402

from eija_studio.domain.evidence import assess_formal_receipt, combine  # noqa: E402
from eija_studio.domain.evidence_kinds import KINDS  # noqa: E402
from eija_studio.domain.formal_bend import CONTROLS, LAWS  # noqa: E402
from eija_studio.domain.formal_bmc import MIN_DEPTH, MUTANTS  # noqa: E402
from eija_studio.domain.formal_smt import INVARIANTS, NAMED_CONTROLS  # noqa: E402

from formal_support import artifacts, context_of, leaves, receipt_of, subject_of, with_change, workflows, at, flipped  # noqa: E402

BASE, CANDIDATE = workflows()
SUBJECT, CONTEXT = subject_of(CANDIDATE), context_of(BASE, CANDIDATE)
ARTS = artifacts(BASE, CANDIDATE)

# Injections that must never yield PASS, whatever the receipt or the artifact's labels say.
BREAKERS = [
    ("bend_proof", ("proof", "laws", 3, "result"), "FAILED"),
    ("bend_proof", ("proof", "full_run", "result"), "FAILED"),
    ("bend_proof", ("negative_controls", 0, "full_run", "result"), "PROVEN"),
    ("bend_proof", ("negative_controls",), []),
    ("bend_proof", ("mode",), "quick"),
    ("bend_proof", ("conformance", "matrix", "agree"), 1),
    ("bend_proof", ("model", "semantic_hash", "Candidate"), "0" * 64),
    ("smt_proof", ("invariants", 2, "status"), "refuted"),
    ("smt_proof", ("invariants", 5, "status"), "unknown"),
    ("smt_proof", ("negative_controls", "named"), []),
    ("smt_proof", ("differential", "candidates"), 3),
    ("smt_proof", ("accepted_set", "semantic_hashes"), ["0" * 64]),
    ("smt_proof", ("binding", "current_sources_sha256_lf", "domain/policy.py"), "0" * 64),
    ("bounded_model_check", ("bounds", "depth"), MIN_DEPTH - 1),
    ("bounded_model_check", ("mutation_self_test",), []),
    ("bounded_model_check", ("counterexamples", "baseline"), [{"invariant": "X", "length": 1, "trace": []}]),
    ("bounded_model_check", ("models", "baseline", "truncated"), True),
]
LABELS = st.dictionaries(
    st.sampled_from(["status", "verdict", "admissible", "result", "summary", "passed", "green"]),
    st.sampled_from(["PASS", True, "PROVEN", {"proof": "PASS"}, 1]), max_size=5)


@settings(max_examples=120, deadline=None)
@given(st.sampled_from(BREAKERS), LABELS, st.booleans())
def test_no_label_on_the_receipt_or_in_the_artifact_raises_a_broken_artifact_to_pass(breaker, labels, green_artifact_labels):
    kind, path, bad = breaker
    artifact = with_change(ARTS[kind], path, bad)
    if green_artifact_labels:
        artifact["reported"] = {"verdict": "PASS", "checks": [{"id": "all", "status": "PASS"}]}
    receipt = receipt_of(kind, artifact, SUBJECT, **labels)
    assert assess_formal_receipt(receipt, SUBJECT, KINDS[kind].claim, kind, CONTEXT).status != "PASS"


@settings(max_examples=150, deadline=None)
@given(st.sampled_from(sorted(ARTS)), st.data())
def test_any_single_value_change_without_rehashing_is_fail(kind, data):
    path = data.draw(st.sampled_from(leaves(ARTS[kind])))
    tampered = with_change(ARTS[kind], path, flipped(at(ARTS[kind], path)))
    receipt = receipt_of(kind, tampered, SUBJECT, rehash=False)
    assert assess_formal_receipt(receipt, SUBJECT, KINDS[kind].claim, kind, CONTEXT).status == "FAIL"


@settings(max_examples=200, deadline=None)
@given(st.lists(st.sampled_from(["PASS", "FAIL", "STALE", "NOT_RUN", "UNKNOWN"]), max_size=8), st.randoms())
def test_combined_status_is_order_free_and_pass_needs_a_pass_and_no_fail(statuses, rnd):
    shuffled = list(statuses)
    rnd.shuffle(shuffled)
    result = combine(statuses)
    assert result == combine(shuffled)
    assert (result == "PASS") == ("PASS" in statuses and "FAIL" not in statuses)
    assert (result == "CONFLICT") == ("PASS" in statuses and "FAIL" in statuses)
    assert ("FAIL" in statuses) <= (result in {"FAIL", "CONFLICT"})  # a failure is never absorbed by other states


def test_the_required_evidence_sets_are_the_ones_the_kernel_pins():
    assert len(LAWS) == 8 and len(CONTROLS) == 6 and len(INVARIANTS) == 12 and len(NAMED_CONTROLS) == 8 and len(MUTANTS) == 6


JSON_VALUES = st.recursive(
    st.none() | st.booleans() | st.integers(-5, 10**6) | st.text(max_size=12) | st.floats(allow_nan=False, allow_infinity=False),
    lambda inner: st.lists(inner, max_size=3) | st.dictionaries(st.text(max_size=6), inner, max_size=3), max_leaves=6)


@settings(max_examples=250, deadline=None)
@given(st.sampled_from(sorted(ARTS)), st.data(), JSON_VALUES)
def test_hostile_artifact_shapes_are_judged_and_never_crash_the_kernel(kind, data, junk):
    """Replace one value with arbitrary JSON and re-hash: the kernel must return a status and never raise, whatever the shape."""
    path = data.draw(st.sampled_from(leaves(ARTS[kind])))
    mutated = with_change(ARTS[kind], path, junk)
    receipt = receipt_of(kind, mutated, SUBJECT)
    status = assess_formal_receipt(receipt, SUBJECT, KINDS[kind].claim, kind, CONTEXT).status
    assert status in {"PASS", "FAIL", "UNKNOWN", "STALE", "NOT_RUN"}
