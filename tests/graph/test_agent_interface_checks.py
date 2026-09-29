"""Oracles for docs/weave/design/agent-interface-and-context-packs.md.

They assert the measured facts the design relies on, on small domains so they run in seconds. The full
report is `python graph/bench/agent_interface_checks.py`. A missing prerequisite (the impact-ranking
reference, the kernel) skips, which is the pytest spelling of NOT_RUN; a skip is never a pass.
"""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[2] / "graph" / "bench" / "agent_interface_checks.py"
spec = importlib.util.spec_from_file_location("agent_interface_checks", BENCH)
checks = importlib.util.module_from_spec(spec)
sys.modules["agent_interface_checks"] = checks
spec.loader.exec_module(checks)

needs_reference = pytest.mark.skipif(checks.load_reference() is None, reason="NOT_RUN: impact_math_reference.py not present")


def test_writer_reproduces_the_identity_aspects_golden_vectors() -> None:
    r = checks.identity_vector_conformance()
    if r["status"] == "NOT_RUN":
        pytest.skip(r["reason"])
    assert r["jcs_bytes_equal"][0] == r["jcs_bytes_equal"][1]
    assert r["node_hash_equal"][0] == r["node_hash_equal"][1]
    assert r["must_reject_cases_rejected"] == [3, 3]


@needs_reference
def test_pass_k_estimator_is_unbiased_and_the_plug_in_is_not() -> None:
    r = checks.passk_estimator_exactness(n=5)
    assert r["status"] == "MEASURED"
    assert r["unbiased_pass_hat_k"] is True and r["unbiased_pass_at_k"] is True
    assert r["plugin_p_hat_pow_k_always_above_truth"] is True
    assert r["plugin_bias_at_q_1_2_n_8_k_4"] == "203/4096"


@needs_reference
def test_same_pass_at_1_hides_different_reliability() -> None:
    r = checks.passk_two_agents()
    assert r["total_success_rate_a"] == r["total_success_rate_b"] == "3/4"
    assert r["pass_hat_k_a"]["1"] == r["pass_hat_k_b"]["1"] == "3/4"
    assert Fraction(r["pass_hat_k_a"]["8"]) == 0 and Fraction(r["pass_hat_k_b"]["8"]) == Fraction(7, 10)


def test_sample_size_table_is_a_prediction_and_shrinks_with_trials() -> None:
    r = checks.tasks_needed_table()
    assert r["status"] == "PREDICTION"
    by = {(x["sigma_delta"], x["trials_per_task_n"]): x["tasks_needed"] for x in r["rows"]}
    assert by[(0.15, 1)] > by[(0.15, 3)] > by[(0.15, 5)] > by[(0.15, 10)]
    assert by[(0.15, 5)] == 78
    mde = {x["tasks"]: x["minimum_detectable_difference"] for x in r["minimum_detectable_difference_rows"]}
    assert mde[78] == 0.0996 and mde[20] > mde[78] > mde[866]


@needs_reference
def test_context_pack_is_identical_under_shuffled_insertion_order() -> None:
    r = checks.context_pack_determinism(shuffles=6)
    assert r["distinct_packs"] == 1
    assert r["verify_flags_only_changed_item"] is True
    assert r["budget_too_small_reports_needed_cost"] is True


@needs_reference
def test_pack_never_exceeds_budget_and_reports_omissions() -> None:
    nodes, edges, cost = checks.synthetic_graph()
    seeds = [nodes[3], nodes[101]]
    pack = checks.build_pack(nodes, edges, cost, seeds, 1500)
    assert pack["spent"] <= 1500
    assert pack["complete"] is (pack["omitted_count"] == 0)
    assert len({it["id"] for it in pack["items"]}) == len(pack["items"])
    # mandatory obligations come first and are never dropped
    roles = [it["role"] for it in pack["items"]]
    assert roles == sorted(roles, key=lambda r: r != "mandatory")


def test_run_log_chain_detects_every_tamper_and_ignores_key_order() -> None:
    r = checks.run_log_chain(length=40)
    assert r["single_field_edits_detected_at_the_edited_index"] == [40, 40]
    assert r["adjacent_swaps_detected"] == [39, 39]
    assert r["truncation_detected"] is True
    assert r["dict_key_order_does_not_change_head"] is True
    assert r["naive_concatenation_collides"] is True and r["json_structured_domain_hash_collides"] is False
    assert r["same_record_under_two_domain_tags_collides"] is False
    assert r["jcs_orders_astral_before_fullwidth_tilde"] is True


def test_jcs_subset_rejects_floats_unsafe_integers_and_lone_surrogates() -> None:
    for bad in (1.0, 2**53, "\ud800"):
        with pytest.raises((TypeError, ValueError)):
            checks.jcs_subset({"a": bad})
    assert checks.jcs_subset({"b": 1, "a": [True, None, "x"]}) == '{"a":[true,null,"x"],"b":1}'
    with pytest.raises(ValueError):
        checks.dhash("not-a-tag", {})


def test_replay_of_recorded_tool_calls_is_exact_on_the_same_snapshot() -> None:
    pytest.importorskip("pydantic")
    r = checks.replay_of_tool_calls()
    assert r["replay_same_snapshot_equal"][0] == r["replay_same_snapshot_equal"][1]
    assert r["graph_root_changes_when_one_edge_is_removed"] is True
    assert r["responses_that_differ_after_drift_because_they_carry_graph_root"] >= r["responses_whose_affected_set_actually_changed"]


def test_sqlite_instruction_budget_is_stable_and_aborts() -> None:
    r = checks.sqlite_instruction_budget()
    assert r["handler_calls_same_insertion_order_5_runs_distinct"] == 1
    assert r["aborts_when_half_the_budget_is_allowed"] is True


def test_rename_probe_partitions_text_matches() -> None:
    r = checks.rename_probe(names=("receipt", "verify"))
    for row in r["rows"].values():
        assert row["word_boundary_text_matches"] == row["code_name_tokens"] + row["in_strings_docstrings_comments"]
        assert row["code_tokens_after_dot"] <= row["code_name_tokens"]


def test_kernel_dry_run_is_pure_and_matches_the_contract_example() -> None:
    pytest.importorskip("pydantic")
    r = checks.kernel_dry_run_example()
    assert r["input_model_unchanged"] is True
    assert r["set_rejection_source_before_enable"] == {"verdict": "REJECTED", "code": "MEANING_REQUIRED"}
    assert r["enable_recommendation"]["changed_actions"] == ["Approve", "Recommend", "Reject"]
    assert r["enable_recommendation"]["closure_size"] == 20


def test_report_sections_are_deterministic_within_a_process() -> None:
    assert checks.tasks_needed_table() == checks.tasks_needed_table()
    assert checks.run_log_chain(length=10) == checks.run_log_chain(length=10)
