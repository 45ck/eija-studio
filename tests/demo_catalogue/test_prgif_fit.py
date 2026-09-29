"""The size/fps/timing fitting that keeps every PR GIF inside the PR-STANDARD limits (pure logic, no ffmpeg)."""
import pytest

from demos.prgif.fit import (
    Candidate,
    DoesNotFitError,
    Limits,
    candidates,
    fit,
    plan_timing,
    widths,
)


def model_encoder(bytes_per_cost, calls):
    """A fake encoder whose size follows fps * width^2 exactly, recording every call."""
    def encode(candidate):
        calls.append(candidate)
        return int(candidate.cost * bytes_per_cost)
    return encode


# -- timing ---------------------------------------------------------------------------------------------

def test_short_recording_plays_at_real_speed():
    timing = plan_timing(12.0)
    assert (timing.speed, timing.output_seconds, timing.cut) == (1.0, 12.0, False)


def test_long_recording_is_sped_up_to_fit_the_whole_story():
    timing = plan_timing(30.0)
    assert timing.speed == pytest.approx(1.5) and timing.output_seconds == 20.0 and not timing.cut


def test_speedup_is_capped_and_the_tail_cut_is_reported():
    timing = plan_timing(60.0)
    assert timing.speed == 2.0 and timing.output_seconds == 20.0 and timing.cut


def test_exactly_the_limit_is_not_retimed():
    assert plan_timing(20.0).speed == 1.0


def test_zero_duration_is_rejected():
    with pytest.raises(ValueError):
        plan_timing(0.0)


# -- candidate ladder -----------------------------------------------------------------------------------

def test_widths_never_upscale_and_never_exceed_the_cap():
    assert widths(1440)[0] == 1280
    assert widths(900)[0] == 900
    assert all(w % 2 == 0 for w in widths(1441))


def test_widths_descend_to_the_minimum():
    found = widths(1280)
    assert found == sorted(found, reverse=True) and found[-1] == Limits().min_width


def test_small_source_is_kept_as_is():
    assert widths(320) == [320]


def test_candidates_start_at_the_best_quality_and_end_at_the_cheapest():
    ladder = candidates(1280)
    assert ladder[0] == Candidate(15, 1280)
    assert ladder[-1] == Candidate(6, Limits().min_width)
    costs = [c.cost for c in ladder]
    assert costs == sorted(costs, reverse=True)


# -- fitting --------------------------------------------------------------------------------------------

def test_first_candidate_is_accepted_when_it_fits():
    calls = []
    result = fit(model_encoder(0.1, calls), candidates(1280), 5_000_000)
    assert result.chosen == Candidate(15, 1280) and len(calls) == 1 and result.size <= 5_000_000


def test_too_large_lowers_fps_or_width_until_it_fits():
    calls = []
    # 15fps at 1280 px would be 15*1280^2*0.6 = 14.7 MB: three times over the limit.
    result = fit(model_encoder(0.6, calls), candidates(1280), 5_000_000)
    assert result.size <= 5_000_000
    assert result.chosen.cost < Candidate(15, 1280).cost
    assert result.attempts[-1] == (result.chosen, result.size)


def test_prediction_skips_hopeless_candidates():
    calls = []
    fit(model_encoder(0.6, calls), candidates(1280), 5_000_000)
    # after the first measurement the model prunes: far fewer encodes than candidates. The default
    # PREDICTION_SLACK (1.15) deliberately keeps borderline candidates, so it tries a few more than an exact model.
    assert 1 < len(calls) <= 5 < len(candidates(1280)) // 4


def test_prediction_without_slack_prunes_to_three_encodes(monkeypatch):
    monkeypatch.setattr("demos.prgif.fit.PREDICTION_SLACK", 1.0)
    calls = []
    fit(model_encoder(0.6, calls), candidates(1280), 5_000_000)
    assert 1 < len(calls) <= 3


def test_accepted_size_is_the_measured_size_not_the_prediction():
    # The real encoder is noisier than the model: the second attempt comes out larger than predicted.
    sizes = iter([9_000_000, 5_200_000, 4_000_000, 3_000_000])
    result = fit(lambda c: next(sizes), [Candidate(15, 1280), Candidate(12, 1088), Candidate(10, 1088),
                                        Candidate(8, 924)], 5_000_000)
    assert result.size == 4_000_000


def test_nothing_fits_raises_with_every_attempt():
    with pytest.raises(DoesNotFitError) as error:
        fit(lambda c: 99_000_000, candidates(1280), 5_000_000)
    # the cheapest candidate is always tried before giving up
    assert error.value.attempts[-1][0] == candidates(1280)[-1]
    assert "shorten the recording" in str(error.value)


def test_empty_ladder_is_an_error():
    with pytest.raises(ValueError):
        fit(lambda c: 1, [], 10)
