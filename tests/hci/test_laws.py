"""Pure-formula tests: known values, boundaries and negative controls (no browser)."""
import math

import pytest

from quality.hci import laws
from quality.hci.wcag import Box, target_size_status


def test_shannon_id_known_values():
    assert laws.shannon_id(0, 40) == 0  # already on target
    assert laws.shannon_id(40, 40) == pytest.approx(1.0)  # D == W is exactly one bit
    assert laws.shannon_id(800, 40) == pytest.approx(math.log2(21))
    assert laws.shannon_id(120, 24) > laws.shannon_id(120, 48)  # smaller target is harder
    assert laws.shannon_id(600, 40) > laws.shannon_id(300, 40)  # farther target is harder


@pytest.mark.parametrize("args", [(10, 0), (10, -3), (-1, 10)])
def test_shannon_id_rejects_impossible_geometry(args):
    with pytest.raises(ValueError):
        laws.shannon_id(*args)


def test_smaller_of_is_orientation_free():
    assert laws.smaller_of(1041, 25) == 25 == laws.smaller_of(25, 1041)


def test_fitts_time_uses_mackenzie_buxton_constants():
    assert laws.FittsModel().a == 0.230 and laws.FittsModel().b == 0.166
    assert laws.fitts_time(0) == pytest.approx(0.230)
    assert laws.fitts_time(4.0) == pytest.approx(0.230 + 0.166 * 4)
    assert laws.fitts_time(3, laws.FittsModel(a=0.0, b=0.1)) == pytest.approx(0.3)  # constants are swappable


def test_hick_bits_and_time():
    assert laws.hick_bits(0) == 0
    assert laws.hick_bits(1) == pytest.approx(1.0)
    assert laws.hick_bits(7) == pytest.approx(3.0)
    assert laws.hick_time(7) == pytest.approx(0.150 * 3)
    assert laws.hick_time(8) > laws.hick_time(7)  # monotonic
    with pytest.raises(ValueError):
        laws.hick_bits(-1)


def test_klm_standard_times():
    assert laws.klm_time("KPBBHM") == pytest.approx(0.28 + 1.10 + 0.10 + 0.10 + 0.40 + 1.35)
    assert laws.klm_time([]) == 0
    click = laws.klm_time("PBB")
    assert click == pytest.approx(1.30)  # point + press + release


def test_klm_unknown_operator_is_an_error_not_free():
    with pytest.raises(ValueError):
        laws.klm_time("KX")
    with pytest.raises(ValueError):
        laws.count_operators("KX")


def test_count_operators_includes_zero_counts():
    assert laws.count_operators("KKM") == {"K": 2, "P": 0, "B": 0, "H": 0, "M": 1}


def test_percentile_is_nearest_rank_and_deterministic():
    data = [5, 1, 3, 2, 4]
    assert laws.percentile(data, 50) == 3
    assert laws.percentile(data, 95) == 5
    assert laws.percentile(data, 0) == 1
    assert laws.percentile([7], 95) == 7
    assert laws.percentile([], 50) is None
    assert data == [5, 1, 3, 2, 4]  # input untouched
    with pytest.raises(ValueError):
        laws.percentile(data, 101)


def test_thresholds_match_the_brief():
    assert (laws.MIN_TARGET_PX, laws.MAX_ID_BITS, laws.MAX_CHOICES, laws.DOHERTY_MS) == (24, 4, 7, 400)


# --- oracles taken from the SOURCES, not from the code under test ------------------------------------
# Every expected number below is derived by hand from the published formula and constants:
#   Fitts (Shannon): MacKenzie (1992) Eq. 7-8, ID = log2(A/W + 1), MT = a + b*ID.
#   MacKenzie & Buxton (1992) CHI '92, smaller-of model: MT = 230 + 166*ID ms, r = .9501, IP = 6.0 bits/s.
#   Hick-Hyman: T = b*log2(n + 1) (Hick 1952, Hyman 1953); b ~ 150 ms/bit (Card, Moran & Newell 1983).
#   KLM: Card, Moran & Newell (1980) operator table.
@pytest.mark.parametrize(
    ("amplitude_over_width", "id_bits", "mt_ms"),
    [
        (1, 1, 396),  # A = W: 230 + 166*1
        (3, 2, 562),  # 230 + 166*2
        (7, 3, 728),  # 230 + 166*3
        (15, 4, 894),  # 230 + 166*4
        (31, 5, 1060),  # 230 + 166*5
    ],
)
def test_fitts_hand_computed_shannon_examples(amplitude_over_width, id_bits, mt_ms):
    width = 40.0
    got_id = laws.shannon_id(amplitude_over_width * width, width)
    assert got_id == pytest.approx(id_bits, abs=1e-12)  # A/W + 1 is a power of two, so ID is an exact integer
    assert laws.fitts_time(got_id) * 1000 == pytest.approx(mt_ms, abs=1e-6)


def test_fitts_index_of_performance_matches_the_paper():
    """MacKenzie & Buxton report IP = 6.0 bits/s for the smaller-of mouse model: IP = 1 / b."""
    assert 1.0 / laws.FittsModel().b == pytest.approx(6.0, abs=0.03)


@pytest.mark.parametrize(("n", "bits"), [(1, 1), (3, 2), (7, 3), (15, 4), (31, 5)])
def test_hick_hand_computed_examples(n, bits):
    assert laws.hick_bits(n) == pytest.approx(bits, abs=1e-12)
    assert laws.hick_time(n) == pytest.approx(0.150 * bits, abs=1e-12)  # b = 150 ms/bit


def test_klm_operator_table_matches_card_moran_newell_1980():
    t = laws.KlmTimes()
    assert (t.K, t.P, t.B, t.H, t.M) == (0.28, 1.10, 0.10, 0.40, 1.35)  # K: average non-secretary typist
    assert laws.klm_time("BB") == pytest.approx(0.20)  # a click is a press plus a release
    assert laws.klm_time("MPBB") == pytest.approx(1.35 + 1.10 + 0.20)  # think, point, click


def test_iqr_is_nearest_rank_and_none_when_empty():
    assert laws.iqr([]) is None
    assert laws.iqr([4, 1, 3, 2]) == (1, 2, 3)  # ranks ceil(.25*4)=1, ceil(.5*4)=2, ceil(.75*4)=3
    assert laws.iqr([9]) == (9, 9, 9)


def test_public_api_is_declared():
    """Other pipelines import these names; removing or renaming one must be a deliberate, reviewed change."""
    assert set(laws.__all__) >= {"shannon_id", "smaller_of", "fitts_time", "hick_bits", "hick_time", "klm_time", "count_operators", "percentile", "iqr"}
    assert all(hasattr(laws, name) for name in laws.__all__)


# --- WCAG 2.5.8 -------------------------------------------------------------------------------
def test_target_size_boundary_is_inclusive_at_24():
    assert target_size_status(0, [Box(0, 0, 24, 24)]) == "pass"
    assert target_size_status(0, [Box(0, 0, 23.9, 24)]) == "pass-spacing"  # alone: spacing exception applies


def test_undersized_neighbours_fail():
    a, b = Box(0, 0, 16, 16), Box(20, 0, 16, 16)  # centres 20 px apart < 24
    assert target_size_status(0, [a, b]) == "fail"
    assert target_size_status(1, [a, b]) == "fail"


def test_undersized_far_apart_pass_by_spacing():
    a, b = Box(0, 0, 16, 16), Box(40, 0, 16, 16)  # centres 40 px apart
    assert target_size_status(0, [a, b]) == "pass-spacing"


def test_undersized_touching_a_large_target_fails():
    small, large = Box(0, 0, 16, 16), Box(19, 0, 100, 44)  # 24 px circle around (8, 8) reaches x=19
    assert target_size_status(0, [small, large]) == "fail"
    assert target_size_status(1, [small, large]) == "pass"
