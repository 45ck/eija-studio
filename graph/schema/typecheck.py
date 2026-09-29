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

try:  # sibling import both as a script directory and as a package
    from build_schemas import expand
except ImportError:  # pragma: no cover
    from .build_schemas import expand

Finding = tuple[str, str, str]  # (code, subject, message)


def _rows(mm: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    out = []
    for r in mm["link_types"][kind]["signatures"]:
        out.append({**r, "_from": set(expand(mm, r["from"])), "_to": set(expand(mm, r["to"]))})
    return out


def _qualifier_ok(row: dict[str, Any], qual: str | None) -> bool:
    """A row without a qualifiers key accepts any qualifier the kind allows; an empty list means none."""
    if "qualifiers" not in row:
        return True
    return qual in row["qualifiers"] if row["qualifiers"] else qual is None


def _rename_cycles(pairs: list[tuple[str, str]]) -> list[list[str]]:
    """Cycles of the LIFTED rename system, each rotated to its smallest element, sorted.

    Rules: an id-level record (an end has a fragment) rewrites one id; a path-level record (two file ids) rewrites the file part
    of any id. Strategy: id-level first, else path-level. Each record can be functional, injective and acyclic while the lifted
    system loops (a.py -> b.py with b.py#f -> a.py#f sends a.py#f to itself). A cycle of the lifted system contains a step
    taken at a left side, so walking from every left side finds every cycle.
    """
    id_map = {a: b for a, b in sorted(pairs) if "#" in a or "#" in b}
    path_map = {a: b for a, b in sorted(pairs) if "#" not in a and "#" not in b}

    def step(cur: str) -> str | None:
        if cur in id_map:
            return id_map[cur]
        path, _, frag = cur.partition("#")
        if path in path_map:
            return path_map[path] + ("#" + frag if frag else "")
        return None

    found: set[tuple[str, ...]] = set()
    for start in sorted({a for a, _ in pairs}):
        seen: dict[str, int] = {}
        order: list[str] = []
        cur: str | None = start
        while cur is not None:
            if cur in seen:
                cyc = order[seen[cur]:]
                i = cyc.index(min(cyc))
                found.add(tuple(cyc[i:] + cyc[:i]))
                break
            seen[cur] = len(order)
            order.append(cur)
            cur = step(cur)
    return [list(c) for c in sorted(found)]


def _cycle(edges: list[tuple[str, str]]) -> list[str]:
    """Lexicographically smallest start of a directed cycle, or []. Iterative DFS, sorted neighbours."""
    adj: dict[str, list[str]] = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
    for k in adj:
        adj[k].sort()
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


def check_document(mm: dict[str, Any], nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[Finding]:
    found: list[Finding] = []
    by_id: dict[str, dict[str, Any]] = {}
    for n in nodes:
        if n["id"] in by_id:
            found.append(("duplicate-id", n["id"], "two node records share one id"))
        by_id[n["id"]] = n
    seen_keys: set[tuple[str, str, str, str]] = set()
    per_kind: dict[str, list[dict[str, Any]]] = {}
    rows_of: dict[str, list[dict[str, Any]]] = {}  # signature rows expanded once per kind

    def rows(kind: str) -> list[dict[str, Any]]:
        if kind not in rows_of:
            rows_of[kind] = _rows(mm, kind)
        return rows_of[kind]

    for e in edges:
        key = (e["kind"], e["from"], e["to"], e.get("qualifier", ""))
        subject = "|".join(key)
        if key in seen_keys:
            found.append(("duplicate-edge", subject, "two edge records share one (kind, from, to, qualifier)"))
        seen_keys.add(key)
        if e["from"] == e["to"]:
            found.append(("self-loop", subject, "no link kind allows a self-loop"))
        kind = mm["link_types"][e["kind"]]
        src, dst = by_id.get(e["from"]), by_id.get(e["to"])
        if src is None and not kind.get("from_may_dangle"):
            found.append(("dangling-link", subject, "source endpoint is not a node"))
        if dst is None:
            found.append(("dangling-link", subject, "target endpoint is not a node"))
        if src is not None and dst is not None:
            match = [r for r in rows(e["kind"]) if src["type"] in r["_from"] and dst["type"] in r["_to"]]
            if not match:
                found.append(("ill-typed-edge", subject, f"no signature row for {src['type']} -{e['kind']}-> {dst['type']}"))
            else:
                qual = e.get("qualifier")
                if not any(_qualifier_ok(r, qual) for r in match):
                    found.append(("ill-typed-edge", subject, f"qualifier {qual!r} is not allowed on this row"))
                for r in match:
                    if r.get("same_type") and src["type"] != dst["type"]:
                        found.append(("ill-typed-edge", subject, "a rename must preserve the node type"))
        per_kind.setdefault(e["kind"], []).append(e)
    # structural cardinality: per signature row, count edges per endpoint
    for kind, es in sorted(per_kind.items()):
        for i, r in enumerate(rows(kind)):
            outs: dict[str, int] = {}
            ins: dict[str, int] = {}
            for e in es:
                src, dst = by_id.get(e["from"]), by_id.get(e["to"])
                if src and dst and src["type"] in r["_from"] and dst["type"] in r["_to"]:
                    outs[e["from"]] = outs.get(e["from"], 0) + 1
                    ins[e["to"]] = ins.get(e["to"], 0) + 1
            if "max_out" in r:
                found += [("cardinality-exceeded", f"{kind}#{i}:{n}", f"out-degree {c} > {r['max_out']}")
                          for n, c in sorted(outs.items()) if c > r["max_out"]]
            if "max_in" in r:
                found += [("cardinality-exceeded", f"{kind}#{i}:{n}", f"in-degree {c} > {r['max_in']}")
                          for n, c in sorted(ins.items()) if c > r["max_in"]]
    for kind, spec in sorted(mm["link_types"].items()):
        if spec["acyclic"] and kind in per_kind:
            cyc = _cycle([(e["from"], e["to"]) for e in per_kind[kind] if e["from"] != e["to"]])
            if cyc:
                found.append(("link-kind-cycle", kind, " -> ".join(cyc)))
            elif kind == "renamed_to":  # the relation is acyclic; the lifted id-level plus path-level system may still loop
                for c in _rename_cycles([(e["from"], e["to"]) for e in per_kind[kind]]):
                    found.append(("rename-cycle", c[0], " -> ".join([*c, c[0]])))
    return sorted(set(found))
