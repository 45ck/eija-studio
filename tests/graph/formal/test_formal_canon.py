"""PO-D1..D5: canonical serialisation, injectivity, RFC 8785 conformance on the subset, framing and Merkle root."""
from __future__ import annotations

import itertools
import random

import pytest
from eijaref import canon, suites

from conftest import load_bench

bench = load_bench()


def test_po_d1_d2_pool_of_hostile_values_has_no_collision_and_round_trips_with_types() -> None:
    r = bench.f3_canon()
    assert r["values"] > 250
    assert r["collisions_between_unequal_values"] == 0
    assert r["roundtrip_failures_incl_type"] == 0
    assert r["dict_permutations_distinct_outputs"] == 1


def test_po_d3_rfc8785_vectors_sorting_and_string_escaping() -> None:
    rfc_in = {"€": "Euro Sign", "\r": "Carriage Return", "דּ": "Hebrew Letter Dalet With Dagesh", "1": "One",
              "\U0001f600": "Emoji: Grinning Face", "\u0080": "Control", "ö": "Latin Small Letter O With Diaeresis"}
    text = canon.dumps(rfc_in).decode("utf-8")
    expected = ["Carriage Return", "One", "Control", "Latin Small Letter O With Diaeresis", "Euro Sign",
                "Emoji: Grinning Face", "Hebrew Letter Dalet With Dagesh"]  # RFC 8785 section 3.2.3
    positions = [text.index(v) for v in expected]
    assert positions == sorted(positions)
    # section 3.2.2: the string of the sample, escaped as JSON.stringify and JCS do
    assert canon.dumps("€$\x0f\nA'B\"\\\"/") == '"€$\\u000f\\nA\'B\\"\\\\\\"/"'.encode()


def test_po_d3_astral_keys_sort_before_U_FFFF_unlike_code_point_order() -> None:
    assert canon.dumps({"\U00010000": 1, "￿": 2}) == '{"\U00010000":1,"￿":2}'.encode("utf-8")
    assert sorted(["\U00010000", "￿"]) == ["￿", "\U00010000"]  # Python str order is by code point


def test_po_d3_differential_against_the_independent_rfc8785_library() -> None:
    pytest.importorskip("rfc8785")
    r = bench.f3_canon()["differential_vs_rfc8785"]
    assert r["status"] == "MEASURED" and r["mismatches"] == 0 and r["values"] == 20000


@pytest.mark.parametrize("bad", [1.0, float("nan"), -0.0, 2 ** 53, "\ud800", {1: "a"}, (1,), {1}, b"a", {True: 1}])
def test_po_d2_values_outside_the_domain_are_refused_not_coerced(bad) -> None:
    with pytest.raises(canon.InvalidValue):
        canon.dumps(bad)


def test_po_d2_kernel_canonical_collapses_distinct_values_which_is_why_it_is_not_reused_for_artefacts() -> None:
    r = bench.f3b_kernel_canonical_hazards()
    if r["status"] == "NOT_RUN":
        pytest.skip(r["reason"])
    c = r["cases"]
    assert c["int_key_and_str_key_same_text"] is True and c["tuple_and_list_same_text"] is True
    assert c["mixed_key_types"] == "TypeError" and c["lone_surrogate_fingerprint"] == "UnicodeEncodeError"
    assert c["numeric_key_order_by_value_not_text"] == '{"9":2,"10":1}'


def test_po_d4_framing_is_injective_where_naive_concatenation_collides() -> None:
    assert canon.naive_concat_digest(b"a", b"bc") == canon.naive_concat_digest(b"ab", b"c")
    assert canon.digest(b"t", b"a", b"bc") != canon.digest(b"t", b"ab", b"c")
    r = bench.f3_canon()["framing"]
    assert r["tuples"] == r["distinct_frames"] == 800


def test_po_d4_domain_separation_a_leaf_cannot_be_read_as_an_interior_node() -> None:
    a, b = canon.digest(b"x.leaf", b"l"), canon.digest(b"x.node", b"l")
    assert a != b
    assert canon.merkle_root([b"a"]) != canon.merkle_root([b"a", b"b"])
    assert canon.merkle_root([]) != canon.merkle_root([b""])


def test_po_d5_merkle_root_is_a_function_of_the_leaf_set_and_sees_every_leaf() -> None:
    r = bench.f3_canon()["merkle"]
    assert r["distinct_roots"] == 1 and r["leaf_change_changes_root"] and r["duplicate_leaf_refused"]


def test_po_d_suite_passes_reference_and_fails_the_kernel_style_json_dumps() -> None:
    assert suites.suite_canon(canon.dumps) == []
    assert suites.suite_canon(suites.wrong_dumps_python_json) != []


def test_po_d1_random_dict_orders_never_change_the_bytes() -> None:
    rng = random.Random(9)
    alphabet = list("ab€\U0001f600￿\"\\\n")
    for _ in range(300):
        keys = ["".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 4))) for _ in range(rng.randrange(0, 6))]
        items = [(k, rng.randrange(0, 3)) for k in dict.fromkeys(keys)]
        outs = {canon.dumps(dict(p)) for p in itertools.islice(itertools.permutations(items), 30)}
        assert len(outs) == 1
