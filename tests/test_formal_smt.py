"""Z3 policy-soundness proof (verification/smt): proofs, faithfulness and negative controls.

Tests marked `formal` take seconds each (whole differential runs, leave-one-out, a full report), so the default
(fast/coverage) pytest run deselects them (`-m "not formal"` in pyproject) and the `formal_smt` session selects
them (`pytest -m formal`). The unmarked tests run in well under a second each.
"""
import json
import sys
from pathlib import Path

import pytest
from eija_studio.domain import models, policy
from eija_studio.domain.models import Transition, Workflow

from verification import formal_report as fr

pytest.importorskip("z3", reason="z3-solver is in the `smt` extra; without it the proof is NOT_RUN, not passed")

import z3
from verification.smt import differential as D
from verification.smt import prove
from verification.smt import vocabulary as V
from verification.smt.__main__ import NOT_RUN_EXIT, main

formal = pytest.mark.formal


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


# ---- the requirement must not move when the kernel constants it is checked against move --------------------

def test_requirement_literals_are_pinned_to_the_documented_values():
    """A deliberate change to FORBIDDEN or BASE_GUARDS fails here first, so the requirement is edited on purpose."""
    assert tuple(sorted(policy.forbidden_effects())) == V.REQUIRED_FORBIDDEN_EFFECTS
    assert tuple(sorted(models.BASE_GUARDS)) == V.REQUIRED_BASE_GUARDS
    effects = policy.effects_table()
    assert set(V.DECISION_AUDIT) <= set(effects["Approve"]) | set(effects["Reject"])


def test_weakening_the_kernel_forbidden_effects_refutes_an_invariant_instead_of_moving_the_goalposts(monkeypatch):
    """Negative control for the shared-constant weakness: the encoded policy follows the kernel constant, the
    requirement does not, so dropping one forbidden effect from the kernel must make the proof fail."""
    monkeypatch.setattr(V, "FORBIDDEN_EFFECTS", ("PaymentCaptured",))
    by_id = {v.id: v.status for v in prove.prove_invariants()}
    assert by_id["INV-FORBIDDEN-EFFECTS-EXCLUDED"] == "refuted"


def test_weakening_the_kernel_base_guards_refutes_an_invariant(monkeypatch):
    monkeypatch.setattr(V, "BASE_GUARD_SET", frozenset(V.REQUIRED_BASE_GUARDS) - {"operation_binding"})
    by_id = {v.id: v.status for v in prove.prove_invariants()}
    assert by_id["INV-MANDATORY-GUARDS-PRESENT"] == "refuted"


# ---- faithfulness of the encoding is sampled: check the sample can fail ---------------------------------

@formal
def test_encoding_agrees_with_real_check_policy_and_covers_every_clause():
    r = D.run(random_mutants=60, random_fresh=60)
    assert r.agrees, (r.code_disagreements[:1], r.invariant_disagreements[:1], r.soundness_violations[:1])
    assert r.accepted > 0 and r.unvalidated > 0            # both admitted candidates and validator-bypassing ones
    assert not r.clauses_never_fired and not r.clauses_never_silent


@formal
def test_differential_detects_an_unfaithful_encoding():
    """Negative control for the faithfulness check itself: a wrong encoding must NOT agree."""
    wrong = frozenset({"PROTECTED_STATE:Reject/from-without-recommendation"})  # a clause a draft encoding could omit
    r = D.run(random_mutants=0, random_fresh=0, drop_clauses=wrong, stop_at_first_disagreement=True)
    assert r.code_disagreements


@formal
def test_differential_detects_a_weakened_kernel_policy(monkeypatch):
    """If check_policy stops enforcing the Approve role, the encoded proof no longer describes it."""
    real = policy.check_policy
    monkeypatch.setattr(D, "check_policy", lambda wf: [e for e in real(wf) if e != "PROTECTED_AUTHORITY:Approve"])
    r = D.run(random_mutants=0, random_fresh=0, stop_at_first_disagreement=True)
    assert r.code_disagreements and r.soundness_violations


@formal
def test_removing_a_clause_yields_a_counterexample_rejected_by_the_real_policy():
    loo = prove.leave_one_out()
    assert all(c["counterexample_found"] for c in loo["named_controls"])
    assert not loo["inconsistent_witnesses"] and not loo["unknown"]
    assert 0 < loo["critical_even_if_validators_are_assumed"] <= loo["critical"]
    row = next(r for r in loo["rows"] if r["clause"] == "PROTECTED_AUTHORITY:Approve/role")
    assert "INV-TEACHER-NOT-DECIDER" in row["violated_invariants"]
    assert "PROTECTED_AUTHORITY:Approve" in policy.check_policy(_workflow(row["witness"]))


def _workflow(dump):
    return Workflow.model_construct(initial_state=dump["initial_state"], states=tuple(dump["states"]),
                                    transitions=tuple(Transition.model_construct(**t) for t in dump["transitions"]))


def test_unique_action_assumption_is_guarded_by_the_validator_and_no_longer_needed_by_the_policy():
    """Before domain packs, check_policy indexed transitions by action (last one wins), so a validator-bypassing duplicate
    hid a Teacher-held Approve. The pack-driven policy judges every transition: the duplicate is refused either way."""
    w = prove.assumption_witness()
    assert w["teacher_holds_approve_in_that_workflow"] and w["workflow_validator_rejects_it"]
    assert not w["unvalidated_duplicate_action_workflow_admitted_by_check_policy"]


# ---- drift alarm: semantic digest, not raw bytes --------------------------------------------------------

POLICY = Path(fr.KERNEL / "domain" / "policy.py")


def _digest(tmp_path, text, *, strip=True):
    path = tmp_path / "m.py"
    path.write_text(text, encoding="utf-8")
    return fr.semantic_sha256(path, strip_annotations=strip)


FUTURE = "from __future__ import annotations\n"


def test_semantic_digest_ignores_formatting_comments_docstrings_and_lazy_annotation_edits(tmp_path):
    original = POLICY.read_text(encoding="utf-8")
    reformatted = "# a comment\n" + original.replace("\n\n", "\n\n\n\n")
    assert _digest(tmp_path, reformatted) == _digest(tmp_path, original)
    # With `from __future__ import annotations` annotations are never evaluated, so editing them is not behaviour.
    before = FUTURE + "def f(x: int) -> int:\n    return x + 1\n"
    after = FUTURE + 'def f(x: "Any") -> None:\n    """doc"""\n    return x + 1\n'
    assert _digest(tmp_path, before) == _digest(tmp_path, after)


def test_semantic_digest_changes_on_any_executable_edit(tmp_path):
    original = POLICY.read_text(encoding="utf-8")
    weakened = original.replace('codes.append("UNSUPPORTED_ACTION")', 'pass')
    assert weakened != original and _digest(tmp_path, weakened) != _digest(tmp_path, original)
    assert _digest(tmp_path, "x = 1\n") != _digest(tmp_path, "x = 2\n")


@pytest.mark.parametrize(
    ("before", "after"),
    [
        # An import alias rebinds a builtin the policy calls (review of PR #25: a one-line backdoor the digest did not see).
        (FUTURE + "from typing import Any\n\ndef f(x: Any):\n    return sorted(x)\n",
         FUTURE + "from typing import Any, get_args as sorted\n\ndef f(x: Any):\n    return sorted(x)\n"),
        (FUTURE + "from collections.abc import Set\n", FUTURE + "from collections.abc import Set as frozenset\n"),
        (FUTURE + "import typing\n", FUTURE + "import typing as builtins\n"),
        # Without the future import annotations are evaluated at definition time, so they are behaviour.
        (FUTURE + "def f(x) -> int:\n    return x\n", "def f(x) -> int:\n    return x\n"),
        ("def f(x: int) -> int:\n    return x\n", "def f(x: g()) -> int:\n    return x\n"),
        ("def f(x) -> int:\n    return x\n", 'def f(x) -> globals().__setitem__("check_policy", lambda m: []):\n    return x\n'),
        ("class C:\n    a: int\n", "class C:\n    a: g()\n"),
    ],
)
def test_semantic_digest_sees_imports_and_evaluated_annotations_as_behaviour(tmp_path, before, after):
    assert _digest(tmp_path, before) != _digest(tmp_path, after)


def test_annotations_are_behaviour_for_modules_that_declare_pydantic_fields(tmp_path):
    a, b = "class M:\n    x: int = 1\n", "class M:\n    x: str = 1\n"
    assert _digest(tmp_path, a, strip=False) != _digest(tmp_path, b, strip=False)


def test_committed_snapshot_embeds_only_semantic_digests():
    doc = json.loads(prove.SNAPSHOT.read_text(encoding="utf-8"))
    assert set(doc["subject"]) == {"function", "sources_semantic_sha256"}


@formal
def test_a_failed_check_refuses_to_rewrite_the_snapshot(tmp_path, monkeypatch):
    """`--write-snapshot` must not launder a refuted invariant into the committed baseline."""
    monkeypatch.setattr(prove, "SNAPSHOT", tmp_path / "accepted_set.json")
    monkeypatch.setattr(prove, "prove_invariants", lambda: [prove.Verdict("INV-X", "x", "refuted", 0.0)])
    report = prove.build_report(differential_mutants=0, differential_fresh=0, write_snapshot=True)
    assert report["verdict"] == "FAIL" and not (tmp_path / "accepted_set.json").exists()
    detail = next(c["detail"] for c in report["checks"] if c["id"] == "committed_snapshot_has_no_drift")
    assert "NOT written" in detail


def test_missing_z3_reports_not_run_never_pass(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "z3", None)  # import z3 -> ImportError
    out = tmp_path / "smt.json"
    assert main(["--out", str(out)]) == NOT_RUN_EXIT
    assert json.loads(out.read_text())["verdict"] == "NOT_RUN"


def test_report_json_is_sorted_and_lf(tmp_path):
    fr.write(tmp_path / "x.json", {"b": 1, "a": {"d": 1, "c": 2}})
    raw = (tmp_path / "x.json").read_bytes()
    assert b"\r" not in raw and raw.index(b'"a"') < raw.index(b'"b"')


def test_platform_info_avoids_the_slow_wmi_query():
    assert fr.platform_info()["platform"] == sys.platform


# ---- leave-one-out: UNKNOWN or an unconfirmed witness is not "not critical" (review of PR #25) ----------------

@pytest.mark.parametrize(
    ("solver_result", "pydantic_accepts", "expected"),
    [
        ("sat", True, "critical"),            # a witness the REAL pydantic models accept: critical even with validators
        ("unsat", False, "not_critical"),     # proved: no validator-valid candidate exists
        ("unknown", False, "inconclusive"),   # timeout or unknown says nothing
        ("sat", False, "inconclusive"),       # pydantic_valid over-approximates: a rejected witness proves nothing either way
    ],
)
def test_validator_assumed_criticality_is_three_valued(solver_result, pydantic_accepts, expected):
    result = {"sat": z3.sat, "unsat": z3.unsat, "unknown": z3.unknown}[solver_result]
    assert prove.validators_assumed_status(result, pydantic_accepts) == expected


@formal
def test_leave_one_out_split_under_validators_is_pinned_and_has_no_inconclusive_row():
    loo = prove.leave_one_out()
    statuses = [r["under_validators"] for r in loo["rows"] if r["status"] == "critical"]
    assert loo["validators_inconclusive"] == [] and statuses.count("inconclusive") == 0
    assert (statuses.count("critical"), statuses.count("not_critical")) == (30, 36)
