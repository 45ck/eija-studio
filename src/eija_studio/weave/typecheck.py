# ADAPTED from graph/schema/typecheck.py (WBS 1.6): docstring, _rows, _qualifier_ok and _cycle are verbatim; check_document and
# _rename_cycles are split into helpers to meet the complexity budget. tests/weave/test_weave_lift.py differential-tests both against
# the source (same findings on valid graphs, planted defects and random edits).
"""Join-level typing checks over a graph document: the part of the metamodel that JSON Schema cannot express.

JSON Schema validates each record alone (id grammar per node type, class, qualifier set, anchors, attrs).
It cannot join an edge to its endpoint nodes, so signature typing, structural cardinality, acyclicity,
self-loops and rename validity live here. This module is the executable definition that the rule lane's
implementation (WV-001, WV-002, WV-003, WV-055, WV-056) must agree with on the fixture graphs. It is
deliberately small and stdlib only. Findings are plain tuples sorted by (code, subject); no wall clock.

Cost: O(R * E + E log E) for E edges, where R is the largest number of signature rows of one kind (a constant of the metamodel,
at most 8). Signature rows are expanded once per kind, adjacency lists are sorted for a deterministic cycle report, and the
rename check walks each rename start once (O(S * L) for S starts and trajectories of length L).

    problems = check_document(metamodel, nodes, edges)   # [] means the document is well formed
"""
from __future__ import annotations

from typing import Any

from .metamodel import expand  # the source imports build_schemas.expand; lifted in metamodel.py

Finding = tuple[str, str, str]  # (code, subject, message)


def _rows(mm: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [{**r, "_from": set(expand(mm, r["from"])), "_to": set(expand(mm, r["to"]))} for r in mm["link_types"][kind]["signatures"]]


def _qualifier_ok(row: dict[str, Any], qual: str | None) -> bool:
    """A row without a qualifiers key accepts any qualifier the kind allows; an empty list means none."""
    if "qualifiers" not in row:
        return True
    return qual in row["qualifiers"] if row["qualifiers"] else qual is None


def _rename_step(id_map: dict[str, str], path_map: dict[str, str], cur: str) -> str | None:
    if cur in id_map:
        return id_map[cur]
    path, _, frag = cur.partition("#")
    if path in path_map:
        return path_map[path] + ("#" + frag if frag else "")
    return None


def _rename_cycle_from(start: str, id_map: dict[str, str], path_map: dict[str, str]) -> tuple[str, ...] | None:
    seen: dict[str, int] = {}
    order: list[str] = []
    cur: str | None = start
    while cur is not None:
        if cur in seen:
            cyc = order[seen[cur]:]
            i = cyc.index(min(cyc))
            return tuple(cyc[i:] + cyc[:i])
        seen[cur] = len(order)
        order.append(cur)
        cur = _rename_step(id_map, path_map, cur)
    return None


def _rename_maps(pairs: list[tuple[str, str]]) -> tuple[dict[str, str], dict[str, str]]:
    id_level = [(a, b) for a, b in sorted(pairs) if "#" in a or "#" in b]
    return dict(id_level), {a: b for a, b in sorted(pairs) if (a, b) not in id_level}


def _rename_cycles(pairs: list[tuple[str, str]]) -> list[list[str]]:
    """Cycles of the LIFTED rename system, each rotated to its smallest element, sorted (adapted from the source:
    the walk and the step are separate functions).

    Rules: an id-level record (an end has a fragment) rewrites one id; a path-level record (two file ids) rewrites the file part
    of any id. Strategy: id-level first, else path-level. Each record can be functional, injective and acyclic while the lifted
    system loops (a.py -> b.py with b.py#f -> a.py#f sends a.py#f to itself).
    """
    id_map, path_map = _rename_maps(pairs)
    found = {c for c in (_rename_cycle_from(s, id_map, path_map) for s in sorted({a for a, _ in pairs})) if c is not None}
    return [list(c) for c in sorted(found)]


def _cycle(edges: list[tuple[str, str]]) -> list[str]:
    """Lexicographically smallest start of a directed cycle, or []. Iterative DFS, sorted neighbours."""
    adj: dict[str, list[str]] = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
    for targets in adj.values():
        targets.sort()
    state: dict[str, int] = {}
    for root in sorted(adj):
        if state.get(root):
            continue
        stack = [(root, iter(adj[root]))]
        path = [root]
        state[root] = 1
        while stack:
            node, it = stack[-1]
            for nxt in it:
                if state.get(nxt) == 1:
                    return [*path[path.index(nxt):], nxt]
                if not state.get(nxt):
                    state[nxt] = 1
                    path.append(nxt)
                    stack.append((nxt, iter(adj.get(nxt, []))))
                    break
            else:
                state[node] = 2
                stack.pop()
                path.pop()
    return []


def _duplicate_nodes(nodes: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[Finding]]:
    found: list[Finding] = []
    by_id: dict[str, dict[str, Any]] = {}
    for n in nodes:
        if n["id"] in by_id:
            found.append(("duplicate-id", n["id"], "two node records share one id"))
        by_id[n["id"]] = n
    return by_id, found


def _signature_findings(subject: str, e: dict[str, Any], src: dict[str, Any], dst: dict[str, Any], rows: list[dict[str, Any]]) -> list[Finding]:
    match = [r for r in rows if src["type"] in r["_from"] and dst["type"] in r["_to"]]
    if not match:
        return [("ill-typed-edge", subject, f"no signature row for {src['type']} -{e['kind']}-> {dst['type']}")]
    qual = e.get("qualifier")
    found: list[Finding] = []
    if not any(_qualifier_ok(r, qual) for r in match):
        found.append(("ill-typed-edge", subject, f"qualifier {qual!r} is not allowed on this row"))
    found += [("ill-typed-edge", subject, "a rename must preserve the node type") for r in match if r.get("same_type") and src["type"] != dst["type"]]
    return found


def _endpoint_findings(mm: dict[str, Any], e: dict[str, Any], subject: str, by_id: dict[str, dict[str, Any]],
                       rows: list[dict[str, Any]]) -> list[Finding]:
    found: list[Finding] = []
    if e["from"] == e["to"]:
        found.append(("self-loop", subject, "no link kind allows a self-loop"))
    src, dst = by_id.get(e["from"]), by_id.get(e["to"])
    if src is None and not mm["link_types"][e["kind"]].get("from_may_dangle"):
        found.append(("dangling-link", subject, "source endpoint is not a node"))
    if dst is None:
        found.append(("dangling-link", subject, "target endpoint is not a node"))
    if src is not None and dst is not None:
        found += _signature_findings(subject, e, src, dst, rows)
    return found


def _degree_findings(kind: str, i: int, row: dict[str, Any], es: list[dict[str, Any]], by_id: dict[str, dict[str, Any]]) -> list[Finding]:
    outs: dict[str, int] = {}
    ins: dict[str, int] = {}
    for e in es:
        src, dst = by_id.get(e["from"]), by_id.get(e["to"])
        if src and dst and src["type"] in row["_from"] and dst["type"] in row["_to"]:
            outs[e["from"]] = outs.get(e["from"], 0) + 1
            ins[e["to"]] = ins.get(e["to"], 0) + 1
    found: list[Finding] = []
    for key, side, counts in (("max_out", "out", outs), ("max_in", "in", ins)):
        if key in row:
            found += [("cardinality-exceeded", f"{kind}#{i}:{n}", f"{side}-degree {c} > {row[key]}")
                      for n, c in sorted(counts.items()) if c > row[key]]
    return found


def _acyclic_findings(kind: str, es: list[dict[str, Any]]) -> list[Finding]:
    cyc = _cycle([(e["from"], e["to"]) for e in es if e["from"] != e["to"]])
    if cyc:
        return [("link-kind-cycle", kind, " -> ".join(cyc))]
    if kind == "renamed_to":  # the relation is acyclic; the lifted id-level plus path-level system may still loop
        return [("rename-cycle", c[0], " -> ".join([*c, c[0]])) for c in _rename_cycles([(e["from"], e["to"]) for e in es])]
    return []


def check_document(mm: dict[str, Any], nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[Finding]:
    """Same findings as the source's check_document (differential-tested), split into helpers."""
    by_id, found = _duplicate_nodes(nodes)
    seen_keys: set[tuple[str, str, str, str]] = set()
    per_kind: dict[str, list[dict[str, Any]]] = {}
    rows_of: dict[str, list[dict[str, Any]]] = {}  # signature rows expanded once per kind

    def rows(kind: str) -> list[dict[str, Any]]:
        if kind not in rows_of:
            rows_of[kind] = _rows(mm, kind)
        return rows_of[kind]

    for e in edges:
        key = (e["kind"], e["from"], e["to"], e.get("qualifier", ""))
        if key in seen_keys:
            found.append(("duplicate-edge", "|".join(key), "two edge records share one (kind, from, to, qualifier)"))
        seen_keys.add(key)
        found += _endpoint_findings(mm, e, "|".join(key), by_id, rows(e["kind"]))
        per_kind.setdefault(e["kind"], []).append(e)
    for kind, es in sorted(per_kind.items()):  # structural cardinality: per signature row, count edges per endpoint
        for i, row in enumerate(rows(kind)):
            found += _degree_findings(kind, i, row, es, by_id)
    for kind, spec in sorted(mm["link_types"].items()):
        if spec["acyclic"] and kind in per_kind:
            found += _acyclic_findings(kind, per_kind[kind])
    return sorted(set(found))
