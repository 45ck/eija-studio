"""Oracles for graph/bench/rule_language_bench.py (ADR-0095, rule-language decision).

Small sizes only: the full benchmark (10^5 nodes, pySHACL up to 2,000) is run by hand and its result is committed in
graph/bench/results/rule-language.json. pySHACL cases skip, which is NOT_RUN, when the package is missing.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "graph" / "bench" / "rule_language_bench.py"
spec = importlib.util.spec_from_file_location("weave_rule_language_bench", BENCH)
bench = importlib.util.module_from_spec(spec)
sys.modules["weave_rule_language_bench"] = bench
spec.loader.exec_module(bench)

DECLARED_READS = {  # what the rules of the benchmark declare they read; the authorizer must agree exactly
    "R1": {"requirement", "verifies"},
    "R2": {"changed", "depends_on"},
    "R3": {"refines", "requirement", "verifies"},
    "R4": {"form_of"},
}
PY = {"R1": bench.py_r1, "R2": bench.py_r2, "R3": bench.py_r3, "R4": bench.py_r4}


@pytest.mark.parametrize("n", [200, 600])
def test_python_sql_and_datalog_agree(n: int) -> None:
    f = bench.make_facts(n)
    db = bench.sql_load(f)
    for rule in bench.RULES:
        expected = PY[rule](f)
        assert bench.sql_run(db, rule, n * 2 + 10) == expected, rule
        assert bench.datalog_run(rule, f) == expected, rule


def test_the_rules_find_something_and_not_everything() -> None:
    f = bench.make_facts(600)
    sizes = {r: len(PY[r](f)) for r in bench.RULES}
    assert all(0 < v < 600 for v in sizes.values()), sizes  # a vacuous rule would agree everywhere


def test_recursion_guard_trips_instead_of_looping() -> None:
    # An artificially small LIMIT stops the recursive CTE; the result is then incomplete, which the engine must
    # notice because the guard is the number of nodes plus one and a full closure never reaches it.
    f = bench.make_facts(200)
    db = bench.sql_load(f)
    full = bench.sql_run(db, "R2", 200 * 2 + 10)
    cut = bench.sql_run(db, "R2", 2)
    assert len(cut) < len(full)


@pytest.mark.parametrize("rule", bench.RULES)
def test_declared_reads_equal_actual_reads(rule: str) -> None:
    db = bench.sql_load(bench.make_facts(200))
    seen: set[str] = set()

    def auth(action, arg1, _arg2, _db, _src):
        if action == sqlite3.SQLITE_READ:
            seen.add(arg1)
        return sqlite3.SQLITE_OK

    db.set_authorizer(auth)
    list(db.execute(bench.SQL[rule], {"guard": 500} if ":guard" in bench.SQL[rule] else {}))
    assert seen == DECLARED_READS[rule]


def test_deny_by_default_rejects_an_undeclared_read() -> None:
    db = bench.sql_load(bench.make_facts(200))

    def deny(action, arg1, _arg2, _db, _src):
        if action == sqlite3.SQLITE_READ and arg1 not in DECLARED_READS["R1"]:
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    db.set_authorizer(deny)
    with pytest.raises(sqlite3.DatabaseError):
        list(db.execute(bench.SQL["R3"], {"guard": 500}))


def test_facts_and_results_do_not_depend_on_the_hash_seed(tmp_path: Path) -> None:
    code = (
        "import sys, hashlib, importlib.util;"
        f"s=importlib.util.spec_from_file_location('b', r'{BENCH}');b=importlib.util.module_from_spec(s);sys.modules['b']=b;s.loader.exec_module(b);"
        "f=b.make_facts(200);db=b.sql_load(f);"
        "out=[b.py_r1(f),b.py_r2(f),b.py_r3(f),b.py_r4(f),b.datalog_run('R3',f),b.sql_run(db,'R3',410)];"
        "print(hashlib.sha256(repr(out).encode()).hexdigest())"
    )
    digests = set()
    for seed in ("0", "1", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "TMP": str(tmp_path), "TEMP": str(tmp_path)}
        cp = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, check=True, encoding="utf-8")
        digests.add(cp.stdout.strip())
    assert len(digests) == 1  # D-07


def test_committed_result_records_agreement_for_every_size_and_rule() -> None:
    res = json.loads((ROOT / "graph" / "bench" / "results" / "rule-language.json").read_text(encoding="utf-8"))
    for size, rules in res["agreement"].items():
        for rule, row in rules.items():
            assert row["engines_identical"] is True, (size, rule)
            assert {"python", "sql", "datalog"} <= set(row["engines_run"]), (size, rule)


def test_shacl_agrees_with_the_other_engines_on_a_small_graph() -> None:
    pytest.importorskip("pyshacl")
    n = 200
    f = bench.make_facts(n)
    for rule in ("R1", "R4"):
        out = bench.shacl_run(rule, n)
        if out["status"] != "RAN":
            pytest.skip(f"NOT_RUN: {out}")
        assert out["violations"] == PY[rule](f), rule
