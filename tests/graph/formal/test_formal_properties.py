"""Property tests (Hypothesis, MPL-2.0, property lane pin) over the same statements the exhaustive suites check on small domains.

Hypothesis explores larger and stranger inputs than the exhaustive enumerations do, at the price of being a sample.
Runs are derandomised (a fixed example sequence per test function) so a failure reproduces and the report is stable.
A missing Hypothesis is a skip, which is NOT_RUN.
"""
from __future__ import annotations

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import HealthCheck, given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from eijaref import canon, closure, order, status  # noqa: E402

settings.register_profile("formal", derandomize=True, database=None, max_examples=300, deadline=None,
                          suppress_health_check=[HealthCheck.too_slow])
settings.load_profile("formal")

text = st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=6)  # no lone surrogates: outside the domain
safe_int = st.integers(min_value=-(2 ** 53 - 1), max_value=2 ** 53 - 1)
values = st.recursive(
    st.none() | st.booleans() | safe_int | text,
    lambda inner: st.lists(inner, max_size=4) | st.dictionaries(text, inner, max_size=4),
    max_leaves=12)


@given(values)
def test_po_d2_canonical_bytes_decode_back_to_the_same_value(v) -> None:
    b = canon.dumps(v)
    back = canon.loads(b)
    assert back == v and canon.dumps(back) == b


@given(st.dictionaries(text, safe_int, max_size=6), st.randoms(use_true_random=False))
def test_po_d1_insertion_order_is_not_observable(d, rnd) -> None:
    items = list(d.items())
    rnd.shuffle(items)
    assert canon.dumps(dict(items)) == canon.dumps(d)


@given(values, values)
def test_po_d2_unequal_values_never_share_bytes(a, b) -> None:
    if canon.dumps(a) == canon.dumps(b):
        assert a == b and type(a) is type(b)


@given(st.lists(st.binary(max_size=4), max_size=4), st.lists(st.binary(max_size=4), max_size=4))
def test_po_d4_framing_is_injective(xs, ys) -> None:
    if canon.frame(b"t", tuple(xs)) == canon.frame(b"t", tuple(ys)):
        assert xs == ys


@given(st.sets(st.binary(min_size=1, max_size=5), min_size=1, max_size=8), st.randoms(use_true_random=False))
def test_po_d5_merkle_root_ignores_leaf_order_and_sees_every_leaf(leaves, rnd) -> None:
    ls = sorted(leaves)
    shuffled = ls[:]
    rnd.shuffle(shuffled)
    assert canon.merkle_root(shuffled) == canon.merkle_root(ls)
    changed = ls[:]
    changed[0] = changed[0] + b"\x00"
    if changed[0] not in ls:
        assert canon.merkle_root(changed) != canon.merkle_root(ls)


node = st.sampled_from([f"n{i}" for i in range(9)])
edge_sets = st.sets(st.tuples(node, node), max_size=25)


@given(edge_sets, st.sets(node, max_size=3))
def test_po_g1_certificate_from_bfs_is_accepted_and_equals_the_kleene_fixed_point(edges, roots) -> None:
    g: dict[str, list[str]] = {}
    for a, b in sorted(edges):
        g.setdefault(a, []).append(b)
    cert = closure.certify(g, roots)
    assert closure.check_certificate(frozenset(edges), roots, cert)[0]
    assert cert["C"] == closure.lfp_kleene(g, roots) == closure.warshall_closure(g, roots)


@given(edge_sets, st.sets(node, min_size=1, max_size=3), node)
def test_po_g2_forged_certificates_are_rejected(edges, roots, extra) -> None:
    g: dict[str, list[str]] = {}
    for a, b in sorted(edges):
        g.setdefault(a, []).append(b)
    good = closure.certify(g, roots)
    if extra in good["C"]:
        return
    forged = {"C": good["C"] | {extra}, "rank": {**good["rank"], extra: 1}, "parent": {**good["parent"], extra: sorted(roots)[0]}}
    if (sorted(roots)[0], extra) in edges:
        return  # then the extra node really is reachable and the certificate would be genuine (but C would already contain it)
    assert closure.check_certificate(frozenset(edges), roots, forged)[0] is False


@given(edge_sets, st.randoms(use_true_random=False))
def test_po_g3_scc_labels_are_canonical_under_any_insertion_order(edges, rnd) -> None:
    nodes = [f"n{i}" for i in range(9)]
    base = order.scc_labels(nodes, sorted(edges))
    e2, n2 = sorted(edges), nodes[:]
    rnd.shuffle(e2)
    rnd.shuffle(n2)
    assert order.scc_labels(n2, e2) == base
    assert order.check_scc_labels(nodes, sorted(edges), base)[0]


@given(st.lists(st.sampled_from(status.VALUES), max_size=8), st.randoms(use_true_random=False))
def test_po_s1_join_ignores_order_and_repetition(xs, rnd) -> None:
    ys = xs + xs
    rnd.shuffle(ys)
    assert status.join(ys) == status.join(xs)


@given(st.lists(st.sampled_from(status.VALUES), max_size=6), st.sampled_from(status.all_chains()))
def test_po_s2_meet_is_pass_iff_all_pass_for_every_admissible_chain(xs, chain) -> None:
    assert (status.meet(xs, chain) == "PASS") == (bool(xs) and all(x == "PASS" for x in xs))
