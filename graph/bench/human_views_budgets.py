"""Measurements behind docs/weave/design/human-comprehension-views.md and graph/schema/views.md.

Question: how big are the slices that the eight human views would show for THIS repository, and do the
proposed budgets hold? What is measured is the size of slices (counts), never whether a person understands
anything: every comprehension effect stays a PREDICTION until the hci lane's study runs (design document,
section 10).

Sections (each reports MEASURED, or NOT_RUN with a reason when a prerequisite does not exist yet):

  inputs        sha256 root over the files read, so a result names the exact bytes it describes
  import_graph  module graph of src/eija_studio (ast): size, density, ego sizes, SCCs, HV-08 selection
  requirements  docs/verification/ACCEPTANCE_MATRIX.csv as the HV-03 rows and columns
  language      ubiquitous-language terms and contexts (HV-05 inputs)
  adrs          ADR files and cross references (HV-07 inputs)
  typed_ripple  a typed graph (module, test, requirement) derived from the repo, tiered closure per module
                (HV-02), witness segments (HV-07), coverage proxies (HV-04)
  kernel_ripple the kernel's own model_impact for the excursion baseline against the candidate (HV-02)
  rollup        laws C1, C2, C4 (badge = chain minimum fold_b, PASS iff every item is PASS); the weave join and
                the kernel aggregate_status re-applied to its own output as NEGATIVE CONTROLS
  budgets       each view's slice measured against the budgets in graph/schema/views.md

Determinism: integers, sorted iteration, seeded SplitMix64 for samples, no clock, no absolute paths, no
floats in the output (shares are printed as integers or n/m strings). Two runs on one checkout give
byte-identical JSON (`deterministic_sha256`). The kernel is imported read-only as a reference oracle (rule
R9: benches and tests may import eija_studio; the eijagraph runtime may not).

    python graph/bench/human_views_budgets.py [--out graph/bench/results/human-views-budgets.json]
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import itertools
import json
import re
import sys
from collections import deque
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import human_views_reference as ref  # noqa: E402  (executable definitions of graph/schema/views.md)

VIEWS_MD = ROOT / "graph" / "schema" / "views.md"
STATUSES = ("PASS", "FAIL", "CONFLICT", "STALE", "UNKNOWN", "NOT_RUN")
MASK64 = (1 << 64) - 1


# ------------------------------------------------------------------------------------------- utilities
class SplitMix64:
    """Tiny integer PRNG: identical on every platform and Python version."""

    def __init__(self, seed: int) -> None:
        self.s = seed & MASK64

    def next(self) -> int:
        self.s = (self.s + 0x9E3779B97F4A7C15) & MASK64
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return z ^ (z >> 31)

    def below(self, n: int) -> int:
        return self.next() % n


def read(path: Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def not_run(reason: str) -> dict:
    return {"status": "NOT_RUN", "reason": reason}


def median_low(values: list[int]) -> int:
    v = sorted(values)
    return v[(len(v) - 1) // 2] if v else 0


def summary(values: list[int]) -> dict:
    return {"n": len(values), "min": min(values) if values else 0, "median": median_low(values),
            "max": max(values) if values else 0}


def load_definition() -> dict:
    text = read(VIEWS_MD)
    m = re.search(r"```json views-definition\n(.*?)\n```", text, re.S)
    if not m:
        raise SystemExit("views.md has no `json views-definition` block")
    return json.loads(m.group(1))


# ------------------------------------------------------------------------------------- input discovery
def adr_files() -> list[Path]:
    """ADR files that exist outside the weave block 0089-0112, so the measurement describes the repository
    before this lane and does not change when a weave record is added."""
    out = []
    for p in sorted((ROOT / "docs" / "adr").glob("[0-9]*.md")):
        m = re.match(r"(\d{4,5})-", p.name)
        if m and int(m.group(1)) < 89:
            out.append(p)
    return out


def input_files() -> list[Path]:
    files: list[Path] = []
    files += sorted(p for p in (ROOT / "src" / "eija_studio").rglob("*.py") if "__pycache__" not in p.parts)
    files += sorted(p for p in (ROOT / "tests").glob("test_*.py"))
    files += adr_files()
    files += [ROOT / "docs" / "architecture" / "ARCHITECTURE.md", ROOT / "docs" / "verification" / "ACCEPTANCE_MATRIX.csv"]
    files += sorted((ROOT / "examples").glob("excursion-*.json"))
    files += [VIEWS_MD]
    return sorted({p for p in files if p.is_file()}, key=rel)


def inputs_section(files: list[Path]) -> dict:
    lines = [f"{rel(p)}\t{sha(read(p))}" for p in files]
    return {"status": "MEASURED", "files": len(files), "root": sha("\n".join(lines)),
            "domain": "src/eija_studio/**/*.py, tests/test_*.py, docs/adr records numbered below 0089, ARCHITECTURE.md, ACCEPTANCE_MATRIX.csv, examples/excursion-*.json, graph/schema/views.md; LF-folded"}


# --------------------------------------------------------------------------------------- import graph
def module_name(path: Path) -> str:
    parts = list(path.relative_to(ROOT / "src").with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def resolve_imports(tree: ast.AST, current: str, is_pkg: bool, known: set[str]) -> set[str]:
    out: set[str] = set()

    def best(name: str) -> str | None:
        parts = name.split(".")
        for k in range(len(parts), 0, -1):
            cand = ".".join(parts[:k])
            if cand in known:
                return cand
        return None

    pkg = current if is_pkg else current.rpartition(".")[0]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                b = best(a.name)
                if b:
                    out.add(b)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = pkg.split(".")
                if node.level > 1:
                    base_parts = base_parts[: len(base_parts) - (node.level - 1)]
                base = ".".join(base_parts + ([node.module] if node.module else []))
            else:
                base = node.module or ""
            for a in node.names:
                cand = f"{base}.{a.name}" if base else a.name
                b = cand if cand in known else best(base) if base else None
                if b:
                    out.add(b)
    return out


def sccs(nodes: list[str], adj: dict[str, list[str]]) -> list[list[str]]:
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on: set[str] = set()
    out: list[list[str]] = []
    counter = 0
    for root in nodes:
        if root in index:
            continue
        work = [(root, 0)]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on.add(root)
        while work:
            u, i = work[-1]
            succ = adj.get(u, [])
            if i < len(succ):
                work[-1] = (u, i + 1)
                v = succ[i]
                if v not in index:
                    index[v] = low[v] = counter
                    counter += 1
                    stack.append(v)
                    on.add(v)
                    work.append((v, 0))
                elif v in on:
                    low[u] = min(low[u], index[v])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[u])
                if low[u] == index[u]:
                    comp = []
                    while True:
                        w = stack.pop()
                        on.discard(w)
                        comp.append(w)
                        if w == u:
                            break
                    out.append(sorted(comp))
    return sorted(out)


def build_import_graph() -> tuple[list[str], set[tuple[str, str]], dict[str, str]]:
    files = sorted(p for p in (ROOT / "src" / "eija_studio").rglob("*.py") if "__pycache__" not in p.parts)
    names = {module_name(p): p for p in files}
    known = set(names)
    edges: set[tuple[str, str]] = set()
    for name, p in sorted(names.items()):
        tree = ast.parse(read(p))
        for dst in resolve_imports(tree, name, p.name == "__init__.py", known):
            if dst != name:
                edges.add((name, dst))
    return sorted(names), edges, {n: rel(p) for n, p in names.items()}


def import_graph_section(defn: dict) -> tuple[dict, tuple]:
    nodes, edges, paths = build_import_graph()
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    und: dict[str, set[str]] = {n: set() for n in nodes}
    for a, b in sorted(edges):
        adj[a].append(b)
        und[a].add(b)
        und[b].add(a)
    und_sorted = {n: sorted(v) for n, v in und.items()}
    n, e = len(nodes), len(edges)
    undirected_edges = len({frozenset(x) for x in edges})
    deg = {k: len(v) for k, v in und_sorted.items()}
    ego1 = sorted(1 + d for d in deg.values())
    b = defn["budgets"]
    comps = sccs(nodes, adj)
    largest = max((len(c) for c in comps), default=0)
    seen: set[str] = set()
    largest_cc = 0
    for x in nodes:
        if x in seen:
            continue
        comp = ref.bfs(und_sorted, [x])
        seen |= set(comp)
        largest_cc = max(largest_cc, len(comp))
    sel_sizes = [len(ref.select_neighbourhood(x, und_sorted, b["neighbourhood_nodes_default_max"], {})) for x in nodes]
    return ({
        "status": "MEASURED",
        "nodes": n, "directed_edges": e, "undirected_edges": undirected_edges,
        "edges_per_node_x1000": (1000 * e) // n if n else 0,
        "density_ppm": (1_000_000 * 2 * undirected_edges) // (n * (n - 1)) if n > 1 else 0,
        "max_degree": max(deg.values()) if deg else 0,
        "closed_ego_1hop_sizes": summary(ego1),
        "modules_with_ego_over_default_budget": sum(1 for s in ego1 if s > b["neighbourhood_nodes_default_max"]),
        "scc_count": len(comps), "largest_scc": largest, "largest_connected_component": largest_cc,
        "whole_graph_nodes_over_default_node_link_budget": n > b["neighbourhood_nodes_default_max"],
        "whole_graph_matrix_cells": n * n,
        "hv08_selection_sizes_at_default_budget": summary(sel_sizes),
        "domain": "modules of src/eija_studio; imports resolved by ast among those modules; stdlib and third party ignored",
    }, (nodes, edges, paths))


# ------------------------------------------------------------------------------------------ requirements
def kind_of(path: str) -> str:
    for prefix, kind in (("tests/", "test"), ("scripts/", "script"), ("docs/", "doc"), ("evidence/", "evidence"),
                         ("verification/", "verification")):
        if path.startswith(prefix):
            return kind
    return "other"


def requirements_section(defn: dict) -> tuple[dict, list[dict]]:
    text = read(ROOT / "docs" / "verification" / "ACCEPTANCE_MATRIX.csv")
    rows = list(csv.DictReader(io.StringIO(text)))
    b = defn["budgets"]
    areas: dict[str, int] = {}
    kinds: set[str] = set()
    filled = 0
    status_counts: dict[str, int] = {}
    files: set[str] = set()
    for r in rows:
        areas[r["area"]] = areas.get(r["area"], 0) + 1
        st = r["v0_2_status"]
        status_counts[st] = status_counts.get(st, 0) + 1
        ks = set()
        for ev in (x.strip() for x in r["v0_2_evidence"].split(";")):
            if ev:
                files.add(ev)
                ks.add(kind_of(ev))
        kinds |= ks
        filled += len(ks)
    n_rows, n_cols = len(rows), len(kinds)
    return ({
        "status": "MEASURED",
        "rows": n_rows, "area_groups": len(areas), "largest_area_group": max(areas.values()) if areas else 0,
        "area_group_sizes": sorted(areas.values(), reverse=True),
        "evidence_kinds_as_columns": sorted(kinds), "columns": n_cols,
        "distinct_evidence_files": len(files),
        "matrix_cells_whole": n_rows * n_cols, "cells_filled_by_kind": filled,
        "v0_2_status_counts": {k: status_counts[k] for k in sorted(status_counts)},
        "pages_at_rows_per_page_budget": -(-n_rows // b["matrix_rows_per_page_max"]),
        "singleton_areas": sum(1 for v in areas.values() if v == 1),
        "whole_table_exceeds_rows_per_page_budget": n_rows > b["matrix_rows_per_page_max"],
                "columns_within_budget": n_cols <= b["matrix_columns_max"],
        "domain": "docs/verification/ACCEPTANCE_MATRIX.csv; a column is a kind of evidence file (test, script, doc, ...); rows are grouped by the `area` column",
    }, [{"id": r["id"], "area": r["area"], "evidence": [x.strip() for x in r["v0_2_evidence"].split(";") if x.strip()]}
        for r in rows])


# -------------------------------------------------------------------------------------------- language, adrs
def language_section(defn: dict) -> dict:
    text = read(ROOT / "docs" / "architecture" / "ARCHITECTURE.md")
    terms = re.findall(r"^\*\*([^*:\n]+):\*\*", text.split("## Ubiquitous language", 1)[1].split("\n## ", 1)[0], re.M)
    ctx_block = text.split("## Context map", 1)[1].split("\n## ", 1)[0]
    ctx_rows = [ln for ln in ctx_block.splitlines() if ln.startswith("|") and not ln.startswith("| Bounded") and not ln.startswith("|---")]
    wf: dict = {}
    try:
        from eija_studio.domain.models import Workflow
        w = Workflow.model_validate(json.loads(read(ROOT / "examples" / "excursion-baseline.json")))
        wf = {"states": len(w.states), "transitions": len(w.transitions), "roles": len({t.role for t in w.transitions})}
    except Exception as exc:  # kernel not importable: report, never guess
        wf = {"status": "NOT_RUN", "reason": f"kernel import failed: {type(exc).__name__}"}
    return {"status": "MEASURED", "terms": len(terms), "contexts": len(ctx_rows), "baseline_workflow": wf,
            "tree_depth_checkable": False,
            "tree_depth_reason": "NOT_RUN: no term registry with ddd_role exists yet, so context -> aggregate -> value object depth cannot be computed",
            "domain": "ARCHITECTURE.md ubiquitous-language paragraphs and context-map rows; examples/excursion-baseline.json"}


def adr_section() -> dict:
    files = adr_files()
    nums = {p.name[:4] for p in files}
    edges: set[tuple[str, str]] = set()
    for p in files:
        me = p.name[:4]
        for m in re.finditer(r"\((\d{4})-[a-z0-9-]+\.md\)|ADR-(\d{4})", read(p)):
            other = m.group(1) or m.group(2)
            if other in nums and other != me:
                edges.add((me, other))
    return {"status": "MEASURED", "adr_files": len(files), "reference_edges": len(edges),
            "domain": "docs/adr records numbered below 0089 (outside the weave block); an edge is a markdown link or an ADR-NNNN mention of another of them"}


# ---------------------------------------------------------------------------------------- typed ripple
SOUND = {"verifies": 0, "depends_on": 1, "covers": 1}


def typed_ripple_section(defn: dict, graph: tuple, req_rows: list[dict]) -> dict:
    nodes, imports, _ = graph
    b = defn["budgets"]
    links: list[tuple[str, str, str]] = []  # (src, link type, dst) in the metamodel direction: test covers module, test verifies req
    tests = sorted(ROOT.joinpath("tests").glob("test_*.py"))
    known = set(nodes)
    for a, c in sorted(imports):
        links.append((f"module:{a}", "depends_on", f"module:{c}"))
    test_ids = []
    for p in tests:
        tid = f"test:{rel(p)}"
        test_ids.append(tid)
        for m in sorted(resolve_imports(ast.parse(read(p)), "tests." + p.stem, False, known)):
            links.append((tid, "covers", f"module:{m}"))
    n_req_no_test = 0
    for r in req_rows:
        tf = [f"test:{e}" for e in r["evidence"] if f"test:{e}" in set(test_ids)]
        if not tf:
            n_req_no_test += 1
        for t in tf:
            links.append((t, "verifies", f"req:{r['id']}"))
    # impact arcs (the direction a change flows): a change in a dependency or in a covered module reaches the
    # dependent module or the covering test (dst -> src); a change in a test reaches the requirement it verifies (src -> dst)
    flow = [(src, dst, SOUND[t]) if t == "verifies" else (dst, src, SOUND[t]) for src, t, dst in links]
    kind_of_pair = {((src, dst) if t == "verifies" else (dst, src)): t for src, t, dst in links}
    per_module: list[dict] = []
    segs_all: list[int] = []
    hops_all: list[int] = []
    examples: dict[str, dict] = {}
    for m in nodes:
        root = f"module:{m}"
        reach = ref.tiered_reach(flow, [root])
        by = {"module": 0, "test": 0, "req": 0}
        by_tier = {0: 0, 1: 0, 2: 0}
        cells: dict[str, int] = {}
        for node, info in reach.items():
            if node == root:
                continue
            by[node.split(":", 1)[0]] += 1
            by_tier[info["tier"]] += 1
            key = f"{node.split(':', 1)[0]}@tier{info['tier']}"
            cells[key] = cells.get(key, 0) + 1
        if m in ("eija_studio.domain.impact", "eija_studio.domain.policy", "eija_studio.interfaces.http"):
            examples[m] = {"by_kind_and_tier": {k: cells[k] for k in sorted(cells)},
                           "direct": sum(1 for n, i in reach.items() if i["distance"] == 1)}
        per_module.append({"module": m, **by, "tier0": by_tier[0], "tier1": by_tier[1], "tier2": by_tier[2]})
        for node, info in reach.items():
            if not node.startswith("req:"):
                continue
            path = [node]
            while path[-1] != root:
                path.append(reach_parent(flow, root, info["tier"], path[-1]))
            path.reverse()
            keys = [(kind_of_pair[(path[i], path[i + 1])],) for i in range(len(path) - 1)]
            segs_all.append(len(ref.segments(keys)))
            hops_all.append(len(keys))
    req_counts = [x["req"] for x in per_module]
    test_counts = [x["test"] for x in per_module]
    over = sum(1 for x in per_module if x["req"] > b["rows_before_more"] or x["test"] > b["rows_before_more"])
    return {"status": "MEASURED",
            "typed_nodes": {"module": len(nodes), "test": len(test_ids), "req": len(req_rows)},
            "typed_links": {"depends_on": sum(1 for _, t, _ in links if t == "depends_on"),
                            "covers": sum(1 for _, t, _ in links if t == "covers"),
                            "verifies": sum(1 for _, t, _ in links if t == "verifies")},
            "affected_requirements_per_changed_module": summary(req_counts),
            "affected_tests_per_changed_module": summary(test_counts),
            "modules_needing_overflow_at_rows_before_more": over,
            "modules_touched_by_no_test": sum(1 for x in per_module if x["test"] == 0),
            "example_changed_modules": {k: examples[k] for k in sorted(examples)},
            "tier0_reach_anywhere": sum(x["tier0"] for x in per_module),
            "requirements_without_any_test_file": n_req_no_test,
            "witness_segments_to_requirements": summary(segs_all), "witness_hops_to_requirements": summary(hops_all),
            "segments_within_default_budget": all(s <= b["witness_segments_default_max"] for s in segs_all),
            "domain": "typed graph derived from this repo: depends_on and covers from ast imports (class derived, soundness may), verifies from the CSV evidence column (declared, must); tiers by nested closure; import-based covers is a proxy, not coverage"}


def reach_parent(flow: list, root: str, tier: int, node: str) -> str:
    """Canonical parent of `node` in the closure of `root` at `tier` (reference BFS)."""
    parent = ref.bfs(ref._adj(flow, tier), [root])[node][1]
    assert parent is not None
    return parent


def kernel_ripple_section() -> dict:
    try:
        from eija_studio.domain.impact import model_impact
        from eija_studio.domain.models import Workflow
        a = Workflow.model_validate(json.loads(read(ROOT / "examples" / "excursion-baseline.json")))
        c = Workflow.model_validate(json.loads(read(ROOT / "examples" / "excursion-candidate.json")))
    except Exception as exc:
        return not_run(f"kernel not importable: {type(exc).__name__}")
    r = model_impact(a, c)
    by_type: dict[str, int] = {}
    for n in r["affected"]:
        k = n.split(":", 1)[0]
        by_type[k] = by_type.get(k, 0) + 1
    return {"status": "MEASURED", "changed_actions": r["changed_actions"], "affected": len(r["affected"]),
            "complete": r["complete"], "affected_by_kind": {k: by_type[k] for k in sorted(by_type)},
            "edge_kinds_in_kernel_graph": 1,
            "note": "the kernel projection has one edge kind, so a witness there is one segment of up to 7 hops; the typed graph is what makes segments informative",
            "domain": "model_impact(excursion-baseline, excursion-candidate)"}


# ------------------------------------------------------------------------------------------ roll-up laws
COVERS = (("NOT_RUN", "UNKNOWN"), ("UNKNOWN", "STALE"), ("STALE", "PASS"), ("STALE", "FAIL"), ("PASS", "CONFLICT"), ("FAIL", "CONFLICT"))


def _leq() -> set[tuple[str, str]]:
    le = {(a, a) for a in STATUSES} | set(COVERS)
    changed = True
    while changed:
        changed = False
        for (a, b_), (c, d) in itertools.product(sorted(le), sorted(le)):
            if b_ == c and (a, d) not in le:
                le.add((a, d))
                changed = True
    return le


LEQ = _leq()


def join2(a: str, b: str) -> str:
    ub = [x for x in STATUSES if (a, x) in LEQ and (b, x) in LEQ]
    least = [x for x in ub if all((x, y) in LEQ for y in ub)]
    assert len(least) == 1
    return least[0]


def join(vals) -> str:
    out = "NOT_RUN"
    for v in vals:
        out = join2(out, v)
    return out


def kernel_agg(statuses) -> str:
    from eija_studio.domain import evidence as kernel_evidence
    with mock.patch.object(kernel_evidence, "assess_receipt", lambda r, s, c, k: r["st"]):
        return kernel_evidence.aggregate_status([{"st": x} for x in statuses], {}, lambda r: True)


def vec(statuses) -> tuple[int, ...]:
    return tuple(sum(1 for s in statuses if s == v) for v in STATUSES)


def rollup_section(defn: dict | None = None) -> dict:
    """Laws C1, C2, C4 for the badge operator fold_b, the join as a negative control for badges, and the kernel
    re-aggregation as a negative control for hierarchical roll-up (it does not occur in the kernel)."""
    defn = defn or load_definition()
    chain = defn["chain_worst_first"]
    out: dict = {"status": "MEASURED"}
    # C1, C2, C4 on seeded random trees (depth 3, random fan-out, leaf statuses uniform over the six values)
    rng = SplitMix64(20260929)
    trees, c1_bad, c2_bad, c4_bad, pass_iff_bad, join_masks = 500, 0, 0, 0, 0, 0

    def gen(depth: int):
        if depth == 0:
            return STATUSES[rng.below(6)]
        return [gen(depth - 1) for _ in range(1 + rng.below(5))]

    def leaves(t):
        return [t] if isinstance(t, str) else [x for c in t for x in leaves(c)]

    def node_vec(t):
        return vec([t]) if isinstance(t, str) else tuple(map(sum, zip(*[node_vec(c) for c in t])))

    for _ in range(trees):
        t = gen(3)
        flat = leaves(t)
        badge = ref.badge_from_counts(node_vec(t), chain)
        c1_bad += node_vec(t) != vec(flat)
        c2_bad += sum(node_vec(t)) != len(flat)
        c4_bad += badge != ref.fold_b(flat, chain)
        pass_iff_bad += (badge == "PASS") != all(x == "PASS" for x in flat)
        join_masks += join(flat) == "PASS" and any(x != "PASS" for x in flat)
    out["counts_vector_and_badge_laws"] = {
        "trees": trees, "c1_mismatches": c1_bad, "c2_mismatches": c2_bad,
        "c4_badge_equals_flat_fold_b_mismatches": c4_bad,
        "badge_pass_iff_every_leaf_pass_violations": pass_iff_bad,
        "negative_control_join_badge_pass_while_a_leaf_is_not_pass": join_masks,
        "domain": "500 seeded random trees of depth 3, fan-out 1 to 5, leaves uniform over six statuses; badge = fold_b (chain minimum) over the support of the counts vector; the negative control is the weave join used as a badge"}
    # exhaustive: which operator may be a badge? PASS iff all PASS, over every sequence of length 1..5
    seqs = pass_iff_fold_b = pass_iff_join = 0
    example = None
    for n in range(1, 6):
        for seq in itertools.product(STATUSES, repeat=n):
            seqs += 1
            all_pass = all(x == "PASS" for x in seq)
            pass_iff_fold_b += (ref.fold_b(seq, chain) == "PASS") != all_pass
            j_bad = (join(seq) == "PASS") != all_pass
            pass_iff_join += j_bad
            if j_bad and example is None:
                example = {"sequence": list(seq), "join": join(seq), "fold_b": ref.fold_b(seq, chain)}
    out["badge_operator_pass_iff_all_pass"] = {
        "sequences": seqs, "fold_b_violations": pass_iff_fold_b, "join_violations_negative_control": pass_iff_join,
        "first_join_example": example,
        "domain": "all sequences over six statuses, length 1 to 5; a violation is a PASS badge with a non-PASS item, or a non-PASS badge with all items PASS"}
    # split composition: fold_b of the two partial badges equals the flat badge (non-empty parts); the join is
    # idempotent and associative too, which is why this check alone cannot tell the two operators apart
    cases = bad_b = bad_j = 0
    for n in range(2, 6):
        for seq in itertools.product(STATUSES, repeat=n):
            for k in range(1, n):
                cases += 1
                bad_b += ref.fold_b([ref.fold_b(seq[:k], chain), ref.fold_b(seq[k:], chain)], chain) != ref.fold_b(seq, chain)
                bad_j += join([join(seq[:k]), join(seq[k:])]) != join(seq)
    out["split_composition_non_empty_parts"] = {
        "cases": cases, "fold_b_mismatches": bad_b, "join_mismatches": bad_j,
        "note": "both operators compose; composition does not decide which one is a valid badge (see badge_operator_pass_iff_all_pass)",
        "domain": "all sequences over six statuses, length 2 to 5, every two-way split"}
    # negative control: kernel aggregate_status re-applied to its own output. The kernel never does this (it
    # aggregates a flat receipt list); the harness feeds statuses back as receipts to show what a hierarchical
    # re-aggregation would do.
    try:
        cases = bad = pass_up = 0
        example = None
        inputs = ("PASS", "FAIL", "STALE", "UNKNOWN")
        for n in range(2, 7):
            for seq in itertools.product(inputs, repeat=n):
                flat = kernel_agg(seq)
                for k in range(1, n):
                    cases += 1
                    rolled = kernel_agg([kernel_agg(seq[:k]), kernel_agg(seq[k:])])
                    if rolled != flat:
                        bad += 1
                        pass_up += rolled == "PASS" and flat != "PASS"
                        if example is None:
                            example = {"sequence": list(seq), "split_at": k, "flat": flat, "rolled_up": rolled}
        out["negative_control_kernel_reaggregation"] = {
            "cases": cases, "mismatches": bad, "rolled_up_pass_while_flat_not_pass": pass_up,
            "first_example": example,
            "mismatch_per_10000": (10000 * bad) // cases if cases else 0,
            "label": "NEGATIVE CONTROL for a hypothetical hierarchical re-aggregation. It is not a failure that occurs in EIJA: the kernel takes receipts and never re-aggregates its own output; the harness patches assess_receipt to identity to feed statuses back in.",
            "domain": "all sequences over {PASS, FAIL, STALE, UNKNOWN}, length 2 to 6, every two-way split; kernel evidence.aggregate_status with assess_receipt patched to identity"}
    except Exception as exc:
        out["negative_control_kernel_reaggregation"] = not_run(f"kernel not importable: {type(exc).__name__}")
    return out


# ------------------------------------------------------------------------------------------------ budgets
def budget_section(defn: dict, sections: dict) -> dict:
    b = defn["budgets"]
    ig, rq, lg, tr = sections["import_graph"], sections["requirements"], sections["language"], sections["typed_ripple"]
    kr = sections["kernel_ripple"]
    checks: list[dict] = []

    def add(view: str, name: str, value, limit, ok: bool | None, note: str = "") -> None:
        checks.append({"view": view, "check": name, "value": value, "limit": limit,
                       "within": ok if ok is None else bool(ok), "note": note})

    add("HV-01", "change digest", None, None, None, "NOT_RUN: no graph snapshots exist, so no keyed diff can be measured")
    add("HV-02", "affected tests per changed module (max)", tr["affected_tests_per_changed_module"]["max"], b["rows_before_more"],
        tr["affected_tests_per_changed_module"]["max"] <= b["rows_before_more"], "over the limit means priority-then-cap and 'N more' apply")
    add("HV-02", "affected requirements per changed module (max)", tr["affected_requirements_per_changed_module"]["max"], b["rows_before_more"],
        tr["affected_requirements_per_changed_module"]["max"] <= b["rows_before_more"], "same")
    if kr.get("status") == "MEASURED":
        add("HV-02", "kernel ripple, affected nodes", kr["affected"], b["l0_rows_max"], kr["affected"] <= b["l0_rows_max"])
    add("HV-03", "rows in the whole table", rq["rows"], b["matrix_rows_per_page_max"], not rq["whole_table_exceeds_rows_per_page_budget"], "over the limit means paging; pages = " + str(rq["pages_at_rows_per_page_budget"]))
    add("HV-03", "columns (evidence kinds)", rq["columns"], b["matrix_columns_max"], rq["columns_within_budget"])
    add("HV-03", "cells of the first page", min(rq["rows"], b["matrix_rows_per_page_max"]) * rq["columns"], b["matrix_cells_max"],
        min(rq["rows"], b["matrix_rows_per_page_max"]) * rq["columns"] <= b["matrix_cells_max"])
    layers = sorted({n.split(".")[1] for n in sections["_nodes"] if n.count(".") >= 1 and n.split(".")[1] in ("domain", "application", "adapters", "interfaces")})
    add("HV-04", "default expansion rows (root plus layers)", 1 + len(layers), b["coverage_default_rows_max"], 1 + len(layers) <= b["coverage_default_rows_max"])
    add("HV-04", "container depth (package, layer, module)", 3, b["tree_depth_max"], 3 <= b["tree_depth_max"])
    add("HV-05", "tree depth", None, b["tree_depth_max"], None, lg["tree_depth_reason"])
    add("HV-06", "findings", None, None, None, "NOT_RUN: no rule is implemented, so no findings exist")
    add("HV-07", "witness segments to a requirement (max)", tr["witness_segments_to_requirements"]["max"], b["witness_segments_default_max"],
        tr["segments_within_default_budget"])
    add("HV-08", "whole import graph nodes", ig["nodes"], b["neighbourhood_nodes_default_max"], not ig["whole_graph_nodes_over_default_node_link_budget"],
        "over the limit means the whole graph is never drawn as one node-link diagram")
    add("HV-08", "closed 1-hop ego size (max)", ig["closed_ego_1hop_sizes"]["max"], b["neighbourhood_nodes_default_max"],
        ig["closed_ego_1hop_sizes"]["max"] <= b["neighbourhood_nodes_default_max"])
    add("HV-08", "largest connected component (upper bound on any selection)", ig["largest_connected_component"], b["neighbourhood_nodes_default_max"],
        ig["largest_connected_component"] <= b["neighbourhood_nodes_default_max"],
        "within means the node budget never binds on this repo; a selection cannot exceed the budget by construction, so its size is not a check")
    return {"status": "MEASURED", "checks": checks,
            "note": "within=null means NOT_RUN. A false 'within' is an expected finding: it says which overflow rule the view needs on this repo."}


# --------------------------------------------------------------------------------------------------- main
def run() -> dict:
    defn = load_definition()
    files = input_files()
    sections: dict = {"inputs": inputs_section(files)}
    ig, graph = import_graph_section(defn)
    sections["import_graph"] = ig
    rq, req_rows = requirements_section(defn)
    sections["requirements"] = rq
    sections["language"] = language_section(defn)
    sections["adrs"] = adr_section()
    sections["typed_ripple"] = typed_ripple_section(defn, graph, req_rows)
    sections["kernel_ripple"] = kernel_ripple_section()
    sections["rollup"] = rollup_section(defn)
    sections["_nodes"] = graph[0]
    sections["budgets"] = budget_section(defn, sections)
    del sections["_nodes"]
    return {"schema": "eija.weave.bench.human-views/v1", "label": "MEASUREMENT of slice sizes; no comprehension effect is measured",
            "definition_digest": ref.definition_digest(defn),
            "sections": sections}


def dumps(doc: dict) -> str:
    return json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    text = dumps(run())
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    else:
        sys.stdout.buffer.write(text.encode("utf-8"))
    print(f"deterministic_sha256 {digest}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
