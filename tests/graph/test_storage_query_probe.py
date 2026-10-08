"""Oracles for docs/weave/design/storage-and-query.md (deterministic block only; no timing, no engines).

Every assertion here backs a sentence in the design doc or ADR-0091. Timing and the optional embedded
graph engine are not exercised here (the engine probe is memory-capped and run by hand, see graph/bench/PLAN.md).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

BENCH = Path(__file__).resolve().parents[2] / "graph" / "bench" / "storage_query_probe.py"
spec = importlib.util.spec_from_file_location("storage_query_probe", BENCH)
sq = importlib.util.module_from_spec(spec)
sys.modules["storage_query_probe"] = sq
spec.loader.exec_module(sq)


def test_witness_is_lexicographically_smallest_shortest_path_and_order_independent() -> None:
    r = sq.witness_checks(graphs=120)
    assert r["mismatches_vs_bruteforce_oracle"] == 0
    assert r["mismatches_under_shuffled_edge_order"] == 0
    assert r["graphs_where_first_parent_bfs_gives_a_different_witness"] == 0


def test_union_terminates_only_on_the_node_column() -> None:
    r = sq.cte_termination()
    assert r["terminated_by_itself"]["UNION on node only"] is True
    assert r["rows_returned"]["UNION on node only"] == 4
    assert r["terminated_by_itself"]["UNION carrying a path column"] is False
    assert r["terminated_by_itself"]["UNION carrying a depth column"] is False
    assert r["terminated_by_itself"]["UNION ALL, no guard except LIMIT"] is False


def test_index_identity_is_the_dump_not_the_file() -> None:
    r = sq.file_bytes_vs_insertion_order()
    for layout in r.values():
        assert layout["distinct_logical_dump_sha256"] == 1
        assert layout["same_shuffle_built_twice_file_bytes_equal"] is True
    # Documented reason for S2: insertion order changes file bytes.
    assert r["rowid_tables"]["distinct_file_sha256_over_6_builds"] > 1


def test_total_order_by_gives_one_result_order() -> None:
    r = sq.row_order_without_order_by()
    for layout in ("without_rowid", "rowid_tables"):
        assert r[layout]["distinct_orders_closure_with_total_order_by"] == 1


def test_violation_query_returns_exactly_the_seeded_uncovered_set() -> None:
    assert sq.query_correctness(n_edges=8000)["violation_query_rows_equal_seeded_set"] is True


def test_collation_facts_used_by_the_design() -> None:
    r = sq.collation_pitfalls()
    assert r["python_sorted_equals_sqlite_binary_order"] is True
    assert r["utf16_code_unit_order_equals_codepoint_order"] is False  # RFC 8785 key order differs for astral characters
    assert r["sqlite_LIKE_A_a_is_case_insensitive"] is True


def test_recorded_deterministic_block_hash_matches_its_content() -> None:
    p = BENCH.parent / "results" / "storage-query-probe.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    blob = json.dumps(d["deterministic"], sort_keys=True, indent=1, ensure_ascii=False)
    assert sq.sha(blob.encode("utf-8")) == d["deterministic_sha256"]
