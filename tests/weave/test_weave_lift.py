"""The lifted files are the source files, or behave identically to them (WBS 1.6).

Three kinds of proof, each with a negative control:

* VERBATIM: functions copied unchanged have the same AST as the source (docstrings included, comments and layout ignored).
* ADAPTED: functions split into helpers to meet the complexity budget (check_certificate, check_document, _rename_cycles,
  build_sarif, sarif_profile_problems, _check_subset) are DIFFERENTIALLY tested against the source on seeded random inputs.
  MEASUREMENT: sample sizes are the module constants below; every sample must agree, and the planted defects must be found.
* The metamodel's ``expand`` is the source's function.
"""
from __future__ import annotations

import ast
import copy
import importlib.util
import json
import random
import sys
from pathlib import Path
from types import ModuleType

import pytest
from weave_support import PACKS, ROOT, index, rng, write_repo

from eija_studio.weave import closure, sarif, typecheck
from eija_studio.weave.metamodel import metamodel
from eija_studio.weave.rules import lint, to_sarif

WEAVE = ROOT / "src" / "eija_studio" / "weave"
HEADER_LINES = 2
GRAPHS = 300      # random closure graphs
DOCUMENTS = 300   # random graph documents
RENAMES = 300     # random rename systems
SARIFS = 120      # random SARIF corruptions
EN_DASH = "\u2013"


def load(name: str, path: Path, extra_path: Path | None = None) -> ModuleType:
    if extra_path is not None:
        sys.path.insert(0, str(extra_path))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if extra_path is not None:
            sys.path.remove(str(extra_path))


@pytest.fixture(scope="module")
def src_closure() -> ModuleType:
    return load("weave_src_closure", ROOT / "graph/formal/eijaref/closure.py")


@pytest.fixture(scope="module")
def src_typecheck() -> ModuleType:
    return load("weave_src_typecheck", ROOT / "graph/schema/typecheck.py", ROOT / "graph/schema")


@pytest.fixture(scope="module")
def src_reference() -> ModuleType:
    return load("weave_src_reference", ROOT / "graph/rules/reference.py")


def functions(path: Path, fold_dash: bool = False) -> dict[str, str]:
    """name -> ast.dump of every top-level function in a file (comments and layout do not count)."""
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text.replace(EN_DASH, "-") if fold_dash else text)
    return {n.name: ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef)}


def drift(source: Path, lifted: Path, names: set[str] | None = None, fold_dash: bool = False) -> list[str]:
    a, b = functions(source, fold_dash), functions(lifted, fold_dash)
    return sorted(n for n in (names if names is not None else set(a)) if n not in b or a.get(n) != b[n])


# ---- verbatim -------------------------------------------------------------------------------------------------

def test_verbatim_lifts_have_the_same_function_asts_as_their_sources() -> None:
    assert drift(ROOT / "quality/okf/codelink.py", WEAVE / "codelink.py", fold_dash=True) == []
    assert drift(ROOT / "graph/formal/eijaref/status.py", WEAVE / "status.py") == []
    assert drift(ROOT / "graph/formal/eijaref/closure.py", WEAVE / "closure.py", {"edge_set", "lfp_kleene", "certify"}) == []
    assert drift(ROOT / "graph/schema/typecheck.py", WEAVE / "typecheck.py", {"_qualifier_ok"}) == []
    assert drift(ROOT / "graph/schema/build_schemas.py", WEAVE / "metamodel.py", {"expand"}) == []
    verbatim = {"canonical_json", "_enc", "fingerprint_v1", "rule_verdict", "fold_verdicts", "exit_code", "_positional", "_render", "dumps_sarif"}
    assert drift(ROOT / "graph/rules/reference.py", WEAVE / "sarif.py", verbatim) == []


def test_status_is_byte_equal_to_its_source_after_the_header() -> None:
    first, _second, rest = (WEAVE / "status.py").read_text(encoding="utf-8").split("\n", HEADER_LINES)
    assert first.startswith("# LIFTED VERBATIM from graph/formal/eijaref/status.py")
    assert rest == (ROOT / "graph/formal/eijaref/status.py").read_text(encoding="utf-8")


def test_negative_control_a_changed_constant_is_reported_as_drift(tmp_path: Path) -> None:
    text = (WEAVE / "closure.py").read_text(encoding="utf-8").replace("if v not in rank", "if v in rank", 1)
    planted = tmp_path / "closure.py"
    planted.write_text(text, encoding="utf-8")
    assert drift(ROOT / "graph/formal/eijaref/closure.py", planted, {"certify"}) == ["certify"]


# ---- adapted: closure -----------------------------------------------------------------------------------------

def random_graph(r: random.Random) -> tuple[dict[str, list[str]], list[str]]:
    nodes = [f"n{i}" for i in range(r.randint(2, 9))]
    graph = {n: sorted({r.choice(nodes) for _ in range(r.randint(0, 3))}) for n in nodes}
    return graph, sorted({r.choice(nodes) for _ in range(r.randint(1, 2))})


def corrupt(cert: dict, r: random.Random) -> dict:
    out = {"C": set(cert["C"]), "rank": dict(cert["rank"]), "parent": dict(cert["parent"])}
    choice = r.randint(0, 3)
    victim = r.choice(sorted(out["C"]))
    if choice == 0:
        out["C"].discard(victim)
    elif choice == 1 and out["parent"]:
        out["parent"][r.choice(sorted(out["parent"]))] = "zz"
    elif choice == 2:
        out["rank"][victim] = 99
    else:
        out["parent"].pop(victim, None)
    return {"C": frozenset(out["C"]), "rank": out["rank"], "parent": out["parent"]}


def test_check_certificate_agrees_with_the_source_on_valid_and_corrupted_certificates(src_closure) -> None:
    r = rng(11)
    rejected = 0
    for _ in range(GRAPHS):
        graph, roots = random_graph(r)
        cert = closure.certify(graph, roots)
        assert closure.certify(graph, roots) == src_closure.certify(graph, roots)
        edges = closure.edge_set(graph)
        assert closure.check_certificate(edges, roots, cert) == src_closure.check_certificate(edges, roots, cert) == (True, "accepted")
        bad = corrupt(cert, r)
        mine, theirs = closure.check_certificate(edges, roots, bad), src_closure.check_certificate(edges, roots, bad)
        assert mine == theirs
        rejected += 0 if mine[0] else 1
        assert closure.lfp_kleene(graph, roots) == src_closure.warshall_closure(graph, roots)  # the two source oracles agree with ours
    assert rejected >= GRAPHS // 3  # negative control: corruption is usually caught, so the comparison is not vacuous


# ---- adapted: typecheck ---------------------------------------------------------------------------------------

def mutate(nodes: list[dict], edges: list[dict], kinds: list[str], r: random.Random) -> tuple[list[dict], list[dict]]:
    nodes, edges = copy.deepcopy(nodes), copy.deepcopy(edges)
    ids = [n["id"] for n in nodes] + ["repo://ghost.py#g"]
    for _ in range(r.randint(1, 4)):
        op = r.randint(0, 5)
        edge = r.choice(edges) if edges else None
        if op == 0 and edge:
            edge["to"] = r.choice(ids)
        elif op == 1 and edge:
            edge["kind"] = r.choice(kinds)
        elif op == 2 and edge:
            edges.append(dict(edge))
        elif op == 3:
            edges.append({"kind": r.choice(kinds), "from": r.choice(ids), "to": r.choice(ids)})
        elif op == 4 and nodes:
            nodes.append(dict(r.choice(nodes), digest="x"))
        elif op == 5 and edge:
            edge["from"] = edge["to"]
    return nodes, edges


def test_check_document_agrees_with_the_source_on_valid_and_mutated_documents(tmp_path: Path, src_typecheck) -> None:
    mm = metamodel()
    kinds = sorted(mm["link_types"])
    r = rng(5)
    found_codes: set[str] = set()
    for name in PACKS:
        root, pack_file = write_repo(tmp_path / name, name)
        _, graph = index(root, pack_file)
        assert typecheck.check_document(mm, graph.nodes, graph.edges) == src_typecheck.check_document(mm, graph.nodes, graph.edges) == []
        for _ in range(DOCUMENTS // 2):
            nodes, edges = mutate(graph.nodes, graph.edges, kinds, r)
            mine, theirs = typecheck.check_document(mm, nodes, edges), src_typecheck.check_document(mm, nodes, edges)
            assert mine == theirs
            found_codes |= {code for code, _s, _m in mine}
    # negative control: the random mutations exercise every finding code this check can emit for this graph shape
    assert {"dangling-link", "ill-typed-edge", "duplicate-edge", "duplicate-id", "self-loop"} <= found_codes


def test_rename_cycles_agree_with_the_source_on_random_rename_systems(src_typecheck) -> None:
    r = rng(9)
    names = ["a.py", "b.py", "c.py", "a.py#f", "b.py#f", "c.py#g"]
    looped = 0
    for _ in range(RENAMES):
        pairs = list({(r.choice(names), r.choice(names)) for _ in range(r.randint(1, 5))})
        mine, theirs = typecheck._rename_cycles(pairs), src_typecheck._rename_cycles(pairs)
        assert mine == theirs
        looped += bool(mine)
    for _ in range(RENAMES):
        edges = [(r.choice(names), r.choice(names)) for _ in range(r.randint(0, 6))]
        assert typecheck._cycle(edges) == src_typecheck._cycle(edges)
    assert looped > 20  # negative control: cycles do occur in the sample
    loop = [("a.py", "b.py"), ("b.py#f", "a.py#f")]  # each record is fine, the lifted system loops (the source documents it)
    assert typecheck._rename_cycles(loop) == src_typecheck._rename_cycles(loop) != []


# ---- adapted: SARIF -------------------------------------------------------------------------------------------

def test_the_committed_example_sarif_is_reproduced_byte_for_byte_by_the_adapted_builder(src_reference, monkeypatch) -> None:
    monkeypatch.setattr(src_reference, "build_sarif", sarif.build_sarif)
    catalogue = json.loads((ROOT / "graph/rules/catalogue.json").read_text(encoding="utf-8"))
    example = (ROOT / "graph/schema/examples/wv-example.sarif.json").read_text(encoding="utf-8")
    assert sarif.dumps_sarif(src_reference.example_document(catalogue)) == example


def test_lint_output_is_identical_from_the_adapted_and_the_source_builder(tmp_path: Path, src_reference) -> None:
    doc_root, pack_file = write_repo(tmp_path, "excursion")
    _, graph = index(doc_root, pack_file)
    graph.edges.append({"kind": "contains", "from": "repo://ghost", "to": "repo://ghost2"})  # dangling twice
    result = lint(graph, None)
    catalogue = json.loads((ROOT / "graph/rules/catalogue.json").read_text(encoding="utf-8"))
    args = {"not_run": result.not_run, "graph_root": result.root_hash, "verdicts": result.verdicts, "tool_version": "t"}
    assert sarif.dumps_sarif(sarif.build_sarif(catalogue, result.findings, **args)) == src_reference.dumps_sarif(
        src_reference.build_sarif(catalogue, result.findings, **args))
    assert len(result.findings) == 2 and to_sarif(doc_root, result, "t")["runs"][0]["results"]


def corrupt_sarif(doc: dict, r: random.Random) -> dict:
    out = copy.deepcopy(doc)
    run = out["runs"][0]
    op = r.randint(0, 5)
    if op == 0:
        run["invocations"][0]["startTimeUtc"] = "2026-01-01T00:00:00Z"
    elif op == 1 and run["results"]:
        run["results"].reverse()
    elif op == 2:
        run["columnKind"] = "utf16CodeUnits"
    elif op == 3 and run["results"]:
        run["results"][0]["locations"] = [{"physicalLocation": {"artifactLocation": {"uri": "C:/abs/path.py", "uriBaseId": "SRCROOT"}}}]
    elif op == 4:
        run["tool"]["driver"]["rules"].reverse()
    elif run["results"]:
        del run["results"][-1]["suppressions"]
    return out


def test_profile_problems_agree_with_the_source_on_the_example_and_on_corruptions(tmp_path: Path, src_reference) -> None:
    doc_root, pack_file = write_repo(tmp_path, "excursion")
    _, graph = index(doc_root, pack_file)
    graph.edges += [{"kind": "contains", "from": f"repo://g{i}", "to": f"repo://h{i}"} for i in range(3)]
    base = to_sarif(doc_root, lint(graph, None), "t")
    assert sarif.sarif_profile_problems(base) == src_reference.sarif_profile_problems(base) == []
    r = rng(3)
    flagged = 0
    for _ in range(SARIFS):
        bad = corrupt_sarif(base, r)
        mine = sarif.sarif_profile_problems(bad)
        assert mine == src_reference.sarif_profile_problems(bad)
        flagged += bool(mine)
    assert flagged >= SARIFS // 2  # negative control: the corruptions are usually profile violations


def test_canonical_subset_check_agrees_with_the_source(src_reference) -> None:
    cases = [None, True, "x", 1, 2**53, 2**53 - 1, 1.5, float("nan"), b"b", [1, [2, {"a": 1}]], {"a": [1, 2]}, {"1a": 1}, {"a-b": 1}, {1: 2}, (1, 2), {"a": {"b": {"c": 1.0}}}]
    for value in cases:
        outcomes = []
        for module in (sarif, src_reference):
            try:
                module._check_subset(value)
                outcomes.append("ok")
            except ValueError as error:
                outcomes.append(str(error))
        assert outcomes[0] == outcomes[1], value
