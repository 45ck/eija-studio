"""Analysis, recommendation, budget and rendering logic over a synthetic trace with known answers."""
import json
import math

import pytest

from quality.hci import analysis, budgets, journey, laws, report
from . import hci_synthetic as syn


@pytest.fixture(scope="module")
def rep():
    return report.build_report(syn.raw())


def test_fitts_rows_use_shannon_smaller_of_and_flags(rep):
    rows = {r["step"]: r for r in rep["fitts"]["targets"]}
    assert rows["s1"]["id_bits"] is None and rows["s1"]["flags"] == []  # first target has no preceding position
    assert rows["s2"]["id_bits"] == pytest.approx(math.log2(400 / 40 + 1), abs=1e-3)
    assert rows["s2"]["predicted_mt_s"] == pytest.approx(0.230 + 0.166 * math.log2(11), abs=1e-3)
    assert rows["s3"]["flags"] == ["W<24"]  # W = min(100, 20)
    assert rows["s4"]["flags"] == ["ID>4"]  # log2(800/40 + 1) = 4.39
    assert rows["s2"]["flags"] == []  # 3.46 bits: negative control, not flagged
    s = rep["fitts"]["summary"]
    assert (s["moves_id_over_4"], s["targets_w_under_24"]) == (1, 1)


def test_nearest_edge_variant_bounds_the_centre_landing_bias(rep):
    """Wide target: the centre landing (D=400) flags nothing here, but a 1000 px wide row is reached at its near edge."""
    assert laws.nearest_edge_distance((0, 0), (300, -20, 200, 40)) == 300  # box 300..500 on the pointer's row
    assert laws.nearest_edge_distance((350, 0), (300, -20, 200, 40)) == 0  # origin inside the box
    assert laws.nearest_edge_distance((0, 0), (30, 40, 10, 10)) == 50  # dx=30, dy=40
    rows = {r["step"]: r for r in rep["fitts"]["targets"]}
    assert rows["s2"]["id_bits_nearest_edge"] < rows["s2"]["id_bits"]  # box edge is nearer than its centre
    assert rows["s1"]["id_bits_nearest_edge"] is None
    s = rep["fitts"]["summary"]
    assert s["moves_id_over_4_nearest_edge"] <= s["moves_id_over_4"]  # a range whose upper end is the primary count
    assert "overstates D" in s["landing_convention_note"]


def test_completion_flags_are_derived_from_the_recorded_steps_not_asserted(rep):
    assert rep["journey"]["completed"] is False  # negative control: the synthetic trace is not the canonical journey
    assert rep["keyboard"]["completed_journey_keyboard_only"] is False
    raw = syn.raw()
    canonical = [{"id": s.id, "label": s.label, "kind": s.kind} for s in journey.journey()]
    for p in (*raw["pointer_passes"], raw["keyboard_pass"]):
        p["steps"] = [dict(x) for x in canonical]
    assert analysis.analyse(raw)["journey"]["completed"] is True
    raw["pointer_passes"][1]["steps"].pop()  # one pass stopped early
    assert analysis.analyse(raw)["journey"]["completed"] is False


def test_hypotheses_are_labelled_and_upper_bounds_do_not_break_ranking_ties(rep):
    by_id = {x["id"]: x for x in rep["recommendations"]}
    focus = by_id["focus-lost-after-render"]
    assert focus["saving_kind"] == "upper bound" and focus["rank_saving_s"] == 0.0 and focus["predicted_saving_s"] > 0
    assert focus["likely_cause"] and "hypothesis" in focus["likely_cause"]
    assert "replaceChildren" not in focus["change"]  # UI-specific diagnosis is not stated as a fact in `change`
    assert by_id["fitts-id-over-4"]["saving_kind"] == "model difference" and by_id["fitts-id-over-4"]["rank_saving_s"] > 0
    md = report.render_markdown(rep)
    assert "UNVERIFIED hypothesis" in md and "upper bound" in md


def test_doherty_recommendation_states_only_what_the_data_says():
    raw = syn.raw()
    for p in raw["pointer_passes"]:
        p["steps"][2]["interaction"]["settled_ms"] = 1500.0  # a step whose median exceeds 400 ms
    for p in raw["pointer_passes"]:
        p["steps"][2]["interaction"]["first_feedback_ms"] = 700.0  # and whose first DOM mutation is slow too
    rec = {x["id"]: x for x in report.build_report(raw)["recommendations"]}["doherty-completion"]
    assert "700" in rec["change"] and "immediate" not in rec["change"]  # the feedback claim comes from the measured number
    assert "SQLite" not in rec["change"] and "SQLite" in rec["likely_cause"]


def test_hick_flags_only_choice_groups_over_seven(rep):
    rows = {r["step"]: r for r in rep["hick_hyman"]["decisions"]}
    assert rows["s2"]["choices"] == 3 and rows["s2"]["over_7"] is False
    assert rows["s3"]["choices"] == 9 and rows["s3"]["over_7"] is True
    assert rows["s2"]["predicted_s"] == pytest.approx(0.150 * 2.0)
    assert rep["hick_hyman"]["summary"]["choice_points_over_7"] == 1


def test_klm_totals_and_fitts_refinement(rep):
    pj = rep["klm"]["pointer_journey"]
    assert pj["operator_counts"] == {"K": 0, "P": 4, "B": 8, "H": 0, "M": 1}
    assert pj["total_s"] == pytest.approx(4 * 1.10 + 8 * 0.10 + 1.35)
    mts = [r["predicted_mt_s"] for r in rep["fitts"]["targets"] if r["predicted_mt_s"] is not None]
    assert pj["fitts_refined_total_s"] == pytest.approx(1.10 + sum(mts) + 8 * 0.10 + 1.35, abs=1e-2)  # first P keeps 1.10 s
    assert rep["klm"]["keyboard_only_journey"]["operator_counts"]["K"] == 2


def test_doherty_percentiles_and_flags(rep):
    d = rep["measured"]["doherty"]
    steps = {s["step"]: s for s in d["steps"]}
    assert steps["s2"]["settled_p95_ms"] == 60.0 and steps["s2"]["over_400ms"] is False
    assert steps["s3"]["settled_p95_ms"] == 900.0 and steps["s3"]["over_400ms"] is True
    assert steps["s3"]["settled_p50_ms"] == 300.0 and steps["s3"]["median_over_400ms"] is False  # tail only
    assert d["first_feedback_p95_ms"] == 1.0


def test_native_interactions_without_dom_updates_are_excluded_from_doherty():
    raw = syn.raw()
    raw["pointer_passes"][0]["steps"][1]["interaction"]["mutation_batches"] = 0
    raw["pointer_passes"][1]["steps"][1]["interaction"]["mutation_batches"] = 0
    d = analysis.doherty(raw["pointer_passes"], raw["keyboard_pass"])
    assert d["native_control_interactions_excluded"] == ["s2"]
    assert "s2" not in [s["step"] for s in d["steps"]]


def test_wcag_aggregation_and_own_target_audit(rep):
    w = rep["wcag"]
    assert [v["id"] for v in w["violations_by_rule"]] == ["color-contrast"]
    assert w["summary"]["serious"] == 1 and w["summary"]["critical"] == 0
    bad = {x["selector"]: x["status"] for x in w["target_size_2_5_8"]["undersized_or_failing"]}
    assert bad == {"#tiny": "fail", "#tiny2": "fail"}  # 20 px apart < 24
    assert w["summary"]["target_size_failures"] == 2


def test_keyboard_metrics(rep):
    k = rep["keyboard"]
    assert k["tab_presses_total"] == 5 and k["activations"] == 2 and k["focus_lost_count"] == 1
    assert k["stops_without_visible_focus_indicator"] == ["#b"]
    assert k["tab_presses_spent_after_focus_loss"] == 4  # step s2 followed a focus loss
    assert k["focus_order_regression_count"] == 1  # #b (y=200) -> #c (y=100)


def test_moves_up_ignores_wrap_row_noise_and_column_jumps():
    r = syn.box
    assert analysis._moves_up(r(0, 200, 5, 5), r(0, 100, 5, 5)) is True
    assert analysis._moves_up(r(0, 200, 5, 5), r(0, 195, 5, 5)) is False  # row alignment noise
    assert analysis._moves_up(r(0, 900, 5, 5), r(0, 0, 5, 5)) is False  # wrapped to the top of the page
    assert analysis._moves_up(r(0, 500, 5, 5), r(300, 100, 5, 5)) is False  # next grid column
    assert analysis._moves_up(None, r(0, 0, 5, 5)) is False


def test_recommendations_are_ranked_deterministically(rep):
    recs = rep["recommendations"]
    assert [x["rank"] for x in recs] == list(range(1, len(recs) + 1))
    keys = [(-x["severity"], -x["rank_saving_s"], x["id"]) for x in recs]
    assert keys == sorted(keys)
    ids = {x["id"] for x in recs}
    assert {"a11y-color-contrast", "fitts-id-over-4", "target-size-fail", "focus-lost-after-render", "doherty-tail"} <= ids
    assert report.build_report(syn.raw())["recommendations"] == recs  # same input, same ranking


def test_budget_statuses_including_not_run_and_regression():
    defs = [{"id": "x", "law": "l", "path": "a.b", "unit": "u", "target": 1, "limit": 3}]
    assert budgets.evaluate({"a": {"b": 1}}, defs)[0]["status"] == "PASS"
    assert budgets.evaluate({"a": {"b": 2}}, defs)[0]["status"] == "GAP"
    assert budgets.evaluate({"a": {"b": 4}}, defs)[0]["status"] == "FAIL"
    assert budgets.evaluate({"a": {}}, defs)[0]["status"] == "NOT_RUN"  # unmeasurable is never PASS


def test_every_committed_budget_path_resolves_against_a_real_report_shape(rep):
    for b in budgets.load():
        assert budgets.lookup(rep, b["path"]) is not None, b["id"]
        assert b["target"] <= b["limit"], b["id"]
    assert len({b["id"] for b in budgets.load()}) == len(budgets.load())


def test_report_serialisation_is_canonical_and_deterministic(rep):
    text = report.dumps(rep)
    assert text == report.dumps(json.loads(text)) and text.endswith("\n") and "\r" not in text
    markdown = report.render_markdown(rep)
    assert markdown == report.render_markdown(json.loads(text))
    assert "\r" not in markdown and "NOT_RUN" in markdown and "Not a human study" in markdown


def test_doherty_reports_median_and_interquartile_range_not_just_a_tail(rep):
    d = rep["measured"]["doherty"]
    assert d["settled_p25_ms"] <= d["settled_p50_ms"] <= d["settled_p75_ms"] <= d["settled_p95_ms"] <= d["settled_max_ms"]
    steps = {s["step"]: s for s in d["steps"]}
    assert (steps["s3"]["settled_p25_ms"], steps["s3"]["settled_p50_ms"], steps["s3"]["settled_p75_ms"]) == (300.0, 300.0, 900.0)  # two samples: nearest rank
    assert any(b["id"] == "doherty.settled_p50" for b in rep["budgets"])  # a median guard exists beside the loose tail guard


def test_markdown_separates_measurement_from_prediction(rep):
    markdown = report.render_markdown(rep)
    headline = markdown.split("## Headline")[1].split("## ")[0]
    assert "| PREDICTION | KLM-GOMS |" in headline and "| MEASUREMENT (wall-clock) | Doherty |" in headline
    assert "Fitts's law (prediction over measured geometry)" in markdown and "Doherty threshold (measurement" in markdown
    assert "not evidence of user benefit" in markdown and "Nothing here shows that any change benefits users" in markdown
