"""Live browser budgets (marker `hci`, opt-in). Real Chrome, real `eija serve`, offline synthetic data.

NOT_RUN (skip) when Chrome/Playwright is unavailable. A budget above its target but within its ratchet
is reported as xfail (a documented gap), so a shortfall is never shown as a pass.
"""
# ruff: noqa: PLC0415 - playwright belongs to the optional `hci` extra; import it only inside tests that run after the NOT_RUN check
from urllib.parse import quote

import pytest

from quality.hci import analysis, budgets, journey

pytestmark = pytest.mark.hci

BUDGET_DEFS = budgets.load()


@pytest.mark.parametrize("budget", BUDGET_DEFS, ids=[b["id"] for b in BUDGET_DEFS])
def test_budget(hci_report, budget):
    result = next(b for b in hci_report["report"]["budgets"] if b["id"] == budget["id"])
    assert result["status"] != "NOT_RUN", f"{budget['id']} could not be measured"
    assert result["status"] != "FAIL", (
        f"REGRESSION {budget['id']}: {result['value']} {result['unit']} exceeds the ratchet {result['limit']} (target {result['target']})")
    if result["status"] == "GAP":
        pytest.xfail(f"known gap: {result['value']} {result['unit']} vs target {result['target']} (ratchet {result['limit']}); see docs/hci/REPORT.md")


def test_journey_completed_on_both_modalities(hci_report):
    expected = ["create-case", "ask-interpretations", "select-meaning", "reset-preview", "submit-teacher", "recommend-teacher",
               "approve-registrar", "denied-recommend", "run-verification", "acknowledge", "approve-exact", "apply-baseline"]
    for run in (hci_report["raw"]["pointer_passes"][0], hci_report["raw"]["keyboard_pass"]):
        done = [s["id"] for s in run["steps"]]
        assert all(step in done for step in expected)


def test_axe_ran_with_wcag22_tags_on_every_checkpoint(hci_report):
    views = hci_report["raw"]["pointer_passes"][0]["views"]
    assert {"start", "change-options", "try-draft", "evidence-verified", "applied"} <= set(views)
    assert all(v["axe"]["axe_core"] for v in views.values())
    assert hci_report["report"]["environment"]["axe_core"].startswith("4.")


def test_structural_metrics_repeat_exactly_across_journeys(hci_report):
    """Reproducibility: the geometry the laws consume must not depend on the run (timings do)."""
    first, *rest = hci_report["raw"]["pointer_passes"]
    for other in rest:
        assert [t["step"] for t in other["pointer_targets"]] == [t["step"] for t in first["pointer_targets"]]
        for a, b in zip(first["pointer_targets"], other["pointer_targets"], strict=True):
            assert a["effective"] == pytest.approx(b["effective"], abs=1.0), a["step"]
        assert [o["op"] for o in other["operators"]] == [o["op"] for o in first["operators"]]


def test_no_javascript_exceptions_and_denial_is_a_409_not_a_silent_success(hci_report):
    errors = hci_report["report"]["runtime_errors"]
    assert errors["javascript_exceptions"] == []
    denied = [e for e in errors["http_error_responses"] if e["step"] == "denied-recommend"]
    assert denied and all(e["status"] == 409 for e in denied)  # the kernel refused the unassigned teacher


# --- negative control: the instrument must flag defects we plant, not just report the Studio ---------
PLANTED = (
    "<!doctype html><html lang='en'><head><title>planted</title></head><body>"
    "<button id='tiny' style='width:10px;height:10px;padding:0;border:0'>x</button>"
    "<button id='tiny2' style='position:absolute;left:14px;top:0;width:10px;height:10px;padding:0;border:0'>y</button>"
    "<p style='color:#bbb;background:#fff'>low contrast text</p>"
    "<input id='nolabel' type='text'></body></html>"
)


def test_planted_defects_are_flagged_by_probe_geometry_and_axe():
    from playwright.sync_api import sync_playwright

    ok, detail = journey.prerequisites()
    if not ok:
        pytest.skip("NOT_RUN: " + detail)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        try:
            context, page = journey.new_page(browser)
            page.goto("data:text/html," + quote(PLANTED))
            controls = page.evaluate("() => window.__hci.controls()")
            statuses = {c["selector"]: s for c, s in analysis.target_statuses(controls)}
            rules = {v["id"] for v in journey.run_axe(page)["violations"]}
            context.close()
        finally:
            browser.close()
    assert statuses["#tiny"] == "fail" and statuses["#tiny2"] == "fail"  # 10 px targets 14 px apart
    assert "color-contrast" in rules and "label" in rules
