"""Z3 policy-soundness proof (verification/smt): proofs, faithfulness and negative controls."""
import sys
from pathlib import Path

import pytest

pytest.importorskip("z3", reason="z3-solver is in the `smt` extra; without it the proof is NOT_RUN, not passed")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # `verification/` is tooling, not a shipped package

from verification.smt import differential as D, prove  # noqa: E402
from verification import formal_report as fr  # noqa: E402
from eija_studio.domain import policy  # noqa: E402


def test_every_authority_invariant_is_proved_over_the_grammar():
    verdicts = prove.prove_invariants()
    assert len(verdicts) >= 10
    assert {v.status for v in verdicts} == {"proved"}, [v for v in verdicts if v.status != "proved"]


def test_proof_is_not_vacuous():
    v = prove.non_vacuity()
    assert v["policy_admits_some_candidate"] and all(v["each_invariant_falsifiable_by_some_candidate"].values())


def test_accepted_set_is_exactly_baseline_plus_two_rejection_sources():
    a = prove.enumerate_accepted()
    assert a["enumeration_complete"] and a["count"] == 3 and a["equals_kernel_reachable_set"]
    assert sorted(x["label"] for x in a["accepted"]) == a["expected_labels"]


def test_committed_snapshot_matches_regeneration():
    assert prove.drift(prove.enumerate_accepted()) is None


def test_encoding_agrees_with_real_check_policy_and_covers_every_clause():
    r = D.run(random_mutants=60, random_fresh=60)
    assert r.agrees, (r.code_disagreements[:1], r.invariant_disagreements[:1], r.soundness_violations[:1])
    assert r.accepted > 0 and r.unvalidated > 0            # both admitted candidates and validator-bypassing ones
    assert not r.clauses_never_fired and not r.clauses_never_silent


def test_differential_detects_an_unfaithful_encoding():
    """Negative control for the faithfulness check itself: a wrong encoding must NOT agree."""
    wrong = frozenset({"PROTECTED_STATE:Reject/from-without-recommendation"})  # the clause my first draft omitted
    r = D.run(random_mutants=0, random_fresh=0, drop_clauses=wrong)
    assert r.code_disagreements


def test_differential_detects_a_weakened_kernel_policy(monkeypatch):
    """If check_policy stops enforcing the Approve role, the encoded proof no longer describes it."""
    real = policy.check_policy
    monkeypatch.setattr(D, "check_policy", lambda wf: [e for e in real(wf) if e != "PROTECTED_AUTHORITY:Approve"])
    r = D.run(random_mutants=0, random_fresh=0)
    assert r.code_disagreements and r.soundness_violations


def test_removing_a_clause_yields_a_counterexample_rejected_by_the_real_policy():
    loo = prove.leave_one_out()
    assert all(c["counterexample_found"] for c in loo["named_controls"])
    assert not loo["inconsistent_witnesses"] and not loo["unknown"]
    row = next(r for r in loo["rows"] if r["clause"] == "PROTECTED_AUTHORITY:Approve/role")
    assert "INV-TEACHER-NOT-DECIDER" in row["violated_invariants"]
    assert "PROTECTED_AUTHORITY:Approve" in policy.check_policy(_workflow(row["witness"]))


def _workflow(dump):
    from eija_studio.domain.models import Transition, Workflow
    return Workflow.model_construct(initial_state=dump["initial_state"], states=tuple(dump["states"]),
                                    transitions=tuple(Transition.model_construct(**t) for t in dump["transitions"]))


def test_unique_action_assumption_is_real_and_guarded_by_the_validator():
    w = prove.assumption_witness()
    assert w["unvalidated_duplicate_action_workflow_admitted_by_check_policy"] and w["workflow_validator_rejects_it"]


def test_missing_z3_reports_not_run_never_pass(tmp_path, monkeypatch):
    from verification.smt.__main__ import NOT_RUN_EXIT, main
    monkeypatch.setitem(sys.modules, "z3", None)  # import z3 -> ImportError
    out = tmp_path / "smt.json"
    assert main(["--out", str(out)]) == NOT_RUN_EXIT
    import json
    assert json.loads(out.read_text())["verdict"] == "NOT_RUN"


def test_report_json_is_sorted_and_lf(tmp_path):
    fr.write(tmp_path / "x.json", {"b": 1, "a": {"d": 1, "c": 2}})
    raw = (tmp_path / "x.json").read_bytes()
    assert b"\r" not in raw and raw.index(b'"a"') < raw.index(b'"b"')
