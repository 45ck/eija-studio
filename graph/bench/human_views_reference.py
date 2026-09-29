"""Executable reference definitions for graph/schema/views.md (the human views).

This file is an ORACLE, not the product: it states, in a few lines each, the computations that the
eventual `eijagraph.views` must reproduce, so the definitions in views.md can be checked by machine and the
production code can later be differential-tested against them. Stdlib only. It never imports the kernel
and never reads the repository.

Determinism: integers and sorted iteration only. No floats, no clock, no randomness, no set iteration
reaches a returned value.

Sections: 0 definition digest  1 counts, badge and roll-up (laws C1 to C5)  2 tiers (maximin closure)  3 canonical witness and
segments  4 best-first neighbourhood and the integer grid  5 change classification (operations, null
edits, chapters, dependency order).
"""
from __future__ import annotations

import hashlib
import heapq
import json
from collections import deque
from typing import Callable, Iterable, Mapping, Sequence

STATUSES = ("PASS", "FAIL", "CONFLICT", "STALE", "UNKNOWN", "NOT_RUN")

# ------------------------------------------------------------------------------------------------
# 0. Definition digest
# ------------------------------------------------------------------------------------------------


def definition_digest(defn: Mapping) -> str:
    """SHA-256 over the canonical form of the views-definition block (views.md section 8).

    The block holds strings, integers, booleans, null, lists and objects and no float; with sorted keys, no
    insignificant whitespace and pure-ASCII strings this is the RFC 8785 form (its key order is by UTF-16
    code unit, its string escaping is minimal; both coincide with ASCII-only content). A non-ASCII string is
    refused instead of being silently escaped differently from RFC 8785.
    """
    text = json.dumps(defn, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if not text.isascii():
        raise ValueError("views-definition block must be ASCII so that its form equals RFC 8785")
    return hashlib.sha256(text.encode("ascii")).hexdigest()


# ------------------------------------------------------------------------------------------------
# 1. Counts vectors and priority-then-cap
# ------------------------------------------------------------------------------------------------


def counts_vector(statuses: Iterable[str]) -> tuple[int, ...]:
    """The counts vector of a multiset of statuses, in STATUSES order."""
    items = list(statuses)
    return tuple(sum(1 for s in items if s == v) for v in STATUSES)


def vec_add(a: Sequence[int], b: Sequence[int]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def fold_b(statuses: Iterable[str], chain_worst_first: Sequence[str]) -> str:
    """Badge operator for a container or any cross-claim roll-up: the chain minimum ("all of these").

    PASS iff every item is PASS, whatever the chain (PASS is the top). The empty collection is NOT_RUN, never
    PASS. This is conjunction B of ADR-0097 IR-8. The weave JOIN (least upper bound in the information order)
    is for repeated observations of ONE claim and must not be used here: join(PASS, NOT_RUN) is PASS.
    `chain_worst_first` is a total order of the six values with PASS last; it is data (views.md section 8,
    `chain_worst_first`), not a display choice.
    """
    pos = {s: i for i, s in enumerate(chain_worst_first)}
    items = list(statuses)
    return min(items, key=lambda s: pos[s]) if items else "NOT_RUN"


def badge_from_counts(vec: Sequence[int], chain_worst_first: Sequence[str]) -> str:
    """Badge from the support of a counts vector (law C4); an empty container is NOT_RUN."""
    return fold_b((s for s, n in zip(STATUSES, vec) if n), chain_worst_first)


def priority_then_cap(items: Sequence[tuple[str, str, int]], cap: int,
                      rank: Mapping[str, int]) -> tuple[list[str], dict]:
    """items are (id, status, distance). Sort by (rank[status], distance, id), keep the first `cap`.

    `rank` maps a status to its position, worst first. It is DATA, not display: it decides which rows are shown
    and which are hidden, so it must be `chain_worst_first` of the views-definition block, which is hashed into
    `definition_digest`. Display order may reorder the shown rows afterwards, never the cut. Returns (shown
    ids, overflow record). Law C5: shown + hidden = total.
    """
    ordered = sorted(items, key=lambda it: (rank[it[1]], it[2], it[0]))
    shown, hidden = ordered[:cap], ordered[cap:]
    by_status = {s: sum(1 for it in hidden if it[1] == s) for s in STATUSES if any(it[1] == s for it in hidden)}
    return [it[0] for it in shown], {"shown": len(shown), "hidden": len(hidden), "hidden_by_status": by_status}


# ------------------------------------------------------------------------------------------------
# 2. Tiers: the least soundness class at which a node is reached (a maximin path)
# ------------------------------------------------------------------------------------------------

Link = tuple[str, str, int]  # (src, dst, soundness) with 0 = must, 1 = may, 2 = heuristic; "src affects dst"


def _adj(links: Iterable[Link], tier: int) -> dict[str, list[str]]:
    adj: dict[str, set[str]] = {}
    for s, d, c in links:
        if c <= tier:
            adj.setdefault(s, set()).add(d)
    return {k: sorted(v) for k, v in sorted(adj.items())}


def bfs(adj: Mapping[str, Sequence[str]], roots: Iterable[str]) -> dict[str, tuple[int, str | None]]:
    """Distance and canonical parent of every reached node. Sorted roots, sorted successors."""
    dist: dict[str, tuple[int, str | None]] = {r: (0, None) for r in sorted(set(roots))}
    q = deque(sorted(set(roots)))
    while q:
        u = q.popleft()
        for v in sorted(adj.get(u, ())):
            if v not in dist:
                dist[v] = (dist[u][0] + 1, u)
                q.append(v)
    return dist


def tiered_reach(links: Sequence[Link], roots: Sequence[str]) -> dict[str, dict]:
    """For every node reached from the roots: tier (least class reaching it), distance and parent in that tier.

    Nested closures R_0 <= R_1 <= R_2, so the tier of a node is the least c with the node in R_c.
    """
    out: dict[str, dict] = {}
    for tier in (0, 1, 2):
        for node, (d, par) in bfs(_adj(links, tier), roots).items():
            if node not in out:
                out[node] = {"tier": tier, "distance": d, "parent": par}
    return {k: out[k] for k in sorted(out)}


def tier_bruteforce(links: Sequence[Link], roots: Sequence[str], target: str) -> int | None:
    """Oracle: min over simple paths from a root to target of the max soundness on the path."""
    adj: dict[str, list[tuple[str, int]]] = {}
    for s, d, c in links:
        adj.setdefault(s, []).append((d, c))
    best: int | None = None

    def dfs(node: str, seen: frozenset[str], worst: int) -> None:
        nonlocal best
        if best is not None and worst >= best:
            return
        if node == target:
            best = worst
            return
        for nxt, c in sorted(adj.get(node, [])):
            if nxt not in seen:
                dfs(nxt, seen | {nxt}, max(worst, c))

    for r in sorted(set(roots)):
        dfs(r, frozenset({r}), 0)
    return best


# ------------------------------------------------------------------------------------------------
# 3. Canonical witness and segments
# ------------------------------------------------------------------------------------------------


def canonical_witness(adj: Mapping[str, Sequence[str]], roots: Sequence[str], target: str) -> list[str] | None:
    """The lexicographically first shortest path from any root to target, or None when unreachable.

    Level order of BFS with sorted roots and sorted successors equals the lexicographic order of canonical
    paths, so the first predecessor found is the one with the smallest prefix.
    """
    reach = bfs(adj, roots)
    if target not in reach:
        return None
    path = [target]
    while reach[path[-1]][1] is not None:
        path.append(reach[path[-1]][1])  # type: ignore[arg-type]
    return path[::-1]


def path_bruteforce(adj: Mapping[str, Sequence[str]], roots: Sequence[str], target: str) -> list[str] | None:
    """Oracle: enumerate all simple paths, keep the shortest, then the lexicographically smallest."""
    found: list[list[str]] = []

    def dfs(path: list[str]) -> None:
        if path[-1] == target:
            found.append(list(path))
            return
        for nxt in sorted(adj.get(path[-1], ())):
            if nxt not in path:
                path.append(nxt)
                dfs(path)
                path.pop()

    for r in sorted(set(roots)):
        dfs([r])
    return min(found, key=lambda p: (len(p), p)) if found else None


def segments(hop_keys: Sequence[tuple]) -> list[tuple[tuple, int]]:
    """Run-length encode consecutive hops with an equal key (link kind, origin class, tier)."""
    out: list[list] = []
    for k in hop_keys:
        if out and out[-1][0] == k:
            out[-1][1] += 1
        else:
            out.append([k, 1])
    return [(k, n) for k, n in out]


# ------------------------------------------------------------------------------------------------
# 4. Best-first neighbourhood and the integer grid
# ------------------------------------------------------------------------------------------------


def select_neighbourhood(focus: str, und: Mapping[str, Sequence[str]], budget: int,
                         api: Mapping[str, int]) -> list[str]:
    """Best-first expansion by integer degree of interest DOI(x | f) = api(x) - D(f, x).

    D is the shortest-path length from the focus in the undirected graph (breadth-first distances computed up
    front, so it does not depend on which neighbour was expanded first). Connected by construction: a node is
    a candidate only after a neighbour was selected. Ties go to the smaller id.
    """
    dist = {n: d for n, (d, _) in bfs({k: sorted(v) for k, v in und.items()}, [focus]).items()}
    heap = [(-(api.get(focus, 1) - 0), focus)]
    pushed = {focus}
    chosen: list[str] = []
    while heap and len(chosen) < budget:
        _, x = heapq.heappop(heap)
        chosen.append(x)
        for y in sorted(und.get(x, ())):
            if y not in pushed:
                pushed.add(y)
                heapq.heappush(heap, (-(api.get(y, 1) - dist[y]), y))
    return sorted(chosen)


def grid_layout(focus: str, selected: Sequence[str], links: Sequence[tuple[str, str, str]]) -> dict[str, tuple[int, int]]:
    """(rank, slot) integers. links are (src, kind, dst). Rank is -distance for nodes first reached through an
    incoming link of the focus, +distance otherwise; slot orders nodes of equal rank by (connecting kind, id)."""
    sel = set(selected)
    out_n: dict[str, list[tuple[str, str]]] = {}
    in_n: dict[str, list[tuple[str, str]]] = {}
    for s, k, d in sorted(links):
        if s in sel and d in sel:
            out_n.setdefault(s, []).append((d, k))
            in_n.setdefault(d, []).append((s, k))
    dist = {focus: 0}
    side = {focus: "out"}
    via = {focus: ""}
    q = deque([focus])
    while q:
        u = q.popleft()
        for v, k in sorted(out_n.get(u, [])) + sorted(in_n.get(u, [])):
            if v not in dist:
                dist[v] = dist[u] + 1
                if u == focus:
                    side[v] = "out" if (v, k) in out_n.get(u, []) else "in"
                else:
                    side[v] = side[u]
                via[v] = k
                q.append(v)
    rank = {n: (-dist[n] if side[n] == "in" else dist[n]) for n in dist}
    slots: dict[int, list[str]] = {}
    for n in sorted(dist, key=lambda x: (rank[x], via[x], x)):
        slots.setdefault(rank[n], []).append(n)
    return {n: (r, i) for r, ns in slots.items() for i, n in enumerate(ns)}


# ------------------------------------------------------------------------------------------------
# 5. Change classification
# ------------------------------------------------------------------------------------------------

Digests = tuple[str, str, str]  # (file digest under lf-sha256-v1, node digest under its own method, method name)


def classify_changes(before: Mapping[str, Digests], after: Mapping[str, Digests],
                     renames: Mapping[str, str]) -> dict:
    """Operations and null edits between two roots. `renames` maps old id to new id (explicit records only).

    A null edit: the file digest differs, the node digest under its own method (not lf-sha256-v1) is equal.
    """
    ops: dict[str, str] = {}
    nulls: dict[str, list[str]] = {}
    renamed_new = set(renames.values())
    for i in sorted(set(before) | set(after)):
        if i in renames:
            ops[i] = "RENAMED"
            continue
        if i in renamed_new:
            continue  # the new side of an explicit rename is one operation, listed under the old id
        b, a = before.get(i), after.get(i)
        if b is None:
            ops[i] = "ADDED"
        elif a is None:
            ops[i] = "REMOVED"
        elif b[1] != a[1]:
            ops[i] = "MODIFIED"
        elif b[0] != a[0] and a[2] != "lf-sha256-v1":
            nulls.setdefault(a[2], []).append(i)
    return {"operations": ops, "null_edits": {m: sorted(v) for m, v in sorted(nulls.items())}}


def chapters(changed: Sequence[str], layer_of: Mapping[str, str], truth_of: Mapping[str, str],
             derived_from: Sequence[tuple[str, str]], core_layers: Sequence[str],
             consequence_truth: Sequence[str], consequence_layers_derived: Sequence[str]) -> dict[str, str]:
    """core, consequences or glue for every changed node (views.md, section 7.3).

    derived_from pairs are (derived, source). A node is a consequence when it is reachable from another changed
    node by derived_from links (source -> derived), or by its layer and truth class.
    """
    changed_set = set(changed)
    forward: dict[str, list[str]] = {}
    for derived, source in derived_from:
        forward.setdefault(source, []).append(derived)
    out: dict[str, str] = {}
    for x in sorted(changed_set):
        reached_from_other = any(x in bfs(forward, [y]) and y != x for y in sorted(changed_set))
        layer, truth = layer_of[x], truth_of[x]
        if reached_from_other or truth in consequence_truth or (truth == "derived" and layer in consequence_layers_derived):
            out[x] = "consequences"
        elif layer in core_layers:
            out[x] = "core"
        else:
            out[x] = "glue"
    return out


def scc_min_labels(nodes: Sequence[str], edges: Iterable[tuple[str, str]]) -> dict[str, str]:
    """Strongly connected components labelled by their minimum member (iterative Tarjan, sorted)."""
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    for a, b in sorted(set(edges)):
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, [])
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on: set[str] = set()
    label: dict[str, str] = {}
    counter = 0
    for root in sorted(adj):
        if root in index:
            continue
        work = [(root, 0)]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on.add(root)
        while work:
            u, i = work[-1]
            if i < len(adj[u]):
                work[-1] = (u, i + 1)
                v = adj[u][i]
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
                    m = min(comp)
                    for w in comp:
                        label[w] = m
    return label


def dependency_order(changed: Sequence[str], precedes: Iterable[tuple[str, str]],
                     key: Callable[[str], tuple] = lambda x: (x,)) -> list[str]:
    """Lexicographically smallest topological order of the changed nodes after collapsing SCCs.

    `precedes` pairs (a, b) mean a is listed before b. Members of one SCC are listed together, by key.
    Nodes not in `changed` are ignored.
    """
    nodes = sorted(set(changed))
    ns = set(nodes)
    edges = [(a, b) for a, b in precedes if a in ns and b in ns and a != b]
    label = scc_min_labels(nodes, edges)
    members: dict[str, list[str]] = {}
    for n in nodes:
        members.setdefault(label[n], []).append(n)
    dag: dict[str, set[str]] = {m: set() for m in members}
    indeg = {m: 0 for m in members}
    for a, b in edges:
        la, lb = label[a], label[b]
        if la != lb and lb not in dag[la]:
            dag[la].add(lb)
            indeg[lb] += 1
    ready = [(min(key(x) for x in members[m]), m) for m in members if indeg[m] == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        _, m = heapq.heappop(ready)
        order.extend(sorted(members[m], key=key))
        for n in sorted(dag[m]):
            indeg[n] -= 1
            if indeg[n] == 0:
                heapq.heappush(ready, (min(key(x) for x in members[n]), n))
    if len(order) != len(nodes):
        raise AssertionError("condensation must be acyclic")
    return order
