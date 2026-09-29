"""Exact-oracle tests of evidence assessment (`domain/evidence.py`), added by the mutation lane (ADR-0033).

`assess_receipt` recomputes a verdict from raw observations and must never trust a supplied status. Each
case here takes one genuine receipt, breaks exactly one property, re-seals the artifact hash where the
break is meant to survive the hash check, and pins the resulting status. Statuses are the contract:
`UNKNOWN` (this verifier has no authority), `FAIL` (malformed or contradicted), `STALE` (wrong subject),
`PASS` (recomputed and consistent). The expected status of each break follows the documented meaning of
those words, not the order of the implementation's `if` statements.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager

import pytest

from eija_studio.adapters.sqlite_store import SQLiteStore
from eija_studio.application.verifier import verify_runtime
from eija_studio.domain.evidence import TECHNICAL_DIMENSIONS, aggregate_status, assess_receipt
from eija_studio.domain.models import SemanticTransaction, fingerprint
from eija_studio.domain.policy import apply_transaction, baseline

SUBJECT = {"semantic": "s", "implementation": "i", "policy": "p", "environment": "e", "harness": "h"}
CLAIM, KIND = "runtime_matrix", "integration_test"


@pytest.fixture(scope="module")
def genuine(tmp_path_factory):
    root = tmp_path_factory.mktemp("evidence")
    count = []

    @contextmanager
    def sandbox():
        count.append(1)
        yield SQLiteStore(root / f"sb{len(count)}", durability="ephemeral")

    model = apply_transaction(baseline(), SemanticTransaction(kind="enable_recommendation"))
    return {"candidate": verify_runtime(model, SUBJECT, sandbox), "baseline": verify_runtime(baseline(), SUBJECT, sandbox)}


def assess(receipt: dict) -> str:
    return assess_receipt(receipt, SUBJECT, CLAIM, KIND)


def resealed(receipt: dict, edit) -> dict:
    """Copy, apply `edit(artifact)`, and recompute the artifact hash so only the structural break remains."""
    copied = copy.deepcopy(receipt)
    edit(copied["artifact"])
    copied["artifact_hash"] = fingerprint(copied["artifact"])
    return copied


def field(receipt: dict, **changes) -> dict:
    copied = copy.deepcopy(receipt)
    copied.update(changes)
    return copied


def cell(artifact: dict, actor="viewer", state="Draft", action="Submit") -> dict:
    return next(c for c in artifact["cells"] if (c["actor"], c["state"], c["action"]) == (actor, state, action))


# ---- what passes -----------------------------------------------------------------------------------

def test_genuine_receipts_pass_for_both_workflow_shapes(genuine):
    assert assess(genuine["candidate"]) == "PASS"
    assert assess(genuine["baseline"]) == "PASS"


def test_a_supplied_status_is_never_used(genuine):
    lying = field(genuine["candidate"], status="PASS")
    lying["artifact"]["cells"][0]["actual"]["accepted"] = not lying["artifact"]["cells"][0]["actual"]["accepted"]
    lying["artifact_hash"] = fingerprint(lying["artifact"])
    assert assess(lying) == "FAIL"
    assert assess(field(genuine["candidate"], status="FAIL")) == "PASS"


# ---- this verifier has no authority over other claims or producers -----------------------------------

@pytest.mark.parametrize("claim,kind", [("human_review", KIND), (CLAIM, "manual_test"), ("human_review", "manual_test")])
def test_other_claims_and_kinds_are_unknown(genuine, claim, kind):
    assert assess_receipt(genuine["candidate"], SUBJECT, claim, kind) == "UNKNOWN"


@pytest.mark.parametrize("changes", [{"claim": "human_review"}, {"kind": "manual_test"}, {"producer": "someone-else"},
                                     {"method": "bounded-runtime-matrix-v2"}])
def test_receipt_that_names_another_claim_kind_producer_or_method_is_unknown(genuine, changes):
    assert assess(field(genuine["candidate"], **changes)) == "UNKNOWN"


def test_an_unknown_protocol_is_unknown_not_a_failure(genuine):
    assert assess(resealed(genuine["candidate"], lambda a: a.update(protocol="bounded-runtime-matrix-v2"))) == "UNKNOWN"


# ---- subject binding ---------------------------------------------------------------------------------

@pytest.mark.parametrize("dimension", TECHNICAL_DIMENSIONS)
def test_any_wrong_technical_dimension_makes_the_receipt_stale(genuine, dimension):
    other = dict(SUBJECT, **{dimension: "different"})
    assert assess_receipt(genuine["candidate"], other, CLAIM, KIND) == "STALE"


def test_a_missing_subject_dimension_is_stale_and_extra_context_is_ignored(genuine):
    assert assess_receipt(genuine["candidate"], {k: v for k, v in SUBJECT.items() if k != "policy"}, CLAIM, KIND) == "STALE"
    assert assess_receipt(genuine["candidate"], SUBJECT | {"layout": "moved"}, CLAIM, KIND) == "PASS"  # layout is not a technical dimension


def test_a_receipt_without_a_subject_object_fails(genuine):
    for bad in (None, "subject", ["s"], 3):
        assert assess(field(genuine["candidate"], subject=bad)) == "FAIL"


# ---- artifact integrity ------------------------------------------------------------------------------

def test_a_tampered_artifact_or_hash_fails(genuine):
    tampered = copy.deepcopy(genuine["candidate"])
    tampered["artifact"]["limitations"].append("x")
    assert assess(tampered) == "FAIL"
    assert assess(field(genuine["candidate"], artifact_hash="0" * 64)) == "FAIL"
    assert assess(field(genuine["candidate"], artifact_hash=None)) == "FAIL"
    for bad in (None, "artifact", [], 3):
        assert assess(field(genuine["candidate"], artifact=bad)) == "FAIL"


# ---- coverage of the matrix --------------------------------------------------------------------------

def test_empty_missing_or_miscounted_cells_fail(genuine):
    receipt = genuine["candidate"]
    assert assess(resealed(receipt, lambda a: a.update(cells=[], expected_cells=0))) == "FAIL"
    assert assess(resealed(receipt, lambda a: a.pop("cells"))) == "FAIL"
    assert assess(resealed(receipt, lambda a: a.update(cells="cells"))) == "FAIL"
    assert assess(resealed(receipt, lambda a: a.pop("expected_cells"))) == "FAIL"
    assert assess(resealed(receipt, lambda a: a.update(expected_cells=124))) == "FAIL"
    assert assess(resealed(receipt, lambda a: a.update(expected_cells=125.0))) == "FAIL"
    assert assess(resealed(receipt, lambda a: a.update(expected_cells=True))) == "FAIL"
    assert assess(resealed(receipt, lambda a: a["cells"].pop())) == "FAIL"


def test_dropping_one_cell_and_padding_with_a_duplicate_still_fails(genuine):
    def swap(artifact):
        artifact["cells"][-1] = copy.deepcopy(artifact["cells"][0])
    assert assess(resealed(genuine["candidate"], swap)) == "FAIL"


def test_extra_cells_for_unlisted_keys_fail_even_when_the_count_is_declared(genuine):
    def extra(artifact):
        artifact["cells"].append(dict(copy.deepcopy(artifact["cells"][0]), actor="intruder"))
        artifact["expected_cells"] += 1
    assert assess(resealed(genuine["candidate"], extra)) == "FAIL"


@pytest.mark.parametrize("edit", [
    lambda m: m.pop("actors"),
    lambda m: m.update(extra=["x"]),
    lambda m: m.update(actors=m["actors"][:-1]),
    lambda m: m.update(actors=m["actors"] + ["auditor"]),
    lambda m: m.update(actions=m["actions"][:-1]),
    lambda m: m.update(actions=m["actions"] + ["Cancel"]),
    lambda m: m.update(states=m["states"] + ["Archived"]),
    lambda m: m.update(states=["Draft", "Submitted", "Approved"]),
    lambda m: m.update(states=m["states"] + ["Draft"]),
    lambda m: m.update(actors=m["actors"] + [m["actors"][0]]),
    lambda m: m.update(states=m["states"][:-1] + [7]),
    lambda m: m.update(actions="Submit"),
], ids=["no-actors", "extra-key", "fewer-actors", "more-actors", "fewer-actions", "more-actions", "extra-state",
        "missing-states", "duplicate-state", "duplicate-actor", "non-text-state", "actions-not-list"])
def test_a_wrong_matrix_definition_fails(genuine, edit):
    assert assess(resealed(genuine["candidate"], lambda a: edit(a["matrix"]))) == "FAIL"


def test_matrix_must_be_an_object(genuine):
    for bad in (None, [], "matrix"):
        assert assess(resealed(genuine["candidate"], lambda a: a.update(matrix=bad))) == "FAIL"


def test_the_baseline_state_set_is_accepted_and_a_mixed_one_is_not(genuine):
    assert assess(genuine["baseline"]) == "PASS"
    def add_recommended(artifact):  # baseline cells, candidate state list: the count and key set no longer agree
        artifact["matrix"]["states"].append("Recommended")
    assert assess(resealed(genuine["baseline"], add_recommended)) == "FAIL"


# ---- cell structure and values -----------------------------------------------------------------------

@pytest.mark.parametrize("edit", [
    lambda c: c.pop("expected"),
    lambda c: c.update(note="x"),
    lambda c: c.update(actor=5),
    lambda c: c.update(action=None),
    lambda c: c.update(state=["Draft"]),
    lambda c: c.update(expected="ok"),
    lambda c: c.update(actual=None),
    lambda c: c["actual"].pop("audit"),
    lambda c: c["actual"].update(extra=0),
    lambda c: c["actual"].update(accepted=1),
    lambda c: c["actual"].update(accepted="false"),
    lambda c: c["actual"].update(state=3),
    lambda c: c["actual"].update(state="Nowhere"),
    lambda c: c["actual"].update(version=2),
    lambda c: c["actual"].update(version=-1),
    lambda c: c["actual"].update(version=True),
    lambda c: c["actual"].update(version=0.0),
    lambda c: c["actual"].update(audit="0"),
    lambda c: c["actual"].update(outbox=2),
    lambda c: c["actual"].update(operations=None),
    lambda c: c["expected"].update(accepted=0),
    lambda c: c["expected"].update(state="Nowhere"),
    lambda c: c["expected"].update(audit=1.0),
], ids=["no-expected", "extra-field", "actor-int", "action-none", "state-list", "expected-str", "actual-none", "no-audit",
        "extra-obs", "accepted-int", "accepted-str", "state-int", "state-unknown", "version-2", "version-neg", "version-bool",
        "version-float", "audit-str", "outbox-2", "operations-none", "expected-accepted-int", "expected-state-unknown",
        "expected-audit-float"])
def test_malformed_cells_and_observations_fail(genuine, edit):
    assert assess(resealed(genuine["candidate"], lambda a: edit(cell(a)))) == "FAIL"


def test_a_cell_whose_actual_differs_from_expected_fails_in_every_observed_field(genuine):
    for name, value in [("accepted", True), ("state", "Approved"), ("version", 1), ("audit", 1), ("outbox", 1), ("operations", 1)]:
        def contradict(artifact, name=name, value=value):
            cell(artifact)["actual"][name] = value
        assert assess(resealed(genuine["candidate"], contradict)) == "FAIL", name


# ---- aggregation over several receipts ---------------------------------------------------------------

def test_aggregate_status_combines_authentic_receipts_without_averaging(genuine):
    good, bad = genuine["candidate"], resealed(genuine["candidate"], lambda a: cell(a).__setitem__("actual", dict(cell(a)["expected"], version=1, state="Approved")))
    stale = field(genuine["candidate"], subject=dict(SUBJECT, policy="old"))
    unknown = field(genuine["candidate"], producer="someone-else")
    always = lambda receipt: True
    assert aggregate_status([], SUBJECT, always) == "UNKNOWN"
    assert aggregate_status([good], SUBJECT, always) == "PASS"
    assert aggregate_status([bad], SUBJECT, always) == "FAIL"
    assert aggregate_status([good, bad], SUBJECT, always) == "CONFLICT"
    assert aggregate_status([good, stale], SUBJECT, always) == "PASS"
    assert aggregate_status([bad, stale], SUBJECT, always) == "FAIL"
    assert aggregate_status([stale], SUBJECT, always) == "STALE"
    assert aggregate_status([stale, unknown], SUBJECT, always) == "STALE"
    assert aggregate_status([unknown], SUBJECT, always) == "UNKNOWN"
    assert aggregate_status([good, bad, stale], SUBJECT, always) == "CONFLICT"


def test_an_unauthenticated_receipt_is_a_failure_even_if_it_would_pass(genuine):
    good = genuine["candidate"]
    assert aggregate_status([good], SUBJECT, lambda receipt: False) == "FAIL"
    assert aggregate_status([good, good], SUBJECT, lambda receipt: receipt is good and False) == "FAIL"
    calls = []
    assert aggregate_status([good], SUBJECT, lambda receipt: calls.append(receipt) or True) == "PASS" and calls == [good]
