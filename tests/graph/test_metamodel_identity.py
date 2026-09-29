"""Oracles for docs/weave/design/metamodel-and-identity.md and ADR-0089.

They assert the coherence of graph/schema/metamodel.json, that the committed schemas are the generated
ones, that every node type and link kind has a valid example, and the measured identity and hashing facts
the ADR relies on. A missing optional package gives a skip, which is the pytest spelling of NOT_RUN; it is
never a pass.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "graph" / "schema"
sys.path.insert(0, str(SCHEMA))
try:
    import build_schemas as bs  # noqa: E402
    import typecheck  # noqa: E402
finally:  # leave sys.path as found: other test modules import their own top-level names
    sys.path.remove(str(SCHEMA))

_spec = importlib.util.spec_from_file_location("identity_checks", ROOT / "graph" / "bench" / "identity_checks.py")
ic = importlib.util.module_from_spec(_spec)
sys.modules["identity_checks"] = ic
_spec.loader.exec_module(ic)

MM = bs.load()
DIGEST = "sha256:" + "a" * 64


def node(type_name: str, node_id: str | None = None) -> dict:
    t = MM["node_types"][type_name]
    return {"id": node_id or t["example"], "type": type_name, "prov": "exact",
            "digest": {"method": t["methods"][0], "value": DIGEST}}


def example_edge(kind: str, row: int = 0) -> dict:
    k = MM["link_types"][kind]
    r = k["signatures"][row]
    frm, to = bs.expand(MM, r["from"])[0], bs.expand(MM, r["to"])[0]
    if r.get("same_type"):
        to = frm
    e = {"kind": kind, "from": MM["node_types"][frm]["example"], "to": MM["node_types"][to]["example"],
         "class": k["classes"][0], "prov": "exact", "asserted_in": "graph/links/example.jsonl"}
    if e["from"] == e["to"]:
        e["to"] = e["to"] + "b" if MM["node_types"][to]["fragment"]["presence"] != "none" else e["to"]
    if r.get("qualifiers"):
        e["qualifier"] = r["qualifiers"][0]
    if k["anchor_ends"]:
        e["anchors"] = [{"end": end, "method": MM["node_types"][(frm, to)[end == "to"]]["methods"][0], "digest": DIGEST}
                        for end in k["anchor_ends"]]
    if k["attrs"] and "generator" in k["attrs"]:
        e["attrs"] = {"generator": "diagrams-v1"}
    if e["class"] == "inferred":
        e["attrs"] = {"tool": "example-tool", "version": "1"}
    return e


# ---- the metamodel itself ---------------------------------------------------------------------------------

def test_metamodel_tables_are_coherent() -> None:
    assert bs.check_metamodel(MM) == []
    assert len(MM["node_types"]) == 42
    assert len(MM["link_types"]) == 29
    assert sum(len(v["signatures"]) for v in MM["link_types"].values()) == 45


def test_generated_files_are_current_and_lf() -> None:
    for name, text in bs.expected_files(MM).items():
        raw = (SCHEMA / name).read_bytes()
        assert b"\r" not in raw, f"{name} has CR bytes"
        assert raw == text.encode("utf-8"), f"{name} is stale: run python graph/schema/build_schemas.py"


def test_every_owner_vocabulary_term_maps_to_real_types() -> None:
    real = set(MM["node_types"]) | set(MM["link_types"])
    for term, spec in MM["aliases"]["owner_vocabulary"].items():
        words = [w.strip(" ()+") for part in spec["maps_to"].replace("|", " ").replace("+", " ").split() for w in [part]]
        assert any(w in real for w in words) or spec["maps_to"].startswith("not an edge"), term


def test_paths_of_this_worktree_fit_the_id_grammar() -> None:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False)
    if out.returncode != 0:
        pytest.skip("NOT_RUN: git not runnable")
    for line in out.stdout.splitlines():
        assert ic.is_canonical_id("repo://" + line), line


# ---- schemas ------------------------------------------------------------------------------------------------

jsonschema = pytest.importorskip("jsonschema", reason="NOT_RUN: jsonschema is not installed")


def validator(name: str):
    schema = json.loads((SCHEMA / name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def test_schemas_are_valid_draft_2020_12() -> None:
    for name in ("node.schema.json", "edge.schema.json", "graph.schema.json"):
        validator(name)


def test_every_node_type_example_validates_and_alien_ids_fail() -> None:
    v = validator("node.schema.json")
    for name in MM["node_types"]:
        assert list(v.iter_errors(node(name))) == [], name
    bad = node("symbol", "repo://docs/architecture/ARCHITECTURE.md#change-case")  # a markdown path is not a symbol
    assert list(v.iter_errors(bad))
    assert list(v.iter_errors(node("adr", "repo://docs/adr/0089-weave-metamodel-identity.md#x")))  # adr takes no fragment
    assert list(v.iter_errors(node("symbol", MM["node_types"]["symbol"]["example"] + "\n")))  # `$` would accept this in Python
    assert list(v.iter_errors(node("symbol", "repo://src/../x.py#f")))
    assert list(v.iter_errors(node("state", "repo://examples/e.json#state/a b")))
    assert list(v.iter_errors(node("state", "repo://examples/e.json#state/a%2fb")))  # lowercase percent-encoding is not canonical


def test_node_records_reject_floats_nulls_and_unknown_fields() -> None:
    v = validator("node.schema.json")
    n = node("symbol")
    assert list(v.iter_errors({**n, "extra": 1}))
    assert list(v.iter_errors({**n, "attrs": {}}))  # empty containers are not canonical: omit the field
    assert list(v.iter_errors({**n, "attrs": {"kind": None}}))
    assert list(v.iter_errors({**n, "digest": {"method": "md5-v1", "value": DIGEST}}))
    assert list(v.iter_errors({**n, "digest": {"method": "csv-row-v1", "value": DIGEST}}))  # not a symbol method
    assert list(v.iter_errors({**n, "prov": "candidate"}))
    ok = {**n, "attrs": {"kind": "function", "visibility": "public"}}
    assert list(v.iter_errors(ok)) == []


def test_every_link_kind_has_a_valid_edge_and_kind_rules_bite() -> None:
    v = validator("edge.schema.json")
    for kind, spec in MM["link_types"].items():
        for i in range(len(spec["signatures"])):
            e = example_edge(kind, i)
            assert list(v.iter_errors(e)) == [], (kind, i, [x.message for x in v.iter_errors(e)][:2])
    sat = example_edge("satisfies")
    assert list(v.iter_errors({**sat, "kind": "tests"}))                          # unknown kind
    assert list(v.iter_errors({**sat, "class": "evidence"}))                      # class not allowed for the kind
    assert list(v.iter_errors({k: x for k, x in sat.items() if k != "anchors"}))  # declared satisfies needs both anchors
    assert list(v.iter_errors({**sat, "anchors": sat["anchors"][:1]}))
    assert list(v.iter_errors({**sat, "anchors": list(reversed(sat["anchors"]))}))  # order is part of the canonical form
    assert list(v.iter_errors({**sat, "qualifier": "x"}))                         # satisfies has no qualifiers
    assert list(v.iter_errors({**sat, "qualifier": ""}))
    dep = example_edge("depends_on")
    assert list(v.iter_errors({**dep, "anchors": [sat["anchors"][0]]}))           # depends_on is not anchored
    assert list(v.iter_errors({**example_edge("names"), "qualifier": "bogus"}))
    assert list(v.iter_errors({**sat, "prov": "candidate"}))                      # candidate needs candidates
    assert list(v.iter_errors({**sat, "candidates": 3}))                          # and only then


def test_inferred_edges_are_proposals_with_tool_and_version() -> None:
    v = validator("edge.schema.json")
    sat = example_edge("satisfies")
    inferred = {k: x for k, x in sat.items() if k != "anchors"} | {"class": "inferred"}
    assert list(v.iter_errors(inferred))                                          # no tool and version
    inferred["attrs"] = {"tool": "graphify", "version": "0.3"}
    assert list(v.iter_errors(inferred)) == []
    inferred["attrs"] = {"tool": "graphify", "version": "0.3", "confidence_permille": 700}
    assert list(v.iter_errors(inferred)) == []
    inferred["attrs"] = {"tool": "graphify", "version": "0.3", "confidence": 0.7}   # a float is not in the subset
    assert list(v.iter_errors(inferred))
    assert list(v.iter_errors({**sat, "attrs": {"tool": "x", "version": "1"}}))    # declared edges carry no such attrs


def test_graph_document_validates() -> None:
    v = validator("graph.schema.json")
    doc = {"schema": "eija.weave.graph/v1", "metamodel": MM["metamodel_version"],
           "nodes": [node("symbol"), node("requirement")], "edges": [example_edge("satisfies")]}
    assert list(v.iter_errors(doc)) == []
    assert list(v.iter_errors({**doc, "schema": "eija.weave.graph/v2"}))
    assert list(v.iter_errors({**doc, "generated_at": "2026-09-29"}))              # no wall clock in artefacts
    assert list(v.iter_errors({**doc, "root": "sha256:xyz"}))


# ---- join-level checks (executable definition for WV-001, WV-002, WV-003, WV-055, WV-056) --------------------------------------

def test_reference_checker_accepts_a_good_graph_and_names_each_defect() -> None:
    types = ["symbol", "requirement", "test", "workflow", "state", "transition", "effect"]
    nodes = [node(t) for t in types]
    ex = lambda t: MM["node_types"][t]["example"]  # noqa: E731
    good = [
        {"kind": "satisfies", "from": ex("symbol"), "to": ex("requirement")},
        {"kind": "verifies", "from": ex("test"), "to": ex("requirement")},
        {"kind": "contains", "from": ex("workflow"), "to": ex("state")},
        {"kind": "contains", "from": ex("workflow"), "to": ex("transition")},
        {"kind": "flows_to", "from": ex("state"), "to": ex("transition")},
        {"kind": "depends_on", "from": ex("transition"), "to": ex("effect"), "qualifier": "required"},
    ]
    assert typecheck.check_document(MM, nodes, good) == []
    bad = good + [
        {"kind": "satisfies", "from": ex("requirement"), "to": ex("symbol")},                  # wrong direction
        {"kind": "depends_on", "from": ex("transition"), "to": ex("effect"), "qualifier": "x"},  # qualifier not on the row
        {"kind": "contains", "from": ex("state"), "to": ex("workflow")},                        # not a signature
        {"kind": "verifies", "from": ex("test"), "to": "repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC99"},  # dangling
        {"kind": "satisfies", "from": ex("symbol"), "to": ex("symbol")},                        # self-loop and ill-typed
    ]
    codes = sorted({f[0] for f in typecheck.check_document(MM, nodes, bad)})
    # the ill-typed contains edge (state -> workflow) also closes a cycle with the good workflow -> state edge
    assert codes == ["dangling-link", "ill-typed-edge", "link-kind-cycle", "self-loop"]


def test_reference_checker_cardinality_and_cycles() -> None:
    a, b, c = "repo://docs/adr/0001-a.md", "repo://docs/adr/0002-b.md", "repo://docs/adr/0003-c.md"
    nodes = [node("adr", x) for x in (a, b, c)]
    cyc = [{"kind": "supersedes", "from": a, "to": b}, {"kind": "supersedes", "from": b, "to": c},
           {"kind": "supersedes", "from": c, "to": a}]
    assert {f[0] for f in typecheck.check_document(MM, nodes, cyc)} == {"link-kind-cycle"}
    two_successors = [{"kind": "supersedes", "from": a, "to": c}, {"kind": "supersedes", "from": b, "to": c}]
    assert {f[0] for f in typecheck.check_document(MM, nodes, two_successors)} == {"cardinality-exceeded"}  # in<=1
    dup = [{"kind": "supersedes", "from": a, "to": b}] * 2
    assert "duplicate-edge" in {f[0] for f in typecheck.check_document(MM, nodes, dup)}


def test_rename_records_may_start_at_a_tombstone_but_must_end_at_a_node() -> None:
    old, new = "repo://src/a.py#f", "repo://src/a.py#g"
    nodes = [node("symbol", new)]
    edges = [{"kind": "renamed_to", "from": old, "to": new}]
    assert typecheck.check_document(MM, nodes, edges) == []
    assert {f[0] for f in typecheck.check_document(MM, [], edges)} == {"dangling-link"}
    mixed = [node("symbol", new)]
    assert {f[0] for f in typecheck.check_document(MM, mixed + [node("module", "repo://src/a.py")],
                                                   [{"kind": "renamed_to", "from": "repo://src/a.py", "to": new}])} == {"ill-typed-edge"}


# ---- identity and hashing measurements ----------------------------------------------------------------------

def test_jcs_subset_writer_agrees_with_the_rfc_implementation_and_with_the_kernel_on_ascii_keys() -> None:
    r = ic.jcs_subset(n=2000)
    assert r["status"] == "MEASURED"
    assert r["all_out_of_subset_inputs_rejected"] is True
    assert r["kernel_canonical_differs_ascii_key_docs"] == 0
    assert r["kernel_differences_not_explained_by_utf16_key_order"] == 0
    if ic.rfc8785 is None:
        pytest.skip("NOT_RUN: rfc8785 is not installed")
    assert r["rfc8785_0.1.4_differs"] == 0


def test_utf16_order_disagrees_with_code_point_order_only_for_supplementary_vs_e000_ffff() -> None:
    r = ic.utf16_order_boundary()
    assert r["exactly_supplementary_vs_e000_ffff"] is True and r["disagreeing_pairs"] > 0


def test_hashing_is_length_safe_and_domain_separated() -> None:
    r = ic.domain_separation()
    assert r["concat_collides_a_bc_vs_ab_c"] is True          # what Doorstop-style concatenation does
    assert r["jcs_array_collides_a_bc_vs_ab_c"] is False
    assert r["same_record_different_domain_collides"] is False
    with pytest.raises(ic.CanonError):
        ic.dhash("not-a-tag", {})


def test_root_is_a_function_of_the_record_set() -> None:
    r = ic.permutation_invariance(shuffles=40)
    assert r["distinct_roots_sorted_records"] == 1 and r["root_equals_unshuffled"] is True
    assert r["distinct_hashes_insertion_order_json_dumps"] > 1     # the naive form is order dependent
    assert r["distinct_hashes_json_dumps_sort_keys_unsorted_lists"] > 1


def test_label_free_hashing_conflates_claims_that_identity_hashing_separates() -> None:
    r = ic.labelling_versus_identity()
    if r.get("status") == "NOT_RUN":
        pytest.skip("NOT_RUN: networkx is not installed")
    assert r["wl_hash_equal_for_c6_and_two_c3_which_are_not_isomorphic"] is True
    assert r["label_free_wl_hash_equal_for_different_claims"] is True
    assert r["sorted_record_root_equal_for_different_claims"] is False


def test_shard_locality() -> None:
    r = ic.shard_locality()
    assert all(r[k] for k in ("digest_change_shards_changed", "digest_change_root_changed", "edge_in_new_file_shards_changed",
                              "reorder_root_unchanged"))


def test_closure_fingerprint_covers_edge_records_and_the_node_only_form_misses_them() -> None:
    r = ic.closure_fingerprint(trials=20)
    assert r["trials_where_changed_set_differs_from_kernel_closure"] == 0
    assert set(r["by_mutation"]) == set(ic.CLOSURE_MUTATIONS) and all(v["trials"] == 4 for v in r["by_mutation"].values())
    assert r["by_mutation"]["node_record"]["missed_by_node_only_v1"] == 0
    assert r["edge_trials_missed_by_node_only_fingerprint"] == 16  # every edge-record mutation is invisible to the v1 form


def _edge(kind: str, a: str, b: str, **extra) -> dict:
    return {"kind": kind, "from": a, "to": b, "class": "derived", "prov": "exact", "asserted_in": "src/x.py", **extra}


def test_view_roots_hash_only_the_records_of_the_view() -> None:
    a, b, c = (ic.make_id("src/v.py", x) for x in "abc")
    nodes = [{"id": i, "type": "symbol", "prov": "exact", "digest": {"method": "ast-v1", "value": "sha256:" + d * 64}}
             for i, d in ((a, "1"), (b, "2"), (c, "3"))]
    edges = [_edge("depends_on", a, b), _edge("names", b, c, qualifier="surface", **{"class": "declared"})]
    structure = ic.graph_root(nodes, edges, view="structure")
    assert structure != ic.graph_root(nodes, edges) and structure != ic.graph_root(nodes, edges, view="language")
    # c is not an endpoint of a structure edge, and the names edge is not in the view: neither changes the structure root
    n2 = [{**n, "digest": {"method": "ast-v1", "value": "sha256:" + "9" * 64}} if n["id"] == c else n for n in nodes]
    assert ic.graph_root(n2, edges, view="structure") == structure
    assert ic.graph_root(nodes, edges[:1], view="structure") == structure
    # an in-view edge attribute, and an endpoint's digest, do change it
    assert ic.graph_root(nodes, [{**edges[0], "class": "declared"}, edges[1]], view="structure") != structure
    n3 = [{**n, "digest": {"method": "ast-v1", "value": "sha256:" + "9" * 64}} if n["id"] == a else n for n in nodes]
    assert ic.graph_root(n3, edges, view="structure") != structure
    with pytest.raises(ic.CanonError):
        ic.graph_root(nodes, edges, view="nonesuch")
    # every view named in the metamodel uses declared kinds
    assert all(set(kinds) <= set(MM["link_types"]) for kinds in MM["views"].values())


def test_shard_row_order_is_the_documented_comparator() -> None:
    v = json.loads((SCHEMA / "identity-vectors.json").read_text(encoding="utf-8"))["shard_rows"]
    nodes, edges = v["nodes"], v["edges"]
    rows: dict[str, list[list[str]]] = {}
    for n in nodes:
        rows.setdefault(ic.node_shard(n), []).append(["n", n["id"], ic.node_rh(n)])
    for e in edges:
        rows.setdefault(e["asserted_in"], []).append(["e", *ic.edge_key(e), ic.edge_rh(e)])
    # an independent spelling of the comparator: element-wise, each string by its UTF-8 bytes
    key = lambda row: [x.encode("utf-8") for x in row]  # noqa: E731
    got = {p: ic.dhash("eija.weave.shard.v1", sorted(r, key=key)) for p, r in rows.items()}
    assert got == v["shard_hashes"]
    assert any({"n", "e"} <= {x[0] for x in r} for r in rows.values())  # node and edge rows share one shard
    reversed_rows = {p: list(reversed(r)) for p, r in rows.items()}
    assert {p: ic.dhash("eija.weave.shard.v1", sorted(r, key=key)) for p, r in reversed_rows.items()} == v["shard_hashes"]
    assert ic.graph_root(nodes, edges) == v["root"]


def test_every_sorted_element_is_ascii_by_schema() -> None:
    # the comparator claim rests on this: ids, kinds, qualifiers and digests are ASCII, so code point, UTF-8 and UTF-16 order agree
    assert all(q.isascii() for k in MM["link_types"].values() for q in k["qualifiers"])
    assert all(k.isascii() for k in MM["link_types"])
    assert not ic.is_canonical_id("repo://x/y.json#state/\u00e9") and not ic.is_canonical_id("repo://x/\u00e9.json")


def test_rename_resolution_is_order_independent_and_rejects_conflicts_and_cycles() -> None:
    r = ic.rename_resolution(trials=20)
    assert r["order_dependent_resolutions"] == 0 and r["nonfunctional_detected"] and r["cycle_detected"]
    assert r["example_probe"] == "repo://src/p/m1.py#g"


MIXED_LEVEL = [("repo://src/a.py", "repo://src/b.py"), ("repo://src/b.py#f", "repo://src/a.py#f")]


def test_mixed_level_renames_can_loop_although_each_record_and_the_relation_are_fine() -> None:
    """Counterexample from the audit: a path-level record plus an id-level record in the opposite direction."""
    a, b = "repo://src/a.py", "repo://src/b.py"
    nodes = [node("module", a), node("module", b), node("symbol", a + "#f"), node("symbol", b + "#f")]
    edges = [{"kind": "renamed_to", "from": x, "to": y} for x, y in MIXED_LEVEL]
    # the single relation is functional, injective, same-typed and acyclic: the per-relation checks alone pass
    (finding,) = typecheck.check_document(MM, nodes, edges)
    assert finding[0] == "rename-cycle" and finding[1] == a + "#f" and finding[2] == f"{a}#f -> {b}#f -> {a}#f"
    problems = ic.check_renames(MIXED_LEVEL)
    assert [p for p in problems if p.startswith(("cycle", "non-functional"))] == []
    assert problems == [f"composite-cycle: {a}#f -> {b}#f -> {a}#f"]
    with pytest.raises(ic.CanonError):
        ic.resolve(a + "#f", MIXED_LEVEL)
    assert ic.resolve(a + "#g", MIXED_LEVEL) == b + "#g"  # other fragments of the file still move
    for one in MIXED_LEVEL:  # each record alone is fine
        assert typecheck.check_document(MM, nodes, [{"kind": "renamed_to", "from": one[0], "to": one[1]}]) == []


def test_rename_cycle_detection_agrees_with_brute_force_and_across_the_two_implementations() -> None:
    import random
    rng = random.Random(20260929)
    files = [f"src/p{i}.py" for i in range(4)]
    frags = ["f", "g"]
    probes = ["repo://" + f + (("#" + x) if x else "") for f in files for x in (None, *frags, "h")]
    cyclic = 0
    for _ in range(400):
        pairs, lefts = [], set()
        for _ in range(rng.randrange(1, 6)):
            if rng.random() < 0.5:
                old, new = rng.sample(["repo://" + f for f in files], 2)
            else:
                old = "repo://" + rng.choice(files) + "#" + rng.choice(frags)
                new = "repo://" + rng.choice(files) + "#" + rng.choice(frags)
            if old == new or old in lefts:
                continue
            lefts.add(old)
            pairs.append((old, new))
        looped = []
        for p in probes:
            try:
                ic.resolve(p, pairs)
            except ic.CanonError:
                looped.append(p)
        cyc = typecheck._rename_cycles(pairs)
        assert bool(cyc) == bool(looped), pairs  # walking from left sides finds every non-terminating probe
        composite = [p for p in ic.check_renames(pairs) if p.startswith("composite-cycle")]
        assert composite == sorted("composite-cycle: " + " -> ".join(c + [c[0]]) for c in cyc), pairs
        cyclic += bool(looped)
    assert 20 < cyclic < 380  # the sample exercises both outcomes


def test_reference_checker_expands_signature_rows_once_per_kind(monkeypatch) -> None:
    calls = []
    real = typecheck._rows
    monkeypatch.setattr(typecheck, "_rows", lambda mm, kind: calls.append(kind) or real(mm, kind))
    nodes = [node("adr", f"repo://docs/adr/{i:04d}-a.md") for i in range(1, 40)]
    edges = [{"kind": "supersedes", "from": nodes[i]["id"], "to": nodes[i + 1]["id"]} for i in range(30)]
    assert typecheck.check_document(MM, nodes, edges) == []
    assert calls == ["supersedes"]


def test_id_canonicality_and_export_ids() -> None:
    assert ic.id_canonicality()["all_as_expected"] is True
    e = ic.export_ids()
    assert e["hand_rfc9562_v5_equals_stdlib"] is True and e["uuid_collisions_in_2000"] == 0 and e["ncname_valid"] is True


def test_git_blob_ids_depend_on_line_endings_but_lf_sha256_does_not() -> None:
    r = ic.swhid_and_line_endings()
    assert r["git_blob_id_lf_vs_crlf_differ"] is True and r["lf_sha256_lf_vs_crlf_equal"] is True
    if r["swhid_cnt_equals_git_hash_object_for_LICENSE"] != {"status": "NOT_RUN", "reason": "git not runnable"}:
        assert r["swhid_cnt_equals_git_hash_object_for_LICENSE"] is True


def test_committed_vectors_are_current_and_reproducible_by_the_rfc_package() -> None:
    committed = json.loads((SCHEMA / "identity-vectors.json").read_text(encoding="utf-8"))
    assert committed == json.loads(ic.dump(ic.vectors()))
    assert b"\r" not in (SCHEMA / "identity-vectors.json").read_bytes()
    if ic.rfc8785 is None:
        pytest.skip("NOT_RUN: rfc8785 is not installed")
    for case in committed["jcs"]:
        assert ic.rfc8785.dumps(case["input"]).decode("utf-8") == case["jcs"], case["name"]


def test_report_is_byte_identical_across_hash_seeds() -> None:
    outs = []
    for seed in ("0", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "TMP": str(ROOT / ".tmp"), "TEMP": str(ROOT / ".tmp")}
        proc = subprocess.run([sys.executable, str(ROOT / "graph" / "bench" / "identity_checks.py")], env=env, capture_output=True,
                              check=True, timeout=300)
        outs.append(proc.stdout)
    assert outs[0] == outs[1]


# ---- declarations other aspects read (impact, ranking, ledger) ---------------------------------------------------

def test_flow_role_and_weight_are_declared_on_every_link_kind() -> None:
    for kind, spec in MM["link_types"].items():
        assert spec["affects"] in ("to_source", "to_target", "both", "none"), kind
        assert spec["rank_weight"] == [2, 1], kind
        assert spec["cover_role"] == {"verifies": "verifier", "covers": "observer"}.get(kind, "none"), kind
    assert MM["link_types"]["renamed_to"]["affects"] == "none" and MM["link_types"]["proposes"]["affects"] == "none"


def test_domain_tag_registry_covers_every_tag_the_reference_uses() -> None:
    registry = {t["tag"] for t in MM["domain_tags"]}
    used = {"eija.weave.node.v1", "eija.weave.edge.v1", "eija.weave.edge-id.v1", "eija.weave.shard.v1", "eija.weave.root.v1",
            "eija.weave.closure.v2"}
    assert used <= registry
    source = (ROOT / "graph" / "bench" / "identity_checks.py").read_text(encoding="utf-8")
    import re
    assert set(re.findall(r'"(eija\.weave\.[a-z0-9.-]+\.v[0-9]+)"', source)) - {"eija.weave.a.v1"} <= registry


def test_decision_ids_are_content_addressed_not_sequence_numbers() -> None:
    v = validator("node.schema.json")
    assert list(v.iter_errors(node("decision"))) == []
    assert list(v.iter_errors(node("decision", "repo://graph/ledger.jsonl#17")))       # a sequence number is not merge safe
    assert list(v.iter_errors(node("decision", "repo://graph/ledger/a.jsonl#" + "F" * 64)))  # lowercase hex only


def test_file_level_and_function_level_tests_use_different_hash_methods() -> None:
    v = validator("node.schema.json")
    fn = node("test")
    assert list(v.iter_errors(fn)) == []
    assert list(v.iter_errors({**fn, "digest": {"method": "lf-sha256-v1", "value": DIGEST}}))   # a function needs ast-v1
    file_level = node("test", "repo://tests/test_domain.py")
    assert list(v.iter_errors({**file_level, "digest": {"method": "lf-sha256-v1", "value": DIGEST}})) == []
    assert list(v.iter_errors(file_level))                                                       # ast-v1 needs a fragment


def test_dogfood_graph_from_this_repository_is_well_formed_and_stable() -> None:
    spec = importlib.util.spec_from_file_location("metamodel_dogfood", ROOT / "graph" / "bench" / "metamodel_dogfood.py")
    df = importlib.util.module_from_spec(spec)
    sys.modules["metamodel_dogfood"] = df
    spec.loader.exec_module(df)
    r = df.report()
    assert r["reference_findings"] == []
    assert r["schema_validation"]["error_count"] == 0
    assert r["non_canonical_ids"] == []
    assert r["root_equal_after_a_second_clean_extraction"] is True and r["root_equal_when_extraction_order_is_shuffled"] is True
    assert r["cross_checks"]["workflow_semantic_v1_equals_kernel_semantic_hash"] is True
    okf = r["cross_checks"]["digests_equal_to_okf_codelink_by_method"]
    if okf.get("status") == "NOT_RUN":
        pytest.skip("NOT_RUN: okf worktree not found")
    assert all(okf.values()) and set(okf) == {"csv-row-v1", "lf-sha256-v1", "md-bold-term-v1"}
    assert r["impact_fanout"]["metamodel_affects"]["sum_of_closure_sizes"] > r["impact_fanout"]["both_collapsed_to_to_source"]["sum_of_closure_sizes"]


def test_okf_bundle_maps_onto_the_metamodel_and_its_hash_methods_are_registered() -> None:
    """Fixture agreement with the okf lane. A failure here means the okf bundle moved: update the mapping or the registry."""
    spec = importlib.util.spec_from_file_location("metamodel_dogfood2", ROOT / "graph" / "bench" / "metamodel_dogfood.py")
    df = importlib.util.module_from_spec(spec)
    sys.modules["metamodel_dogfood2"] = df
    spec.loader.exec_module(df)
    r = df.okf_bundle()
    if r.get("status") == "NOT_RUN":
        pytest.skip("NOT_RUN: okf worktree not found")
    assert r["pages_of_unmapped_types"] == {}, "an okf page type has no weave node type"
    assert r["hash_methods_not_in_the_weave_registry"] == [], "an okf hash method is not in metamodel.json"
    # every mismatch is a non-canonical slug fragment (an underscore), the known Verification Technique case
    assert all("_" in resource.split("#", 1)[-1] for _, resource in
               [(t, u) for t, u in r["examples"]]), r["examples"]


def test_design_document_states_the_counts_of_the_metamodel() -> None:
    doc = ROOT / "docs" / "weave" / "design" / "metamodel-and-identity.md"
    if not doc.exists():
        pytest.skip("NOT_RUN: design document not written yet")
    text = doc.read_text(encoding="utf-8")
    for needle in (f"{len(MM['node_types'])} node types", f"{len(MM['link_types'])} link kinds",
                   f"{sum(len(v['signatures']) for v in MM['link_types'].values())} signature rows"):
        assert needle in text, needle
    assert "\r" not in text
    assert copy.deepcopy(MM)["metamodel_version"] in text
