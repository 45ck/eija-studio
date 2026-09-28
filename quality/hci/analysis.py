"""Trace -> metrics. Applies the HCI laws in `laws.py` / `wcag.py` to what `journey.py` recorded.

Pure and deterministic: the same trace always yields the same metrics. Sections that come from
wall-clock measurements are keyed under `measured` and are excluded from geometry-only comparisons.

Evidence kinds, kept apart on purpose: geometry, axe results and focus behaviour are MEASURED on the
running Studio; Fitts / Hick / KLM times are PREDICTIONS from population-average models applied to
that geometry; Doherty timings are MEASURED wall-clock and vary run to run.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from . import laws
from .journey import journey
from .wcag import Box, target_size_status

FITTS = laws.DEFAULT_FITTS
HICK = laws.DEFAULT_HICK
KLM = laws.DEFAULT_KLM
RESPONSE_NOTE = "settled = last DOM mutation before quiescence, from the click event; excludes OS/browser input latency"
STATUS_ORDER = {"pass": 0, "pass-spacing": 1, "fail": 2}


def r(value: float | None, digits: int = 3) -> float | None:
    return None if value is None else round(value, digits)


# --- Fitts ------------------------------------------------------------------------------------
def _nearest_edge_id(t: dict, box: dict, width: float) -> float:
    """Sensitivity variant: ID with D measured to the nearest edge of the target instead of its centre."""
    distance = laws.nearest_edge_distance(tuple(t["from"]), (box["x"], box["y"], box["w"], box["h"]))
    return laws.shannon_id(distance, width)


def _fitts_row(t: dict, target_status: dict[str, str]) -> dict[str, Any]:
    box = t["effective"]
    width = laws.smaller_of(box["w"], box["h"])
    row: dict[str, Any] = {
        "step": t["step"],
        "target": t["name"],
        "selector": t["selector"],
        "w_px": r(width, 1),
        "raw_w_px": r(laws.smaller_of(t["raw"]["w"], t["raw"]["h"]), 1),
        "via_label": t["via_label"],
        "scrolled_before": t["scrolled"],
        "wcag_2_5_8": target_status.get(t["selector"], "not-audited"),
    }
    if t["from"] is None:
        row.update(
            distance_px=None,
            id_bits=None,
            predicted_mt_s=None,
            flags=[],
            id_bits_nearest_edge=None,
            note="first pointer target: no preceding position",
        )
        return row
    distance = math.dist(t["from"], t["to"])
    id_bits = laws.shannon_id(distance, width)
    flags = (["ID>4"] if id_bits > laws.MAX_ID_BITS else []) + (["W<24"] if width < laws.MIN_TARGET_PX else [])
    row.update(
        distance_px=r(distance, 1),
        id_bits=r(id_bits, 3),
        predicted_mt_s=r(laws.fitts_time(id_bits, FITTS), 3),
        flags=flags,
        id_bits_nearest_edge=r(_nearest_edge_id(t, box, width), 3),
    )
    return row


def _mean(values: list[float]) -> float | None:
    return r(sum(values) / len(values), 3) if values else None


def _fitts_summary(rows: list[dict]) -> dict[str, Any]:
    moves = [x for x in rows if x["id_bits"] is not None]
    hardest = max(moves, key=lambda x: x["id_bits"], default=None)
    return {
        "pointer_targets": len(rows),
        "moves_with_distance": len(moves),
        "mean_id_bits": _mean([x["id_bits"] for x in moves]),
        "max_id_bits": hardest and hardest["id_bits"],
        "max_id_step": hardest and hardest["step"],
        **_fitts_flag_counts(rows),
        "predicted_pointing_time_s": r(sum(x["predicted_mt_s"] for x in moves), 3),
        "total_distance_px": r(sum(x["distance_px"] for x in moves), 1),
    }


def _fitts_flag_counts(rows: list[dict]) -> dict[str, Any]:
    return {
        "moves_id_over_4": sum("ID>4" in x["flags"] for x in rows),
        "moves_id_over_4_nearest_edge": sum((x.get("id_bits_nearest_edge") or 0) > laws.MAX_ID_BITS for x in rows),
        "landing_convention_note": "primary D uses the centre of the effective box, which overstates D for wide targets; "
        "moves_id_over_4_nearest_edge recomputes D to the nearest edge, so the flag count is a range",
        "targets_w_under_24": sum("W<24" in x["flags"] for x in rows),
        "scrolls_needed": sum(1 for x in rows if x["scrolled_before"]),
    }


def fitts(pass0: dict, target_status: dict[str, str]) -> dict:
    rows = [_fitts_row(t, target_status) for t in pass0["pointer_targets"]]
    return {
        "model": {
            "form": "MT = a + b*log2(D/W + 1), W = min(width, height)",
            "a_s": FITTS.a,
            "b_s_per_bit": FITTS.b,
            "citation": FITTS.citation,
        },
        "targets": rows,
        "summary": _fitts_summary(rows),
    }


# --- Hick-Hyman -------------------------------------------------------------------------------
def _hick_row(step: dict) -> dict[str, Any]:
    d = step["decision"]
    n, screen = d["n_choices"], d["n_screen"]
    return {
        "step": step["id"],
        "decision": d["name"],
        "choices": n,
        "bits": r(laws.hick_bits(n), 3),
        "predicted_s": r(laws.hick_time(n, HICK), 3),
        "over_7": n > laws.MAX_CHOICES,
        "screen_controls": screen,
        "screen_over_7": screen > laws.MAX_CHOICES,
        "screen_predicted_s": r(laws.hick_time(screen, HICK), 3),
    }


def hick(pass0: dict) -> dict:
    rows = [_hick_row(s) for s in pass0["steps"] if s.get("decision")]
    return {
        "model": {
            "form": "T = b*log2(n + 1)",
            "b_s_per_bit": HICK.b,
            "citation": HICK.citation,
            "note": "choices = enabled alternatives in the declared choice group; screen_controls = every enabled control in the "
            "viewport (an upper bound: an expert who knows the target does not search them all)",
        },
        "decisions": rows,
        "summary": {
            "decision_points": len(rows),
            "max_choices": max((x["choices"] for x in rows), default=0),
            "choice_points_over_7": sum(x["over_7"] for x in rows),
            "screen_points_over_7": sum(x["screen_over_7"] for x in rows),
            "predicted_choice_time_s": r(sum(x["predicted_s"] for x in rows), 3),
        },
    }


# --- KLM ----------------------------------------------------------------------------------------
def fitts_moves(targets: list[dict]) -> list[float | None]:
    """Predicted MT per pointer target in order (None for the first, which has no preceding position)."""
    out: list[float | None] = []
    for t in targets:
        if t["from"] is None:
            out.append(None)
            continue
        width = laws.smaller_of(t["effective"]["w"], t["effective"]["h"])
        out.append(laws.fitts_time(laws.shannon_id(math.dist(t["from"], t["to"]), width), FITTS))
    return out


def _fitts_refined_total(operators: list[dict], targets: list[dict]) -> float:
    """KLM total with each modelled `P` replaced by its Fitts MT (the first target keeps the standard P)."""
    moves = iter(fitts_moves(targets))
    total = 0.0
    for o in operators:
        if o["op"] == "P" and o.get("fitts"):
            mt = next(moves)
            total += KLM.P if mt is None else mt
        else:
            total += laws.klm_time([o["op"]], KLM)
    return total


def _per_step_seconds(operators: list[dict]) -> dict[str, float]:
    per_step: dict[str, float] = defaultdict(float)
    for o in operators:
        per_step[o["step"]] += laws.klm_time([o["op"]], KLM)
    return {k: round(v, 3) for k, v in per_step.items()}


def _klm_block(operators: list[dict], targets: list[dict] | None) -> dict:
    symbols = [o["op"] for o in operators]
    refined = None if targets is None else r(_fitts_refined_total(operators, targets), 3)
    return {
        "operator_counts": laws.count_operators(symbols),
        "total_s": r(laws.klm_time(symbols, KLM), 3),
        "fitts_refined_total_s": refined,
        "per_step_s": _per_step_seconds(operators),
        "operators": [{k: v for k, v in o.items() if k != "fitts"} | {"seconds": getattr(KLM, o["op"])} for o in operators],
    }


def klm(pass0: dict, keyboard_pass: dict) -> dict:
    mouse = _klm_block(pass0["operators"], pass0["pointer_targets"])
    kb = _klm_block(keyboard_pass["operators"], None)
    return {
        "times_s": {"K": KLM.K, "P": KLM.P, "B": KLM.B, "H": KLM.H, "M": KLM.M},
        "citation": "Card, Moran & Newell 1980 (CACM 23(7)); K = average non-secretary typist (~40 wpm)",
        "placement_rules": "M is placed once per deliberate decision or reading moment (annotated per step in journey.py); H is derived "
        "from every mouse<->keyboard switch; a click is P + B + B; Shift counts as its own K; select lists model open "
        "and choose as two P+B+B; scrolling and system response R are NOT in the standard total",
        "pointer_journey": mouse,
        "keyboard_only_journey": kb,
        "expert_time_pointer_s": mouse["total_s"],
        "expert_time_keyboard_only_s": kb["total_s"],
    }


# --- Doherty ------------------------------------------------------------------------------------
def _collect_interactions(pointer_passes: list[dict]) -> tuple[dict[str, dict[str, list[float]]], set[str]]:
    """Per step, the first-feedback and settled samples over all repeats; steps whose control changes no DOM."""
    per_step: dict[str, dict[str, list[float]]] = defaultdict(lambda: {"first": [], "settled": []})
    native: set[str] = set()
    for p in pointer_passes:
        for s in p["steps"]:
            i = s.get("interaction")
            if not i:
                continue
            if i["mutation_batches"] == 0:
                native.add(s["id"])
                continue
            per_step[s["id"]]["first"].append(i["first_feedback_ms"])
            per_step[s["id"]]["settled"].append(i["settled_ms"])
    return per_step, native


def _spread(values: list[float]) -> dict[str, float | None]:
    """p25 / median / p75 / p95 / max of one sample set (nearest rank)."""
    quartiles = laws.iqr(values)
    low, mid, high = quartiles if quartiles else (None, None, None)
    return {
        "p25_ms": r(low, 1),
        "p50_ms": r(mid, 1),
        "p75_ms": r(high, 1),
        "p95_ms": r(laws.percentile(values, 95), 1),
        "max_ms": r(max(values), 1) if values else None,
    }


def _doherty_step(step_id: str, v: dict[str, list[float]]) -> dict[str, Any]:
    settled, first = _spread(v["settled"]), _spread(v["first"])
    return {
        "step": step_id,
        "samples": len(v["settled"]),
        "first_feedback_p50_ms": first["p50_ms"],
        "first_feedback_p95_ms": first["p95_ms"],
        "settled_p25_ms": settled["p25_ms"],
        "settled_p50_ms": settled["p50_ms"],
        "settled_p75_ms": settled["p75_ms"],
        "settled_p95_ms": settled["p95_ms"],
        "over_400ms": laws.percentile(v["settled"], 95) > laws.DOHERTY_MS,
        "median_over_400ms": laws.percentile(v["settled"], 50) > laws.DOHERTY_MS,
    }


def _flatten(per_step: dict[str, dict[str, list[float]]], kind: str) -> list[float]:
    return [x for v in per_step.values() for x in v[kind]]


def _keyboard_settled(keyboard_pass: dict) -> list[float]:
    return [
        s["interaction"]["settled_ms"]
        for s in keyboard_pass["steps"]
        if s.get("interaction") and s["interaction"]["mutation_batches"] > 0
    ]


def doherty(pointer_passes: list[dict], keyboard_pass: dict) -> dict:
    """MEASURED wall-clock click -> DOM response, pooled over repeats. Medians and IQR, not single runs."""
    per_step, native = _collect_interactions(pointer_passes)
    steps = [_doherty_step(s["id"], per_step[s["id"]]) for s in pointer_passes[0]["steps"] if s["id"] in per_step]
    firsts, settled = _spread(_flatten(per_step, "first")), _spread(_flatten(per_step, "settled"))
    keyboard = _spread(_keyboard_settled(keyboard_pass))
    return {
        "threshold_ms": laws.DOHERTY_MS,
        "note": RESPONSE_NOTE,
        "method": "nearest-rank percentiles over all repeats; medians and interquartile range are the headline, p95 is the maximum with few samples",
        "citation": "Doherty & Thadani 1982 (IBM Systems Journal 21(1)); ~400 ms",
        "interactions_measured": len(_flatten(per_step, "settled")),
        "native_control_interactions_excluded": sorted(native),
        "first_feedback_p50_ms": firsts["p50_ms"],
        "first_feedback_p95_ms": firsts["p95_ms"],
        "settled_p25_ms": settled["p25_ms"],
        "settled_p50_ms": settled["p50_ms"],
        "settled_p75_ms": settled["p75_ms"],
        "settled_p95_ms": settled["p95_ms"],
        "settled_max_ms": settled["max_ms"],
        "keyboard_settled_p50_ms": keyboard["p50_ms"],
        "keyboard_settled_p95_ms": keyboard["p95_ms"],
        "journey_wait_p50_sum_s": r(sum(x["settled_p50_ms"] for x in steps) / 1000.0, 3),
        "steps": steps,
        "steps_over_400ms": [x["step"] for x in steps if x["over_400ms"]],
        "steps_median_over_400ms": [x["step"] for x in steps if x["median_over_400ms"]],
    }


# --- WCAG ---------------------------------------------------------------------------------------
def target_statuses(controls: list[dict]) -> list[tuple[dict, str]]:
    enabled = [c for c in controls if not c["disabled"]]
    boxes = [Box(c["x"], c["y"], c["w"], c["h"]) for c in enabled]
    return [(c, target_size_status(i, boxes)) for i, c in enumerate(enabled)]


def _axe_rules(views: dict[str, dict]) -> tuple[list[dict], dict[str, dict]]:
    """Violations aggregated by rule across views (unique nodes) and axe `incomplete` results by rule."""
    rules: dict[str, dict] = {}
    incomplete: dict[str, dict] = {}
    for view, data in sorted(views.items()):
        for v in data["axe"]["violations"]:
            rule = rules.setdefault(
                v["id"],
                {"id": v["id"], "impact": v["impact"], "help": v["help"], "help_url": v["help_url"], "tags": v["tags"], "nodes": set(), "views": set()},
            )
            rule["views"].add(view)
            rule["nodes"].update(n["target"] for n in v["nodes"])
        for v in data["axe"]["incomplete"]:
            incomplete.setdefault(v["id"], {"id": v["id"], "impact": v["impact"], "views": set()})["views"].add(view)
    by_rule = [
        {
            **{k: x[k] for k in ("id", "impact", "help", "help_url", "tags")},
            "node_count": len(x["nodes"]),
            "nodes": sorted(x["nodes"]),
            "views": sorted(x["views"]),
        }
        for x in sorted(rules.values(), key=lambda x: x["id"])
    ]
    return by_rule, incomplete


def _worst_target_status(views: dict[str, dict]) -> dict[str, tuple[str, dict]]:
    """Own WCAG 2.5.8 audit across every audited view: the worst status per control selector."""
    worst: dict[str, tuple[str, dict]] = {}
    for _, data in sorted(views.items()):
        for c, status in target_statuses(data["controls"]):
            known = worst.get(c["selector"])
            if known is None or STATUS_ORDER[status] > STATUS_ORDER[known[0]]:
                worst[c["selector"]] = (status, c)
    return worst


def _undersized_rows(worst: dict[str, tuple[str, dict]]) -> list[dict]:
    rows = [
        {
            "selector": k,
            "name": c["name"],
            "status": s,
            "effective_px": [r(c["w"], 1), r(c["h"], 1)],
            "raw_px": [r(c["raw_w"], 1), r(c["raw_h"], 1)],
            "via_label": c["via_label"],
        }
        for k, (s, c) in worst.items()
        if min(c["raw_w"], c["raw_h"]) < laws.MIN_TARGET_PX or s != "pass"
    ]
    return sorted(rows, key=lambda x: x["selector"])


def _responsive_rows(responsive: dict) -> dict[str, dict]:
    out = {}
    for size, tabs in sorted(responsive.items()):
        out[size] = {
            "horizontal_overflow_tabs": sorted(t for t, v in tabs.items() if v["scroll_width"] > v["inner_width"]),
            "targets_fail_2_5_8": sum(1 for v in tabs.values() for _, s in target_statuses(v["controls"]) if s == "fail"),
        }
    return out


def _state_only_elements(views: dict[str, dict]) -> list[str]:
    return sorted({item.split(" (")[0] for d in views.values() for item in d.get("visual_state_only", [])})


def _impact_counts(by_rule: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for x in by_rule:
        counts[x["impact"] or "unknown"] += 1
    return counts


def _wcag_summary(by_rule: list[dict], tally: dict[str, int], responsive: dict[str, dict]) -> dict[str, int]:
    by_impact = _impact_counts(by_rule)
    return {
        "rules": len(by_rule),
        "nodes": sum(x["node_count"] for x in by_rule),
        "target_size_failures": tally.get("fail", 0),
        **{impact: by_impact.get(impact, 0) for impact in ("critical", "serious", "moderate", "minor")},
        "reflow_overflow_views": sum(len(v["horizontal_overflow_tabs"]) for v in responsive.values()),
    }


def wcag(pass0: dict) -> tuple[dict, dict[str, str]]:
    views = pass0["views"]
    by_rule, incomplete = _axe_rules(views)
    worst = _worst_target_status(views)
    statuses = {k: v[0] for k, v in worst.items()}
    tally: dict[str, int] = defaultdict(int)
    for s in statuses.values():
        tally[s] += 1
    responsive = _responsive_rows(pass0.get("responsive") or {})
    return {
        "engine": "axe-core (tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa)",
        "summary": _wcag_summary(by_rule, tally, responsive),
        "violations_by_rule": by_rule,
        "violation_rules_by_impact": dict(sorted(_impact_counts(by_rule).items())),
        "needs_review_rules": [
            {"id": x["id"], "impact": x["impact"], "views": sorted(x["views"])} for x in sorted(incomplete.values(), key=lambda x: x["id"])
        ],
        "views_audited": sorted(views),
        "target_size_2_5_8": {
            "controls_audited": len(statuses),
            "status_counts": dict(sorted(tally.items())),
            "undersized_or_failing": _undersized_rows(worst),
            "exceptions_not_evaluated": ["inline", "user-agent controlled", "equivalent control", "essential"],
        },
        "reflow_and_targets_by_viewport": responsive,
        "supplementary_state_only_visual": {
            "check": "interactive element styled active/selected without aria-current/selected/pressed/checked/expanded",
            "elements": _state_only_elements(views),
            "authority": "heuristic; not an axe rule",
        },
    }, statuses


# --- keyboard ----------------------------------------------------------------------------------
def _moves_up(previous: dict | None, current: dict | None) -> bool:
    """Heuristic for a focus jump against reading order (WCAG 2.4.3). Not counted: moves of <= 8 px (row
    alignment noise), a jump to the top of the page (Tab wrapped around past the last element), and a jump
    to a column further right (grid cards read column by column in DOM order)."""
    if not previous or not current:
        return False
    if current["y"] <= 1 or current["x"] - previous["x"] >= 100:
        return False
    return current["y"] < previous["y"] - 8


def _scan_focus(steps: list[dict]) -> tuple[dict[str, dict], list[dict]]:
    """Distinct focus stops (first sighting per selector) and upward focus moves, over the whole traversal."""
    stops: dict[str, dict] = {}
    regressions: list[dict] = []
    for s in steps:
        last = None
        for stop in s.get("focus_stops", []):
            if stop["lost"]:
                continue
            stops.setdefault(stop["selector"], stop)
            if last and _moves_up(last["rect"], stop["rect"]):
                regressions.append({"step": s["id"], "from": last["name"], "to": stop["name"]})
            last = stop
    return stops, regressions


def _focus_loss(steps: list[dict]) -> tuple[list[str], int]:
    """Activations after which focus fell to <body>, and the Tab presses spent on the step right after a loss."""
    lost_after: list[str] = []
    tabs_after_loss = 0
    prev_lost = False
    for s in steps:
        if s.get("tab_presses") is not None and prev_lost:
            tabs_after_loss += s["tab_presses"]
        if s.get("interaction") is not None:
            prev_lost = bool(s.get("focus_lost_after"))
            if prev_lost:
                lost_after.append(s["id"])
    return lost_after, tabs_after_loss


def _completed(one_pass: dict) -> bool:
    """True iff the pass recorded exactly the canonical journey's steps, in order. A step that failed raises in
    the driver, so a shorter or different trace means the journey was not completed."""
    return [s["id"] for s in one_pass["steps"]] == [s.id for s in journey()]


def keyboard(kb_pass: dict) -> dict:
    steps = kb_pass["steps"]
    presses = {s["id"]: s["tab_presses"] for s in steps if s.get("tab_presses") is not None}
    stops, regressions = _scan_focus(steps)
    lost_after, tabs_after_loss = _focus_loss(steps)
    no_ring = sorted(k for k, v in stops.items() if not v["visible_ring"])
    return {
        "completed_journey_keyboard_only": _completed(kb_pass),
        "tab_presses_total": sum(presses.values()),
        "tab_presses_by_step": presses,
        "max_tab_presses_for_one_target": max(presses.values(), default=0),
        "unique_focus_stops_seen": len(stops),
        "stops_without_visible_focus_indicator": no_ring,
        "focus_order_regressions": regressions,
        "activations": sum(1 for s in steps if s.get("interaction") is not None),
        "activations_that_lost_focus": lost_after,
        "focus_lost_count": len(lost_after),
        "stops_without_indicator_count": len(no_ring),
        "focus_order_regression_count": len(regressions),
        "tab_presses_spent_after_focus_loss": tabs_after_loss,
        "note": "Real Tab / Shift-free forward traversal; focus indicator = computed outline or box-shadow on the focused element; "
        "'focus lost' = document.activeElement is <body> once the DOM settled after activation",
    }


# --- working memory -----------------------------------------------------------------------------
def _memory_row(name: str, v: dict) -> dict[str, Any]:
    c = v["chunks_viewport"]
    return {
        "view": name,
        "controls": c["controls"],
        "content_groups": c["content_groups"],
        "chunks_viewport": c["chunks"],
        "chunks_page": v["chunks_page"]["chunks"],
        "atoms_viewport": c["atoms"],
        "over_miller_9": c["chunks"] > laws.MILLER_UPPER,
        "over_cowan_4": c["chunks"] > laws.COWAN_LIMIT,
    }


def working_memory(pass0: dict) -> dict:
    rows = [_memory_row(name, v) for name, v in sorted(pass0["views"].items())]
    return {
        "label": "HEURISTIC PROXY - counts what is simultaneously visible, not what a person holds in memory",
        "definition": "chunks = visible operable controls (a checkbox and its label are one) + groups of visible static text/heading atoms "
        "that share a parent element; viewport = first screen at scroll top, page = whole rendered view",
        "citations": ["Miller 1956 (7 +/- 2)", "Cowan 2001 (about 4)"],
        "views": rows,
        "summary": {
            "views": len(rows),
            "max_chunks_viewport": max((x["chunks_viewport"] for x in rows), default=0),
            "views_over_miller_9": sum(x["over_miller_9"] for x in rows),
        },
    }


# --- assembly -----------------------------------------------------------------------------------
def _runtime_errors(passes: list[dict]) -> dict[str, Any]:
    exceptions = sorted({e for p in passes for e in p["errors"] if e.startswith("pageerror")})
    failures = sorted({(f["status"], f["method"], f["path"], f["step"]) for p in passes for f in p["http_failures"]})
    return {
        "javascript_exceptions": exceptions,
        "javascript_exception_count": len(exceptions),
        "http_error_responses": [{"status": a, "method": b, "path": c, "step": d} for a, b, c, d in failures],
    }


def analyse(raw: dict) -> dict:
    """Full metric set from `journey.collect()` output."""
    passes = raw["pointer_passes"]
    pass0 = passes[0]
    wcag_section, statuses = wcag(pass0)
    return {
        "environment": raw["environment"],
        "journey": {
            "steps": [{"id": s["id"], "label": s["label"], "kind": s["kind"]} for s in pass0["steps"]],
            "completed": all(_completed(p) for p in passes) and _completed(raw["keyboard_pass"]),
            "scripted_answers_note": "review answers are scripted fixture text; not a human comprehension measure",
        },
        "fitts": fitts(pass0, statuses),
        "hick_hyman": hick(pass0),
        "klm": klm(pass0, raw["keyboard_pass"]),
        "wcag": wcag_section,
        "keyboard": keyboard(raw["keyboard_pass"]),
        "working_memory": working_memory(pass0),
        "runtime_errors": _runtime_errors(passes),
        "measured": {"doherty": doherty(passes, raw["keyboard_pass"])},
    }
