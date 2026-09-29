"""Reproducible measurements behind docs/weave/design/formal-verification-of-weave.md.

Every check reports MEASURED with its domain (what was enumerated or sampled, with sizes), or NOT_RUN with a
reason when an optional prerequisite is missing. Nothing here is a proof for all inputs: each check is an
exhaustive enumeration of a stated small domain or a seeded sample, and says which. The theorems themselves
are proven on paper in the design document; these runs test the statements and the implementations.

Uses only ``graph/formal/eijaref`` (independent, stdlib only) plus, as third opinions, the kernel
(``eija_studio.domain``) and, when installed, ``rfc8785`` and ``networkx``.

    python graph/bench/formal_checks.py                 # all checks, canonical ASCII JSON on stdout
    python graph/bench/formal_checks.py --only F1,F5    # a subset
    python graph/bench/formal_checks.py --timing        # adds wall-clock seconds (not deterministic)

Output is sorted-key ASCII JSON without timestamps: two runs on one platform are byte-identical.
"""
from __future__ import annotations

import ast
import inspect
import itertools
import json
import os
import random
import sqlite3
import subprocess
import sys
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "graph" / "formal"))
sys.path.insert(0, str(ROOT / "src"))

from eijaref import asp, canon, catalogue, closure, lens, metamodel, order, rules, status  # noqa: E402

try:
    from eija_studio.domain import evidence as kernel_evidence
    from eija_studio.domain.impact import closure as kernel_closure
    from eija_studio.domain.models import canonical as kernel_canonical
    from eija_studio.domain.models import fingerprint as kernel_fingerprint
except ImportError:  # the kernel is a third opinion, never required
    kernel_closure = kernel_canonical = kernel_fingerprint = kernel_evidence = None
try:
    import rfc8785
except ImportError:
    rfc8785 = None
try:
    import networkx as nx
except ImportError:
    nx = None


def not_run(reason: str) -> dict:
    return {"status": "NOT_RUN", "reason": reason}


def _digraphs(n: int):
    """All 2**(n*n) digraphs (self-loops allowed) on nodes n0..n{n-1}, as (nodes, edge tuple)."""
    nodes = [f"n{i}" for i in range(n)]
    slots = [(a, b) for a in nodes for b in nodes]
    for mask in range(1 << len(slots)):
        yield nodes, tuple(slots[i] for i in range(len(slots)) if mask >> i & 1)


def _adj(nodes, edges):
    g = {x: [] for x in nodes}
    for a, b in edges:
        g[a].append(b)
    return g


def _subsets(items):
    for k in range(len(items) + 1):
        yield from itertools.combinations(items, k)


# ---- F1: impact closure against independent references and the certificate checker ------------------

def f1_closure(n_big: int = 4, n_sql: int = 3) -> dict:
    cases = mism_kernel = mism_warshall = cert_rejected = neg_rejected = 0
    for nodes, edges in _digraphs(n_big):
        g = _adj(nodes, edges)
        edge_s = frozenset(edges)
        for roots in _subsets(nodes):
            cases += 1
            ref = closure.lfp_kleene(g, roots)
            if kernel_closure is not None and kernel_closure(g, list(roots))["affected"] != sorted(ref):
                mism_kernel += 1
            if n_big <= 4 and closure.warshall_closure(g, roots) != ref:
                mism_warshall += 1
            cert = closure.certify(g, roots)
            ok, _ = closure.check_certificate(edge_s, roots, cert)
            cert_rejected += not (ok and cert["C"] == ref)
            for t in nodes:
                if t not in ref and not closure.check_unreachable(edge_s, roots, ref, t)[0]:
                    neg_rejected += 1
    sql_cases = sql_mism = 0
    for nodes, edges in _digraphs(n_sql):
        db = sqlite3.connect(":memory:")
        db.execute("create table e(a, b)")
        db.executemany("insert into e values (?, ?)", sorted(edges))
        for roots in _subsets(nodes):
            db.execute("drop table if exists r")
            db.execute("create table r(x)")
            db.executemany("insert into r values (?)", [(x,) for x in roots])
            got = [x for (x,) in db.execute(
                "with recursive reach(x) as (select x from r union select e.b from e join reach on e.a = reach.x) "
                "select x from reach order by x")]
            sql_cases += 1
            sql_mism += got != sorted(closure.lfp_kleene(_adj(nodes, edges), roots))
        db.close()
    return {"status": "MEASURED",
            "domain": f"all 2^{n_big * n_big} digraphs with self-loops on {n_big} nodes x all {2 ** n_big} root sets",
            "cases": cases, "kernel_present": kernel_closure is not None,
            "kernel_vs_kleene_mismatches": mism_kernel, "warshall_vs_kleene_mismatches": mism_warshall,
            "bfs_certificate_rejected_or_wrong": cert_rejected, "negative_witness_rejected": neg_rejected,
            "sqlite_cte": {"domain": f"all digraphs on {n_sql} nodes x all root sets", "cases": sql_cases,
                           "mismatches": sql_mism}}


def f1b_budget_semantics(n: int = 3) -> dict:
    """The kernel's budgeted closure: affected is inside the true closure, complete implies equality."""
    if kernel_closure is None:
        return not_run("kernel not importable")
    cases = bad_subset = bad_complete = bad_frontier = 0
    for nodes, edges in _digraphs(n):
        g = _adj(nodes, edges)
        for roots in _subsets(nodes):
            full = set(closure.lfp_kleene(g, roots))
            for budget in range(n + 2):
                r = kernel_closure(g, list(roots), budget)
                cases += 1
                bad_subset += not set(r["affected"]) <= full
                bad_complete += r["complete"] and set(r["affected"]) != full
                bad_frontier += not set(r["frontier"]) <= full
    return {"status": "MEASURED", "domain": f"all digraphs on {n} nodes x all root sets x budgets 0..{n + 1}",
            "cases": cases, "affected_not_subset_of_closure": bad_subset,
            "complete_but_not_equal_to_closure": bad_complete, "frontier_not_in_closure": bad_frontier}


def _certificate_candidates(nodes, roots, ranks):
    for c in _subsets(nodes):
        rest = [x for x in c if x not in roots]
        parents = [[*list(nodes), None]] * len(rest)
        for pv in itertools.product(*parents):
            for rv in itertools.product(ranks, repeat=len(nodes)):  # rank is total on V: only b2 keeps it off non-members
                yield frozenset(c), dict(zip(nodes, rv, strict=False)), {r: p for r, p in zip(rest, pv, strict=False) if p is not None}


def f1c_checker_soundness_and_mutants(n_exh: int = 2, n_mut: int = 3, seed: int = 11, samples: int = 60000) -> dict:
    """Real checker: accept implies C == lfp (exhaustive at n_exh, seeded sample at larger n). Mutants (each
    drops one condition): a counterexample must exist. The unrestricted candidate space is searched for mutants."""
    exh = accepted = wrong = 0
    for nodes, edges in _digraphs(n_exh):
        g, edge_s = _adj(nodes, edges), frozenset(edges)
        for roots in _subsets(nodes):
            ref = closure.lfp_kleene(g, roots)
            for c, rank, parent in _certificate_candidates(nodes, set(roots), range(n_exh + 1)):
                exh += 1
                if closure.check_certificate(edge_s, roots, {"C": c, "rank": rank, "parent": parent})[0]:
                    accepted += 1
                    wrong += c != ref
    rng = random.Random(seed)
    sampled = s_acc = s_wrong = 0
    for _ in range(samples):
        n = rng.randrange(3, 7)
        nodes = [f"n{i}" for i in range(n)]
        edges = tuple((a, b) for a in nodes for b in nodes if rng.random() < 0.25)
        g, edge_s = _adj(nodes, edges), frozenset(edges)
        roots = tuple(x for x in nodes if rng.random() < 0.3)
        good = closure.certify(g, roots)
        cert = {"C": set(good["C"]), "rank": dict(good["rank"]), "parent": dict(good["parent"])}
        kind = rng.randrange(5)  # perturb one thing in a correct certificate
        victim = rng.choice(nodes)
        if kind == 0:
            cert["C"] ^= {victim}
        elif kind == 1 and cert["parent"]:
            cert["parent"][rng.choice(sorted(cert["parent"]))] = victim
        elif kind == 2 and cert["rank"]:
            cert["rank"][rng.choice(sorted(cert["rank"]))] = rng.randrange(0, 4)
        elif kind == 3:
            cert["C"] |= {victim}
            cert["rank"].setdefault(victim, rng.randrange(0, 4))
            cert["parent"].setdefault(victim, rng.choice(nodes))
        cert["C"] = frozenset(cert["C"])
        sampled += 1
        if closure.check_certificate(edge_s, roots, cert)[0]:
            s_acc += 1
            s_wrong += cert["C"] != closure.lfp_kleene(g, roots)
    found: dict[str, bool] = {}
    for name, mutant in sorted(closure.MUTANTS.items()):
        hit = False
        for nodes, edges in _digraphs(n_mut):
            g, edge_s = _adj(nodes, edges), frozenset(edges)
            for roots in _subsets(nodes):
                ref = closure.lfp_kleene(g, roots)
                for c, rank, parent in _certificate_candidates(nodes, set(roots), range(n_mut)):
                    if c != ref and mutant(edge_s, roots, {"C": c, "rank": rank, "parent": parent})[0]:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                break
        found[name] = hit
    return {"status": "MEASURED",
            "real_checker_exhaustive": {"domain": f"all digraphs on {n_exh} nodes x roots x every (C, parent, rank in 0..{n_exh})",
                                        "candidates": exh, "accepted": accepted, "accepted_but_not_closure": wrong},
            "real_checker_perturbed_sample": {"domain": f"seeded ({seed}) one-field perturbations of correct certificates, 3..6 nodes",
                                              "candidates": sampled, "accepted": s_acc, "accepted_but_not_closure": s_wrong},
            "mutants_with_counterexample": found,
            "mutant_domain": f"first counterexample searched over all digraphs on {n_mut} nodes"}


# ---- F2: status algebras -------------------------------------------------------------------------------

def _kernel_aggregate(statuses):
    from unittest import mock
    with mock.patch.object(kernel_evidence, "assess_receipt", lambda r, s, c, k: r["st"]):
        return kernel_evidence.aggregate_status([{"st": x} for x in statuses], {}, lambda r: True)


def f2_status() -> dict:
    laws = status.check_laws()
    kernel_vals = ("PASS", "FAIL", "STALE", "UNKNOWN")
    seqs = [p for k in range(7) for p in itertools.product(kernel_vals, repeat=k)]
    agree = None
    if kernel_evidence is not None:
        agree = all(status.join(p) == _kernel_aggregate(p) for p in seqs if p)
    chains = status.all_chains()
    # Gate invariance: for every chain, meet is PASS iff all inputs are PASS (multisets up to size 4).
    inv_bad = 0
    pools = [p for k in range(1, 5) for p in itertools.combinations_with_replacement(status.VALUES, k)]
    for chain in chains:
        for p in pools:
            inv_bad += (status.meet(p, chain) == "PASS") != all(x == "PASS" for x in p)
    # Two-level claim status: PASS iff every required check has a PASS and no other observation that is
    # FAIL/CONFLICT-producing (join is PASS), over up to 3 required checks with evidence as SUBSETS of values.
    subsets = list(_subsets(status.VALUES))
    two_level_bad = 0
    two_level_cases = 0
    for k in range(1, 4):
        for checks in itertools.product(subsets, repeat=k):
            two_level_cases += 1
            got = status.claim_status(checks)
            expect_pass = all(status.join(ev) == "PASS" for ev in checks)
            two_level_bad += (got == "PASS") != expect_pass
    # Where the wrong-but-natural implementations fail (negative controls for the law suite).
    vacuous_passes_empty = status.vacuous_meet([]) == "PASS"
    leaky_gate = status.leaky_meet(["PASS", "NOT_RUN"])
    # Alternative evidence joined with a required check: NOT_RUN in the join layer is the classic mistake.
    masked = status.join(["PASS", "NOT_RUN"])
    lift_only_covered_is_pass = [s for s, v in sorted(status.LIFT.items()) if v == "PASS"]
    # The join is the kernel's aggregate on flat inputs, but re-aggregation of the kernel's output differs.
    return {"status": "MEASURED",
            "domain": "6 values: all pairs and 216 triples; flat kernel sequences of length 0..6 over 4 values; "
                      "120 chains x multisets of size 1..4; 64^k evidence-subset combinations for k = 1..3 checks",
            "join_laws": laws, "kernel_present": kernel_evidence is not None,
            "join_equals_kernel_aggregate_on_flat_inputs": agree, "flat_sequences_checked": len(seqs) - 1,
            "chains": len(chains), "gate_is_pass_iff_all_pass_violations_over_all_chains": inv_bad,
            "two_level_cases": two_level_cases, "two_level_pass_iff_every_check_joins_to_pass_violations": two_level_bad,
            "empty_meet_is_not_run": status.meet([]) == "NOT_RUN", "empty_join_is_not_run": status.join([]) == "NOT_RUN",
            "empty_claim_is_not_run": status.claim_status([]) == "NOT_RUN",
            "negative_control_vacuous_meet_passes_empty_gate": vacuous_passes_empty,
            "negative_control_leaky_meet_of_PASS_and_NOT_RUN": leaky_gate,
            "join_of_PASS_and_NOT_RUN_is_PASS_so_required_checks_must_use_meet": masked,
            "link_statuses_lifting_to_PASS": lift_only_covered_is_pass}


# ---- F3: canonical serialisation ---------------------------------------------------------------------

def _value_pool():
    scalars = [None, True, False, 0, 1, -1, 2 ** 53 - 1, -(2 ** 53 - 1), "", "a", "b", "\"", "\\", "\n", "\x00", "\x1f",
               "\x7f", "€", "דּ", "\U0001f600", "￿", " ", "1", "true", "null"]
    keys = ["", "a", "b", "1", "€", "\U0001f600", "דּ", "￿", "A"]
    pool = list(scalars)
    lists = [[]] + [[x] for x in scalars] + [[x, y] for x in scalars[:8] for y in scalars[:8]]
    dicts = [{}] + [{k: v} for k in keys for v in scalars[:6]] + [{k1: v1, k2: v2} for k1, k2 in
                                                                   itertools.combinations(keys, 2)
                                                                   for v1, v2 in [(0, 1), ("a", None)]]
    pool += lists + dicts
    pool += [[d] for d in dicts[:20]] + [{"k": lst} for lst in lists[:20]]
    return pool


def f3_canon() -> dict:
    pool = _value_pool()
    seen: dict[bytes, object] = {}
    collisions = roundtrip_bad = 0
    for v in pool:
        b = canon.dumps(v)
        if canon.loads(b) != v or type(canon.loads(b)) is not type(v):
            roundtrip_bad += 1
        if b in seen and seen[b] != v:
            collisions += 1
        seen.setdefault(b, v)
    # T1: dict order must not be observable (all permutations of a 4-key dict).
    base = {"b": 1, "\U0001f600": [True], "€": None, "a": "x"}
    outs = {canon.dumps(dict(p)) for p in itertools.permutations(base.items())}
    # RFC 8785 vectors (sections 3.2.2.2 and 3.2.3).
    rfc_in = {"€": "Euro Sign", "\r": "Carriage Return", "דּ": "Hebrew Letter Dalet With Dagesh",
              "1": "One", "\U0001f600": "Emoji: Grinning Face", "\u0080": "Control",
              "ö": "Latin Small Letter O With Diaeresis"}
    text = canon.dumps(rfc_in).decode("utf-8")
    order_seen = [text.index(json.dumps(v, ensure_ascii=False)) for v in
                  ["Carriage Return", "One", "Control", "Latin Small Letter O With Diaeresis", "Euro Sign",
                   "Emoji: Grinning Face", "Hebrew Letter Dalet With Dagesh"]]
    rfc_order_ok = order_seen == sorted(order_seen)
    rfc_string = canon.dumps("€$\x0f\nA'B\"\\\\\"/".replace("\\\\", "\\")) == \
        '"€$\\u000f\\nA\'B\\"\\\\\\"/"'.encode()
    astral_vs_kernel = None
    if kernel_canonical is not None:
        astral_vs_kernel = {"jcs_subset": canon.dumps({"\U00010000": 1, "￿": 2}).decode(),
                            "kernel": kernel_canonical({"\U00010000": 1, "￿": 2})}
    # Differential against the independent rfc8785 library on random members of V (never floats).
    diff: dict = not_run("rfc8785 not installed")
    if rfc8785 is not None:
        rng = random.Random(5)
        alphabet = [*list('ab"\\\n\t\x00\x1f\x7f€דּ😀\uffff\u2028 /1'), "\x80", "ö"]

        def rstr():
            return "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 5)))

        def rval(d):
            r = rng.randrange(7 if d < 3 else 4)
            return [None, True, False, rng.randrange(-2 ** 53 + 1, 2 ** 53), rstr(), None, True][r] if r < 4 else \
                ([rval(d + 1) for _ in range(rng.randrange(0, 4))] if r < 6 else
                 {rstr(): rval(d + 1) for _ in range(rng.randrange(0, 4))})
        n = mism = 0
        for _ in range(20000):
            v = rval(0)
            n += 1
            mism += rfc8785.dumps(v) != canon.dumps(v)
        diff = {"status": "MEASURED", "rfc8785_version": "0.1.4", "values": n, "mismatches": mism,
                "domain": "seeded random members of V: null, bool, safe integers, strings over a hostile 20-character alphabet, lists, dicts (depth <= 3)"}
    # Refusals that make T2 hold.
    refused = {}
    for name, bad in [("float", 1.0), ("nan", float("nan")), ("neg_zero_float", -0.0), ("big_int", 2 ** 53),
                      ("lone_surrogate", "\ud800"), ("int_key", {1: "a"}), ("tuple", (1,)), ("set", {1}),
                      ("bytes", b"a"), ("bool_key", {True: 1})]:
        try:
            canon.dumps(bad)
            refused[name] = False
        except canon.InvalidValue:
            refused[name] = True
    # Framing (T3): naive concatenation collides, frame does not; exhaustive over a tiny alphabet.
    naive_collides = canon.naive_concat_digest(b"a", b"bc") == canon.naive_concat_digest(b"ab", b"c")
    framed_distinct = canon.digest(b"t", b"a", b"bc") != canon.digest(b"t", b"ab", b"c")
    strings = [b"".join(p) for k in range(3) for p in itertools.product([b"a", b"b"], repeat=k)]
    tuples = [(tag, fs) for tag in (b"x", b"xy") for k in range(4) for fs in itertools.product(strings, repeat=k)]
    frames = {canon.frame(t, fs) for t, fs in tuples}
    # T4 Merkle: permutation invariance (all 24 orders), leaf sensitivity, duplicate refusal.
    leaves = [b"l0", b"l1", b"l2", b"l3"]
    roots = {canon.merkle_root(list(p)) for p in itertools.permutations(leaves)}
    sensitive = all(canon.merkle_root([b"x" if i == j else leaf for j, leaf in enumerate(leaves)]) != next(iter(roots))
                    for i in range(4))
    try:
        canon.merkle_root([b"a", b"a"])
        dup_refused = False
    except canon.InvalidValue:
        dup_refused = True
    return {"status": "MEASURED",
            "domain": f"{len(pool)} hand-built values over a hostile alphabet (quote, backslash, controls, DEL, U+2028, U+FFFF, "
                      "astral, digit-like strings), dicts of up to 2 keys, lists of up to 2 items, nesting 2",
            "values": len(pool), "distinct_texts": len(seen), "collisions_between_unequal_values": collisions,
            "roundtrip_failures_incl_type": roundtrip_bad, "dict_permutations_distinct_outputs": len(outs),
            "rfc8785_section_3_2_3_sort_vector_ok": rfc_order_ok, "rfc8785_section_3_2_2_string_vector_ok": rfc_string,
            "astral_vs_bmp_key_order": astral_vs_kernel, "differential_vs_rfc8785": diff, "refusals": refused,
            "framing": {"naive_concat_collides_a_bc_vs_ab_c": naive_collides, "framed_distinct": framed_distinct,
                        "tuples": len(tuples), "distinct_frames": len(frames)},
            "merkle": {"permutations": 24, "distinct_roots": len(roots), "leaf_change_changes_root": sensitive,
                       "duplicate_leaf_refused": dup_refused}}


def f3b_kernel_canonical_hazards() -> dict:
    """What the kernel's canonical() does outside V. It is correct for its own current inputs (typed models);
    these are the hazards that stop it being reused for committed graph artefacts on unvalidated data."""
    if kernel_canonical is None:
        return not_run("kernel not importable")
    out: dict = {}
    out["int_key_and_str_key_same_text"] = kernel_canonical({1: "a"}) == kernel_canonical({"1": "a"})
    try:
        kernel_canonical({1: "a", "1": "b"})
        out["mixed_key_types"] = "accepted"
    except TypeError:
        out["mixed_key_types"] = "TypeError"
    out["tuple_and_list_same_text"] = kernel_canonical((1, 2)) == kernel_canonical([1, 2])
    out["float_and_int_differ"] = (kernel_canonical(1.0), kernel_canonical(1))
    out["negative_zero"] = kernel_canonical(-0.0)
    try:
        kernel_canonical(float("nan"))
        out["nan"] = "accepted"
    except ValueError:
        out["nan"] = "ValueError"
    try:
        kernel_fingerprint("\ud800")
        out["lone_surrogate_fingerprint"] = "accepted"
    except UnicodeEncodeError:
        out["lone_surrogate_fingerprint"] = "UnicodeEncodeError"
    out["integer_above_2_53_kept_exact"] = kernel_canonical(2 ** 60)
    out["numeric_key_order_by_value_not_text"] = kernel_canonical({10: 1, 9: 2})
    return {"status": "MEASURED", "cases": out}


# ---- F4: SCC labelling and lexicographic topological order ---------------------------------------------

def f4_order(n: int = 4, n_lab: int = 3) -> dict:
    graphs = accepted = topo_cases = topo_bad = topo_brute_bad = 0
    for nodes, edges in _digraphs(n):
        graphs += 1
        lab = order.scc_labels(nodes, edges)
        accepted += order.check_scc_labels(nodes, edges, lab)[0]
        # independent definition: mutual reachability, class minimum
        reach = {x: closure.lfp_kleene(_adj(nodes, edges), [x]) for x in nodes}
        truth = {x: min(y for y in nodes if y in reach[x] and x in reach[y]) for x in nodes}
        if lab != truth:
            topo_bad += 1
    # exhaustive labelling search: the checker accepts exactly the canonical labelling.
    lab_cases = wrong_accept = 0
    for nodes, edges in _digraphs(n_lab):
        reach = {x: closure.lfp_kleene(_adj(nodes, edges), [x]) for x in nodes}
        truth = {x: min(y for y in nodes if y in reach[x] and x in reach[y]) for x in nodes}
        for choice in itertools.product(nodes, repeat=len(nodes)):
            cand = dict(zip(nodes, choice, strict=False))
            lab_cases += 1
            wrong_accept += order.check_scc_labels(nodes, edges, cand)[0] != (cand == truth)
    dag_n = dag_topo = 0
    for nodes, edges in _digraphs(n):
        if any(a == b for a, b in edges):
            continue
        order_l = order.lexicographic_topological_order(nodes, edges)
        valid = [p for p in itertools.permutations(nodes) if all(p.index(a) < p.index(b) for a, b in edges)]
        best = min(valid) if valid else None
        topo_cases += 1
        if order_l is None:
            topo_brute_bad += best is not None
            continue
        dag_n += 1
        topo_brute_bad += tuple(order_l) != best
        dag_topo += order.check_lexicographic_topological_order(nodes, edges, order_l)[0]
    return {"status": "MEASURED", "domain": f"all digraphs on {n} nodes (SCC, topological order), all 27 x 512 labelings on {n_lab} nodes",
            "graphs": graphs, "producer_labels_accepted_by_checker": accepted,
            "producer_labels_different_from_mutual_reachability_definition": topo_bad,
            "labelings_tried_on_3_nodes": lab_cases, "checker_disagrees_with_definition": wrong_accept,
            "loopless_digraphs": topo_cases, "acyclic_among_them": dag_n,
            "producer_order_differs_from_brute_force_lexicographic_minimum": topo_brute_bad,
            "checker_accepts_producer_order": dag_topo}


def f4b_library_defaults(trials: int = 60) -> dict:
    if nx is None:
        return not_run("networkx not installed")
    nodes = [f"n{i}" for i in range(6)]
    edges = [("n0", "n1"), ("n1", "n0"), ("n1", "n2"), ("n3", "n2"), ("n4", "n5"), ("n5", "n4"), ("n3", "n4")]
    nx_forms, ours = set(), set()
    checker_rejects_nx = accepted_after_relabel = 0
    for seed in range(trials):
        e = edges[:]
        random.Random(seed).shuffle(e)
        g = nx.DiGraph()
        g.add_nodes_from(random.Random(seed + 1000).sample(nodes, len(nodes)))
        g.add_edges_from(e)
        cond = nx.condensation(g)
        nx_lab = {m: str(k) for k, d in cond.nodes(data=True) for m in d["members"]}
        nx_forms.add(json.dumps(sorted(nx_lab.items())))
        checker_rejects_nx += not order.check_scc_labels(nodes, edges, nx_lab)[0]
        least = {}
        for m, lab in nx_lab.items():
            least[lab] = min(least.get(lab, m), m)
        relabelled = {m: least[lab] for m, lab in nx_lab.items()}
        accepted_after_relabel += order.check_scc_labels(nodes, edges, relabelled)[0]
        ours.add(json.dumps(sorted(order.scc_labels(nodes, e).items())))
    return {"status": "MEASURED", "domain": f"{trials} seeded insertion orders of one 6-node graph", "networkx": nx.__version__,
            "distinct_nx_condensation_labellings": len(nx_forms), "distinct_min_member_labellings": len(ours),
            "checker_rejects_raw_nx_labels_as_non_canonical": checker_rejects_nx,
            "checker_accepts_nx_partition_after_min_member_relabel": accepted_after_relabel}


# ---- F5: rule IR, stratification, SQL differential, recursion guard ------------------------------------

PROGRAMS = {
    "uncovered": ("R1: verified(R) :- verifies(T, R).\nR2: violation(R) :- requirement(R), not verified(R).",
                  {"verifies": 2, "requirement": 1, "verified": 1, "violation": 1}),
    "reach_and_cycle": ("R1: reach(X, Y) :- edge(X, Y).\nR2: reach(X, Z) :- reach(X, Y), edge(Y, Z).\nR3: cyc(X) :- reach(X, X).",
                        {"edge": 2, "reach": 2, "cyc": 1}),
    "orphan_and_ill_typed": ("R1: violation(L) :- link(L, K, S, T), not node(T).\n"
                             "R2: violation(L) :- link(L, K, S, T), ntype(S, TS), ntype(T, TT), not sig(K, TS, TT).",
                             {"link": 4, "node": 1, "ntype": 2, "sig": 3, "violation": 1}),
    "stratified_two_levels": ("R1: reach(X, Y) :- edge(X, Y).\nR2: reach(X, Z) :- reach(X, Y), edge(Y, Z).\n"
                              "R3: unreached(X) :- node(X), not reach(a, X), neq(X, a).",
                              {"edge": 2, "reach": 2, "node": 1, "unreached": 1}),
}


def _random_facts(name: str, arity: dict, rng: random.Random):
    consts = ["a", "b", "c", "d"]
    typed = [*consts, "req", "sym"]
    base = {"uncovered": ["verifies", "requirement"], "reach_and_cycle": ["edge"],
            "orphan_and_ill_typed": ["link", "node", "ntype", "sig"], "stratified_two_levels": ["edge", "node"]}[name]
    facts: rules.Facts = {}
    for p in base:
        pool = typed if (name == "orphan_and_ill_typed" and p in ("ntype", "sig")) else consts
        facts[p] = {tuple(rng.choice(pool) for _ in range(arity[p])) for _ in range(rng.randrange(0, 7))}
    return facts


def f5_rules(samples: int = 200, seed: int = 3) -> dict:
    diff = {}
    for name, (text, arity) in sorted(PROGRAMS.items()):
        prog = rules.parse(text)
        rng = random.Random(seed)
        mism = fired = 0
        heads = sorted({r.head.pred for r in prog} - {a.pred for r in prog for a in r.body})
        for _ in range(samples):
            base = _random_facts(name, arity, rng)
            a = rules.evaluate(prog, base)
            b = rules.evaluate_sql(prog, base, arity)
            keys = set(a) | set(b)
            mism += any(a.get(k, set()) != b.get(k, set()) for k in keys)
            fired += any(a.get(h) for h in heads)
        diff[name] = {"random_fact_sets": samples, "mismatches_reference_vs_sqlite": mism,
                      "fact_sets_where_a_final_head_is_non_empty": fired,
                      "strata": dict(sorted(rules.stratify(prog).items()))}
    rejected = {}
    for label, text in {"negation_in_recursion": "R1: p(X) :- q(X), not p(X).",
                        "mutual_negation": "R1: p(X) :- q(X), not r(X).\nR2: r(X) :- q(X), not p(X).",
                        "unsafe_head_variable": "R1: p(X, Y) :- q(X).",
                        "unsafe_negated_variable": "R1: p(X) :- q(X), not r(Y)."}.items():
        try:
            rules.stratify(rules.parse(text))
            rejected[label] = False
        except rules.RuleError:
            rejected[label] = True
    # Recursion guard: SQLite documents that LIMIT stops a recursive CTE silently.
    db = sqlite3.connect(":memory:")
    db.execute("create table e(a, b)")
    db.executemany("insert into e values (?, ?)", [(f"n{i:03d}", f"n{i + 1:03d}") for i in range(50)])
    q = ("with recursive reach(x) as (select 'n000' union select e.b from e join reach on e.a = reach.x) "
         "select count(*) from reach")
    full = db.execute(q).fetchone()[0]
    limited = db.execute(q.replace("select count(*) from reach", "select count(*) from (select x from reach limit 10)")).fetchone()[0]
    guarded = db.execute(q.replace("select count(*) from reach", "select count(*) from (select x from reach limit 11)")).fetchone()[0]
    limit_in_cte = db.execute(
        "with recursive reach(x) as (select 'n000' union select e.b from e join reach on e.a = reach.x limit 10) "
        "select count(*) from reach").fetchone()[0]
    db.close()
    return {"status": "MEASURED", "differential": diff, "loader_rejects": rejected,
            "recursion_guard": {"true_reach_size": full, "count_with_limit_10_applied_outside": limited,
                                "count_with_limit_inside_the_recursive_select": limit_in_cte,
                                "detect_truncation_by_asking_for_limit_plus_one": guarded == 11,
                                "note": "a LIMIT that truncates silently must be turned into a finding, never into a shorter result"},
            "sqlite": sqlite3.sqlite_version}


def f5b_asp_bridge(samples: int = 100, seed: int = 4) -> dict:
    """clingo as a third evaluator and a fixture synthesiser; every synthesised fixture is replayed in the reference."""
    if not asp.available():
        return not_run("clingo not installed")
    out: dict = {"status": "MEASURED", "clingo": __import__("clingo").__version__}
    diff, fixtures = {}, {}
    finals = {"uncovered": ("violation", 1), "reach_and_cycle": ("cyc", 1), "orphan_and_ill_typed": ("violation", 1),
              "stratified_two_levels": ("unreached", 1)}
    universes = {"uncovered": ["a", "b", "t"], "reach_and_cycle": ["a", "b", "c"],
                 "orphan_and_ill_typed": ["l1", "req", "sym", "a", "b", "calls"], "stratified_two_levels": ["a", "b", "c"]}
    for name, (text, arity) in sorted(PROGRAMS.items()):
        prog = rules.parse(text)
        rng = random.Random(seed)
        mism = 0
        for _ in range(samples):
            base = _random_facts(name, arity, rng)
            a, b = rules.evaluate(prog, base), asp.evaluate_asp(prog, base)
            mism += any(a.get(k, set()) != b.get(k, set()) for k in set(a) | set(b))
        diff[name] = {"random_fact_sets": samples, "mismatches_reference_vs_clingo": mism}
        base_arity = {p: k for p, k in arity.items() if p in _random_facts(name, arity, random.Random(0)) or
                      p in {"verifies", "requirement", "edge", "link", "node", "ntype", "sig"}}
        base_arity = {p: k for p, k in base_arity.items() if p not in {r.head.pred for r in prog}}
        target, tk = finals[name]
        fx = asp.synthesise(prog, base_arity, universes[name], target, tk, max_facts=6)
        replay = bool(fx) and bool(rules.evaluate(prog, fx).get(target)) and             bool(rules.evaluate_sql(prog, fx, arity).get(target))
        fixtures[name] = {"target": target, "facts": sum(len(v) for v in (fx or {}).values()), "replayed_in_reference_and_sqlite": replay,
                          "fixture": {p: sorted(map(list, v)) for p, v in sorted((fx or {}).items())}}
    dead = rules.parse("R9: violation(X) :- requirement(X), not requirement(X).")
    out["differential"] = diff
    out["synthesised_positive_fixtures"] = fixtures
    out["dead_rule_control_returns_none"] = asp.synthesise(dead, {"requirement": 1}, ["a", "b"], "violation", 1, 4) is None
    return out


# ---- F6: lens law harness validated by the paper's own examples ----------------------------------------

def f6_lens() -> dict:
    return {"status": "MEASURED", "source": "Foster et al., TOPLAS 2007, section 3 (read 2026-09-29)",
            "controls": lens.run_paper_controls()}


# ---- F7: size of the reference checkers (what a trusted kernel can cost) -----------------------------------

def _logical_lines(fn) -> int:
    tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    body = tree.body[0].body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    lines = set()
    for stmt in body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.stmt):
                lines.add(node.lineno)
    return len(lines)


def f7_sizes() -> dict:
    parts = {
        "closure.check_certificate": [closure.check_certificate],
        "closure.check_unreachable": [closure.check_unreachable],
        "order.check_scc_labels": [order.check_scc_labels],
        "order.check_lexicographic_topological_order": [order.check_lexicographic_topological_order],
        "status.join2+join+meet2+meet+claim_status": [status.join2, status.join, status.meet2, status.meet, status.claim_status],
        "canon.dumps (_string, _utf16_key, _text, dumps)": [canon._string, canon._utf16_key, canon._text, canon.dumps],
        "canon.frame+digest": [canon.frame, canon.digest],
        "rules.check_safety+stratify+evaluate (+ helpers)": [rules.check_safety, rules.dependency_edges, rules.stratify,
                                                             rules._matches, rules._rule_facts, rules.evaluate],
        "order.scc_labels (producer, for scale)": [order.scc_labels],
    }
    return {"status": "MEASURED",
            "definition": "count of distinct statement lines in the function bodies, docstrings excluded (ast); "
                          "size of these REFERENCE implementations, not a promise for the production kernel",
            "logical_lines": {k: sum(_logical_lines(f) for f in fs) for k, fs in sorted(parts.items())}}


# ---- F8: sensitivity of the determinism harness (a harness that cannot fail proves nothing) --------------------

_TOY = "\n".join([
    "import sys",
    "names = ['req:%s' % c for c in 'abcdefghij']",
    "mode = sys.argv[1]",
    "out = list({n for n in names}) if mode == 'set_order' else sorted({n for n in names})",
    "sys.stdout.write(','.join(out))",
])


def f8_harness_sensitivity(seeds: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6, 7)) -> dict:
    """Run a toy pipeline in fresh interpreters under different PYTHONHASHSEED values. The unsorted variant iterates a
    set of strings: its output must vary (the harness sees the defect); the sorted variant must not."""
    results: dict[str, set[str]] = {"set_order": set(), "sorted": set()}
    for mode in results:
        for seed in seeds:
            env = dict(os.environ, PYTHONHASHSEED=str(seed))
            proc = subprocess.run([sys.executable, "-c", _TOY, mode], capture_output=True, env=env, cwd=str(ROOT), timeout=60)
            if proc.returncode != 0:
                return not_run(f"subprocess failed: {proc.stderr.decode('utf-8', 'replace')[:200]}")
            results[mode].add(proc.stdout.decode("utf-8"))
    return {"status": "MEASURED", "domain": f"fresh interpreters, PYTHONHASHSEED in {list(seeds)}, a 10-string set",
            "distinct_outputs_iterating_a_set": len(results["set_order"]), "distinct_outputs_sorted": len(results["sorted"]),
            "harness_detects_the_seeded_defect": len(results["set_order"]) > 1 and len(results["sorted"]) == 1}


# ---- F9: the metamodel in graph/brief.json (or graph/schema when it exists) ----------------------------------

def _load_path(name: str, path: Path):
    """Import a sibling lane's file by path under a private name (their module names collide: two 'reference.py')."""
    import importlib.util
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    except Exception:  # a sibling file that does not import is NOT_RUN for us, never a failure of ours
        return None
    finally:
        sys.path.remove(str(path.parent))
    return module


def f9_metamodel(instances: int = 600, seed: int = 3) -> dict:
    """graph/schema/metamodel.json (metamodel aspect) and graph/rules/catalogue.json (rules aspect), checked by an
    independent reading of the same specification, plus a differential test against the aspect's own reference."""
    mm_path, cat_path, brief_path = (ROOT / "graph" / "schema" / "metamodel.json", ROOT / "graph" / "rules" / "catalogue.json",
                                     ROOT / "graph" / "brief.json")
    out: dict = {"status": "MEASURED"}
    if brief_path.is_file():
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
        found = metamodel.check_brief(brief)
        out["brief_json_table_findings"] = {"node_types": len(brief["node_types"]), "link_types": len(brief["link_types"]),
                                            "by_code": dict(sorted({c: sum(1 for k, _ in found if k == c) for c, _ in found}.items())),
                                            "isolated_node_types": sorted(s for c, s in found if c == "MM-004")}
    if not mm_path.is_file():
        return {**out, "metamodel_json": not_run("graph/schema/metamodel.json missing")}
    mm = json.loads(mm_path.read_text(encoding="utf-8"))
    cat = json.loads(cat_path.read_text(encoding="utf-8")) if cat_path.is_file() else None
    rule_ids = {r["id"] for r in cat["rules"]} if cat else None
    nodes, edges = metamodel.constructive_instance(mm)
    obligations = sum(len(r.get("obligations", [])) for k in mm["link_types"].values() for r in k["signatures"])
    out["metamodel_json"] = {"node_types": len(mm["node_types"]), "link_types": len(mm["link_types"]), "min_obligations": obligations,
                             "table_findings": [list(f) for f in metamodel.check_tables(mm, rule_ids)],
                             "constructive_instance": {"nodes": len(nodes), "edges": len(edges),
                                                       "findings_incl_min_obligations": sorted(map(list, metamodel.check_instance(mm, nodes, edges, True)))}}
    ref = None
    for name in ("typecheck.py", "reference.py"):  # the metamodel aspect renamed reference.py to typecheck.py on 2026-09-29
        ref = _load_path("weave_schema_typecheck", ROOT / "graph" / "schema" / name)
        if ref is not None:
            break
    if ref is None:
        out["differential_vs_schema_reference"] = not_run("graph/schema/typecheck.py (or reference.py) is missing or not importable")
    else:
        out["metamodel_json"]["constructive_instance"]["reference_findings"] = sorted(map(list, ref.check_document(mm, nodes, edges)))
        rng = random.Random(seed)
        types, kinds = sorted(mm["node_types"]), sorted(mm["link_types"])
        pool = [{"id": f"n:{t}:{i}", "type": t} for t in types for i in range(2)]
        ids_by_type: dict[str, list[str]] = {}
        for n in pool:
            ids_by_type.setdefault(n["type"], []).append(n["id"])
        mism = nonclean = 0
        codes: set[str] = set()
        for _ in range(instances):
            es = []
            for _ in range(rng.randrange(0, 25)):
                k = rng.choice(kinds)
                spec = mm["link_types"][k]
                if rng.random() < 0.7:
                    row = rng.choice(spec["signatures"])
                    f, t = rng.choice(metamodel.expand(mm, row["from"])), rng.choice(metamodel.expand(mm, row["to"]))
                else:
                    f, t = rng.choice(types), rng.choice(types)
                e = {"kind": k, "from": rng.choice(ids_by_type[f]), "to": rng.choice(ids_by_type[t])}
                if rng.random() < 0.4 and spec["qualifiers"]:
                    e["qualifier"] = rng.choice(spec["qualifiers"])
                elif rng.random() < 0.1:
                    e["qualifier"] = "bogus"
                if rng.random() < 0.05:
                    e["to"] = "n:missing"
                es.append(e)
            a = {(c, s) for c, s, _ in ref.check_document(mm, pool, es)}
            mism += a != metamodel.check_instance(mm, pool, es)
            nonclean += bool(a)
            codes |= {c for c, _ in a}
        out["differential_vs_schema_reference"] = {
            "instances": instances, "instances_with_findings": nonclean, "mismatches": mism, "codes_exercised": sorted(codes),
            "domain": f"seeded ({seed}) random edge sets over 2 nodes per type, 70% signature-guided, 0 to 24 edges"}
    if cat is None:
        out["catalogue"] = not_run("graph/rules/catalogue.json missing")
    else:
        rec = catalogue.recompute(cat)
        try:
            catalogue.stratify_catalogue(cat)
            stratifiable = True
        except rules.RuleError as exc:
            stratifiable = str(exc)
        out["catalogue"] = {"rules": rec["rules"], "stratum_problems": rec["problems"], "as_program_is_stratifiable": stratifiable,
                            "assumption": "rules of stratum 3 feed finding3, which nothing reads (the catalogue's description of the finding relation)"}
    return out


CHECKS = {
    "F1": ("F1_closure", f1_closure), "F1b": ("F1b_budget_semantics", f1b_budget_semantics),
    "F1c": ("F1c_checker_soundness_and_mutants", f1c_checker_soundness_and_mutants),
    "F2": ("F2_status_algebras", f2_status), "F3": ("F3_canonical_serialisation", f3_canon),
    "F3b": ("F3b_kernel_canonical_hazards", f3b_kernel_canonical_hazards), "F4": ("F4_scc_and_topological_order", f4_order),
    "F4b": ("F4b_library_default_labels", f4b_library_defaults), "F5": ("F5_rules", f5_rules),
    "F5b": ("F5b_clingo_bridge", f5b_asp_bridge), "F6": ("F6_lens_laws", f6_lens), "F7": ("F7_checker_sizes", f7_sizes),
    "F8": ("F8_harness_sensitivity", f8_harness_sensitivity), "F9": ("F9_metamodel", f9_metamodel),
}


def main(argv: list[str]) -> int:
    only = None
    for a in argv:
        if a.startswith("--only"):
            only = set((a.split("=", 1)[1] if "=" in a else argv[argv.index(a) + 1]).split(","))
    report: dict = {"schema": "eija.weave.formal-checks.v1", "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
                    "networkx": getattr(nx, "__version__", None), "rfc8785": "0.1.4" if rfc8785 else None}
    timing = {}
    for key, (name, fn) in CHECKS.items():
        if only and key not in only:
            continue
        t0 = time.perf_counter()
        report[name] = fn()
        timing[name] = round(time.perf_counter() - t0, 2)
    if "--timing" in argv:
        report["timing_seconds_NOT_DETERMINISTIC"] = timing
    text = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    sys.stdout.buffer.write(text.encode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
