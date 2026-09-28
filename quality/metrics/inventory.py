"""Test inventory (static, ast) and statement/branch coverage (coverage.py JSON).

The inventory counts what the source of the tests declares; it is not a measure of test QUALITY. An
assertion count says a check exists, not that it can fail (mutation analysis is a separate lane). Layer
attribution is by import: a test file "touches" a layer directly when it imports a module of that layer,
and transitively when the import graph reaches the layer from what it imports.

Coverage is read from `reports/coverage/coverage.json` when present (produced by
`python -m quality.metrics coverage`, which runs the suite under coverage.py) and otherwise reported
NOT_RUN. A line executed by a test is not a line verified: coverage is necessary, not sufficient.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import grimp

from . import ROOT
from .common import MEASURED, measured, not_run, r3, rel, write_text
from .structure import PACKAGE, layer_of

TESTS = ROOT / "tests"
COVERAGE_JSON = ROOT / "reports" / "coverage" / "coverage.json"
COVERAGE_DATA = ROOT / "reports" / "coverage" / ".coverage"
COVERAGE_META = ROOT / "reports" / "coverage" / "coverage.meta.json"
SRC = ROOT / "src" / PACKAGE
CRLF, LF = bytes([13, 10]), bytes([10])


def tree_fingerprint() -> str:
    """SHA-256 over every `*.py` file of the measured package and of tests/ (path + LF-normalised bytes).

    Binds a coverage report to the code and tests it was measured on. It establishes that the tree has not
    changed since the coverage run; it does not say the coverage run was complete or that its tests passed.
    """
    digest = hashlib.sha256()
    for path in sorted([*SRC.rglob("*.py"), *TESTS.rglob("*.py")]):
        digest.update(path.relative_to(ROOT).as_posix().encode() + bytes(1))
        digest.update(path.read_bytes().replace(CRLF, LF) + bytes(1))
    return digest.hexdigest()


def _is_test_function(node: ast.AST) -> bool:
    return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test")


def _parametrize_factor(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Product of literal argvalue counts of `@pytest.mark.parametrize` decorators (1 if not literal)."""
    factor = 1
    for dec in fn.decorator_list:
        if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "parametrize" and len(dec.args) >= 2:
            values = dec.args[1]
            if isinstance(values, (ast.List, ast.Tuple)):
                factor *= max(1, len(values.elts))
    return factor


def _is_assertion_call(node: ast.Call) -> bool:
    name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
    return name.startswith("assert") and name != "assert_"


def _raises_blocks(node: ast.AST) -> int:
    n = 0
    for w in ast.walk(node):
        if isinstance(w, (ast.With, ast.AsyncWith)):
            for item in w.items:
                call = item.context_expr
                if isinstance(call, ast.Call) and getattr(call.func, "attr", "") in {"raises", "warns"}:
                    n += 1
    return n


def _imported_modules(tree: ast.AST) -> set[str]:
    found: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.level == 0 and n.module.split(".")[0] == PACKAGE:
            found.add(n.module)
            found.update(f"{n.module}.{a.name}" for a in n.names)
        elif isinstance(n, ast.Import):
            found.update(a.name for a in n.names if a.name.split(".")[0] == PACKAGE)
    return found


def scan_file(path: Path) -> dict:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    funcs = [n for n in ast.walk(tree) if _is_test_function(n)]
    asserts = sum(isinstance(n, ast.Assert) for f in funcs for n in ast.walk(f))
    asserts += sum(isinstance(n, ast.Call) and _is_assertion_call(n) for f in funcs for n in ast.walk(f))
    return {"file": rel(path), "tests": sum(_parametrize_factor(f) for f in funcs), "test_functions": len(funcs),
            "asserts": asserts, "raises_blocks": sum(_raises_blocks(f) for f in funcs),
            "imports": sorted(_imported_modules(tree))}


def collected_count(python: str = sys.executable, timeout: int = 180) -> int | None:
    """Number of tests pytest itself collects (exact, including dynamic parametrisation), or None."""
    try:
        out = subprocess.run([python, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "-o", "addopts="], cwd=ROOT,
                             capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r"(\d+) tests? collected", out.stdout) or re.search(r"^(\d+)/\d+ tests? collected", out.stdout, re.M)
    if match:
        return int(match.group(1))
    lines = [ln for ln in out.stdout.splitlines() if "::" in ln]
    return len(lines) if lines else None


def _attribute_layers(per_file: list[dict], graph) -> None:
    """Add layers_direct / layers_transitive to each scanned file (in place) and drop its raw import list."""
    known = set(graph.modules)
    for row in per_file:
        direct = {m for m in row["imports"] if m in known}
        reach = set(direct)
        for m in direct:
            reach |= set(graph.find_upstream_modules(m))  # grimp "upstream" = everything m imports
        row["layers_direct"] = sorted({layer_of(m) for m in direct})
        row["layers_transitive"] = sorted({layer_of(m) for m in reach if m != PACKAGE})
        del row["imports"]


def _by_layer(per_file: list[dict], layers: list[str]) -> list[dict]:
    rows = []
    for layer in layers:
        direct = [r for r in per_file if layer in r["layers_direct"]]
        trans = [r for r in per_file if layer in r["layers_transitive"]]
        rows.append({"layer": layer,
                     "files_direct": len(direct), "tests_direct": sum(r["tests"] for r in direct),
                     "asserts_direct": sum(r["asserts"] for r in direct),
                     "files_transitive": len(trans), "tests_transitive": sum(r["tests"] for r in trans)})
    return rows


def _inventory_summary(per_file: list[dict], collected: int | None) -> dict:
    total_tests = sum(r["tests"] for r in per_file)
    total_asserts = sum(r["asserts"] for r in per_file)
    return {"test_files": len(per_file), "tests_static": total_tests, "asserts": total_asserts,
            "raises_blocks": sum(r["raises_blocks"] for r in per_file),
            "asserts_per_test": r3(total_asserts / total_tests) if total_tests else None,
            "tests_collected_by_pytest": collected,
            "static_matches_collected": (collected == total_tests) if collected is not None else None}


def collect(run_pytest_collection: bool = True) -> dict:
    files = sorted(TESTS.rglob("test_*.py"))
    if not files:
        return not_run("no tests/ directory or no test_*.py files")
    graph = grimp.build_graph(PACKAGE, include_external_packages=False, cache_dir=None)
    per_file = [scan_file(p) for p in files]
    _attribute_layers(per_file, graph)
    layers = sorted({layer_of(m) for m in graph.modules if m != PACKAGE})
    collected = collected_count() if run_pytest_collection else None
    return measured(
        method="ast scan of tests/**/test_*.py; layer attribution from imports and the grimp import graph",
        not_measured=["test quality or fault-detection power (see the mutation lane)", "dynamic parametrisation beyond literals",
                      "tests outside tests/"],
        files=per_file, by_layer=_by_layer(per_file, layers),
        summary=_inventory_summary(per_file, collected))


def run_coverage(python: str = sys.executable) -> dict:
    """Run the suite under coverage.py (branch mode) and write reports/coverage/coverage.json.

    Returns a small status dict. A failing test run or a missing coverage.py is reported, never hidden.
    """
    COVERAGE_JSON.parent.mkdir(parents=True, exist_ok=True)
    for stale in (COVERAGE_JSON, COVERAGE_META, COVERAGE_DATA):  # a failed run must not leave old evidence behind
        stale.unlink(missing_ok=True)
    fingerprint = tree_fingerprint()
    env_args = ["--data-file", str(COVERAGE_DATA)]
    run = subprocess.run([python, "-m", "coverage", "run", "--branch", "--source", str(ROOT / "src" / PACKAGE), *env_args,
                          "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=ROOT, capture_output=True, text=True, check=False)
    if not COVERAGE_DATA.exists():
        return {"status": "NOT_RUN", "reason": "coverage produced no data file", "stderr": run.stderr[-400:]}
    out = subprocess.run([python, "-m", "coverage", "json", *env_args, "-o", str(COVERAGE_JSON)],
                         cwd=ROOT, capture_output=True, text=True, check=False)
    if out.returncode != 0:
        return {"status": "NOT_RUN", "reason": "coverage json failed", "stderr": out.stderr[-400:]}
    meta = {"tree_sha256": fingerprint, "pytest_returncode": run.returncode}
    write_text(COVERAGE_META, json.dumps(meta, sort_keys=True) + "\n")
    return {"status": MEASURED, "pytest_returncode": run.returncode, "pytest_tail": run.stdout.strip().splitlines()[-1:]}


def coverage_freshness() -> str | None:
    """None when reports/coverage was measured on the current tree; otherwise the reason it cannot be used."""
    if not COVERAGE_JSON.exists():
        return "reports/coverage/coverage.json not found; run `python -m quality.metrics coverage`"
    try:
        recorded = json.loads(COVERAGE_META.read_text(encoding="utf-8")).get("tree_sha256")
    except (OSError, ValueError, AttributeError):
        return "reports/coverage/coverage.meta.json missing or unreadable: coverage.json is not bound to any tree"
    if recorded != tree_fingerprint():
        return "reports/coverage/coverage.json is stale: src/ or tests/ changed since it was measured; re-run `python -m quality.metrics coverage`"
    return None


def collect_coverage() -> dict:
    """Coverage per layer, only when the report was measured on the tree that is on disk now (else NOT_RUN)."""
    reason = coverage_freshness()
    if reason:
        return not_run(reason)
    data = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    per_layer: dict[str, dict[str, int]] = {}
    files = []
    for name, entry in sorted(data["files"].items()):
        path = name.replace("\\", "/")
        module = (PACKAGE + "." + path.split(f"{PACKAGE}/", 1)[-1].removesuffix(".py").replace("/", ".")).removesuffix(".__init__")
        layer = layer_of(module)
        s = entry["summary"]
        agg = per_layer.setdefault(layer, dict.fromkeys(("statements", "covered", "branches", "covered_branches"), 0))
        agg["statements"] += s["num_statements"]
        agg["covered"] += s["covered_lines"]
        agg["branches"] += s.get("num_branches", 0)
        agg["covered_branches"] += s.get("covered_branches", 0)
        files.append({"module": module.removeprefix(PACKAGE + "."), "layer": layer, "statements": s["num_statements"],
                      "percent": r3(s["percent_covered"]), "missing_lines": s["missing_lines"]})
    layers = [{"layer": layer, **v, "line_percent": r3(100 * v["covered"] / v["statements"]) if v["statements"] else None,
               "branch_percent": r3(100 * v["covered_branches"] / v["branches"]) if v["branches"] else None}
              for layer, v in sorted(per_layer.items())]
    totals = data["totals"]
    return measured(
        method="coverage.py json report of `pytest` under `coverage run --branch --source=src/eija_studio`",
        source="coverage.py " + data.get("meta", {}).get("version", "?"),
        not_measured=["whether covered lines are asserted on (mutation lane)", "subprocess-only or browser-driven paths"],
        layers=layers, files=files,
        summary={"statements": totals["num_statements"], "covered": totals["covered_lines"],
                 "percent": r3(totals["percent_covered"]),
                 "line_percent": r3(100 * totals["covered_lines"] / totals["num_statements"]) if totals["num_statements"] else None, "branches": totals.get("num_branches", 0),
                 "covered_branches": totals.get("covered_branches", 0)})
