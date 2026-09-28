import json
from pathlib import Path

from quality.metrics import aggregate, budgets
from quality.metrics.common import MEASURED, NOT_RUN


def write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc if isinstance(doc, str) else json.dumps(doc), encoding="utf-8")


def group(result, name):
    return next(g for g in result["groups"] if g["group"] == name)


def collect(root):
    """aggregate.collect with `rel` pointed at the fixture directory (it lives outside the repo)."""
    return aggregate.collect(root)


def test_missing_reports_are_not_run_never_pass(tmp_path):
    result = collect(tmp_path)
    assert result["summary"]["groups_not_run"] == 4
    assert all(g["status"] == NOT_RUN and g["reports"] == [] for g in result["groups"])


def test_status_is_copied_not_inferred_and_unknown_never_becomes_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "formal" / "tla.json", {"status": "PASS", "technique": "tlc", "distinct_states": 1200, "duration_s": 2.0})
    write(tmp_path / "formal" / "z3.json", {"result": "sat"})  # no status field
    write(tmp_path / "hci" / "a11y.json", "{not json")
    result = collect(tmp_path)
    formal = group(result, "formal")
    by_file = {r["file"].rsplit("/", 1)[-1]: r for r in formal["reports"]}
    assert by_file["tla.json"]["status"] == "PASS" and by_file["z3.json"]["status"] == "UNKNOWN"
    assert formal["status"] == "UNKNOWN"  # the weakest report decides; unknown never rounds up to PASS
    assert group(result, "hci")["reports"][0]["status"] == "UNREADABLE"
    assert group(result, "mutation")["status"] == NOT_RUN


def test_a_single_fail_dominates_and_trips_the_lane_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "mutation" / "summary.json", {"status": "FAIL", "summary": {"mutation_score": 0.4, "mutants": 10, "killed": 4}})
    write(tmp_path / "formal" / "bend.json", {"status": "PASS"})
    result = collect(tmp_path)
    assert group(result, "mutation")["reports"][0]["values"] == {"mutation_score": 0.4, "mutants": 10, "killed": 4}
    doc = {"sections": {"lane_reports": result}}
    assert next(r for r in budgets.evaluate(doc) if r["id"] == "LANE-01")["status"] == "FAIL"


def test_yield_rows_only_from_reports_with_state_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "rel", lambda p: p.relative_to(tmp_path).as_posix())
    write(tmp_path / "formal" / "tla.json", {"status": "PASS", "technique": "tlc", "summary": {"states": 2000, "counterexamples": 0, "seconds": 4}})
    write(tmp_path / "formal" / "z3.json", {"status": "PASS", "checks": 12})
    rows = aggregate.yield_rows(collect(tmp_path))
    assert [r["technique"] for r in rows] == ["tlc"]
    assert rows[0]["states_explored"] == 2000 and rows[0]["states_per_s"] == 500 and rows[0]["findings"] == 0


def test_lane_budget_is_not_run_when_no_lane_reported():
    doc = {"sections": {"lane_reports": collect(Path("does-not-exist"))}}
    assert next(r for r in budgets.evaluate(doc) if r["id"] == "LANE-01")["status"] == NOT_RUN
    assert doc["sections"]["lane_reports"]["status"] == MEASURED
