import copy
import json
import re
from itertools import pairwise
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest

from quality.metrics import ROOT, dashboard, svg
from quality.metrics.__main__ import DOCS, SNAPSHOT, cmd_drift
from quality.metrics.common import dumps, meta


@pytest.fixture(scope="module")
def doc():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_committed_snapshot_is_labelled_with_platform_and_commit(doc):
    m = doc["meta"]
    assert m["schema"] == "eija.metrics.v1" and m["platform"]["system"] and m["platform"]["python"]
    assert m["source"]["commit"] and len(m["source"]["commit"]) == 40
    assert set(doc["sections"]) == {"martin", "complexity", "tests", "coverage", "lane_reports", "performance", "scaling",
                                    "verification_yield"}
    assert all(s["status"] in {"MEASURED", "NOT_RUN"} for s in doc["sections"].values())


def test_snapshot_file_is_canonical_json(doc):
    """Regenerating the JSON text from the parsed document is byte-identical: sorted keys, LF, trailing newline."""
    raw = SNAPSHOT.read_bytes()
    assert raw == dumps(doc).encode("utf-8") and b"\r" not in raw


def test_dashboard_and_markdown_have_not_drifted_from_the_snapshot(capsys):
    assert cmd_drift(SimpleNamespace(freshness="off")) == 0, capsys.readouterr().out


def test_render_is_deterministic(doc):
    assert dashboard.render_html(doc) == dashboard.render_html(copy.deepcopy(doc))
    assert dashboard.render_markdown(doc) == dashboard.render_markdown(copy.deepcopy(doc))


def test_dashboard_is_self_contained_and_themed(doc):
    html = dashboard.render_html(doc)
    assert "<script" not in html and "http://" not in html and "https://" not in html  # no network, no scripts
    assert "prefers-color-scheme:dark" in html and 'data-theme="dark"' in html and 'data-theme="light"' in html
    assert 'name="viewport"' in html
    svgs = re.findall(r"<svg.*?</svg>", html, re.S)
    assert len(svgs) >= 6
    for chart in svgs:
        ET.fromstring(chart)  # noqa: S314  (input is generated in-process by svg.py, not untrusted)
        assert "role=\"img\"" in chart and "aria-label=" in chart


def test_untrusted_strings_are_escaped(doc):
    evil = copy.deepcopy(doc)
    evil["sections"]["martin"]["layers"][0]["name"] = "<img src=x onerror=alert(1)>"
    evil["sections"]["martin"]["modules"][0]["name"] = "<b>&"
    html = dashboard.render_html(evil)
    assert "<img src=x" not in html and "&lt;img src=x" in html


def test_not_run_sections_render_as_not_run_never_as_zero(doc):
    bare = copy.deepcopy(doc)
    bare["sections"]["coverage"] = {"status": "NOT_RUN", "reason": "no coverage report"}
    bare["sections"]["tests"] = {"status": "NOT_RUN", "reason": "no tests"}
    html, md = dashboard.render_html(bare), dashboard.render_markdown(bare)
    assert "NOT_RUN" in html and "no coverage report" in html
    assert "Coverage: NOT_RUN" in md and "Tests: NOT_RUN" in md


def test_svg_helpers_are_stable():
    assert svg.fmt(None) == "n/a" and svg.fmt(1234567) == "1,234,567" and svg.fmt(0.5) == "0.5" and svg.fmt(2.0) == "2"
    assert svg.nice_ticks(0, 100, 5) == [0, 20, 40, 60, 80, 100]
    placed = svg.spread_labels([(10, "a", ""), (11, "b", ""), (12, "c", "")], gap=13)
    ys = [p[0] for p in placed]
    assert all(b - a >= 13 for a, b in pairwise(ys))  # direct labels never overlap


def test_meta_omits_timestamps_unless_passed():
    assert "generated_at" not in meta("quick", None)
    assert meta("quick", "2026-09-28")["generated_at"] == "2026-09-28"
    assert (DOCS / "index.html").exists() and (ROOT / "docs" / "metrics" / "latest.md").exists()


def test_dashboard_and_markdown_state_the_limits_that_only_the_json_used_to_carry(doc):
    """Regression: the human-facing renderings dropped not_measured lists and the harness/oracle caveats."""
    html, md = dashboard.render_html(doc), dashboard.render_markdown(doc)
    for rendering in (html, md):
        assert "metrics-harness" in rendering and "same-author oracle" in rendering and "offline provider" in rendering
    for name, section in doc["sections"].items():
        for item in section.get("not_measured", []):
            assert svg.esc(item) in html and item in md, (name, item)


def test_timing_reruns_are_disclosed_in_the_rendering(doc):
    rerun = copy.deepcopy(doc)
    rerun["meta"]["timing_runs"] = [{"run": 1, "failed_timing_budgets": ["PERF-02"]}, {"run": 2, "failed_timing_budgets": []}]
    assert "LAST of 2 runs" in dashboard.render_markdown(rerun) and "run 1: PERF-02" in dashboard.render_html(rerun)
    single = copy.deepcopy(doc)
    single["meta"]["timing_runs"] = [{"run": 1, "failed_timing_budgets": []}]
    assert "LAST of" not in dashboard.render_markdown(single)  # a single run says nothing extra
