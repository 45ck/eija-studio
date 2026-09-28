"""Trace -> metrics. Applies the HCI laws in `laws.py` / `wcag.py` to what `journey.py` recorded.

Pure and deterministic: the same trace always yields the same metrics. Sections that come from
wall-clock measurements are keyed under `measured` and are excluded from geometry-only comparisons.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from . import laws
from .wcag import Box, target_size_status

FITTS = laws.FittsModel()
HICK = laws.HickModel()
KLM = laws.KlmTimes()
RESPONSE_NOTE = "settled = last DOM mutation before quiescence, from the click event; excludes OS/browser input latency"


def r(value: float | None, digits: int = 3) -> float | None:
    return None if value is None else round(value, digits)


# --- Fitts ------------------------------------------------------------------------------------
def fitts(pass0: dict, target_status: dict[str, str]) -> dict:
    rows = []
    for t in pass0["pointer_targets"]:
        box = t["effective"]
        width = laws.smaller_of(box["w"], box["h"])
        raw_width = laws.smaller_of(t["raw"]["w"], t["raw"]["h"])
        row: dict[str, Any] = {
            "step": t["step"], "target": t["name"], "selector": t["selector"], "w_px": r(width, 1), "raw_w_px": r(raw_width, 1),
            "via_label": t["via_label"], "scrolled_before": t["scrolled"],
            "wcag_2_5_8": target_status.get(t["selector"], "not-audited"),
        }
        if t["from"] is None:
            row.update(distance_px=None, id_bits=None, predicted_mt_s=None, flags=[], id_bits_nearest_edge=None, note="first pointer target: no preceding position")
        else:
            d = math.dist(t["from"], t["to"])
            id_bits = laws.shannon_id(d, width)
            flags = []
            if id_bits > laws.MAX_ID_BITS:
                flags.append("ID>4")
            if width < laws.MIN_TARGET_PX:
                flags.append("W<24")
            box_xywh = (box["x"], box["y"], box["w"], box["h"])
            near = laws.shannon_id(laws.nearest_edge_distance(tuple(t["from"]), box_xywh), width)
            row.update(distance_px=r(d, 1), id_bits=r(id_bits, 3), predicted_mt_s=r(laws.fitts_time(id_bits, FITTS), 3), flags=flags,
                       id_bits_nearest_edge=r(near, 3))
        rows.append(row)
    moves = [x for x in rows if x["id_bits"] is not None]
    hardest = max(moves, key=lambda x: x["id_bits"]) if moves else None
    return {
        "model": {"form": "MT = a + b*log2(D/W + 1), W = min(width, height)", "a_s": FITTS.a, "b_s_per_bit": FITTS.b, "citation": FITTS.citation},
        "targets": rows,
        "summary": {
            "pointer_targets": len(rows), "moves_with_distance": len(moves),
            "mean_id_bits": r(sum(x["id_bits"] for x in moves) / len(moves), 3) if moves else None,
            "max_id_bits": hardest["id_bits"] if hardest else None, "max_id_step": hardest["step"] if hardest else None,
            "moves_id_over_4": sum("ID>4" in x["flags"] for x in rows),
            "moves_id_over_4_nearest_edge": sum((x.get("id_bits_nearest_edge") or 0) > laws.MAX_ID_BITS for x in rows),
            "landing_convention_note": "primary D uses the centre of the effective box, which overstates D for wide targets; "
                                       "moves_id_over_4_nearest_edge recomputes D to the nearest edge, so the flag count is a range",
            "targets_w_under_24": sum("W<24" in x["flags"] for x in rows),
            "predicted_pointing_time_s": r(sum(x["predicted_mt_s"] for x in moves), 3),
            "total_distance_px": r(sum(x["distance_px"] for x in moves), 1),
            "scrolls_needed": sum(1 for x in rows if x["scrolled_before"]),
        },
    }


# --- Hick-Hyman -------------------------------------------------------------------------------
def hick(pass0: dict) -> dict:
    rows = []
    for s in pass0["steps"]:
        d = s.get("decision")
        if not d:
            continue
        rows.append({
            "step": s["id"], "decision": d["name"], "choices": d["n_choices"], "bits": r(laws.hick_bits(d["n_choices"]), 3),
            "predicted_s": r(laws.hick_time(d["n_choices"], HICK), 3), "over_7": d["n_choices"] > laws.MAX_CHOICES,
            "screen_controls": d["n_screen"], "screen_over_7": d["n_screen"] > laws.MAX_CHOICES,
            "screen_predicted_s": r(laws.hick_time(d["n_screen"], HICK), 3),
        })
    return {
        "model": {"form": "T = b*log2(n + 1)", "b_s_per_bit": HICK.b, "citation": HICK.citation,
                  "note": "choices = enabled alternatives in the declared choice group; screen_controls = every enabled control in the "
                          "viewport (an upper bound: an expert who knows the target does not search them all)"},
        "decisions": rows,
        "summary": {"decision_points": len(rows), "max_choices": max((x["choices"] for x in rows), default=0),
                    "choice_points_over_7": sum(x["over_7"] for x in rows),
                    "screen_points_over_7": sum(x["screen_over_7"] for x in rows),
                    "predicted_choice_time_s": r(sum(x["predicted_s"] for x in rows), 3)},
    }


# --- KLM ----------------------------------------------------------------------------------------
def _klm_block(operators: list[dict], targets: list[dict] | None) -> dict:
    symbols = [o["op"] for o in operators]
    standard = laws.klm_time(symbols, KLM)
    refined = standard
    if targets is not None:
        moves = [t for t in fitts_moves(targets)]
        it = iter(moves)
        refined = 0.0
        for o in operators:
            if o["op"] == "P" and o.get("fitts"):
                mt = next(it)
                refined += mt if mt is not None else KLM.P
            else:
                refined += laws.klm_time([o["op"]], KLM)
    per_step: dict[str, float] = defaultdict(float)
    for o in operators:
        per_step[o["step"]] += laws.klm_time([o["op"]], KLM)
    return {
        "operator_counts": laws.count_operators(symbols),
        "total_s": r(standard, 3),
        "fitts_refined_total_s": r(refined, 3) if targets is not None else None,
        "per_step_s": {k: r(v, 3) for k, v in per_step.items()},
        "operators": [{k: v for k, v in o.items() if k != "fitts"} | {"seconds": getattr(KLM, o["op"])} for o in operators],
    }


def fitts_moves(targets: list[dict]) -> list[float | None]:
    """Predicted MT per pointer target in order (None for the first, which has no preceding position)."""
    out: list[float | None] = []
    for t in targets:
        if t["from"] is None:
            out.append(None)
        else:
            width = laws.smaller_of(t["effective"]["w"], t["effective"]["h"])
            out.append(laws.fitts_time(laws.shannon_id(math.dist(t["from"], t["to"]), width), FITTS))
    return out


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
def doherty(pointer_passes: list[dict], keyboard_pass: dict) -> dict:
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
    firsts = [x for v in per_step.values() for x in v["first"]]
    settled = [x for v in per_step.values() for x in v["settled"]]
    kb = [s["interaction"]["settled_ms"] for s in keyboard_pass["steps"]
          if s.get("interaction") and s["interaction"]["mutation_batches"] > 0]
    steps = []
    for step_id in [s["id"] for s in pointer_passes[0]["steps"] if s["id"] in per_step]:
        v = per_step[step_id]
        steps.append({
            "step": step_id, "samples": len(v["settled"]),
            "first_feedback_p50_ms": r(laws.percentile(v["first"], 50), 1), "first_feedback_p95_ms": r(laws.percentile(v["first"], 95), 1),
            "settled_p50_ms": r(laws.percentile(v["settled"], 50), 1), "settled_p95_ms": r(laws.percentile(v["settled"], 95), 1),
            "over_400ms": laws.percentile(v["settled"], 95) > laws.DOHERTY_MS,
            "median_over_400ms": laws.percentile(v["settled"], 50) > laws.DOHERTY_MS,
        })
    return {
        "threshold_ms": laws.DOHERTY_MS, "note": RESPONSE_NOTE, "method": "nearest-rank percentiles over all repeats",
        "citation": "Doherty & Thadani 1982 (IBM Systems Journal 21(1)); ~400 ms",
        "interactions_measured": len(settled), "native_control_interactions_excluded": sorted(native),
        "first_feedback_p50_ms": r(laws.percentile(firsts, 50), 1), "first_feedback_p95_ms": r(laws.percentile(firsts, 95), 1),
        "settled_p50_ms": r(laws.percentile(settled, 50), 1), "settled_p95_ms": r(laws.percentile(settled, 95), 1),
        "settled_max_ms": r(max(settled), 1) if settled else None,
        "keyboard_settled_p50_ms": r(laws.percentile(kb, 50), 1), "keyboard_settled_p95_ms": r(laws.percentile(kb, 95), 1),
        "journey_wait_p50_sum_s": r(sum(x["settled_p50_ms"] for x in steps) / 1000.0, 3),
        "steps": steps,
        "steps_over_400ms": [x["step"] for x in steps if x["over_400ms"]],
        "steps_median_over_400ms": [x["step"] for x in steps if x["median_over_400ms"]],
    }


# --- WCAG ---------------------------------------------------------------------------------------
def _status_table(controls: list[dict]) -> list[tuple[dict, str]]:
    enabled = [c for c in controls if not c["disabled"]]
    boxes = [Box(c["x"], c["y"], c["w"], c["h"]) for c in enabled]
    return [(c, target_size_status(i, boxes)) for i, c in enumerate(enabled)]


def wcag(pass0: dict) -> tuple[dict, dict[str, str]]:
    rules: dict[str, dict] = {}
    incomplete: dict[str, dict] = {}
    for view, data in sorted(pass0["views"].items()):
        for v in data["axe"]["violations"]:
            rule = rules.setdefault(v["id"], {"id": v["id"], "impact": v["impact"], "help": v["help"], "help_url": v["help_url"],
                                              "tags": v["tags"], "nodes": set(), "views": set()})
            rule["views"].add(view)
            for n in v["nodes"]:
                rule["nodes"].add(n["target"])
        for v in data["axe"]["incomplete"]:
            inc = incomplete.setdefault(v["id"], {"id": v["id"], "impact": v["impact"], "views": set()})
            inc["views"].add(view)
    by_rule = [{**{k: x[k] for k in ("id", "impact", "help", "help_url", "tags")}, "node_count": len(x["nodes"]),
                "nodes": sorted(x["nodes"]), "views": sorted(x["views"])} for x in sorted(rules.values(), key=lambda x: x["id"])]
    by_impact: dict[str, int] = defaultdict(int)
    for x in by_rule:
        by_impact[x["impact"] or "unknown"] += 1
    # own WCAG 2.5.8 audit across every audited view (worst status per selector)
    order = {"pass": 0, "pass-spacing": 1, "fail": 2}
    worst: dict[str, tuple[str, dict]] = {}
    for view, data in sorted(pass0["views"].items()):
        for c, status in _status_table(data["controls"]):
            key = c["selector"]
            if key not in worst or order[status] > order[worst[key][0]]:
                worst[key] = (status, c)
    statuses = {k: v[0] for k, v in worst.items()}
    under = sorted(({"selector": k, "name": c["name"], "status": s, "effective_px": [r(c["w"], 1), r(c["h"], 1)],
                     "raw_px": [r(c["raw_w"], 1), r(c["raw_h"], 1)], "via_label": c["via_label"]}
                    for k, (s, c) in worst.items() if min(c["raw_w"], c["raw_h"]) < laws.MIN_TARGET_PX or s != "pass"),
                   key=lambda x: x["selector"])
    tally = defaultdict(int)
    for s in statuses.values():
        tally[s] += 1
    responsive = {}
    for size, tabs in sorted((pass0.get("responsive") or {}).items()):
        row = {"horizontal_overflow_tabs": sorted(t for t, v in tabs.items() if v["scroll_width"] > v["inner_width"]), "targets_fail_2_5_8": 0}
        for tab, v in sorted(tabs.items()):
            row["targets_fail_2_5_8"] += sum(1 for _, s in _status_table(v["controls"]) if s == "fail")
        responsive[size] = row
    visual_state = sorted({item.split(" (")[0] for d in pass0["views"].values() for item in d.get("visual_state_only", [])})
    summary = {"rules": len(by_rule), "nodes": sum(x["node_count"] for x in by_rule),
               "target_size_failures": tally.get("fail", 0),
               **{impact: by_impact.get(impact, 0) for impact in ("critical", "serious", "moderate", "minor")},
               "reflow_overflow_views": sum(len(v["horizontal_overflow_tabs"]) for v in responsive.values())}
    return {
        "engine": "axe-core (tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa)",
        "summary": summary,
        "violations_by_rule": by_rule,
        "violation_rules_by_impact": dict(sorted(by_impact.items())),
        "needs_review_rules": [{"id": x["id"], "impact": x["impact"], "views": sorted(x["views"])} for x in sorted(incomplete.values(), key=lambda x: x["id"])],
        "views_audited": sorted(pass0["views"]),
        "target_size_2_5_8": {"controls_audited": len(statuses), "status_counts": dict(sorted(tally.items())), "undersized_or_failing": under,
                              "exceptions_not_evaluated": ["inline", "user-agent controlled", "equivalent control", "essential"]},
        "reflow_and_targets_by_viewport": responsive,
        "supplementary_state_only_visual": {"check": "interactive element styled active/selected without aria-current/selected/pressed/checked/expanded",
                                           "elements": visual_state, "authority": "heuristic; not an axe rule"},
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


def _completed(one_pass: dict) -> bool:
    """True iff the pass recorded exactly the canonical journey's steps, in order. A step that failed raises in
    the driver, so a shorter or different trace means the journey was not completed."""
    from .journey import journey  # local import: journey.py is the data definition; analysis stays importable without a browser

    return [s["id"] for s in one_pass["steps"]] == [s.id for s in journey()]


def keyboard(kb_pass: dict) -> dict:
    steps = kb_pass["steps"]
    presses = {s["id"]: s.get("tab_presses") for s in steps if s.get("tab_presses") is not None}
    stops_by_selector: dict[str, dict] = {}
    regressions = []
    lost_after = []
    tabs_after_loss = 0
    prev_lost = False
    for s in steps:
        if s.get("tab_presses") is not None and prev_lost:
            tabs_after_loss += s["tab_presses"]
        if s.get("interaction") is not None:
            prev_lost = bool(s.get("focus_lost_after"))
            if prev_lost:
                lost_after.append(s["id"])
        last = None
        for stop in s.get("focus_stops", []):
            if stop["lost"]:
                continue
            stops_by_selector.setdefault(stop["selector"], stop)
            if last and _moves_up(last["rect"], stop["rect"]):
                regressions.append({"step": s["id"], "from": last["name"], "to": stop["name"]})
            last = stop
    no_ring = sorted(k for k, v in stops_by_selector.items() if not v["visible_ring"])
    activations = [s for s in steps if s.get("interaction") is not None]
    return {
        "completed_journey_keyboard_only": _completed(kb_pass),
        "tab_presses_total": sum(presses.values()),
        "tab_presses_by_step": presses,
        "max_tab_presses_for_one_target": max(presses.values(), default=0),
        "unique_focus_stops_seen": len(stops_by_selector),
        "stops_without_visible_focus_indicator": no_ring,
        "focus_order_regressions": regressions,
        "activations": len(activations),
        "activations_that_lost_focus": lost_after,
        "focus_lost_count": len(lost_after),
        "stops_without_indicator_count": len(no_ring),
        "focus_order_regression_count": len(regressions),
        "tab_presses_spent_after_focus_loss": tabs_after_loss,
        "note": "Real Tab / Shift-free forward traversal; focus indicator = computed outline or box-shadow on the focused element; "
                "'focus lost' = document.activeElement is <body> once the DOM settled after activation",
    }


# --- working memory -----------------------------------------------------------------------------
def working_memory(pass0: dict) -> dict:
    rows = []
    for name, v in sorted(pass0["views"].items()):
        c = v["chunks_viewport"]
        rows.append({"view": name, "controls": c["controls"], "content_groups": c["content_groups"], "chunks_viewport": c["chunks"],
                     "chunks_page": v["chunks_page"]["chunks"], "atoms_viewport": c["atoms"],
                     "over_miller_9": c["chunks"] > laws.MILLER_UPPER, "over_cowan_4": c["chunks"] > laws.COWAN_LIMIT})
    return {
        "label": "HEURISTIC PROXY - counts what is simultaneously visible, not what a person holds in memory",
        "definition": "chunks = visible operable controls (a checkbox and its label are one) + groups of visible static text/heading atoms "
                      "that share a parent element; viewport = first screen at scroll top, page = whole rendered view",
        "citations": ["Miller 1956 (7 +/- 2)", "Cowan 2001 (about 4)"],
        "views": rows,
        "summary": {"views": len(rows), "max_chunks_viewport": max((x["chunks_viewport"] for x in rows), default=0),
                    "views_over_miller_9": sum(x["over_miller_9"] for x in rows)},
    }


def analyse(raw: dict) -> dict:
    """Full metric set from `journey.collect()` output."""
    passes = raw["pointer_passes"]
    pass0 = passes[0]
    wcag_section, statuses = wcag(pass0)
    failures = sorted({(f["status"], f["method"], f["path"], f["step"]) for p in passes for f in p["http_failures"]})
    return {
        "environment": raw["environment"],
        "journey": {"steps": [{"id": s["id"], "label": s["label"], "kind": s["kind"]} for s in pass0["steps"]],
                    "completed": all(_completed(p) for p in passes) and _completed(raw["keyboard_pass"]), "scripted_answers_note": "review answers are scripted fixture text; not a human comprehension measure"},
        "fitts": fitts(pass0, statuses),
        "hick_hyman": hick(pass0),
        "klm": klm(pass0, raw["keyboard_pass"]),
        "wcag": wcag_section,
        "keyboard": keyboard(raw["keyboard_pass"]),
        "working_memory": working_memory(pass0),
        "runtime_errors": {
            "javascript_exceptions": sorted({e for p in passes for e in p["errors"] if e.startswith("pageerror")}),
            "javascript_exception_count": len({e for p in passes for e in p["errors"] if e.startswith("pageerror")}),
            "http_error_responses": [{"status": a, "method": b, "path": c, "step": d} for a, b, c, d in failures],
        },
        "measured": {"doherty": doherty(passes, raw["keyboard_pass"])},
    }
