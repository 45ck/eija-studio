"""WBS 1.6 proof: the index and its root hash are functions of the repository and the pack, nothing else.

MEASUREMENT: the root hash is byte-identical across runs, across processes with different hash seeds, and across
SHUFFLES declaration lists of the pack (PERMUTATIONS shuffles per pack, seeds 0..N-1, on both packs). Negative controls: a
real change to a pack element, a bound symbol or a web id changes the root; a comment-only edit does not.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from weave_support import rng, BIND, LIB, PACKS, ROOT, SWAPPED, index, read_pack, shuffled, write_repo

from eija_studio.weave.index import dhash, edge_id

PERMUTATIONS = 12
GOLDEN_EDGE = {"kind": "satisfies", "from": "repo://src/a.py#f", "to": "repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC01"}


@pytest.mark.parametrize("name", PACKS)
def test_root_hash_is_identical_across_runs_and_declaration_reordering(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path / "base", name)
    _, graph = index(root, pack_file)
    assert index(root, pack_file)[1].root_hash == graph.root_hash
    for seed in range(PERMUTATIONS):
        other, other_file = write_repo(tmp_path / f"p{seed}", name, shuffled(read_pack(name), rng(seed)))
        assert index(other, other_file)[1].root_hash == graph.root_hash, f"{name} seed {seed}"


@pytest.mark.parametrize("name", PACKS)
def test_negative_control_real_changes_move_the_root(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path / "base", name)
    base = index(root, pack_file)[1].root_hash
    doc = read_pack(name)
    current = doc["model"]["transitions"][0]["role"]
    doc["model"]["transitions"][0]["role"] = next(r["id"] for r in doc["roles"] if r["id"] != current)
    changed = {
        "transition role": write_repo(tmp_path / "a", name, doc),
        "bound symbol body": write_repo(tmp_path / "b", name, lib=LIB.replace("x + 1", "x + 2")),
        "new symbol": write_repo(tmp_path / "c", name, lib=LIB + "\n\ndef added():\n    return 1\n"),
    }
    for label, (other, other_file) in changed.items():
        assert index(other, other_file)[1].root_hash != base, label
    web = tmp_path / "base" / "web" / "app.html"
    web.write_text(web.read_text(encoding="utf-8") + f'<b data-eija-id="{name}.state.{sorted(read_pack(name)["model"]["states"])[1]}"></b>', encoding="utf-8")
    assert index(root, pack_file)[1].root_hash != base, "new data-eija-id"


@pytest.mark.parametrize("name", PACKS)
def test_comment_reformat_and_symbol_order_do_not_move_the_root(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path / "base", name)
    base = index(root, pack_file)[1].root_hash
    commented = LIB.replace("# a comment", "# another comment, longer").replace("x + 1", "x  +  1")
    swapped = SWAPPED
    for label, text in (("comment and layout", commented), ("symbol order", swapped)):
        other, other_file = write_repo(tmp_path / label.replace(" ", "-"), name, lib=text)
        assert index(other, other_file)[1].root_hash == base, label


def test_root_hash_is_byte_identical_across_processes_with_different_hash_seeds(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    outputs = []
    for seed in ("0", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(ROOT / "src")}
        cmd = [sys.executable, "-m", "eija_studio", "index", "--root", str(root), "--pack", str(pack_file), "--json"]
        run = subprocess.run(cmd, capture_output=True, env=env, check=True, timeout=120)  # noqa: S603 - our own interpreter and arguments
        outputs.append(run.stdout)
    assert outputs[0] == outputs[1] and json.loads(outputs[0])["root_hash"].startswith("sha256:")


@pytest.mark.parametrize("name", PACKS)
def test_index_shape_on_the_mini_repository(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path, name)
    pack, graph = index(root, pack_file)
    counts = graph.counts()
    types = counts["node_types"]
    assert types["state"] >= len(pack.model.states) and types["transition"] >= len(pack.model.transitions)
    assert types["role"] == len(pack.roles) and types["formal_law"] == len(pack.laws) and types["term"] == len(pack.language.terms)
    assert types["diagram_element"] == len(pack.model.states) + len(pack.model.transitions) + len(pack.roles)
    assert (types["symbol"], types["test"], counts["gaps"]) == (4, 1, 0)  # helper, Box, Box.get, CONST; test_helper
    assert {n["id"] for n in graph.nodes} >= {f"repo://{graph.pack_path}#state/{min(pack.model.states)}", "repo://src/lib.py#helper"}
    assert [b for b in graph.bindings if b.target == BIND and b.digest is not None]


def test_a_data_eija_id_of_another_pack_is_ignored_and_one_of_this_pack_realises_its_element(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    pack, graph = index(root, pack_file)
    realises = [e for e in graph.edges if e["kind"] == "realises" and e["from"].startswith("repo://web/app.html")]
    assert sorted(e["to"] for e in realises) == sorted([f"repo://{graph.pack_path}#state/{min(pack.model.states)}",
                                                        f"repo://{graph.pack_path}#transition/{min(t.id for t in pack.model.transitions)}"])
    assert not any("other.state" in n["id"] for n in graph.nodes)


def test_an_unparsable_python_file_is_a_recorded_gap_not_an_omission(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    (root / "src" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    _, graph = index(root, pack_file)
    assert [g["path"] for g in graph.gaps] == ["src/broken.py"] and "parse" in graph.gaps[0]["reason"]
    assert graph.root_hash != index(*write_repo(tmp_path / "clean", "excursion"))[1].root_hash


def test_a_lone_surrogate_string_keeps_its_symbol_with_a_labelled_fallback_digest(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion", lib=LIB + '\n\ndef odd():\n    return "\\ud800"\n')
    _, graph = index(root, pack_file)
    odd = next(n for n in graph.nodes if n["id"] == "repo://src/lib.py#odd")
    assert odd["digest"].startswith("ast-dump-v0:") and graph.counts()["gaps"] == 0


def test_edge_id_matches_the_identity_aspects_golden_vector_and_domain_separation() -> None:
    vectors = json.loads((ROOT / "graph/schema/identity-vectors.json").read_text(encoding="utf-8"))
    assert edge_id(GOLDEN_EDGE) == vectors["edge_id"]["id"]
    assert dhash("eija.weave.root.v1", []) != dhash("eija.weave.edge-id.v1", [])
