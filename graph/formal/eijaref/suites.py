"""Implementation-agnostic law suites. Each suite takes the function(s) under test and returns a list of
violations (empty means the suite found none on its stated finite domain).

The same suite runs against (1) the reference in this package, which must pass, (2) a deliberately wrong
implementation, which must fail (a suite that cannot fail proves nothing), and (3) the production function
named in ``graph/formal/binding.json`` when it exists (NOT_RUN when it does not).

Domains are small and exhaustive on purpose; the size is part of each suite's name in the report.
"""
from __future__ import annotations

import itertools
from typing import Callable, Iterable

from . import canon as ref_canon
from . import closure as ref_closure
from . import order as ref_order
from . import status as ref_status

Violations = list[str]


def _digraphs(n: int):
    nodes = [f"n{i}" for i in range(n)]
    slots = [(a, b) for a in nodes for b in nodes]
    for mask in range(1 << len(slots)):
        yield nodes, tuple(slots[i] for i in range(len(slots)) if mask >> i & 1)


def _subsets(items):
    for k in range(len(items) + 1):
        yield from itertools.combinations(items, k)


def _adj(nodes, edges):
    g = {x: [] for x in nodes}
    for a, b in edges:
        g[a].append(b)
    return g


# ---- closure: impl(graph: dict[str, list[str]], roots: list[str]) -> iterable of affected nodes ---------------
def suite_closure(impl: Callable, n: int = 3) -> Violations:
    bad: Violations = []
    for nodes, edges in _digraphs(n):
        g = _adj(nodes, edges)
        for roots in _subsets(nodes):
            want = sorted(ref_closure.lfp_kleene(g, roots))
            got = sorted(impl(g, list(roots)))
            if got != want:
                bad.append(f"closure mismatch: edges={edges} roots={roots} got={got} want={want}")
                if len(bad) >= 3:
                    return bad
    # monotone in roots and in edges (metamorphic; needs no reference)
    for nodes, edges in _digraphs(2):
        g = _adj(nodes, edges)
        small, big = sorted(impl(g, ["n0"])), sorted(impl(g, ["n0", "n1"]))
        if not set(small) <= set(big):
            bad.append("closure not monotone in roots")
    return bad


# ---- order: scc(nodes, edges) -> dict, topo(nodes, edges) -> list | None ---------------------------------
def suite_order(scc: Callable, topo: Callable, n: int = 3) -> Violations:
    bad: Violations = []
    for nodes, edges in _digraphs(n):
        lab = scc(nodes, edges)
        ok, why = ref_order.check_scc_labels(nodes, edges, dict(lab))
        if not ok:
            bad.append(f"scc labels rejected ({why}): edges={edges}")
        shuffled = list(reversed(edges))
        if scc(list(reversed(nodes)), shuffled) != lab:
            bad.append(f"scc labels depend on insertion order: edges={edges}")
        order = topo(nodes, edges)
        want = ref_order.lexicographic_topological_order(nodes, edges)
        if order != want:
            bad.append(f"topological order mismatch: edges={edges} got={order} want={want}")
        if len(bad) >= 3:
            break
    return bad


# ---- canonical serialisation: dumps(value) -> bytes ------------------------------------------------------
def _canon_pool():
    return [None, True, False, 0, 1, -1, 2 ** 53 - 1, "", "a", "\"", "\\", "\n", "\x00", "\x7f", "€", "דּ",
            "\U0001f600", "￿", " ", "1", [], [1, [2]], ["a", None], {}, {"a": 1}, {"b": 1, "a": 2},
            {"\U0001f600": 1, "￿": 2, "€": 3}, {"a": {"b": [True, {"c": "d"}]}}]


def suite_canon(dumps: Callable[[object], bytes]) -> Violations:
    bad: Violations = []
    for v in _canon_pool():
        if dumps(v) != ref_canon.dumps(v):
            bad.append(f"differs from reference for {v!r}")
    d = {"b": 1, "\U0001f600": [True], "€": None, "a": "x"}
    outs = {dumps(dict(p)) for p in itertools.permutations(d.items())}
    if len(outs) != 1:
        bad.append(f"dict order observable: {len(outs)} outputs")
    for name, value in [("float", 1.0), ("int_key", {1: "a"}), ("lone_surrogate", "\ud800"), ("big_int", 2 ** 53),
                        ("tuple", (1,))]:
        try:
            dumps(value)
            bad.append(f"accepted a value outside the domain: {name}")
        except Exception:  # noqa: BLE001 - any refusal is acceptable, silence is not
            pass
    return bad


# ---- status algebra: join(values), meet(values), claim(required_checks) ------------------------------------
KERNEL_FIVE = ("PASS", "FAIL", "STALE", "UNKNOWN", "CONFLICT")


def suite_status(join: Callable, meet: Callable, claim: Callable) -> Violations:
    """Representation-agnostic: the join is only exercised on the kernel's five values (an implementation may or may
    not accept NOT_RUN there, and may return UNKNOWN or NOT_RUN for an empty join); what is required of every
    implementation is (i) join laws, (ii) a gate is PASS iff every input is PASS, (iii) NOT_RUN absorbs PASS,
    (iv) an empty gate and a required check without evidence never pass."""
    bad: Violations = []
    for a, b in itertools.product(KERNEL_FIVE, repeat=2):
        if join([a, b]) != join([b, a]):
            bad.append(f"join not commutative on {a},{b}")
    for a in KERNEL_FIVE:
        if join([a, a]) != a:
            bad.append(f"join not idempotent on {a}")
    for a, b, c in itertools.product(KERNEL_FIVE, repeat=3):
        if join([join([a, b]), c]) != join([a, join([b, c])]):
            bad.append(f"join not associative on {a},{b},{c}")
    for k in range(1, 4):
        for p in itertools.combinations_with_replacement(ref_status.VALUES, k):
            got = meet(list(p))
            if (got == "PASS") != all(x == "PASS" for x in p):
                bad.append(f"meet is PASS unless all PASS: {p} -> {got}")
            if "NOT_RUN" in p and got == "PASS":
                bad.append(f"NOT_RUN did not absorb PASS: {p}")
    if meet([]) == "PASS":
        bad.append("empty gate passes (vacuous truth)")
    if claim([]) == "PASS":
        bad.append("a claim with no required checks passes")
    if claim([["PASS"], []]) == "PASS":
        bad.append("a required check with no evidence let the claim pass")
    if claim([["PASS", "STALE"], ["PASS"]]) != "PASS":
        bad.append("a current PASS with an older STALE observation of the same check should stay PASS (kernel behaviour)")
    if claim([["PASS", "FAIL"], ["PASS"]]) == "PASS":
        bad.append("PASS and FAIL for one check (CONFLICT) let the claim pass")
    return bad[:5]


# ---- link status: fn(baseline, observation, acks, link_id) -> status -----------------------------------------
LINK_OBSERVATIONS = ("UNRESOLVED", "ABSENT", "AMBIGUOUS", ("DIGEST", "b"), ("DIGEST", "x"))
ACK_POOL = (("L", "b"), ("L", "x"), ("L", "y"), ("M", "x"))  # acks are (link id, digest) pairs


def link_status_ref(baseline: str, observation, acks: frozenset, link_id: str) -> str:
    """Reference decision table (DESIGN; precedence among the three non-digest cases is ADR-0093's choice)."""
    if observation == "UNRESOLVED":
        return "UNRESOLVED"
    if observation == "ABSENT":
        return "ORPHANED"
    if observation == "AMBIGUOUS":
        return "AMBIGUOUS"
    digest = observation[1]
    if digest == baseline or (link_id, digest) in acks:
        return "COVERED"
    return "SUSPECT"


def suite_link_status(fn: Callable) -> Violations:
    bad: Violations = []
    ack_sets = [frozenset(s) for s in _subsets(ACK_POOL)]
    for obs in LINK_OBSERVATIONS:
        for acks in ack_sets:
            got = fn("b", obs, acks, "L")
            if got not in ref_status.LINK_STATUSES:
                bad.append(f"not a link status: {got!r}")
                continue
            # COVERED soundness
            if got == "COVERED":
                if not (isinstance(obs, tuple) and (obs[1] == "b" or ("L", obs[1]) in acks)):
                    bad.append(f"COVERED without a matching digest or ack: obs={obs} acks={sorted(acks)}")
            # an unresolved resolver is never covered
            if obs == "UNRESOLVED" and got == "COVERED":
                bad.append("UNRESOLVED observation reported COVERED")
            # acks can clear SUSPECT only
            if obs in ("ABSENT", "AMBIGUOUS", "UNRESOLVED") and got == "COVERED":
                bad.append(f"ack cleared {obs}")
            # monotone in the ledger and local in the digest
            for extra in ACK_POOL:
                got2 = fn("b", obs, acks | {extra}, "L")
                if got2 != got and not (got == "SUSPECT" and got2 == "COVERED" and extra == ("L", obs[1] if isinstance(obs, tuple) else "")):
                    bad.append(f"adding ack {extra} changed {got} to {got2} for obs={obs}")
            # determinism
            if fn("b", obs, acks, "L") != got:
                bad.append("not deterministic")
    # agent independence: a proposal-shaped extra argument does not exist in the signature; the metamorphic check is
    # that permuting the ack set representation does not change the result.
    for obs in LINK_OBSERVATIONS:
        for acks in ack_sets:
            if fn("b", obs, frozenset(sorted(acks, reverse=True)), "L") != fn("b", obs, acks, "L"):
                bad.append("depends on ack representation")
    return bad[:5]


# ---- deliberately wrong implementations (negative controls) ----------------------------------------------------
def wrong_closure_one_hop(graph, roots):
    return sorted(set(roots) | {v for r in roots for v in graph.get(r, ())})


def wrong_scc_nx_style(nodes, edges):
    """Insertion-order dependent numbering: label by first-seen order, as nx.condensation does."""
    lab, seen = {}, {}
    for n in list(nodes):
        seen.setdefault(n, str(len(seen)))
        lab[n] = seen[n]
    return lab


def wrong_dumps_python_json(value):
    import json
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def wrong_status_vacuous(values):
    return ref_status.vacuous_meet(values)


def wrong_link_status_any_ack(baseline, observation, acks, link_id):
    if observation in ("UNRESOLVED", "ABSENT", "AMBIGUOUS"):
        return link_status_ref(baseline, observation, acks, link_id)
    return "COVERED" if observation[1] == baseline or any(a[1] == observation[1] for a in acks) else "SUSPECT"


def wrong_link_status_unresolved_covered(baseline, observation, acks, link_id):
    return "COVERED" if observation == "UNRESOLVED" else link_status_ref(baseline, observation, acks, link_id)
