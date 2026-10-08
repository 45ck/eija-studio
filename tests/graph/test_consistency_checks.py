"""Oracles for docs/weave/design/consistency-and-sync.md and graph/schema/transformations.md.

They assert the measured facts the design relies on: the keyed three-way merge laws, the invariants a clean
merge does not preserve, the lens laws (and that the suite fails on broken translators), and how git's line
merge behaves on sorted line files. A missing prerequisite (git, the okf worktree) gives a skip, which is the
pytest spelling of NOT_RUN; it is never a pass. Results are samples or exhaustive enumerations of small
domains, not proofs for all inputs.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[2] / "graph" / "bench" / "consistency_checks.py"
spec = importlib.util.spec_from_file_location("consistency_checks", BENCH)
checks = importlib.util.module_from_spec(spec)
sys.modules["consistency_checks"] = checks
spec.loader.exec_module(checks)


def test_keyed_merge_is_symmetric_idempotent_identity_and_associative_when_defined() -> None:
    r = checks.keyed_merge_laws(trials=600)
    assert r["status"] == "MEASURED"
    assert set(r["passes"].values()) == {600}, r["passes"]
    assert r["trials_defined"] > 300 and r["trials_with_conflict"] > 20  # both branches of the law are exercised


def test_merge3_conflict_cases_are_explicit() -> None:
    base = {"a": "1", "b": "1"}
    merged, conflicts = checks.merge3(base, {"a": "2", "b": "1"}, {"a": "3", "b": "1"})
    assert merged == {"b": "1"} and [c["key"] for c in conflicts] == ["a"]
    # delete versus edit conflicts; identical edits and identical deletes do not (pseudo conflicts)
    assert checks.merge3(base, {"b": "1"}, {"a": "2", "b": "1"})[1][0]["key"] == "a"
    assert checks.merge3(base, {"a": "2", "b": "1"}, {"a": "2", "b": "1"})[1] == []
    assert checks.merge3(base, {"b": "1"}, {"b": "1"}) == ({"b": "1"}, [])


def test_clean_keyed_merge_does_not_preserve_uniqueness_or_referential_integrity_but_does_for_inserts() -> None:
    r = checks.non_confluent_invariants()["scenarios"]
    assert r["control_insert_only"]["merged_structure"] == "valid"
    for name in ("unique_action_specific_value", "foreign_key_delete_vs_insert"):
        assert r[name]["keyed_merge_conflicts"] == 0
        # computed, not assumed: each side passes the Workflow constructor, the merge does not
        assert r[name]["ours_structure_errors"] == [] and r[name]["theirs_structure_errors"] == [], name
        assert r[name]["merged_structure"] == "invalid" and r[name]["emergent_structure_errors"], name
    # the control (insert only) introduces no policy finding that neither parent had
    assert r["control_insert_only"]["emergent_policy_findings_when_merged_valid"] == []


def test_lens_laws_hold_for_the_reference_translator_and_fail_for_broken_ones() -> None:
    r = checks.lens_laws_on_kernel_alphabet()
    assert checks._law_failures(r) == []
    assert r["L5_order"]["distinct_batch_translator_results"] == 1
    assert r["L5_order"]["naive_input_order_failures"] > 0  # input order matters without dependency ordering
    # the kernel completes an edit: the amendment is reported, not silent
    amend = r["L2_amendments_reported_to_human"]["baseline:add_edge/Recommend/Submitted/Recommended"]
    assert amend["amended_edges_added"] and amend["amended_edges_removed"]
    for law in ("L2b_putgetput_replay_is_noop", "L6_typed_non_commutation", "L10_identity_by_id"):
        assert r[law]["pairs"] > 0 and r[law]["pass"] == r[law]["pairs"], law
    n = checks.lens_negative_controls()
    assert n["reference_failures"] == []
    for bad in ("bad_getput", "bad_putget", "bad_layout", "bad_unapplicable"):
        assert n[bad + "_detected_by"], bad


def test_pure_checks_are_byte_identical_between_runs() -> None:
    names = ["keyed_merge_laws", "non_confluent_invariants", "lens_laws_on_kernel_alphabet", "lens_negative_controls"]
    a = json.dumps(checks.report(names), sort_keys=True)
    b = json.dumps(checks.report(names), sort_keys=True)
    assert a == b


@pytest.mark.skipif(not checks._git_ok(), reason="git not found (NOT_RUN)")
def test_git_line_merge_on_sorted_line_files_versus_keyed_merge() -> None:
    r = checks.git_line_merge_vs_keyed(trials=8, n=10)
    assert r["status"] == "MEASURED"
    assert set(r["gap_distance_rule_n12"]) == {str(d) for d in range(11)}  # n=10 base lines gives gaps 0..10; every distance reported, not only 1 to 3
    for name, row in r.items():
        if name.startswith("A_sorted_set_adds"):
            assert row["keyed_conflicts"] == 0
            assert row["git_clean_equals_keyed_result"] == row["git_clean_merges"]
    b = r["B_append_only_sequence_numbers"]
    assert b["git_text_conflicts"] == 8 and b["git_union_yields_duplicate_seq"] == 8
    c = r["C_edit_two_distinct_records"]
    assert c["keyed_conflicts"] == 0 and c["git_clean_equals_keyed_result"] == c["git_clean_merges"]


def test_okf_generated_block_rewriter_is_idempotent_and_replaces_only_generated_regions() -> None:
    r = checks.okf_complement_preservation()
    if r["status"] == "NOT_RUN":
        pytest.skip(r["reason"])
    for name, case in r["cases"].items():
        assert case["idempotent"] and case["generated_regions_replaced"], name
    assert r["cases"]["plain_notes"]["human_text_preserved"]
