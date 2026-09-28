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
