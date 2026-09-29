"""Reference implementations behind docs/weave/design/impact-ranking-and-confidence.md.

Purpose: an executable, stdlib-only statement of the computations that `eijagraph` will implement, so
the worked examples in graph/schema/math-oracles.md can be checked by machine and the production code
can later be differential-tested against them. This file is a REFERENCE (oracle), not the product: it
favours clarity over speed. It never imports the kernel; tests import the kernel as a second oracle.

Determinism: integers, Fractions and sorted iteration only. No floats reach any returned value except
where a function says so (none do). No clock, no randomness, no set iteration into output.

Sections: 1 closure (least fixed point, tiers, witnesses, flow from the metamodel, changeset overlap)
2 SCC and condensation  3 personalised PageRank in integers  4 context selection (knapsack)  5 set cover
6 vertex-disjoint paths and the canonical minimum cut  7 status algebra (two operators)  8 counting
statistics  9 risk vector ordering.
"""
from __future__ import annotations

import heapq
import itertools
from collections import deque
from functools import cmp_to_key
from fractions import Fraction
from math import comb

Adj = dict[str, list[str]]

# ---------------------------------------------------------------------------------------------
# 1. Impact closure: least fixed point of X -> roots U succ(X), with witnesses, tiers and a budget
# ---------------------------------------------------------------------------------------------


def closure(graph: Adj, roots: list[str], budget: int | None = None) -> dict:
    """Same observable behaviour as eija_studio.domain.impact.closure, plus distance and parent.

    Edges mean "source affects target". BFS with sorted roots and sorted successors, so the parent
    path of every node is the lexicographically smallest shortest path from any root.
    """
    if budget is not None and budget < 0:
        raise ValueError("Negative traversal budget")
    queue = deque(sorted(set(roots)))
    seen = set(queue)
    dist = {r: 0 for r in queue}
    parent: dict[str, str | None] = {r: None for r in queue}
    visited: list[str] = []
    done: set[str] = set()
    while queue:
        if budget is not None and len(done) >= budget:
            break
        node = queue.popleft()
        done.add(node)
        visited.append(node)
        for nxt in sorted(set(graph.get(node, []))):
            if nxt not in seen:
                seen.add(nxt)
                dist[nxt] = dist[node] + 1
                parent[nxt] = node
                queue.append(nxt)
    frontier = sorted(seen - done)
    return {"affected": sorted(done), "complete": not frontier, "frontier": frontier,
            "order": visited, "distance": {k: dist[k] for k in sorted(done)},
            "parent": {k: parent[k] for k in sorted(done)}}


def witness(report: dict, node: str) -> list[str]:
    """Path root -> node through parent pointers."""
    path = [node]
    while report["parent"][path[-1]] is not None:
        path.append(report["parent"][path[-1]])
    return path[::-1]


def arcs_for_tier(links: list[tuple[str, str, str]], flow: dict[str, str], soundness: dict[str, int],
                  tier: int) -> Adj:
    """Impact digraph I_c from typed links (src, link_type, dst).

    flow[t] is a subset of "FR": F = a change at src affects dst, R = a change at dst affects src.
    soundness[t] is 0 (must), 1 (may) or 2 (heuristic). Only link types with soundness <= tier count.
    """
    adj: dict[str, set[str]] = {}
    for src, t, dst in links:
        if soundness[t] > tier:
            continue
        if "F" in flow[t]:
            adj.setdefault(src, set()).add(dst)
        if "R" in flow[t]:
            adj.setdefault(dst, set()).add(src)
    return {k: sorted(v) for k, v in sorted(adj.items())}


def tiered_impact(links: list[tuple[str, str, str]], flow: dict[str, str], soundness: dict[str, int],
                  roots: list[str]) -> dict[str, dict]:
    """For every affected node: tier (least class at which it is reached), distance and witness in that tier."""
    out: dict[str, dict] = {}
    for tier in (0, 1, 2):
        rep = closure(arcs_for_tier(links, flow, soundness, tier), roots)
        for node in rep["affected"]:
            if node not in out:
                out[node] = {"tier": tier, "distance": rep["distance"][node], "witness": witness(rep, node)}
    return {k: out[k] for k in sorted(out)}


def flow_covers_anchor(flow: str, anchor: str | None) -> bool:
    """Lint: a link type whose digest is anchored on `src` must let a change flow src -> dst (F); anchored on
    `dst`, dst -> src (R). Otherwise a suspect link's far end could lie outside the impact set."""
    return anchor is None or ("F" if anchor == "src" else "R") in flow


def suspect_far_ends(links: list[tuple[str, str, str]], anchor: dict[str, str | None], changed: set[str]) -> list[str]:
    """Nodes whose link goes SUSPECT because the anchored endpoint changed (one hop, early cutoff)."""
    out: set[str] = set()
    for src, t, dst in links:
        if anchor[t] == "src" and src in changed:
            out.add(dst)
        elif anchor[t] == "dst" and dst in changed:
            out.add(src)
    return sorted(out)


def changeset_overlap(links: list[tuple[str, str, str]], flow: dict[str, str], soundness: dict[str, int],
                      roots_a: list[str], roots_b: list[str]) -> dict:
    """Pre-merge conflict prediction between two change sets (two agents, two worktrees).

    direct: nodes both sets edit. a_reaches_b / b_reaches_a: nodes one side edits that the other side's
    change reaches, with the tier of that reach (0 = over sound arcs only). shared: nodes both changes
    reach, at tier max(tier_a, tier_b): the weakest class needed for both to touch them.
    """
    ia = tiered_impact(links, flow, soundness, roots_a)
    ib = tiered_impact(links, flow, soundness, roots_b)
    set_a, set_b = set(roots_a), set(roots_b)
    return {
        "direct": sorted(set_a & set_b),
        "a_reaches_b": {n: ia[n]["tier"] for n in sorted(set_b - set_a) if n in ia},
        "b_reaches_a": {n: ib[n]["tier"] for n in sorted(set_a - set_b) if n in ib},
        "shared": {n: max(ia[n]["tier"], ib[n]["tier"]) for n in sorted(set(ia) & set(ib))},
    }


# ---------------------------------------------------------------------------------------------
# 2. SCC condensation with minimum-member labels, lexicographic topological order, reach counts
# ---------------------------------------------------------------------------------------------


def scc_labels(nodes: list[str], adj: Adj) -> dict[str, str]:
    """Iterative Tarjan. Label of a component = its minimum member id. Independent of input order."""
    order = sorted(set(nodes) | {v for vs in adj.values() for v in vs})
    succ = {u: sorted(set(adj.get(u, []))) for u in order}
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    label: dict[str, str] = {}
    counter = 0
    for root in order:
        if root in index:
            continue
        work = [(root, 0)]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            u, i = work[-1]
            if i < len(succ[u]):
                work[-1] = (u, i + 1)
                v = succ[u][i]
                if v not in index:
                    index[v] = low[v] = counter
                    counter += 1
                    stack.append(v)
                    on_stack.add(v)
                    work.append((v, 0))
                elif v in on_stack:
                    low[u] = min(low[u], index[v])
            else:
                work.pop()
                if work:
                    p = work[-1][0]
                    low[p] = min(low[p], low[u])
                if low[u] == index[u]:
                    comp = []
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        comp.append(w)
                        if w == u:
                            break
                    m = min(comp)
                    for w in comp:
                        label[w] = m
    return {k: label[k] for k in order}


def condensation(nodes: list[str], adj: Adj) -> tuple[dict[str, str], dict[str, list[str]], Adj]:
    """(label per node, members per label, DAG adjacency over labels). Everything sorted."""
    label = scc_labels(nodes, adj)
    members: dict[str, list[str]] = {}
    for n, l in label.items():
        members.setdefault(l, []).append(n)
    dag: dict[str, set[str]] = {l: set() for l in members}
    for u, vs in adj.items():
        for v in vs:
            if label[u] != label[v]:
                dag[label[u]].add(label[v])
    return ({k: label[k] for k in sorted(label)}, {k: sorted(members[k]) for k in sorted(members)},
            {k: sorted(dag[k]) for k in sorted(dag)})


def lex_topological_order(dag: Adj) -> list[str]:
    """Lexicographically smallest topological order (Kahn with a min-heap). Raises on a cycle."""
    nodes = sorted(set(dag) | {v for vs in dag.values() for v in vs})
    indeg = {n: 0 for n in nodes}
    for u in dag:
        for v in set(dag[u]):
            indeg[v] += 1
    heap = [n for n in nodes if indeg[n] == 0]
    heapq.heapify(heap)
    out: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        out.append(n)
        for v in sorted(set(dag.get(n, []))):
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    if len(out) != len(nodes):
        raise ValueError("cycle in supposed DAG")
    return out


def reach_counts(nodes: list[str], adj: Adj) -> dict[str, int]:
    """|closure({v})| for every node, by bitset dynamic programming over the condensation."""
    label, members, dag = condensation(nodes, adj)
    ids = {n: i for i, n in enumerate(sorted(label))}
    mask: dict[str, int] = {}
    for comp in reversed(lex_topological_order(dag)):
        m = 0
        for n in members[comp]:
            m |= 1 << ids[n]
        for succ in dag[comp]:
            m |= mask[succ]
        mask[comp] = m
    return {n: mask[label[n]].bit_count() for n in sorted(label)}


def exposure_counts(nodes: list[str], adj: Adj) -> dict[str, int]:
    """Number of nodes whose closure contains v (fan-in in the reachability sense), v itself included."""
    rev: dict[str, set[str]] = {}
    for u, vs in adj.items():
        for v in vs:
            rev.setdefault(v, set()).add(u)
    return reach_counts(nodes, {k: sorted(v) for k, v in rev.items()})


# ---------------------------------------------------------------------------------------------
# 3. Personalised PageRank, fixed-point integers, bit-exact
# ---------------------------------------------------------------------------------------------


def choose_iterations(alpha: tuple[int, int], bits: int = 24) -> int:
    """Smallest K with 2 * (1 - alpha)^K <= 2^-bits, decided in exact integer arithmetic."""
    a, b = alpha
    k = 0
    while (1 << (bits + 1)) * (b - a) ** k > b**k:
        k += 1
    return k


def _spread(mass: int, targets: list[tuple[str, int]]) -> list[int]:
    """Split integer mass proportionally to integer weights; remainder units go to the first targets."""
    total = sum(w for _, w in targets)
    shares = [mass * w // total for _, w in targets]
    for i in range(mass - sum(shares)):
        shares[i] += 1
    return shares


def ppr_int(nodes: list[str], weights: dict[tuple[str, str], int], seeds: dict[str, int],
            alpha: tuple[int, int] = (1, 5), bits: int = 24, scale: int = 1 << 40,
            iterations: int | None = None) -> dict:
    """Personalised PageRank pi = alpha*s + (1-alpha)*pi*P as exact integer arithmetic.

    P(u, v) = w(u, v) / W_u; a node with W_u = 0 (dangling) returns to the seed distribution s.
    Total mass is exactly `scale` after every iteration. Returns integer scores in units of 1/scale
    and a proven L1 error bound (in the same units) against the exact fixed point.
    """
    a, b = alpha
    if not (0 < a < b):
        raise ValueError("alpha must be a fraction in (0, 1)")
    order = sorted(set(nodes) | {v for (_, v) in weights} | {u for (u, _) in weights} | set(seeds))
    out: dict[str, list[tuple[str, int]]] = {u: [] for u in order}
    for (u, v), w in sorted(weights.items()):
        if w > 0:
            out[u].append((v, w))
    seed_list = sorted((s, w) for s, w in seeds.items() if w > 0)
    if not seed_list:
        raise ValueError("at least one seed with positive weight")
    k = choose_iterations(alpha, bits) if iterations is None else iterations
    x = {u: 0 for u in order}
    for (s, _), sh in zip(seed_list, _spread(scale, seed_list)):
        x[s] += sh
    for _ in range(k):
        y = {u: 0 for u in order}
        tele = 0
        for u in order:
            if x[u] == 0:
                continue
            cont = x[u] * (b - a) // b
            tele += x[u] - cont
            if out[u]:
                for (v, _), sh in zip(out[u], _spread(cont, out[u])):
                    y[v] += sh
            else:
                tele += cont
        for (s, _), sh in zip(seed_list, _spread(tele, seed_list)):
            y[s] += sh
        x = y
    arcs = sum(len(v) for v in out.values())
    eps = arcs + 2 * len(order) + len(seed_list)
    contraction = Fraction(2 * scale * (b - a) ** k, b**k)
    err = -(-contraction.numerator // contraction.denominator) + -(-eps * b // a)
    ranking = sorted(order, key=lambda n: (-x[n], n))
    return {"scores": x, "ranking": ranking, "iterations": k, "scale": scale, "err_bound_units": err,
            "ppm": {n: (x[n] * 1_000_000 + scale // 2) // scale for n in order}}


def ppr_exact(nodes: list[str], weights: dict[tuple[str, str], int], seeds: dict[str, int],
              alpha: tuple[int, int] = (1, 5)) -> dict[str, Fraction]:
    """Exact rational solution of (I - (1-alpha) P^T) pi = alpha s by Gaussian elimination (test oracle only)."""
    a, b = alpha
    order = sorted(set(nodes) | {v for (_, v) in weights} | {u for (u, _) in weights} | set(seeds))
    n = len(order)
    idx = {u: i for i, u in enumerate(order)}
    total_seed = sum(w for w in seeds.values() if w > 0)
    s = [Fraction(0)] * n
    for k, w in seeds.items():
        if w > 0:
            s[idx[k]] = Fraction(w, total_seed)
    P = [[Fraction(0)] * n for _ in range(n)]
    for u in order:
        outs = [(v, w) for (uu, v), w in weights.items() if uu == u and w > 0]
        wu = sum(w for _, w in outs)
        if wu == 0:
            P[idx[u]] = list(s)
        else:
            for v, w in outs:
                P[idx[u]][idx[v]] += Fraction(w, wu)
    beta = Fraction(b - a, b)
    A = [[(Fraction(1) if i == j else Fraction(0)) - beta * P[j][i] for j in range(n)] for i in range(n)]
    rhs = [Fraction(a, b) * s[i] for i in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        rhs[col], rhs[piv] = rhs[piv], rhs[col]
        inv = 1 / A[col][col]
        A[col] = [v * inv for v in A[col]]
        rhs[col] *= inv
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
                rhs[r] -= f * rhs[col]
    return {u: rhs[idx[u]] for u in order}


# ---------------------------------------------------------------------------------------------
# 4. Context selection: pinned seeds, then density greedy with the best-single-item safeguard
# ---------------------------------------------------------------------------------------------


def select_context(pinned: dict[str, int], candidates: dict[str, tuple[int, int]], budget: int) -> dict:
    """pinned: id -> cost (always included). candidates: id -> (score, cost). Costs and scores are integers.

    Returns chosen ids, total cost, and EVERY candidate that was not chosen in `omitted`, each with a reason in
    `omitted_reasons` (nothing is dropped silently):

        NOT_SELECTED_BUDGET   fits the room but lost the density greedy or the best-single-item comparison
        TOO_LARGE_FOR_ROOM    cost is larger than the room left after the pinned nodes (the budget was the cause)
        NON_POSITIVE_SCORE    score <= 0 (nothing to gain)
        NON_POSITIVE_COST     cost <= 0 (density undefined; a rendered page has at least one byte)

    `omitted` lists the fitting candidates by density first, then the excluded ones by id.
    """
    used = sum(pinned.values())
    if used > budget:
        return {"status": "BUDGET_TOO_SMALL", "needed": used, "chosen": [], "omitted": [], "omitted_reasons": {}}
    room = budget - used
    reasons: dict[str, str] = {}
    pool = []
    for i in sorted(candidates):
        s, c = candidates[i]
        if c <= 0:
            reasons[i] = "NON_POSITIVE_COST"
        elif s <= 0:
            reasons[i] = "NON_POSITIVE_SCORE"
        elif c > room:
            reasons[i] = "TOO_LARGE_FOR_ROOM"
        else:
            pool.append((i, s, c))

    def denser(x: tuple[str, int, int], y: tuple[str, int, int]) -> int:
        """Negative when x should come first: higher score per unit cost (cross-multiplied), then smaller id."""
        left, right = x[1] * y[2], y[1] * x[2]
        if left != right:
            return -1 if left > right else 1
        return -1 if x[0] < y[0] else (1 if x[0] > y[0] else 0)

    pool.sort(key=cmp_to_key(denser))
    chosen, left = [], room
    for i, s, c in pool:
        if c <= left:
            chosen.append(i)
            left -= c
    best_single = min(pool, key=lambda t: (-t[1], t[0]), default=None)
    greedy_value = sum(candidates[i][0] for i in chosen)
    if best_single is not None and best_single[1] > greedy_value:
        chosen, left = [best_single[0]], room - best_single[2]
    chosen = sorted(chosen)
    fitting_omitted = [i for i, _, _ in pool if i not in chosen]
    for i in fitting_omitted:
        reasons[i] = "NOT_SELECTED_BUDGET"
    omitted = fitting_omitted + sorted(i for i in reasons if reasons[i] != "NOT_SELECTED_BUDGET")
    return {"status": "OK", "chosen": chosen, "cost": budget - left, "value": sum(candidates[i][0] for i in chosen),
            "omitted": omitted, "omitted_reasons": {i: reasons[i] for i in sorted(reasons)}}


# ---------------------------------------------------------------------------------------------
# 5. Weighted set cover
# ---------------------------------------------------------------------------------------------


def greedy_cover(universe: set[str], sets: dict[str, tuple[int, frozenset[str]]]) -> dict:
    """sets: id -> (cost, elements). Repeatedly take the set with least cost per newly covered element.

    Ties: more newly covered, then smaller id. Elements no set contains are reported, never dropped.
    """
    uncovered = set(universe)
    coverable = set().union(*(e for _, e in sets.values())) if sets else set()
    unreachable = sorted(uncovered - coverable)
    uncovered &= coverable
    chosen: list[str] = []
    cost = 0
    while uncovered:
        best = None
        for sid in sorted(sets):
            c, elems = sets[sid]
            new = len(elems & uncovered)
            if new == 0:
                continue
            key = (Fraction(c, new), -new, sid)
            if best is None or key < best[0]:
                best = (key, sid)
        chosen.append(best[1])
        cost += sets[best[1]][0]
        uncovered -= sets[best[1]][1]
    return {"chosen": chosen, "cost": cost, "unreachable": unreachable}


def optimal_cover_cost(universe: set[str], sets: dict[str, tuple[int, frozenset[str]]]) -> int | None:
    """Exact minimum cost by exhaustive search (test oracle for small instances)."""
    target = set(universe) & set().union(*(e for _, e in sets.values()))
    ids = sorted(sets)
    best = None
    for r in range(len(ids) + 1):
        for combo in itertools.combinations(ids, r):
            covered = set().union(*(sets[i][1] for i in combo)) if combo else set()
            if target <= covered:
                c = sum(sets[i][0] for i in combo)
                if best is None or c < best:
                    best = c
    return best


def harmonic(d: int) -> Fraction:
    return sum((Fraction(1, k) for k in range(1, d + 1)), Fraction(0))


# ---------------------------------------------------------------------------------------------
# 6. Evidence redundancy: vertex-disjoint paths and the canonical (source-side minimal) minimum cut
# ---------------------------------------------------------------------------------------------


def vertex_connectivity(adj: Adj, source: str, sink: str, cap: int | None = None) -> dict:
    """Max number of internally vertex-disjoint source->sink paths (= min vertex cut, Menger) and the
    canonical minimum vertex cut: internal vertices whose in-copy is reachable from the source in the
    residual graph of a maximum flow but whose out-copy is not. Source and sink are uncuttable.
    Requires source != sink and no direct arc source->sink (then the value is unbounded, reported as None).
    """
    if sink in adj.get(source, []):
        return {"k": None, "cut": None}
    nodes = sorted(set(adj) | {v for vs in adj.values() for v in vs} | {source, sink})
    big = len(nodes) + 1
    cap_edge: dict[tuple[str, str], int] = {}
    nbr: dict[str, set[str]] = {}

    def add(u: str, v: str, c: int) -> None:
        cap_edge[(u, v)] = cap_edge.get((u, v), 0) + c
        cap_edge.setdefault((v, u), 0)
        nbr.setdefault(u, set()).add(v)
        nbr.setdefault(v, set()).add(u)

    for n in nodes:
        add(n + "#in", n + "#out", big if n in (source, sink) else 1)
    for u in sorted(adj):
        for v in sorted(set(adj[u])):
            add(u + "#out", v + "#in", big)
    s, t = source + "#out", sink + "#in"
    flow = 0
    while cap is None or flow < cap:
        par = {s: None}
        q = deque([s])
        while q and t not in par:
            u = q.popleft()
            for v in sorted(nbr.get(u, ())):
                if v not in par and cap_edge[(u, v)] > 0:
                    par[v] = u
                    q.append(v)
        if t not in par:
            break
        v = t
        while par[v] is not None:
            u = par[v]
            cap_edge[(u, v)] -= 1
            cap_edge[(v, u)] += 1
            v = u
        flow += 1
    reach = {s}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in sorted(nbr.get(u, ())):
            if v not in reach and cap_edge[(u, v)] > 0:
                reach.add(v)
                q.append(v)
    cut = sorted(n for n in nodes if n not in (source, sink) and n + "#in" in reach and n + "#out" not in reach)
    return {"k": flow, "cut": cut if (cap is None or flow < cap) else None}


# ---------------------------------------------------------------------------------------------
# 7. Status algebra: two operators, never mixed
# ---------------------------------------------------------------------------------------------

EVIDENCE = ("UNKNOWN", "STALE", "PASS", "FAIL", "CONFLICT")  # carrier of the replication join (A)
INFO_LEQ = {(x, x) for x in EVIDENCE} | {("UNKNOWN", y) for y in EVIDENCE} | {("STALE", y) for y in ("PASS", "FAIL", "CONFLICT")} \
    | {("PASS", "CONFLICT"), ("FAIL", "CONFLICT")}
# Default verdict chain for conjunction across distinct checks (B), worst first. Owner decides the
# order among non-PASS values; PASS must stay the top element (SYNTHESIS open question 1).
CHAIN = ("FAIL", "CONFLICT", "STALE", "NOT_RUN", "UNKNOWN", "PASS")
LINK_TO_STATUS = {"COVERED": "PASS", "SUSPECT": "STALE", "ORPHANED": "FAIL", "AMBIGUOUS": "CONFLICT",
                  "UNRESOLVED": "NOT_RUN"}
LIFT = LINK_TO_STATUS  # the name the formal reference and the human views use


def join_a(x: str, y: str) -> str:
    """Least upper bound in UNKNOWN < STALE < {PASS, FAIL} < CONFLICT (repeat observations of ONE check)."""
    ub = [z for z in EVIDENCE if (x, z) in INFO_LEQ and (y, z) in INFO_LEQ]
    least = [z for z in ub if all((z, w) in INFO_LEQ for w in ub)]
    assert len(least) == 1
    return least[0]


def fold_a(statuses: list[str]) -> str:
    """Replication join. The empty fold is UNKNOWN, exactly like the kernel's aggregate_status([]).
    NOT_RUN is not a receipt status and is refused here: it belongs to B (a check that could not run)."""
    out = "UNKNOWN"
    for s in statuses:
        if s not in EVIDENCE:
            raise ValueError(f"{s!r} is not a receipt status; NOT_RUN and link statuses belong to fold_b")
        out = join_a(out, s)
    return out


def meet_b(x: str, y: str, chain: tuple[str, ...] = CHAIN) -> str:
    """Chain minimum (conjunction across DISTINCT checks). PASS is the top element."""
    return x if chain.index(x) <= chain.index(y) else y


def fold_b(required_slots: list[str], chain: tuple[str, ...] = CHAIN) -> str:
    """Conjunction over the REQUIRED slots of a claim. An empty list is NOT_RUN, never PASS: a gate that
    requires nothing has proved nothing (the empty meet would otherwise be the top element, PASS)."""
    if not required_slots:
        return "NOT_RUN"
    out = chain[-1]
    for s in required_slots:
        out = meet_b(out, s, chain)
    return out


def flow_from_metamodel(affects: str, anchor_ends: list[str]) -> str:
    """Impact flow of a link kind from the metamodel's own fields: `affects` (to_source: a change at the
    to-end reaches the from-end; to_target: the reverse; both; none) plus one arc away from every anchored end
    (a changed anchored end makes the link suspect, so the far end needs re-checking).
    Returns a subset of "FR" (F: from -> to, R: to -> from)."""
    flow = set()
    if affects not in ("to_source", "to_target", "both", "none"):
        raise ValueError(f"unknown metamodel affects value {affects!r}")
    if affects in ("to_target", "both") or "from" in anchor_ends:
        flow.add("F")
    if affects in ("to_source", "both") or "to" in anchor_ends:
        flow.add("R")
    return "".join(sorted(flow, key="FR".index))


DEFAULT_RANK_WEIGHT = (2, 1)  # (impact direction, reverse direction): the default recorded in the ADR
COVER_ROLES = ("none", "observer", "verifier")


def rank_weight_from_metamodel(spec: dict) -> tuple[int, int]:
    """(fwd, rev) relevance weights of a link kind, read from the metamodel's own `rank_weight` field.

    Two non-negative integers, not both zero. The metamodel is the single source of truth: the ranking never
    hard-codes a weight per kind name.
    """
    w = spec.get("rank_weight")
    if (not isinstance(w, (list, tuple)) or len(w) != 2 or not all(isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in w)
            or w[0] + w[1] == 0):
        raise ValueError(f"rank_weight must be two non-negative integers, not both zero: {w!r}")
    return (w[0], w[1])


def cover_role_from_metamodel(spec: dict) -> str:
    """`none`, `observer` (covers: measured) or `verifier` (verifies: declared), read from the metamodel."""
    role = spec.get("cover_role")
    if role not in COVER_ROLES:
        raise ValueError(f"unknown metamodel cover_role {role!r}")
    return role


def relevance_weights(links: list[tuple[str, str, str]], flow: dict[str, str],
                      rank_weights: dict[str, tuple[int, int]], damp: bool = False) -> dict[tuple[str, str], int]:
    """Relevance digraph H (design section 5.3). Each impact arc of a link gets the kind's `fwd`, the reversal of
    each impact arc gets `rev` unless that reversal is itself an impact arc of the same link (flow FR keeps `fwd`
    both ways). The weight of x -> y sums over all links joining x and y. `damp` multiplies the weight of every
    arc into y by 65536 // (1 + deg(y)), deg = number of distinct neighbours of y (integer division only)."""
    w: dict[tuple[str, str], int] = {}
    for u, kind, v in sorted(links):
        fwd, rev = rank_weights[kind]
        impact = set()
        if "F" in flow[kind]:
            impact.add((u, v))
        if "R" in flow[kind]:
            impact.add((v, u))
        for a, b in sorted(impact):
            w[(a, b)] = w.get((a, b), 0) + fwd
        for a, b in sorted(impact):
            if (b, a) not in impact and rev:
                w[(b, a)] = w.get((b, a), 0) + rev
    if damp:
        nbrs: dict[str, set[str]] = {}
        for a, b in w:
            nbrs.setdefault(a, set()).add(b)
            nbrs.setdefault(b, set()).add(a)
        w = {(a, b): x * (65536 // (1 + len(nbrs[b]))) for (a, b), x in sorted(w.items())}
    return dict(sorted(w.items()))


# ---------------------------------------------------------------------------------------------
# 8. Counting statistics (exact, no floats)
# ---------------------------------------------------------------------------------------------


def pass_hat_k(n: int, c: int, k: int) -> Fraction:
    """C(c,k)/C(n,k): probability that k distinct trials drawn from n recorded trials all passed."""
    if not (0 <= c <= n and 1 <= k <= n):
        raise ValueError("need 0 <= c <= n and 1 <= k <= n")
    return Fraction(comb(c, k), comb(n, k))


def miss_probability(mass: Fraction, n: int) -> Fraction:
    """P(no draw lands in a failure region of generator-mass `mass`) after n iid draws."""
    return (1 - mass) ** n


def frechet_lower(probs: list[Fraction]) -> Fraction:
    """Distribution-free lower bound on P(all events) = max(0, sum p - (n-1))."""
    return max(Fraction(0), sum(probs, Fraction(0)) - (len(probs) - 1))


def beta_posterior_mean(successes: int, failures: int, a: Fraction, b: Fraction) -> Fraction:
    """Posterior mean of a success probability under a Beta(a, b) prior."""
    return (successes + a) / (successes + failures + a + b)


# ---------------------------------------------------------------------------------------------
# 9. Change-risk vector: exact counts, dominance, canonical lexicographic order
# ---------------------------------------------------------------------------------------------

RISK_FIELDS = ("protected_paths_touched", "pinned_statements_changed", "impacted_obligations_without_observer",
               "suspect_links", "tier0_size", "tier1_size", "tier2_size", "changed_nodes")


def dominates(a: dict[str, int], b: dict[str, int]) -> bool:
    """a is at least as risky as b in every field, strictly in one (product order)."""
    return all(a[f] >= b[f] for f in RISK_FIELDS) and any(a[f] > b[f] for f in RISK_FIELDS)


def risk_key(v: dict[str, int]) -> tuple[int, ...]:
    """Lexicographic key over RISK_FIELDS; a linear extension of the product order, so it never ranks a
    dominated change above the change that dominates it. Larger key = review first."""
    return tuple(v[f] for f in RISK_FIELDS)
