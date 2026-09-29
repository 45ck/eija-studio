"""Canonical strongly connected components and topological order, with certificate checkers.

Facts used (each is elementary; proofs are in the design document):

* The partition of a digraph into strongly connected components (SCCs) is unique. So a checker that
  accepts any valid partition accepts THE partition, and canonical naming is a separate, pure step:
  label each component by its minimum member (nodes are strings, compared by Python str order, that
  is by code point; any fixed total order would do).
* The condensation (quotient by SCC) is acyclic, and a DAG has at least one topological order. The
  lexicographically smallest topological order over node names is unique: at each step choose the
  minimum node whose predecessors are all placed.

Certificate for "label is the canonical SCC labelling of (V, E)":

    (1) label is total on V and label[n] is a member of the class it names, and it is the minimum member
    (2) every class is strongly connected inside the class (forward and backward BFS from one member
        stay within the class and reach all of it)
    (3) the quotient graph has no cycle (Kahn on the quotient consumes every class)

(2) shows each class is contained in an SCC; (3) shows no two classes are mutually reachable, hence each
class is a whole SCC. Both directions are needed: (2) alone accepts singletons; (3) alone accepts one
class that is the whole node set.

The checker is not Tarjan: it has no lowlink and no stack.
"""
from __future__ import annotations

import heapq
from collections import defaultdict, deque
from typing import Iterable

Edge = tuple[str, str]


def _adj(nodes: Iterable[str], edges: Iterable[Edge]) -> dict[str, list[str]]:
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    for u, v in sorted(set(edges)):
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, [])
    return adj


def scc_labels(nodes: Iterable[str], edges: Iterable[Edge]) -> dict[str, str]:
    """Untrusted producer: iterative Tarjan over sorted adjacency; each node labelled by its class minimum."""
    adj = _adj(nodes, edges)
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    label: dict[str, str] = {}
    counter = 0
    for root in sorted(adj):
        if root in index:
            continue
        work = [(root, iter(adj[root]))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, it = work[-1]
            advanced = False
            for succ in it:
                if succ not in index:
                    index[succ] = low[succ] = counter
                    counter += 1
                    stack.append(succ)
                    on_stack.add(succ)
                    work.append((succ, iter(adj[succ])))
                    advanced = True
                    break
                if succ in on_stack:
                    low[node] = min(low[node], index[succ])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                members = []
                while True:
                    m = stack.pop()
                    on_stack.discard(m)
                    members.append(m)
                    if m == node:
                        break
                least = min(members)
                for m in members:
                    label[m] = least
    return label


def check_scc_labels(nodes: Iterable[str], edges: Iterable[Edge], label: dict[str, str]) -> tuple[bool, str]:
    node_s = set(nodes) | {x for e in edges for x in e}
    edge_l = sorted(set(edges))
    if set(label) != node_s:
        return False, "1:label-not-total"
    classes: dict[str, list[str]] = defaultdict(list)
    for n in sorted(node_s):
        classes[label[n]].append(n)
    for name, members in classes.items():
        if name != members[0]:  # members are sorted: members[0] is the minimum
            return False, "1:label-not-minimum-member"
    fwd, bwd = defaultdict(list), defaultdict(list)
    for u, v in edge_l:
        if label[u] == label[v]:
            fwd[u].append(v)
            bwd[v].append(u)
    for name, members in classes.items():
        for side in (fwd, bwd):
            seen, queue = {name}, deque([name])
            while queue:
                for w in side[queue.popleft()]:
                    if w not in seen:
                        seen.add(w)
                        queue.append(w)
            if seen != set(members):
                return False, "2:class-not-strongly-connected"
    indeg = {k: 0 for k in classes}
    out = defaultdict(set)
    for u, v in edge_l:
        if label[u] != label[v] and label[v] not in out[label[u]]:
            out[label[u]].add(label[v])
            indeg[label[v]] += 1
    ready = [k for k, d in indeg.items() if d == 0]
    done = 0
    while ready:
        k = ready.pop()
        done += 1
        for w in out[k]:
            indeg[w] -= 1
            if indeg[w] == 0:
                ready.append(w)
    return (done == len(classes)), ("accepted" if done == len(classes) else "3:quotient-has-cycle")


def lexicographic_topological_order(nodes: Iterable[str], edges: Iterable[Edge]) -> list[str] | None:
    """Untrusted producer: Kahn with a min-heap. Returns None when the graph has a cycle."""
    adj = _adj(nodes, edges)
    indeg = {n: 0 for n in adj}
    for u in adj:
        for v in adj[u]:
            indeg[v] += 1
    heap = [n for n, d in indeg.items() if d == 0]
    heapq.heapify(heap)
    order: list[str] = []
    while heap:
        n = heapq.heappop(heap)
        order.append(n)
        for v in adj[n]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    return order if len(order) == len(adj) else None


def check_lexicographic_topological_order(nodes: Iterable[str], edges: Iterable[Edge],
                                          order: list[str]) -> tuple[bool, str]:
    """Checker: order is a permutation, every edge goes forward, and at every position the chosen node
    is the minimum among the unplaced nodes whose predecessors are all placed. O(V * (V + E)), by design
    the naive reading of the definition."""
    node_s = set(nodes) | {x for e in edges for x in e}
    edge_s = set(edges)
    if len(order) != len(set(order)) or set(order) != node_s:
        return False, "not-a-permutation"
    pos = {n: i for i, n in enumerate(order)}
    if any(pos[u] >= pos[v] for u, v in edge_s):
        return False, "edge-goes-backward"
    preds = defaultdict(set)
    for u, v in edge_s:
        preds[v].add(u)
    for i, chosen in enumerate(order):
        placed = set(order[:i])
        available = [n for n in node_s - placed if preds[n] <= placed]
        if chosen != min(available):
            return False, "not-lexicographically-smallest"
    return True, "accepted"
