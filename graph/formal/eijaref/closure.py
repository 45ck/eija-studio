"""Reachability closure: reference semantics and a certificate checker.

Definitions (finite or infinite digraph G = (V, E), roots R subset of V):

    F_R(X) = R  union  { v : (u, v) in E, u in X }        (monotone, and it distributes over unions)
    lfp(F_R) = union over k >= 0 of F_R^k(empty set)       (the impact closure)

Certificate for "C is the closure of R in G" (positive and negative parts in one object):

    C      a set of nodes
    rank   a map C -> natural numbers
    parent a map (C minus R) -> C

Checker accepts iff all of
    (a) R is a subset of C
    (b) for every c in C minus R: (parent[c], c) is in E, parent[c] is in C, rank[parent[c]] < rank[c]
    (c) for every (u, v) in E: u in C implies v in C                      (C is forward-closed)

Theorem (certificate soundness). If the checker accepts then C = lfp(F_R).
Proof. (C is a subset of lfp) by induction on rank: a node of C in R lies in F_R(empty); any other c
has parent p in C with smaller rank, so p is in lfp by the induction hypothesis, hence c in F_R(lfp) =
lfp. (lfp is a subset of C) by induction on k, F_R^k(empty) is a subset of C: k = 0 is trivial and
F_R^(k+1)(empty) = R union E[F_R^k(empty)] is a subset of R union E[C], which is a subset of C by
(a) and (c). No finiteness assumption is used: F_R distributes over unions, so the Kleene union is
the least fixed point. QED.

Corollary (negative witness). If (a) and (c) hold for some C and a node t is not in C, then t is not
in the closure. C is an inductive invariant: it is the same object a model checker would return.

Completeness: for every finite G and R, BFS produces a certificate the checker accepts.

The checker below is deliberately not the algorithm it checks: it has no queue and no iteration.
"""
from __future__ import annotations

from collections import deque
from typing import Iterable, Mapping

Graph = Mapping[str, Iterable[str]]  # the kernel's shape: node -> successors ("source affects target")


def edge_set(graph: Graph) -> frozenset[tuple[str, str]]:
    return frozenset((u, v) for u, vs in graph.items() for v in vs)


def lfp_kleene(graph: Graph, roots: Iterable[str]) -> frozenset[str]:
    """Naive Kleene iteration of F_R from the empty set. Quadratic, obviously correct, the reference."""
    edges, root_set = edge_set(graph), frozenset(roots)
    x: frozenset[str] = frozenset()
    while True:
        nxt = root_set | frozenset(v for (u, v) in edges if u in x)
        if nxt == x:
            return x
        x = nxt


def warshall_closure(graph: Graph, roots: Iterable[str]) -> frozenset[str]:
    """Second independent reference: Warshall's transitive closure over an index set, then roots + reach."""
    root_set = frozenset(roots)
    nodes = sorted(set(graph) | {v for vs in graph.values() for v in vs} | root_set)
    idx = {n: i for i, n in enumerate(nodes)}
    reach = [[False] * len(nodes) for _ in nodes]
    for u, vs in graph.items():
        for v in vs:
            reach[idx[u]][idx[v]] = True
    for k in range(len(nodes)):
        for i in range(len(nodes)):
            if reach[i][k]:
                for j in range(len(nodes)):
                    if reach[k][j]:
                        reach[i][j] = True
    out = set(root_set)
    for r in root_set:
        out.update(nodes[j] for j in range(len(nodes)) if reach[idx[r]][j])
    return frozenset(out)


def certify(graph: Graph, roots: Iterable[str]) -> dict:
    """Untrusted producer: BFS with parent pointers. Rank is the BFS depth (roots have rank 0)."""
    root_set = sorted(set(roots))
    rank = {r: 0 for r in root_set}
    parent: dict[str, str] = {}
    queue = deque(root_set)
    while queue:
        u = queue.popleft()
        for v in sorted(graph.get(u, ())):
            if v not in rank:
                rank[v] = rank[u] + 1
                parent[v] = u
                queue.append(v)
    return {"C": frozenset(rank), "rank": rank, "parent": parent}


def check_certificate(edges: Iterable[tuple[str, str]], roots: Iterable[str], cert: dict) -> tuple[bool, str]:
    """The trusted checker. Returns (accepted, first violated condition id). About 15 lines of logic."""
    edge_s, root_s = frozenset(edges), frozenset(roots)
    c, rank, parent = cert["C"], cert["rank"], cert["parent"]
    if not root_s <= c:
        return False, "a:roots-not-in-C"
    for n in sorted(c - root_s):
        p = parent.get(n)
        if p is None or (p, n) not in edge_s:
            return False, "b1:parent-edge-missing"
        if p not in c:
            return False, "b2:parent-not-in-C"
        if not (p in rank and n in rank and rank[p] < rank[n]):
            return False, "b3:rank-not-decreasing"
    for u, v in sorted(edge_s):
        if u in c and v not in c:
            return False, "c:not-forward-closed"
    return True, "accepted"


def check_unreachable(edges: Iterable[tuple[str, str]], roots: Iterable[str], closed_set: Iterable[str],
                      target: str) -> tuple[bool, str]:
    """Negative witness: closed_set contains the roots, is forward-closed, and omits target."""
    edge_s, root_s, c = frozenset(edges), frozenset(roots), frozenset(closed_set)
    if not root_s <= c:
        return False, "a:roots-not-in-C"
    if any(u in c and v not in c for u, v in edge_s):
        return False, "c:not-forward-closed"
    return (target not in c), ("accepted" if target not in c else "target-in-C")


# Mutants of the checker: each drops exactly one condition. They exist so that the test-suite can show
# the suite would notice a checker that forgot a condition (a negative control on the checker itself).
def _mutant(drop: str):
    def check(edges, roots, cert):
        edge_s, root_s = frozenset(edges), frozenset(roots)
        c, rank, parent = cert["C"], cert["rank"], cert["parent"]
        if drop != "a" and not root_s <= c:
            return False, "a"
        for n in sorted(c - root_s):
            p = parent.get(n)
            if drop != "b1" and (p is None or (p, n) not in edge_s):
                return False, "b1"
            if drop != "b2" and p not in c:
                return False, "b2"
            if drop != "b3" and not (p in rank and n in rank and rank[p] < rank[n]):
                return False, "b3"
        if drop != "c":
            for u, v in sorted(edge_s):
                if u in c and v not in c:
                    return False, "c"
        return True, "accepted"
    return check


MUTANTS = {name: _mutant(name) for name in ("a", "b1", "b2", "b3", "c")}
