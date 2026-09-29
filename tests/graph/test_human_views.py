"""Oracles for graph/schema/views.md and docs/weave/design/human-comprehension-views.md.

What is checked: the machine-readable definition is internally consistent and total over the metamodel;
the executable reference definitions (graph/bench/human_views_reference.py) satisfy the laws that the
views rely on (counts roll up as a monoid, tiers are maximin paths, the canonical witness is the
lexicographically first shortest path, priority-then-cap never shows a PASS while hiding a non-PASS,
operations and null edits partition a keyed diff, dependency order is a topological order); and the
measurement script is deterministic. Nothing here measures whether a person understands anything.

A missing optional prerequisite (the kernel, the metamodel file) gives a skip, which is the pytest
spelling of NOT_RUN; it is never a pass.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "graph" / "bench"
sys.path.insert(0, str(BENCH))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ref = _load("human_views_reference", BENCH / "human_views_reference.py")
bench = _load("human_views_budgets", BENCH / "human_views_budgets.py")
DEFN = bench.load_definition()
MASK = (1 << 64) - 1


class Rng:
    """SplitMix64: identical on every platform, so a failing seed reproduces anywhere."""

    def __init__(self, seed: int) -> None:
        self.s = seed & MASK

    def below(self, n: int) -> int:
        self.s = (self.s + 0x9E3779B97F4A7C15) & MASK
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return (z ^ (z >> 31)) % n


def shuffled(items: list, rng: Rng) -> list:
    items = list(items)
    for i in range(len(items) - 1, 0, -1):
        j = rng.below(i + 1)
        items[i], items[j] = items[j], items[i]
    return items


# ---------------------------------------------------------------------------------------- definition
def _walk(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from _walk(v)
    elif isinstance(value, list):
        for v in value:
            yield from _walk(v)
    else:
        yield value


def test_definition_has_no_floats_and_names_six_statuses() -> None:
    assert not [v for v in _walk(DEFN) if isinstance(v, float)]
    assert DEFN["status_values"] == ["PASS", "FAIL", "CONFLICT", "STALE", "UNKNOWN", "NOT_RUN"]
    assert sorted(DEFN["chain_worst_first"]) == sorted(DEFN["status_values"])
    assert DEFN["chain_worst_first"][-1] == "PASS"  # PASS is the top of the chain: a badge is PASS only if all are
    assert "display_order_default" not in DEFN  # display order is presentation and is not part of the hashed definition


def test_definition_is_internally_consistent() -> None:
    b = DEFN["budgets"]
    views = DEFN["views"]
    assert [v["id"] for v in views] == [f"HV-0{i}" for i in range(1, 9)]
    assert len({v["name"] for v in views}) == 8
    for v in views:
        assert v["tasks"] and all(re.fullmatch(r"T\d\d", t) for t in v["tasks"])
        assert v["default_form"] and v["alt_forms"]
        if "chunks" in v:
            assert 1 <= len(v["chunks"]) <= b["chunks_top_level_max"], v["id"]
    assert b["chunks_top_level_max"] == 4 and b["disclosure_levels_after_l0_max"] == 2
    assert b["matrix_cells_max"] == b["matrix_rows_per_page_max"] * b["matrix_columns_max"]
    assert b["neighbourhood_nodes_default_max"] <= b["neighbourhood_nodes_expanded_max"] <= b["neighbourhood_nodes_hard_stop"]
    assert b["witness_segments_default_max"] <= b["chunks_top_level_max"]
    assert b["rows_before_more"] < b["l0_rows_max"]
    by_id = {v["id"]: v for v in views}
    assert by_id["HV-03"]["rows_per_page_max"] == b["matrix_rows_per_page_max"]
    assert by_id["HV-03"]["columns_max"] == b["matrix_columns_max"]
    assert by_id["HV-08"]["nodes_default_max"] == b["neighbourhood_nodes_default_max"]
    assert by_id["HV-08"]["nodes_hard_stop"] == b["neighbourhood_nodes_hard_stop"]
    assert by_id["HV-07"]["segments_max"] == b["witness_segments_default_max"]
    assert by_id["HV-05"]["depth_max"] == by_id["HV-04"]["depth_max"] == b["tree_depth_max"]
    assert set(DEFN["budget_basis"]) <= set(b), "a basis entry names a budget that does not exist"
    assert all("HYPOTHESIS" in DEFN["budget_basis"][k] or "PREDICTION" in DEFN["budget_basis"][k] for k in DEFN["budget_basis"])


def _metamodel_types() -> tuple[set[str], set[str], str]:
    mm = ROOT / "graph" / "schema" / "metamodel.json"
    if mm.exists():
        m = json.loads(mm.read_text(encoding="utf-8"))
        return set(m["node_types"]), set(m["link_types"]), "metamodel.json"
    brief = ROOT / "graph" / "brief.json"
    if not brief.exists():
        pytest.skip("NOT_RUN: neither graph/schema/metamodel.json nor graph/brief.json exists")
    b = json.loads(brief.read_text(encoding="utf-8"))
    return {n["id"] for n in b["node_types"]}, {l["id"] for l in b["link_types"]}, "brief.json"


def test_view_mapping_is_total_over_the_metamodel() -> None:
    """WV-028 in miniature: every node type and link type is shown by some view or is listed as not_shown."""
    nodes, links, source = _metamodel_types()
    view_ids = {v["id"] for v in DEFN["views"]}
    mapped_n, mapped_l = set(DEFN["node_type_views"]), set(DEFN["link_type_views"])
    not_shown = set(DEFN["not_shown"])
    assert nodes <= mapped_n | not_shown, f"node types with no view ({source}): {sorted(nodes - mapped_n - not_shown)}"
    assert links <= mapped_l | not_shown, f"link types with no view ({source}): {sorted(links - mapped_l - not_shown)}"
    assert mapped_n <= nodes, f"mapping names unknown node types: {sorted(mapped_n - nodes)}"
    assert mapped_l <= links, f"mapping names unknown link types: {sorted(mapped_l - links)}"
    for table in (DEFN["node_type_views"], DEFN["link_type_views"]):
        for k, vs in table.items():
            assert vs and set(vs) <= view_ids, k


def test_negative_control_totality_detects_a_missing_type() -> None:
    nodes, _, _ = _metamodel_types()
    broken = {k: v for k, v in DEFN["node_type_views"].items() if k != "requirement"}
    assert not nodes <= set(broken) | set(DEFN["not_shown"])


OWNER_ONLY = {"approve", "apply", "clear", "clear_suspect", "select", "select_meaning", "edit", "layout", "discard", "save",
              "reset_preview", "execute", "export", "ack", "ledger_append"}  # agents lane OWNER_ONLY_OPERATIONS plus the ledger acts


def _offered_names(defn: dict) -> set[str]:
    """Every key of the definition and every entry of the lists that name what a view offers."""
    names: set[str] = set()

    def walk(v) -> None:
        if isinstance(v, dict):
            names.update(str(k).lower() for k in v)
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)

    walk(defn)
    for view in defn["views"]:
        names.add(view["default_form"].lower())
        names.update(a.lower() for a in view["alt_forms"])
        names.update(q.lower() for q in view.get("question_kinds", []))
        names.update(c.lower() for c in view.get("chunks", []))
        names.add(view["name"].lower())
    return names


def test_no_view_offers_an_owner_operation() -> None:
    """HCI P2, I4: no approve, apply, clear, select or edit exists in any view definition."""
    assert not _offered_names(DEFN) & OWNER_ONLY


def test_negative_control_an_offered_owner_operation_is_detected() -> None:
    broken = json.loads(json.dumps(DEFN))
    broken["views"][6]["question_kinds"].append("approve")
    assert _offered_names(broken) & OWNER_ONLY == {"approve"}


# ----------------------------------------------------------------------------------- counts, roll-up
def _tree(rng: Rng, depth: int):
    if depth == 0:
        return ref.STATUSES[rng.below(6)]
    return [_tree(rng, depth - 1) for _ in range(1 + rng.below(5))]


def _leaves(t) -> list[str]:
    return [t] if isinstance(t, str) else [x for c in t for x in _leaves(c)]


def _vec(t) -> tuple[int, ...]:
    if isinstance(t, str):
        return ref.counts_vector([t])
    out = (0,) * 6
    for c in t:
        out = ref.vec_add(out, _vec(c))
    return out


def test_counts_vector_is_a_monoid_homomorphism() -> None:
    rng = Rng(11)
    for _ in range(300):
        t = _tree(rng, 3)
        flat = _leaves(t)
        assert _vec(t) == ref.counts_vector(flat)  # C1: any grouping gives the flat counts
        assert sum(_vec(t)) == len(flat)  # C2
        assert ref.counts_vector(shuffled(flat, rng)) == ref.counts_vector(flat)  # order independent


CHAIN = DEFN["chain_worst_first"]


def test_badge_is_fold_b_from_counts_and_is_pass_only_if_every_leaf_is_pass() -> None:
    rng = Rng(41)
    for _ in range(400):
        t = _tree(rng, 3)
        flat = _leaves(t)
        badge = ref.badge_from_counts(_vec(t), CHAIN)
        assert badge == ref.fold_b(flat, CHAIN)  # C4: from the counts, equal to the flat fold
        assert (badge == "PASS") == all(x == "PASS" for x in flat)
    # targeted cases where one unhealthy item sits among healthy ones (uniform random trees rarely produce them)
    for bad in ("NOT_RUN", "UNKNOWN", "STALE", "FAIL", "CONFLICT"):
        assert ref.fold_b(["PASS"] * 9 + [bad], CHAIN) == bad
    assert ref.fold_b([], CHAIN) == "NOT_RUN"  # an empty container has proved nothing
    assert ref.badge_from_counts((0,) * 6, CHAIN) == "NOT_RUN"


def test_pass_iff_all_pass_holds_for_every_chain_with_pass_on_top() -> None:
    from itertools import permutations
    non_pass = [s for s in ref.STATUSES if s != "PASS"]
    for perm in permutations(non_pass):
        chain = [*list(perm), "PASS"]
        for n in range(1, 4):
            for seq in itertools.product(ref.STATUSES, repeat=n):
                assert (ref.fold_b(seq, chain) == "PASS") == all(x == "PASS" for x in seq)


def test_negative_control_the_join_masks_non_pass_and_is_not_a_badge_operator() -> None:
    """The weave join is for repeated observations of one claim. As a badge it shows PASS over an unrun item."""
    j = bench.join
    for masked in ("NOT_RUN", "UNKNOWN", "STALE"):
        assert j(["PASS", masked]) == "PASS"  # what a container badge must never do
        assert ref.fold_b(["PASS", masked], CHAIN) == masked
    r = bench.rollup_section(DEFN)
    b = r["badge_operator_pass_iff_all_pass"]
    assert b["fold_b_violations"] == 0
    assert b["join_violations_negative_control"] > 0
    assert b["first_join_example"]["join"] == "PASS" and b["first_join_example"]["fold_b"] != "PASS"
    laws = r["counts_vector_and_badge_laws"]
    assert laws["c1_mismatches"] == laws["c2_mismatches"] == laws["c4_badge_equals_flat_fold_b_mismatches"] == 0
    assert laws["badge_pass_iff_every_leaf_pass_violations"] == 0
    sp = r["split_composition_non_empty_parts"]
    assert sp["fold_b_mismatches"] == 0 and sp["join_mismatches"] == 0  # both compose: composition does not pick the badge operator


def test_negative_control_kernel_reaggregation_is_not_compositional() -> None:
    """Hypothetical hierarchical re-aggregation of the kernel function. The kernel does not do this; the harness
    feeds statuses back as receipts. It shows what a roll-up built that way would do."""
    k = bench.rollup_section(DEFN)["negative_control_kernel_reaggregation"]
    if k.get("status") == "NOT_RUN":
        pytest.skip(k["reason"])
    assert k["mismatches"] > 0 and k["rolled_up_pass_while_flat_not_pass"] > 0
    assert k["first_example"] == {"flat": "CONFLICT", "rolled_up": "PASS", "sequence": ["PASS", "PASS", "FAIL"], "split_at": 1}
    assert "NEGATIVE CONTROL" in k["label"]


# ------------------------------------------------------------------------------- priority-then-cap
RANK = {s: i for i, s in enumerate(DEFN["chain_worst_first"])}


def test_priority_then_cap_is_exact_and_never_hides_a_problem_behind_a_pass() -> None:
    rng = Rng(5)
    for _ in range(300):
        n = 1 + rng.below(40)
        items = [(f"n{i:03d}", ref.STATUSES[rng.below(6)], rng.below(4)) for i in range(n)]
        cap = 1 + rng.below(8)
        shown, ov = ref.priority_then_cap(shuffled(items, rng), cap, RANK)
        assert ov["shown"] + ov["hidden"] == n and len(shown) == ov["shown"]  # C5
        assert sum(ov["hidden_by_status"].values()) == ov["hidden"]
        st = {i: s for i, s, _ in items}
        if any(st[i] != "PASS" for i in st if i not in shown):
            assert all(st[i] != "PASS" for i in shown)  # a PASS is never shown while a non-PASS is hidden


def test_negative_control_capping_by_id_alone_hides_problems() -> None:
    items = [("a", "PASS", 0), ("b", "PASS", 0), ("c", "FAIL", 0), ("d", "UNKNOWN", 0)]
    naive = [i for i, _, _ in sorted(items)[:2]]
    shown, _ = ref.priority_then_cap(items, 2, RANK)
    assert naive == ["a", "b"] and shown == ["c", "d"]


def _document(items, cap) -> str:
    """A list document as canonical JSON. It takes no display order: the cut uses the definition's chain."""
    shown, ov = ref.priority_then_cap(items, cap, RANK)
    return json.dumps({"shown": shown, "overflow": ov}, sort_keys=True, separators=(",", ":"))


def test_documents_are_byte_equal_for_two_display_orders_and_the_cut_is_data() -> None:
    items = [(f"n{i}", ref.STATUSES[i % 6], i % 3) for i in range(20)]
    doc = _document(items, 5)
    display_a = ["CONFLICT", "FAIL", "STALE", "UNKNOWN", "NOT_RUN", "PASS"]
    display_b = ["PASS", "NOT_RUN", "UNKNOWN", "STALE", "FAIL", "CONFLICT"]
    st = {i: s for i, s, _ in items}
    shown = json.loads(doc)["shown"]
    for display in (display_a, display_b):  # a renderer reorders the rows it was given; the document is unchanged
        rendered = sorted(shown, key=lambda i: (display.index(st[i]), i))
        assert sorted(rendered) == sorted(shown)
        assert _document(items, 5) == doc
    # Control: a different SEVERITY rank changes the cut, which is why the rank is data, not display.
    other = {s: i for i, s in enumerate(display_b)}
    shown_other, _ = ref.priority_then_cap(items, 5, other)
    assert sorted(shown_other) != sorted(shown)
    assert any(st[i] == "PASS" for i in shown_other)  # the wrong rank shows PASS rows while hiding problems


def test_definition_digest_covers_the_cut_order_and_is_stable() -> None:
    d = ref.definition_digest(DEFN)
    assert re.fullmatch(r"[0-9a-f]{64}", d) and d == ref.definition_digest(json.loads(json.dumps(DEFN)))
    reordered = json.loads(json.dumps(DEFN))
    reordered["chain_worst_first"] = list(reversed(reordered["chain_worst_first"]))
    assert ref.definition_digest(reordered) != d
    reshuffled = {k: DEFN[k] for k in sorted(DEFN, reverse=True)}  # key order in the source does not matter
    assert ref.definition_digest(reshuffled) == d
    with pytest.raises(ValueError):
        ref.definition_digest({"label": "caf\u00e9"})


# ------------------------------------------------------------------------------------------- tiers
def _random_links(rng: Rng, n: int, m: int) -> list[tuple[str, str, int]]:
    return sorted({(f"n{rng.below(n)}", f"n{rng.below(n)}", rng.below(3)) for _ in range(m)})


def test_tiers_are_nested_and_equal_the_maximin_oracle() -> None:
    rng = Rng(21)
    for _ in range(150):
        n = 2 + rng.below(6)
        links = [l for l in _random_links(rng, n, 1 + rng.below(12)) if l[0] != l[1]]
        roots = sorted({f"n{rng.below(n)}" for _ in range(1 + rng.below(2))})
        reach = ref.tiered_reach(shuffled(links, rng), roots)
        r = [set(ref.bfs(ref._adj(links, t), roots)) for t in (0, 1, 2)]
        assert r[0] <= r[1] <= r[2]  # X4
        assert set(reach) == r[2]
        for node, info in reach.items():
            oracle = 0 if node in roots else ref.tier_bruteforce(links, roots, node)
            assert info["tier"] == oracle, (links, roots, node)


def test_tiers_are_independent_of_link_order() -> None:
    rng = Rng(3)
    links = _random_links(rng, 8, 20)
    a = ref.tiered_reach(links, ["n0", "n1"])
    for _ in range(20):
        assert ref.tiered_reach(shuffled(links, rng), ["n1", "n0"]) == a


# ----------------------------------------------------------------------------- witness and segments
def test_canonical_witness_is_the_lexicographically_first_shortest_path() -> None:
    rng = Rng(9)
    for _ in range(200):
        n = 2 + rng.below(7)
        adj: dict[str, list[str]] = {}
        for a, b, _ in _random_links(rng, n, 1 + rng.below(14)):
            adj.setdefault(a, []).append(b)
        adj = {k: shuffled(sorted(set(v)), rng) for k, v in adj.items()}
        roots = sorted({f"n{rng.below(n)}" for _ in range(1 + rng.below(2))})
        target = f"n{rng.below(n)}"
        assert ref.canonical_witness(adj, roots, target) == ref.path_bruteforce(adj, roots, target)


def test_segments_are_runs_of_equal_keys() -> None:
    keys = [("depends_on",), ("depends_on",), ("covers",), ("verifies",), ("verifies",)]
    assert ref.segments(keys) == [(("depends_on",), 2), (("covers",), 1), (("verifies",), 2)]
    assert ref.segments([]) == []


# ------------------------------------------------------------------------- neighbourhood and grid
def _und(rng: Rng, n: int, m: int) -> dict[str, list[str]]:
    und: dict[str, set[str]] = {f"n{i:02d}": set() for i in range(n)}
    for _ in range(m):
        a, b = f"n{rng.below(n):02d}", f"n{rng.below(n):02d}"
        if a != b:
            und[a].add(b)
            und[b].add(a)
    return {k: sorted(v) for k, v in und.items()}


def test_neighbourhood_is_bounded_connected_and_order_independent() -> None:
    rng = Rng(17)
    for _ in range(100):
        und = _und(rng, 30, 45)
        api = {k: 1 + rng.below(4) for k in und}
        focus = f"n{rng.below(30):02d}"
        budget = 1 + rng.below(12)
        sel = ref.select_neighbourhood(focus, und, budget, api)
        assert focus in sel and len(sel) <= budget
        assert set(ref.bfs({k: [v for v in vs if v in sel] for k, vs in und.items() if k in sel}, [focus])) == set(sel)  # connected
        again = ref.select_neighbourhood(focus, {k: shuffled(v, rng) for k, v in shuffled(list(und.items()), rng)}, budget, api)
        assert again == sel


def _doi_oracle(focus, und, budget, api):
    """Independent oracle: recompute shortest distances by repeated relaxation, then select greedily."""
    dist = {focus: 0}
    changed = True
    while changed:
        changed = False
        for a in sorted(und):
            for b in und[a]:
                if a in dist and dist.get(b, 10**9) > dist[a] + 1:
                    dist[b] = dist[a] + 1
                    changed = True
    chosen = [focus]
    while len(chosen) < budget:
        cand = sorted({y for x in chosen for y in und.get(x, ()) if y not in chosen}, key=lambda y: (-(api.get(y, 1) - dist[y]), y))
        if not cand:
            break
        chosen.append(cand[0])
    return sorted(chosen)


def test_neighbourhood_uses_shortest_path_distance_not_expansion_depth() -> None:
    # f-a, f-c, a-b, b-y, c-y; y is at shortest distance 2 (via c) but is first reached through b at depth 3
    # when b is expanded first because its api is high.
    und = {"f": ["a", "c"], "a": ["b", "f"], "b": ["a", "y"], "c": ["f", "y"], "y": ["b", "c"]}
    api = {"f": 1, "a": 1, "b": 10, "c": 1, "y": 3}
    assert ref.bfs(und, ["f"])["y"][0] == 2
    got = ref.select_neighbourhood("f", und, 4, api)
    # DOI(y) = 3 - 2 = 1 beats DOI(c) = 1 - 1 = 0; the old expansion-depth rule gave y 3 - 3 = 0, tied with c, and c won on id
    assert got == _doi_oracle("f", und, 4, api) == ["a", "b", "f", "y"]


def test_neighbourhood_equals_an_independent_doi_oracle() -> None:
    rng = Rng(53)
    for _ in range(150):
        und = _und(rng, 14, 18)
        api = {k: 1 + rng.below(6) for k in und}
        focus = f"n{rng.below(14):02d}"
        budget = 1 + rng.below(10)
        assert ref.select_neighbourhood(focus, und, budget, api) == _doi_oracle(focus, und, budget, api)


def test_neighbourhood_prefers_the_node_with_a_problem() -> None:
    und = {"f": ["a", "b", "c"], "a": ["f"], "b": ["f"], "c": ["f"]}
    assert ref.select_neighbourhood("f", und, 2, {"f": 1, "a": 1, "b": 1, "c": 5}) == ["c", "f"]
    assert ref.select_neighbourhood("f", und, 2, {}) == ["a", "f"]  # ties go to the smaller id


def test_grid_layout_is_a_function_of_the_selection_with_unique_cells() -> None:
    rng = Rng(23)
    links = [("r1", "satisfies", "f"), ("r2", "satisfies", "f"), ("f", "verifies", "t1"), ("f", "verifies", "t2"), ("t1", "covers", "m1")]
    sel = ["f", "r1", "r2", "t1", "t2", "m1"]
    grid = ref.grid_layout("f", sel, links)
    assert grid["f"] == (0, 0)
    assert grid["r1"][0] == grid["r2"][0] == -1 and grid["t1"][0] == grid["t2"][0] == 1 and grid["m1"][0] == 2
    assert len(set(grid.values())) == len(grid)
    for _ in range(20):
        assert ref.grid_layout("f", shuffled(sel, rng), shuffled(links, rng)) == grid
    assert all(isinstance(x, int) for cell in grid.values() for x in cell)


# --------------------------------------------------------------------------------------- changes
def test_operations_and_null_edits_partition_the_keyed_diff() -> None:
    before = {"a": ("f1", "n1", "ast-v1"), "b": ("f2", "n2", "ast-v1"), "c": ("f3", "n3", "lf-sha256-v1"),
              "d": ("f4", "n4", "ast-v1"), "old": ("f5", "n5", "ast-v1")}
    after = {"a": ("f1x", "n1", "ast-v1"),  # formatting only: null edit
             "b": ("f2x", "n2x", "ast-v1"),  # modified
             "c": ("f3", "n3", "lf-sha256-v1"),  # unchanged
             "e": ("f6", "n6", "ast-v1"),  # added
             "new": ("f5", "n5", "ast-v1")}  # renamed from old; d removed
    r = ref.classify_changes(before, after, {"old": "new"})
    assert r["operations"] == {"b": "MODIFIED", "d": "REMOVED", "e": "ADDED", "old": "RENAMED"}
    assert r["null_edits"] == {"ast-v1": ["a"]}
    listed = set(r["operations"]) | {i for v in r["null_edits"].values() for i in v}
    changed = {i for i in set(before) | set(after) if before.get(i) != after.get(i)} - {"new"}
    assert listed == changed and not set(r["operations"]) & {i for v in r["null_edits"].values() for i in v}  # X6


def test_a_whole_file_method_has_no_null_edit_notion() -> None:
    r = ref.classify_changes({"x": ("f1", "f1", "lf-sha256-v1")}, {"x": ("f2", "f2", "lf-sha256-v1")}, {})
    assert r == {"operations": {"x": "MODIFIED"}, "null_edits": {}}


def test_chapters_follow_layer_truth_and_derived_from() -> None:
    c = DEFN["chapters"]
    layer = {"t": "language", "m": "code", "d": "views", "e": "verification", "g": "code", "v": "code"}
    truth = {"t": "declared", "m": "derived", "d": "derived", "e": "evidence", "g": "derived", "v": "declared"}
    out = ref.chapters(["t", "m", "d", "e", "g", "v"], layer, truth, [("g", "t")],
                       c["core_layers"], c["consequence_truth"], c["consequence_layers_derived"])
    assert out == {"t": "core", "m": "glue", "d": "consequences", "e": "consequences", "g": "consequences", "v": "glue"}
    alone = ref.chapters(["g"], layer, truth, [("g", "t")], c["core_layers"], c["consequence_truth"], c["consequence_layers_derived"])
    assert alone == {"g": "glue"}  # not a consequence when its source did not change


def test_dependency_order_is_topological_deterministic_and_keeps_cycles_together() -> None:
    rng = Rng(31)
    for _ in range(100):
        nodes = [f"n{i}" for i in range(2 + rng.below(8))]
        pairs = [(f"n{rng.below(len(nodes))}", f"n{rng.below(len(nodes))}") for _ in range(rng.below(14))]
        pairs = [p for p in pairs if p[0] in nodes and p[1] in nodes]
        order = ref.dependency_order(shuffled(nodes, rng), shuffled(pairs, rng))
        assert sorted(order) == sorted(nodes) and order == ref.dependency_order(nodes, pairs)
        label = ref.scc_min_labels(nodes, pairs)
        pos = {n: i for i, n in enumerate(order)}
        for a, b in pairs:
            if label[a] != label[b]:
                assert pos[a] < pos[b]
        for lab in set(label.values()):  # members of an SCC are adjacent in the order
            idx = sorted(pos[n] for n in nodes if label[n] == lab)
            assert idx[-1] - idx[0] == len(idx) - 1
    assert ref.dependency_order(["b", "a"], []) == ["a", "b"]
    assert ref.dependency_order(["b", "a"], [("b", "a")]) == ["b", "a"]


# --------------------------------------------------------------------------------- bench output
def test_bench_output_is_deterministic_and_clean() -> None:
    a = bench.dumps(bench.run())
    b = bench.dumps(bench.run())
    assert a == b
    doc = json.loads(a)
    assert not [v for v in _walk(doc) if isinstance(v, float)]
    assert str(ROOT) not in a and str(ROOT).replace("\\", "/") not in a
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", a)  # no timestamp
    s = doc["sections"]
    assert s["inputs"]["status"] == "MEASURED" and re.fullmatch(r"[0-9a-f]{64}", s["inputs"]["root"])
    assert s["import_graph"]["nodes"] >= 1 and s["requirements"]["rows"] >= 1
    for section in ("import_graph", "requirements", "typed_ripple", "rollup", "budgets"):
        assert s[section]["status"] == "MEASURED"
    checks = s["budgets"]["checks"]
    assert {c["view"] for c in checks} == {v["id"] for v in DEFN["views"]}
    for c in checks:
        assert c["within"] in (True, False, None)
        if c["within"] is None:
            assert "NOT_RUN" in c["note"]  # an unmeasured budget says so and is never a pass


def test_bench_agrees_with_an_independent_recount_of_the_csv() -> None:
    import csv
    from collections import Counter

    rows = list(csv.DictReader((ROOT / "docs" / "verification" / "ACCEPTANCE_MATRIX.csv").read_text(encoding="utf-8").splitlines()))
    r = bench.requirements_section(DEFN)[0]
    sizes = Counter(x["area"] for x in rows)
    assert r["rows"] == len(rows) and sum(r["area_group_sizes"]) == len(rows)
    assert r["largest_area_group"] == max(sizes.values()) and r["area_groups"] == len(sizes)
