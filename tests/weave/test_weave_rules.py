"""WBS 1.6 proof: WV-001 dangling, WV-002 ill-typed, WV-003 duplicate, WV-005 suspect binding, each with a planted defect.

Every gate here has a NEGATIVE CONTROL: the clean repository gives zero findings, and one planted defect gives EXACTLY
one finding of the expected rule and no other. NOT_RUN is never PASS: no baseline (WV-005) and partial extraction are
NOT_RUN. SARIF output satisfies the EIJA determinism profile and is byte-identical across runs.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from weave_support import rng, BIND, LIB, PACKS, bound_term, index, read_pack, shuffled, write_repo

from eija_studio.weave.rules import baseline_text, lint, load_baseline, to_sarif, write_baseline
from eija_studio.weave.sarif import dumps_sarif, sarif_profile_problems


def rules_of(result) -> list[str]:
    return [f["rule"] for f in result.findings]


def with_baseline(root: Path, pack_file: Path, tmp: Path):
    _, graph = index(root, pack_file)
    path = tmp / "baseline.json"
    write_baseline(path, graph)
    return load_baseline(path)


@pytest.mark.parametrize("name", PACKS)
def test_the_clean_repository_has_no_findings_and_passes_the_rules_that_can_run(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path, name)
    _, graph = index(root, pack_file)
    result = lint(graph, with_baseline(root, pack_file, tmp_path))
    assert result.findings == [] and set(result.verdicts.values()) == {"PASS"} and result.verdict == "PASS"


@pytest.mark.parametrize("name", PACKS)
def test_a_planted_dangling_repo_binding_gives_exactly_one_wv_001(tmp_path: Path, name: str) -> None:
    doc = read_pack(name)
    bound_term(doc)["binds"].append("repo://src/missing.py#ghost")
    root, pack_file = write_repo(tmp_path, name, doc)
    result = lint(index(root, pack_file)[1], None)
    assert rules_of(result) == ["WV-001"] and result.verdicts["WV-001"] == "FAIL"
    assert result.findings[0]["args"]["endpoint"] == "repo://src/missing.py#ghost" and result.findings[0]["args"]["side"] == "source"


@pytest.mark.parametrize("name", PACKS)
def test_a_dangling_term_reference_gives_exactly_one_wv_001(tmp_path: Path, name: str) -> None:
    doc = read_pack(name)
    bound_term(doc)["refs"].append("state:NoSuchState")
    root, pack_file = write_repo(tmp_path, name, doc)
    result = lint(index(root, pack_file)[1], None)
    assert rules_of(result) == ["WV-001"] and result.findings[0]["args"]["side"] == "target"


@pytest.mark.parametrize("name", PACKS)
def test_a_planted_duplicate_binding_gives_exactly_one_wv_003(tmp_path: Path, name: str) -> None:
    doc = read_pack(name)
    bound_term(doc)["binds"].append(BIND)  # write_repo appends BIND once more: the same binding twice
    root, pack_file = write_repo(tmp_path, name, doc)
    result = lint(index(root, pack_file)[1], None)
    assert rules_of(result) == ["WV-003"] and result.verdicts["WV-003"] == "FAIL"


@pytest.mark.parametrize("name", PACKS)
def test_binding_a_whole_python_module_is_ill_typed_wv_002(tmp_path: Path, name: str) -> None:
    doc = read_pack(name)
    bound_term(doc)["binds"].append("repo://src/lib.py")  # a module is not a symbol: no signature admits it
    root, pack_file = write_repo(tmp_path, name, doc)
    result = lint(index(root, pack_file)[1], None)
    assert rules_of(result) == ["WV-002"]
    assert result.findings[0]["args"]["from_type"] == "module" and result.findings[0]["args"]["to_type"] == "term"


@pytest.mark.parametrize("name", PACKS)
def test_a_planted_ill_typed_edge_gives_exactly_one_wv_002(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path, name)
    _, graph = index(root, pack_file)
    state = next(n["id"] for n in graph.nodes if n["type"] == "state")
    term = next(n["id"] for n in graph.nodes if n["type"] == "term")
    graph.edges.append({"kind": "contains", "from": state, "to": term})  # a state does not contain a term
    result = lint(graph, None)
    assert rules_of(result) == ["WV-002"] and result.findings[0]["args"]["from_type"] == "state"


@pytest.mark.parametrize("name", PACKS)
def test_a_conflicting_duplicate_node_and_a_second_container_are_reported_once_each(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path, name)
    _, graph = index(root, pack_file)
    dup = copy.deepcopy(next(n for n in graph.nodes if n["type"] == "role"))
    dup["digest"] = "0" * 64
    graph.nodes.append(dup)
    assert rules_of(lint(graph, None)) == ["WV-003"]
    _, graph = index(root, pack_file)
    graph.nodes.append({"id": "repo://src/other.py", "type": "module", "digest": "0" * 64})
    graph.edges.append({"kind": "contains", "from": "repo://src/other.py", "to": "repo://src/lib.py#helper"})
    result = lint(graph, None)
    assert rules_of(result) == ["WV-055"] and result.findings[0]["args"]["count"] == "2"


@pytest.mark.parametrize("name", PACKS)
def test_suspect_binding_fires_on_a_semantic_edit_and_not_on_a_comment_or_reformat(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path / "r", name)
    baseline = with_baseline(root, pack_file, tmp_path)
    assert baseline is not None and any(BIND in key for key in baseline)
    (root / "src" / "lib.py").write_text(LIB.replace("# a comment", "# reworded").replace("x + 1", "x  +  1"), encoding="utf-8")
    assert lint(index(root, pack_file)[1], baseline).findings == []  # early cutoff: nothing semantic changed
    (root / "src" / "lib.py").write_text(LIB.replace("x + 1", "x + 2"), encoding="utf-8")
    result = lint(index(root, pack_file)[1], baseline)
    assert rules_of(result) == ["WV-005"] and result.verdicts["WV-005"] == "FAIL"
    assert result.findings[0]["args"]["target"] == BIND
    assert result.findings[0]["args"]["baseline_digest"] != result.findings[0]["args"]["current_digest"]


@pytest.mark.parametrize("name", PACKS)
def test_without_a_baseline_wv_005_is_not_run_never_pass(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path, name)
    result = lint(index(root, pack_file)[1], None)
    assert result.verdicts["WV-005"] == "NOT_RUN" and result.verdict == "NOT_RUN"
    assert [n["rule"] for n in result.not_run] == ["WV-005"] and "human" in result.not_run[0]["reason"]


def test_partial_extraction_makes_silence_not_run_but_a_finding_still_fails(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    (root / "src" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    baseline = with_baseline(root, pack_file, tmp_path)
    result = lint(index(root, pack_file)[1], baseline)
    assert result.findings == [] and result.verdicts["WV-001"] == "NOT_RUN" and result.verdict == "NOT_RUN"
    doc = read_pack("excursion")
    bound_term(doc)["binds"].append("repo://src/missing.py#ghost")
    other, other_file = write_repo(tmp_path / "o", "excursion", doc)
    (other / "src" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    assert lint(index(other, other_file)[1], baseline).verdicts["WV-001"] == "FAIL"


def test_the_baseline_is_canonical_and_a_malformed_one_is_treated_as_absent(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    _, graph = index(root, pack_file)
    text = baseline_text(graph)
    assert text == baseline_text(index(root, pack_file)[1]) and text.endswith("}\n") and "\r" not in text
    for bad in ("not json", "[]", '{"schema": "x", "bindings": {}}', '{"schema": "eija.weave.baseline.v1", "bindings": []}'):
        (tmp_path / "b.json").write_text(bad, encoding="utf-8")
        assert load_baseline(tmp_path / "b.json") is None
    assert load_baseline(tmp_path / "absent.json") is None


def test_sarif_is_profile_clean_deterministic_and_reorder_stable(tmp_path: Path) -> None:
    doc = read_pack("excursion")
    bound_term(doc)["binds"].append("repo://src/missing.py#ghost")
    root, pack_file = write_repo(tmp_path / "a", "excursion", doc)
    result = lint(index(root, pack_file)[1], None)
    sarif = to_sarif(root, result, "0.0.0-test")
    text = dumps_sarif(sarif)
    assert sarif_profile_problems(sarif) == [] and text == dumps_sarif(to_sarif(root, lint(index(root, pack_file)[1], None), "0.0.0-test"))
    run = sarif["runs"][0]
    findings = [r for r in run["results"] if r.get("kind") == "fail"]
    assert [r["ruleId"] for r in findings] == ["WV-001"] and run["properties"]["graphRoot"] == result.root_hash
    fingerprint = findings[0]["partialFingerprints"]["eijaFinding/v1"]
    other, other_file = write_repo(tmp_path / "b", "excursion", shuffled(doc, rng(3)))
    again = to_sarif(other, lint(index(other, other_file)[1], None), "0.0.0-test")
    assert [r["partialFingerprints"]["eijaFinding/v1"] for r in again["runs"][0]["results"] if r.get("kind") == "fail"] == [fingerprint]
    assert json.loads(text)["runs"][0]["properties"]["verdict"] == "FAIL"
