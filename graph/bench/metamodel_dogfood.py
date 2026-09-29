"""Apply the metamodel to this repository's real artefacts and report what fits and what does not.

A minimal prototype, NOT the extractor lane's product: it reads the excursion workflow JSON, the acceptance
matrix, the ubiquitous-language terms, the ADR files and two Python symbols with stdlib parsers, builds a
graph document, validates it against graph/schema/graph.schema.json and graph/schema/typecheck.py, and
checks that the root hash is stable across file order and rebuilds. Digest methods that the okf lane already
implements are cross-checked against quality/okf/codelink.py in the sibling worktree when it is present
(NOT_RUN otherwise). The kernel is used as a test oracle only.

    python graph/bench/metamodel_dogfood.py           # print the report (canonical ASCII JSON)
    python graph/bench/metamodel_dogfood.py --write   # also write graph/bench/results/metamodel-dogfood.json
"""
from __future__ import annotations

import ast
import csv
import hashlib
import importlib.util
import io
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_PATHS = [str(HERE), str(ROOT / "graph" / "schema"), str(ROOT / "src")]
sys.path[:0] = _PATHS
try:
    import build_schemas
    import identity_checks as ic
    import typecheck

    from eija_studio.domain.impact import closure as kernel_closure
    from eija_studio.domain.models import Workflow
finally:  # do not leave the bench and schema directories on sys.path for other modules
    for _p in _PATHS[:2]:
        if _p in sys.path:
            sys.path.remove(_p)

try:
    import jsonschema
except ImportError:
    jsonschema = None

MM = build_schemas.load()
WORKFLOW = "examples/excursion-baseline.json"
MATRIX = "docs/verification/ACCEPTANCE_MATRIX.csv"
ARCH = "docs/architecture/ARCHITECTURE.md"
IMPACT = "src/eija_studio/domain/impact.py"
LINKS = "graph/links/acceptance-matrix.jsonl"  # hypothetical committed file that would assert the matrix-derived links


def text(rel: str) -> str:
    return (ROOT / rel).read_bytes().decode("utf-8").replace("\r\n", "\n")


def sha(value: Any) -> str:
    return "sha256:" + hashlib.sha256(ic.jcs_dumps(value)).hexdigest()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def okf_codelink():
    path = ROOT.parent / "okf" / "quality" / "okf" / "codelink.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("okf_codelink", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["okf_codelink"] = mod
    spec.loader.exec_module(mod)
    return mod


def rec(node_id: str, type_name: str, method: str, value: str, attrs: dict | None = None) -> dict:
    r = {"id": node_id, "type": type_name, "prov": "exact", "digest": {"method": method, "value": value}}
    if attrs:
        r["attrs"] = attrs
    return r


def workflow_semantic(doc: dict) -> str:
    """workflow-semantic-v1: Workflow.semantic_hash reimplemented from the JSON (kernel canonical(), bare digest)."""
    data = json.loads(json.dumps(doc))
    data["states"] = sorted(data["states"])
    data["transitions"] = sorted(data["transitions"], key=lambda x: x["id"])
    for t in data["transitions"]:
        for key in ("guards", "required_effects", "forbidden_effects"):
            t[key] = sorted(t[key])
    blob = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build(files_shuffle_seed: int | None = None) -> dict[str, Any]:
    ok = okf_codelink()
    nodes: list[dict] = []
    edges: list[dict] = []
    stats: dict[str, Any] = {}
    cross: dict[str, Any] = {}

    def edge(kind: str, a: str, b: str, asserted: str, cls: str = "derived", qualifier: str | None = None,
             anchors: list[dict] | None = None) -> None:
        e = {"kind": kind, "from": a, "to": b, "class": cls, "prov": "exact", "asserted_in": asserted}
        if qualifier:
            e["qualifier"] = qualifier
        if anchors:
            e["anchors"] = anchors
        edges.append(e)

    # ---- workflow: 1 workflow, states, transitions, roles, guards, effects
    wf = json.loads(text(WORKFLOW))
    sem = workflow_semantic(wf)
    kernel = Workflow.model_validate(wf).semantic_hash
    cross["workflow_semantic_v1_equals_kernel_semantic_hash"] = sem == kernel
    wid = ic.make_id(WORKFLOW)
    nodes.append(rec(wid, "workflow", "workflow-semantic-v1", "sha256:" + sem))
    elements: dict[tuple[str, str], str] = {}

    def element(kind: str, name: str, payload: Any, attrs: dict | None = None) -> str:
        nid = ic.make_id(WORKFLOW, kind, name)
        if (kind, name) not in elements:
            elements[(kind, name)] = nid
            nodes.append(rec(nid, kind, "workflow-element-v1", sha({kind: payload}), attrs))
            edge("contains", wid, nid, WORKFLOW)
        return nid

    for s in wf["states"]:
        element("state", s, s, {"initial": True} if s == wf["initial_state"] else None)
    for t in wf["transitions"]:
        norm = {**t, "guards": sorted(t["guards"]), "required_effects": sorted(t["required_effects"]),
                "forbidden_effects": sorted(t["forbidden_effects"])}
        element("transition", t["id"], norm, {"action": t["action"]})
        element("role", t["role"], t["role"])
        for g in t["guards"]:
            element("guard", g, g)
        for x in t["required_effects"] + t["forbidden_effects"]:
            element("effect", x, x)
    for t in wf["transitions"]:
        tid = elements[("transition", t["id"])]
        edge("flows_to", elements[("state", t["from_state"])], tid, WORKFLOW)
        edge("flows_to", tid, elements[("state", t["to_state"])], WORKFLOW)
        edge("depends_on", tid, elements[("role", t["role"])], WORKFLOW)
        for g in t["guards"]:
            edge("depends_on", tid, elements[("guard", g)], WORKFLOW)
        for x in t["required_effects"]:
            edge("depends_on", tid, elements[("effect", x)], WORKFLOW, qualifier="required")
        for x in t["forbidden_effects"]:
            edge("depends_on", tid, elements[("effect", x)], WORKFLOW, qualifier="forbidden")

    # ---- requirements (csv-row-v1)
    rows = list(csv.DictReader(io.StringIO(text(MATRIX), newline="")))
    req_ids: dict[str, str] = {}
    agree: dict[str, bool] = {}  # per hash method: does this file's digest equal the okf lane's, on every node checked

    def check(method: str, ref: Any, value: str) -> None:
        if ok:
            agree[method] = agree.get(method, True) and "sha256:" + ok.digest(ROOT, ref, method) == value

    for r in rows:
        rid = ic.make_id(MATRIX, r["id"])
        value = "sha256:" + hashlib.sha256(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        nodes.append(rec(rid, "requirement", "csv-row-v1", value, {"area": r["area"]}))
        req_ids[r["id"]] = rid
        check("csv-row-v1", ok and ok.CodeRef(MATRIX, r["id"]), value)

    # ---- matrix evidence column -> file-level test nodes and declared verifies links
    tokens = []
    for r in rows:
        for tok in re.split(r";\s*", r["v0_2_evidence"]):
            if tok.strip():
                tokens.append((r["id"], tok.strip()))
    test_nodes: dict[str, str] = {}
    unresolved, not_verifiers, with_fragment = [], [], 0
    for rid, tok in tokens:
        with_fragment += ("::" in tok) or ("#" in tok)
        path = tok.split("::")[0]
        if not (ROOT / path).is_file():
            unresolved.append(tok)
            continue
        if not re.fullmatch(r"(?:tests|scripts)/.+\.py", path):
            not_verifiers.append(tok)
            continue
        if path not in test_nodes:
            tid = ic.make_id(path)
            test_nodes[path] = tid
            value = ic.lf_sha256((ROOT / path).read_bytes())
            nodes.append(rec(tid, "test", "lf-sha256-v1", value, {"kind": "e2e" if path.startswith("scripts/") else "unit"}))
            check("lf-sha256-v1", ok and ok.CodeRef(path), value)
        req = next(n for n in nodes if n["id"] == req_ids[rid])
        tnode = next(n for n in nodes if n["id"] == test_nodes[path])
        edge("verifies", test_nodes[path], req_ids[rid], LINKS, cls="declared", anchors=[
            {"end": "from", "method": "lf-sha256-v1", "digest": tnode["digest"]["value"]},
            {"end": "to", "method": "csv-row-v1", "digest": req["digest"]["value"]}])
    stats["matrix"] = {"requirements": len(rows), "evidence_references": len(tokens), "references_with_a_function_fragment": with_fragment,
                       "references_that_are_existing_test_or_script_files": sum(1 for _, t in tokens if t.split("::")[0] in test_nodes),
                       "distinct_test_files": len(test_nodes), "unresolved_as_written": sorted(unresolved),
                       "existing_files_that_are_not_verifiers": sorted(not_verifiers),
                       "requirements_with_no_verifies_link": sorted(k for k, v in req_ids.items()
                                                                   if not any(e["kind"] == "verifies" and e["to"] == v for e in edges))}

    # ---- terms (md-bold-term-v1): "**Term:** definition" paragraphs of the ubiquitous language
    arch = text(ARCH)
    terms, seen_slugs = [], {}
    for para in re.split(r"\n\s*\n", arch):
        m = re.match(r"^\*\*(?P<term>[^*]+?):\*\*\s*(?P<body>.*)$", " ".join(para.split()))
        if m:
            terms.append((m["term"].strip(), " ".join(m["body"].split())))
    for term, body in terms:
        frag = slug(term)
        seen_slugs.setdefault(frag, []).append(term)
        tid = ic.make_id(ARCH, frag)
        value = "sha256:" + hashlib.sha256(json.dumps([term, body], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        if not any(n["id"] == tid for n in nodes):
            nodes.append(rec(tid, "term", "md-bold-term-v1", value))
        check("md-bold-term-v1", ok and ok.CodeRef(ARCH, frag), value)
    stats["terms"] = {"terms": len(terms), "slug_collisions": sorted(k for k, v in seen_slugs.items() if len(v) > 1)}

    # ---- ADRs (lf-sha256-v1)
    adrs = sorted(p.name for p in (ROOT / "docs" / "adr").glob("*.md") if re.fullmatch(r"[0-9]{4}-[a-z0-9-]+\.md", p.name))
    for name in adrs:
        rel = f"docs/adr/{name}"
        nodes.append(rec(ic.make_id(rel), "adr", "lf-sha256-v1", ic.lf_sha256((ROOT / rel).read_bytes())))
    stats["adrs"] = len(adrs)

    # ---- two python symbols and their module (ast-v1, ast-api-v1)
    src = text(IMPACT)
    tree = ast.parse(src)
    mid = ic.make_id(IMPACT)
    if ok:
        api = ok.digest(ROOT, ok.CodeRef(IMPACT), "ast-api-v1")
        nodes.append(rec(mid, "module", "ast-api-v1", "sha256:" + api, {"lang": "python"}))
        for fn in ("closure", "model_impact"):
            nodes.append(rec(ic.make_id(IMPACT, fn), "symbol", "ast-v1", "sha256:" + ok.digest(ROOT, ok.CodeRef(IMPACT, fn), "ast-v1"),
                             {"lang": "python", "kind": "function", "visibility": "public"}))
            edge("contains", mid, ic.make_id(IMPACT, fn), IMPACT)
        edge("depends_on", ic.make_id(IMPACT, "model_impact"), ic.make_id(IMPACT, "closure"), IMPACT)
        stats["python"] = {"functions_seen_by_ast": sorted(n.name for n in tree.body if isinstance(n, ast.FunctionDef))}
    else:
        stats["python"] = {"status": "NOT_RUN", "reason": "okf worktree not found; ast-v1 needs its normaliser"}

    cross["digests_equal_to_okf_codelink_by_method"] = (
        dict(sorted(agree.items())) if ok else {"status": "NOT_RUN", "reason": "okf worktree not found"})
    if files_shuffle_seed is not None:
        rng = random.Random(files_shuffle_seed)
        rng.shuffle(nodes)
        rng.shuffle(edges)
    return {"nodes": nodes, "edges": edges, "stats": stats, "cross": cross}


#: okf lane page `type` -> weave node type (symbol kinds share one weave type)
OKF_TYPES = {"Acceptance Criterion": "requirement", "Architecture Decision Record": "adr", "Method": "symbol", "Function": "symbol",
             "Class": "symbol", "Constant": "symbol", "Type Alias": "symbol", "Module": "module", "Capability Lane": "lane",
             "Ubiquitous Language Term": "term", "Bounded Context": "bounded_context", "Quality Gate": "gate",
             "Verification Technique": "document"}


def okf_bundle() -> dict:
    """Map every concept page of the sibling okf bundle to a weave node type and test its `resource` against the id pattern."""
    bundle = ROOT.parent / "okf" / "okf"
    if not bundle.is_dir():
        return {"status": "NOT_RUN", "reason": "okf worktree not found"}
    import collections
    patterns = {t: re.compile(build_schemas.id_pattern(MM, t)) for t in MM["node_types"]}
    pages = collections.Counter()
    unmapped, invalid, noncanonical_slug = collections.Counter(), [], 0
    methods_seen: collections.Counter = collections.Counter()
    for f in sorted(bundle.rglob("*.md")):
        if f.name in ("index.md", "log.md"):
            continue
        raw = f.read_bytes().decode("utf-8").replace("\r\n", "\n")
        m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
        if not m:
            continue
        fm = m.group(1)
        ty, res = re.search(r"^type:\s*(.+)$", fm, re.M), re.search(r"^resource:\s*(.+)$", fm, re.M)
        if not ty:
            continue
        pages[ty.group(1).strip()] += 1
        for hm in re.findall(r"hash_method:\s*(\S+)", fm):
            methods_seen[hm] += 1
        weave = OKF_TYPES.get(ty.group(1).strip())
        if weave is None:
            unmapped[ty.group(1).strip()] += 1
        elif res and not patterns[weave].fullmatch(res.group(1).strip()):
            invalid.append([ty.group(1).strip(), res.group(1).strip()])
    known = {m["id"] for m in MM["hash_methods"]}
    return {"status": "MEASURED", "domain": "concept pages (index.md and log.md excluded) of the okf worktree bundle at the time of the run",
            "concept_pages": sum(pages.values()), "okf_types": dict(sorted(pages.items())),
            "pages_of_unmapped_types": dict(sorted(unmapped.items())),
            "resources_not_matching_the_pattern_of_the_mapped_type": len(invalid), "examples": sorted(invalid)[:3],
            "hash_methods_used": dict(sorted(methods_seen.items())),
            "hash_methods_not_in_the_weave_registry": sorted(set(methods_seen) - known)}


def arcs(edges: list[dict], collapse_both: bool) -> dict[str, list[str]]:
    """Impact adjacency from the metamodel's `affects`: a change at the key affects the values (kernel closure shape)."""
    adj: dict[str, list[str]] = {}
    for e in edges:
        flow = MM["link_types"][e["kind"]]["affects"]
        if flow == "both" and collapse_both:
            flow = "to_source"
        if flow in ("to_target", "both"):
            adj.setdefault(e["from"], []).append(e["to"])
        if flow in ("to_source", "both"):
            adj.setdefault(e["to"], []).append(e["from"])
    return adj


def fanout(nodes: list[dict], edges: list[dict]) -> dict:
    """Closure sizes over every node as a root: `both` on the anchored trace kinds versus dependent-affected-only."""
    out: dict[str, Any] = {"status": "MEASURED", "domain": f"the {len(nodes)}-node dogfood graph, every node as one root, kernel closure()"}
    for name, collapse in (("metamodel_affects", False), ("both_collapsed_to_to_source", True)):
        adj = arcs(edges, collapse)
        sizes = [len(kernel_closure(adj, [n["id"]])["affected"]) for n in nodes]
        out[name] = {"arcs": sum(len(v) for v in adj.values()), "sum_of_closure_sizes": sum(sizes), "max_closure": max(sizes),
                     "roots_reaching_more_than_half_the_nodes": sum(1 for s in sizes if 2 * s > len(nodes))}
    return out


def anchor_flow_lint() -> dict:
    """The impact aspect's lint: an anchored end needs the flow that leaves that end (from anchored: F; to anchored: R)."""
    bad = []
    for kind, k in sorted(MM["link_types"].items()):
        flow = {"to_target": {"F"}, "to_source": {"R"}, "both": {"F", "R"}, "none": set()}[k["affects"]]
        need = {"F"} if "from" in k["anchor_ends"] else set()
        need |= {"R"} if "to" in k["anchor_ends"] else set()
        if not need <= flow:
            bad.append(kind)
    return {"kinds_with_an_anchored_end_and_no_flow_away_from_it": bad, "kinds_with_anchors": sum(1 for k in MM["link_types"].values() if k["anchor_ends"])}


def report() -> dict:
    a = build()
    nodes = sorted(a["nodes"], key=lambda n: n["id"])
    edges = sorted(a["edges"], key=lambda e: ic.edge_key(e))
    doc = {"schema": "eija.weave.graph/v1", "metamodel": MM["metamodel_version"], "nodes": nodes, "edges": edges}
    out: dict[str, Any] = {"schema": "eija.weave.bench.dogfood/v1", "status": "MEASURED",
                           "domain": "this worktree at the state of the run: one workflow, the acceptance matrix, ARCHITECTURE.md, docs/adr, impact.py",
                           "nodes": len(nodes), "edges": len(edges),
                           "nodes_by_type": {t: sum(1 for n in nodes if n["type"] == t) for t in sorted({n["type"] for n in nodes})},
                           "edges_by_kind": {k: sum(1 for e in edges if e["kind"] == k) for k in sorted({e["kind"] for e in edges})},
                           "cross_checks": a["cross"], "stats": a["stats"]}
    findings = typecheck.check_document(MM, nodes, edges)
    out["reference_findings"] = [list(f) for f in findings]
    if jsonschema is None:
        out["schema_validation"] = {"status": "NOT_RUN", "reason": "jsonschema not installed"}
    else:
        schema = json.loads((ROOT / "graph" / "schema" / "graph.schema.json").read_text(encoding="utf-8"))
        errs = sorted(f"{list(e.absolute_path)[:3]}: {e.message[:100]}" for e in jsonschema.Draft202012Validator(schema).iter_errors(doc))
        out["schema_validation"] = {"status": "MEASURED", "errors": errs[:10], "error_count": len(errs)}
    r1 = ic.graph_root(nodes, edges)
    rebuilt = build()
    shuffled = build(3)
    out["root"] = r1
    out["root_equal_after_a_second_clean_extraction"] = r1 == ic.graph_root(rebuilt["nodes"], rebuilt["edges"])
    out["root_equal_when_extraction_order_is_shuffled"] = r1 == ic.graph_root(shuffled["nodes"], shuffled["edges"])
    out["shards"] = len(ic.shard_hashes(nodes, edges))
    out["impact_fanout"] = fanout(nodes, edges)
    out["okf_bundle"] = okf_bundle()
    out["anchor_flow_lint"] = anchor_flow_lint()
    # every id in the document must be canonical
    out["non_canonical_ids"] = sorted(n["id"] for n in nodes if not ic.is_canonical_id(n["id"]))
    return out


def dump(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main(argv: list[str]) -> int:
    rep = report()
    sys.stdout.write(dump(rep))
    if "--write" in argv:
        (ROOT / "graph" / "bench" / "results").mkdir(exist_ok=True)
        (ROOT / "graph" / "bench" / "results" / "metamodel-dogfood.json").write_bytes(dump(rep).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
