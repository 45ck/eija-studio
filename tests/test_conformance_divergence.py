"""The generated conformance suite catches an app that stops matching its model, by behaviour alone (ADR-0242).

`verification.conformance.divergence` builds a real app that is wrong in one way, keeps the reviewed oracle, re-points
only its identity fields and reseals the build identity, then runs the app's own generated tests. These tests run a
few divergences of each family, including every one the suite used to miss, and the controls that keep the harness
honest: a resealed app with no divergence passes, and a divergence counts as caught only by a behavioural test.

Each divergence starts an app's whole generated suite in a fresh process, so the parametrized ones are marked `slow`
(issue #206). `nox -s conformance_divergence` (full tier) runs all of them and more, and requires none to be missed.
"""
from __future__ import annotations

import json

import pytest

from eija_studio.application.app_runs import journeys
from eija_studio.application.appgen import valid_values
from verification.conformance.divergence import (CODE, EQUIVALENT, Divergence, _assemble, _divergent, _workflow,
                                                  divergences, judge, run_suite, shipped, variants)

SUBJECTS = {s.name: s for s in shipped() + variants()}
IDENTITY = {"test_built_from_the_same_model", "setUpClass"}


def _reviewed(name: str):
    subject = SUBJECTS[name]
    return subject, _assemble(subject.pack, subject.model, subject.data)[1]


def _find(name: str, kind: str, ref: str = "") -> Divergence:
    return next(d for d in divergences(SUBJECTS[name]) if d.kind == kind and d.ref.startswith(ref))


def test_a_resealed_app_with_no_divergence_passes():
    """The control: resealing and re-pointing identity alone never fails the suite, so a failure is the divergence."""
    subject, reviewed = _reviewed("library-loan")
    code, failed, text = run_suite(_divergent(subject, Divergence("none", "none", "no divergence"), reviewed))
    assert code == 0 and not failed, text[-2000:]


def test_identity_is_re_pointed_so_only_behaviour_can_fail():
    subject, reviewed = _reviewed("library-loan")
    files = _divergent(subject, _find("library-loan", "initial-state-moved"), reviewed)
    oracle = json.loads(files["tests/oracle.json"])
    assert oracle["model_hash"] != reviewed["model_hash"]
    assert oracle["cases"] == reviewed["cases"] and oracle["create_cases"] == reviewed["create_cases"]


# Each was MISSED before ADR-0242: the old suite seeded every record straight into a state, compared effect names only,
# never started a record through the app, never asked what it offers, and never spoke HTTP.
ONCE_MISSED = [
    ("library-loan", "initial-state-moved", ""),
    ("library-loan", "recipient-changed", "effect:Notification:MemberNotified"),
    ("library-loan", "effect-kind-changed", "effect:Audit:LoanCancelled"),
    ("library-loan", "attribute-length-changed", "attribute:Loan.memberCard"),
    ("library-loan", "attribute-choice-dropped", "attribute:Loan.format"),
    ("library-loan", "attribute-required-flipped", "attribute:Loan.renewals"),
    ("library-loan+features", "association-unbuilt", "association:Loan-Member"),
    ("refund-desk+features", "value-guard-flipped", ""),
    ("refund-desk+features", "separation-law-dropped", ""),
    ("refund-desk+features", "initiator-added", ""),
]


@pytest.mark.slow
@pytest.mark.parametrize(("name", "kind", "ref"), ONCE_MISSED, ids=[f"{n}:{k}" for n, k, _ in ONCE_MISSED])
def test_model_divergences_are_caught_by_behaviour(name, kind, ref):
    subject, reviewed = _reviewed(name)
    outcome = judge(subject, _find(name, kind, ref), reviewed)
    assert outcome.status == "CAUGHT", outcome
    assert set(outcome.failed) - IDENTITY, outcome.failed


CODE_ONCE_MISSED = {  # fault: the subject whose app reaches the code it breaks
    "notification sent to nobody": "library-loan", "notification names no record": "library-loan",
    "created record not stamped with its data model": "library-loan", "revoked actors may start a record": "library-loan",
    "offered actions ignore the actor": "library-loan", "history shows every record's steps": "library-loan",
    "HTTP drops the expected version": "library-loan", "HTTP drops the operation id": "library-loan",
    "HTTP refusals answered as success": "library-loan", "HTTP drops record values": "library-loan",
    "guards read no record values": "refund-desk+features", "who acted is not remembered": "refund-desk+features",
    "anyone may start a record": "refund-desk+features", "offered actions ignore value guards": "refund-desk+features",
    "offered actions ignore separation of duties": "refund-desk+features",
    "rule table shows one source per action": "library-loan+features",
}


@pytest.mark.slow
@pytest.mark.parametrize("name", sorted(CODE_ONCE_MISSED))
def test_code_divergences_are_caught_by_behaviour(name):
    subject, reviewed = _reviewed(CODE_ONCE_MISSED[name])
    outcome = judge(subject, _find(subject.name, "code", f"code:{name}"), reviewed)
    assert outcome.status == "CAUGHT", outcome
    assert set(outcome.failed) - IDENTITY, outcome.failed


def test_a_fault_in_code_a_pack_never_reaches_is_not_counted():
    """No shipped pack has value guards, so that fault is not applicable to library-loan, rather than missed."""
    assert not any(d.ref == "code:guards read no record values" for d in divergences(SUBJECTS["library-loan"]))
    assert any(d.ref == "code:guards read no record values" for d in divergences(SUBJECTS["refund-desk+features"]))


def test_every_seeded_fault_still_matches_the_templates():
    """A template edit that moves a seeded fault's text would silently drop it from the check: refuse that."""
    subject = SUBJECTS["library-loan"]
    files = _assemble(subject.pack, subject.model, subject.data)[0]
    for name, (path, before, _) in CODE.items():
        assert before in files[path], name


def test_one_model_and_one_code_divergence_are_caught_in_the_fast_tier():
    subject, reviewed = _reviewed("library-loan")
    for divergence in (_find("library-loan", "initial-state-moved"), _find("library-loan", "code", "code:notification sent to nobody")):
        outcome = judge(subject, divergence, reviewed)
        assert outcome.status == "CAUGHT" and set(outcome.failed) - IDENTITY, outcome


def test_only_a_listed_equivalence_may_go_uncaught():
    subject, reviewed = _reviewed("library-loan")
    outcome = judge(subject, _find("library-loan", "forbidden-effect-dropped"), reviewed)
    assert outcome.status in ("EQUIVALENT", "REFUSED") and set(EQUIVALENT) == {"forbidden-effect-dropped"}


def test_a_journey_starts_on_a_record_created_just_now():
    """Review regression (PR #247): a journey's record is created by the app and acted on at once, so a time event
    leaving the initial state is not yet due; the oracle once assumed every wait had passed and expected a commit."""
    subject = SUBJECTS["refund-desk"]
    first = next(t for t in subject.model.transitions if t.from_state == subject.model.initial_state)
    timed = _workflow(subject.model, lambda raw: next(t for t in raw["transitions"] if t["id"] == first.id).update(
        after={"amount": 2, "unit": "days"}))
    assert not isinstance(timed, str)
    found = journeys(subject.pack, timed, valid_values(subject.data))
    assert found and all(step["expect"].get("code") != "TIMER_NOT_DUE" for j in found for step in j["steps"])
    assert first.id not in {j["transition"] for j in found}
