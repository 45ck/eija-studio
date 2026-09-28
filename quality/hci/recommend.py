"""Ranked, concrete recommendations derived from the metrics (never free-form opinion).

Each recommendation names the evidence numbers that triggered it, the smallest concrete change, and a
predicted effect *when a law can compute one*. Ranking is deterministic:

    sort by (severity desc, predicted_saving_s desc, id asc)

Severity: 5 critical WCAG failure, 4 serious WCAG failure / focus loss / >1 s wait, 3 moderate
WCAG failure / 400 ms - 1 s wait / WCAG 2.5.8 failure, 2 measurable law flag (Fitts, Hick, KLM,
working-memory proxy), 1 informational. Predicted savings are model outputs (see docs/hci/README.md),
not measurements of a person. Recommendations are for the visual lane's next wave; this lane edits no UI.
"""
from __future__ import annotations

from typing import Any

from . import laws
from .analysis import FITTS, KLM

IMPACT_SEVERITY = {"critical": 5, "serious": 4, "moderate": 3, "minor": 2}
AXE_FIXES = {
    "scrollable-region-focusable": "Give each scrollable <pre> (Try: audit/outbox, Evidence: raw packet, Impact: closure JSON) tabindex=\"0\", "
                                   "role=\"region\" and an aria-label so keyboard users can scroll it, or wrap the content in a <details> "
                                   "that is closed by default.",
    "color-contrast": "Raise the text/background contrast ratio to at least 4.5:1 (3:1 for large text) on the listed nodes.",
    "label": "Associate a programmatic label with each listed form control.",
    "button-name": "Give each listed button a text or aria-label name.",
    "link-name": "Give each listed link discernible text.",
    "aria-allowed-attr": "Remove ARIA attributes that are not allowed on the listed elements' roles.",
    "region": "Wrap page content in landmark regions.",
    "target-size": "Enlarge the listed targets to 24x24 CSS px (44x44 recommended) or space them per WCAG 2.5.8.",
}


def _rec(rid: str, title: str, category: str, severity: int, evidence: dict, change: str, saving_s: float = 0.0,
         laws_: tuple[str, ...] = (), targets: list[str] | None = None, effect: str = "") -> dict[str, Any]:
    return {"id": rid, "title": title, "category": category, "severity": severity, "evidence": evidence, "change": change,
            "predicted_effect": effect, "predicted_saving_s": round(saving_s, 3), "laws": list(laws_), "targets": sorted(targets or [])}


def _axe(m: dict) -> list[dict]:
    out = []
    for v in m["wcag"]["violations_by_rule"]:
        out.append(_rec(
            f"a11y-{v['id']}", f"WCAG: {v['help']} ({v['id']})", "wcag", IMPACT_SEVERITY.get(v["impact"], 3),
            {"impact": v["impact"], "nodes": v["node_count"], "views": v["views"], "tags": v["tags"], "reference": v["help_url"]},
            AXE_FIXES.get(v["id"], v["help"]), laws_=("WCAG 2.2 AA",), targets=v["nodes"]))
    return out


def _target_size(m: dict) -> list[dict]:
    fails = [x for x in m["wcag"]["target_size_2_5_8"]["undersized_or_failing"] if x["status"] == "fail"]
    marginal = [x for x in m["wcag"]["target_size_2_5_8"]["undersized_or_failing"]
                if x["status"] != "fail" and min(x["effective_px"]) < 44]
    out = []
    if fails:
        out.append(_rec("target-size-fail", f"{len(fails)} pointer target(s) fail WCAG 2.5.8", "wcag", 3,
                        {"targets": [f"{x['selector']} {x['effective_px'][0]}x{x['effective_px'][1]}px" for x in fails]},
                        "Raise each listed target to at least 24x24 CSS px (min-height/min-width or padding).",
                        laws_=("WCAG 2.5.8", "Fitts"), targets=[x["selector"] for x in fails]))
    if marginal:
        out.append(_rec("target-size-marginal", f"{len(marginal)} target(s) pass 2.5.8 but are under 44 px", "fitts", 2,
                        {"targets": [f"{x['name'][:40]} eff {x['effective_px'][0]}x{x['effective_px'][1]} raw {x['raw_px'][0]}x{x['raw_px'][1]}px"
                                     for x in marginal]},
                        "Give the checkbox label (the real click area) min-height 44 px and enlarge the raw 18 px input box or its hit padding, "
                        "so the control meets the 44 px guideline (WCAG 2.5.5 AAA) as well as the 24 px minimum.",
                        laws_=("WCAG 2.5.8", "Fitts"), targets=[x["selector"] for x in marginal],
                        effect="removes the smallest-W pointing target from the journey"))
    return out


def _fitts(m: dict) -> list[dict]:
    moves = [x for x in m["fitts"]["targets"] if x["id_bits"] is not None]
    hard = [x for x in moves if "ID>4" in x["flags"]]
    out = []
    if hard:
        saving = 0.0
        for x in hard:
            w2 = max(x["w_px"], 44.0)
            new_id = laws.shannon_id(x["distance_px"] * 0.5, w2)
            saving += x["predicted_mt_s"] - laws.fitts_time(new_id, FITTS)
        out.append(_rec(
            "fitts-id-over-4", f"{len(hard)} pointer move(s) exceed 4 bits", "fitts", 2,
            {"moves": [f"{x['step']}: D={x['distance_px']} px, W={x['w_px']} px, ID={x['id_bits']} bits, MT={x['predicted_mt_s']} s" for x in hard]},
            "Place the next action next to the previous target (primary actions currently sit at the far right edge of section headings while "
            "the preceding target is on the left), i.e. halve D, and give wide-but-short rows min-height 44 px.",
            saving, ("Fitts", "MacKenzie & Buxton 1992"), [x["selector"] for x in hard],
            f"model: halving D and W>=44 px saves {saving:.2f} s of pointing time across the flagged moves"))
    total = m["fitts"]["summary"]
    if total["scrolls_needed"]:
        out.append(_rec(
            "layout-hero-scroll", f"{total['scrolls_needed']} journey click(s) needed a scroll first at 1440x900", "fitts", 2,
            {"steps": [x["step"] for x in m["fitts"]["targets"] if x["scrolled_before"]], "viewport": m["environment"]["viewport"]},
            "Collapse the marketing hero/boundary banner once a case is open (or make the tab bar and primary action sticky) so the "
            "journey's targets stay above the fold.", saving_s=total["scrolls_needed"] * 0.5, laws_=("Fitts", "KLM"),
            effect="each avoided scroll removes one unmodelled operator (the standard KLM total excludes scrolling)"))
    return out


def _hick(m: dict) -> list[dict]:
    h = m["hick_hyman"]
    out = []
    flagged = [x for x in h["decisions"] if x["over_7"]]
    if flagged:
        out.append(_rec("hick-choice-over-7", f"{len(flagged)} choice group(s) exceed 7 alternatives", "hick", 2,
                        {"groups": [f"{x['step']}: n={x['choices']}" for x in flagged]},
                        "Group or progressively disclose the alternatives (<= 7 visible per group).", laws_=("Hick-Hyman",)))
    over_screen = [x for x in h["decisions"] if x["screen_over_7"]]
    if over_screen:
        extra = sum(x["screen_predicted_s"] - x["predicted_s"] for x in over_screen)
        out.append(_rec("hick-screen-load", f"{len(over_screen)}/{len(h['decisions'])} decision points have more than 7 visible controls on screen",
                        "hick", 1,
                        {"max_screen_controls": max(x["screen_controls"] for x in over_screen), "max_group_choices": h["summary"]["max_choices"],
                         "note": "upper bound; the choice groups themselves are all <= 7"},
                        "Keep one visually dominant primary action per view and demote the rest (secondary/text buttons), which lowers effective "
                        "uncertainty for first-time users (Hyman).", extra, ("Hick-Hyman",),
                        effect=f"if a novice searched the whole screen instead of the choice group: +{extra:.2f} s (upper bound, model)"))
    return out


def _klm(m: dict) -> list[dict]:
    ops = m["klm"]["pointer_journey"]["operators"]
    counts = m["klm"]["pointer_journey"]["operator_counts"]
    total = m["klm"]["pointer_journey"]["total_s"]
    out = []
    # what-if: move between answer fields with Tab instead of point-click-rehome
    answer = [o for o in ops if o["step"].startswith("answer-")]
    later = [o for o in answer if not o["step"].endswith("authority")]
    if later:
        cost = laws.klm_time([o["op"] for o in later if o["op"] in ("P", "B", "H")], KLM)
        keep_k = sum(1 for o in later if o["op"] == "K")
        tabs = 2
        saving = cost - tabs * KLM.K
        if saving > 0:
            out.append(_rec(
                "klm-answer-fields-tab", "Review answers: move between fields with Tab instead of point-click and re-homing", "klm", 2,
                {"operators_replaced": {"P": sum(o["op"] == "P" for o in later), "B": sum(o["op"] == "B" for o in later),
                                         "H": sum(o["op"] == "H" for o in later)}, "typed_keystrokes_unchanged": keep_k,
                 "keyboard_only_journey_tab_presses": m["keyboard"]["tab_presses_by_step"]},
                "Focus the first question when Evidence opens after verification and make Enter in a field move to the next one "
                "(or submit on the last), so the three answers are typed without leaving the keyboard.", saving, ("KLM",),
                targets=["#q-assignment", "#q-reject_entry"],
                effect=f"model: {saving:.1f} s of {total:.1f} s expert time ({100 * saving / total:.0f}%)"))
    if counts["M"]:
        out.append(_rec("klm-mental-load", f"{counts['M']} mental operators = {counts['M'] * KLM.M:.1f} s ({100 * counts['M'] * KLM.M / total:.0f}% of expert time)",
                        "klm", 1, {"M_by_step": sorted({o["step"] for o in ops if o["op"] == "M"})},
                        "Each M is a reading or decision moment; the largest are the interpretation choice and the three review answers. "
                        "Keep their wording short and put the decision-relevant text next to the control (no cross-tab lookup).",
                        laws_=("KLM",), effect="informational: M is the irreducible cognitive floor of the journey"))
    kb = m["klm"]["keyboard_only_journey"]
    out.append(_rec("klm-keyboard-vs-pointer", f"Keyboard-only journey costs {kb['total_s']:.1f} s vs {total:.1f} s with the pointer (model)", "klm", 1,
                    {"keyboard_K": kb["operator_counts"]["K"], "pointer_total_s": total, "keyboard_total_s": kb["total_s"]},
                    "Not a defect by itself; use it to decide where shortcuts (tab shortcuts, access keys) pay off.", laws_=("KLM",)))
    return out


def _keyboard(m: dict) -> list[dict]:
    k = m["keyboard"]
    out = []
    if k["activations_that_lost_focus"]:
        wasted = k["tab_presses_spent_after_focus_loss"] * KLM.K
        out.append(_rec(
            "focus-lost-after-render", f"{len(k['activations_that_lost_focus'])}/{k['activations']} keyboard activations dropped focus to <body>", "keyboard", 4,
            {"steps": k["activations_that_lost_focus"], "tab_presses_after_loss": k["tab_presses_spent_after_focus_loss"],
             "max_tab_presses_for_one_target": k["max_tab_presses_for_one_target"]},
            "render() rebuilds whole regions with replaceChildren(), destroying the focused button. Update disabled/text in place, or re-focus "
            "the same control (by data-action / id) after render, and move focus deliberately to the new content on tab changes (WCAG 2.4.3 Focus Order, 3.2.2).",
            wasted, ("WCAG 2.4.3", "KLM"), effect=f"model: up to {wasted:.1f} s of Tab keystrokes spent re-finding position"))
    if k["stops_without_visible_focus_indicator"]:
        out.append(_rec("focus-indicator-missing", f"{len(k['stops_without_visible_focus_indicator'])} focus stop(s) without a visible indicator", "keyboard", 4,
                        {"stops": k["stops_without_visible_focus_indicator"]}, "Give every focusable element a :focus-visible outline (WCAG 2.4.7, 2.4.11).",
                        laws_=("WCAG 2.4.7",), targets=k["stops_without_visible_focus_indicator"]))
    if k["focus_order_regressions"]:
        out.append(_rec("focus-order-regression", f"{len(k['focus_order_regressions'])} Tab step(s) move upward on screen", "keyboard", 3,
                        {"examples": [f"{x['from']} -> {x['to']}" for x in k["focus_order_regressions"][:5]]},
                        "Align DOM order with visual order (WCAG 2.4.3).", laws_=("WCAG 2.4.3",)))
    if k["max_tab_presses_for_one_target"] >= 10:
        out.append(_rec("tab-cost-high", f"Reaching one control took {k['max_tab_presses_for_one_target']} Tab presses", "keyboard", 2,
                        {"tab_presses_by_step": k["tab_presses_by_step"]},
                        "Make the work-area tabs a single tab stop with arrow-key navigation (WAI-ARIA tabs pattern: role=tablist/tab, aria-selected, roving tabindex) "
                        "and keep the sidebar after main content in DOM order or behind the skip link.",
                        laws_=("KLM", "WCAG 2.1.1")))
    return out


def _state_only(m: dict) -> list[dict]:
    els = m["wcag"]["supplementary_state_only_visual"]["elements"]
    if not els:
        return []
    return [_rec("state-only-visual", f"{len(els)} control(s) convey their active state only through CSS", "wcag", 3,
                 {"elements": els[:8]}, "Expose the state programmatically: aria-current=\"page\" or role=tab + aria-selected on the work-area tabs and "
                 "aria-current on the selected case in the sidebar (WCAG 1.3.1, 4.1.2).", laws_=("WCAG 4.1.2",),
                 targets=[e.split(" (")[0] for e in els])]


def _doherty(m: dict) -> list[dict]:
    d = m["measured"]["doherty"]
    slow = [x for x in d["steps"] if x["median_over_400ms"]]
    tail = [x for x in d["steps"] if x["over_400ms"] and not x["median_over_400ms"]]
    out = []
    if slow:
        worst = max(x["settled_p50_ms"] for x in slow)
        out.append(_rec("doherty-completion", f"{len(slow)} interaction(s) usually take longer than 400 ms to finish", "doherty", 4 if worst > 1000 else 3,
                        {"first_feedback_p95_ms": d["first_feedback_p95_ms"],
                         "slow_steps": [f"{x['step']}: p50 {x['settled_p50_ms']} / p95 {x['settled_p95_ms']} ms" for x in slow]},
                        "First feedback is immediate (the busy notice), so the 400 ms acknowledgement is met, but completion is not. For the slow steps "
                        "show a determinate progress message (for verification: matrix cells done / total), keep the previous result visible until the new one "
                        "lands, and profile the server commit path (durable SQLite commit per action).",
                        laws_=("Doherty threshold",), targets=[x["step"] for x in slow],
                        effect="measured on this machine; wall-clock, sensitive to load from other processes"))
    if tail:
        out.append(_rec("doherty-tail", f"{len(tail)} interaction(s) occasionally exceed 400 ms (median under)", "doherty", 2,
                        {"steps": [f"{x['step']}: p50 {x['settled_p50_ms']} / p95 {x['settled_p95_ms']} ms ({x['samples']} samples)" for x in tail]},
                        "Tail latency on the durable commit path (first commit after start, disk contention). Re-measure with more --repeats before acting; "
                        "with few samples p95 is the maximum.", laws_=("Doherty threshold",), targets=[x["step"] for x in tail],
                        effect="measured; may be machine noise"))
    return out


def _console(m: dict) -> list[dict]:
    fails = [x for x in m["runtime_errors"]["http_error_responses"] if x["status"] == 404]
    out = []
    if fails:
        out.append(_rec("http-404", f"{len(fails)} 404 response(s) during the journey", "hygiene", 1,
                        {"requests": [f"{x['method']} {x['path']} (during {x['step']})" for x in fails]},
                        "Serve the missing asset (for /favicon.ico add <link rel=\"icon\" href=\"data:,\"> or a real icon) to keep the console clean.",
                        targets=[x["path"] for x in fails]))
    if m["runtime_errors"]["javascript_exceptions"]:
        out.append(_rec("js-exceptions", "Uncaught JavaScript exceptions during the journey", "hygiene", 4,
                        {"errors": m["runtime_errors"]["javascript_exceptions"][:5]}, "Fix the exceptions before anything else."))
    return out


def _memory(m: dict) -> list[dict]:
    wm = m["working_memory"]
    over = [x for x in wm["views"] if x["over_miller_9"]]
    if not over:
        return []
    worst = max(over, key=lambda x: x["chunks_viewport"])
    return [_rec("working-memory-proxy", f"{len(over)}/{len(wm['views'])} views show more than 9 chunks at once (proxy)", "working-memory", 2,
                 {"worst_view": worst["view"], "worst_chunks": worst["chunks_viewport"], "label": wm["label"],
                  "views": [f"{x['view']}: {x['chunks_viewport']}" for x in over]},
                 "Move persistent chrome (hero copy, boundary banner, footer disclaimer, sidebar note) out of the working area once a case is open, and keep "
                 "raw JSON blocks collapsed by default, so the work area competes for fewer chunks.", laws_=("Miller 1956", "Cowan 2001"),
                 effect="heuristic only: not a measurement of anyone's memory")]


def recommend(m: dict) -> list[dict]:
    """All recommendations, deterministically ranked (rank field added, 1 = do first)."""
    recs = (_axe(m) + _target_size(m) + _fitts(m) + _hick(m) + _klm(m) + _keyboard(m) + _state_only(m)
            + _doherty(m) + _console(m) + _memory(m))
    recs.sort(key=lambda x: (-x["severity"], -x["predicted_saving_s"], x["id"]))
    for i, x in enumerate(recs, 1):
        x["rank"] = i
    return recs
