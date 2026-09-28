"""Canonical JSON report, deterministic Markdown rendering, snapshot publishing and the drift check.

`build_report` is pure over a `journey.collect()` result (the raw trace). The raw trace is committed
beside the snapshot (docs/hci/trace.snapshot.json), so `python -m quality.hci check` can re-derive the
snapshot from trace + current laws + current budgets and re-render REPORT.md, byte for byte, without a
browser. The check never re-measures anything: the measured numbers live in the committed trace, a
labelled point-in-time record, so a slower or faster machine can never fail it. Consequence: an edit to
laws.py, analysis/recommend code or budgets.json without a refresh (`python -m quality.hci rederive`, no
browser) is a drift failure in the fast tier.

Evidence kinds are separated in the rendering: MEASUREMENT (geometry, axe, focus, wall-clock timings on
the running Studio) and PREDICTION (population-average model times computed from that geometry).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from . import analysis, budgets, journey, recommend

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "hci"
SNAPSHOT = DOCS / "report.snapshot.json"
TRACE = DOCS / "trace.snapshot.json"
REPORT_MD = DOCS / "REPORT.md"
SCHEMA = "eija.hci.report.v1"

LIMITATIONS = [
    "Every law is a population-average model from laboratory studies. Predicted times rank alternatives; they are not measurements of any user.",
    "This is NOT a human usability study. No participant, persona or task-success rate is represented (human study: NOT_RUN).",
    "The journey answers the three review questions with scripted fixture text; it exercises the UI and says nothing about comprehension.",
    "Approval and apply run under the kernel-test harness identity (source differs from the owner-stamped fixture); they are UI evidence, not a release approval.",
    "Doherty timings are wall-clock on one shared Windows PC, headless Chrome, loopback server; they exclude OS/input latency and are sensitive to load (the settled p95 varied between about 1.4 and 2.5 s across runs). Read the medians and interquartile ranges, not a single number; the snapshot is one point-in-time record.",
    "'First feedback' is the first DOM mutation after the click (a JavaScript-task latency). It excludes style, layout, paint and compositing, so it is not perceived latency.",
    "Fitts D lands at the centre of the effective box, which overstates D for wide targets; the report also gives a nearest-edge variant so the flag count is a range. Geometry-based budgets are specific to this Chrome build and font set.",
    "Only uncaught page exceptions and HTTP error responses are counted as runtime hygiene; console.error and console.warn messages are not.",
    "Hick b and the KLM operator times came from secondary sources (Card, Moran & Newell as cited in the literature); only the Fitts constants were checked against the primary paper text.",
    "axe-core detects only a subset of WCAG failures; a clean axe run is not conformance. Exceptions to 2.5.8 other than spacing are not evaluated.",
    "The working-memory number is a visibility-based heuristic proxy for Miller/Cowan chunk limits, not a measure of anyone's memory.",
    "Nothing here shows that any change benefits users; recommendations are model-ranked hypotheses to be tested with people.",
]
NOT_RUN = [
    "Human usability study / think-aloud / task-success rate: NOT_RUN (needs participants; see docs/hci/README.md protocol notes)",
    "Screen-reader testing (NVDA, JAWS, VoiceOver, TalkBack): NOT_RUN",
    "Browsers other than Google Chrome (Firefox, Safari/WebKit): NOT_RUN",
    "Real touch devices and 400% browser zoom (only 390x844 and 320x568 viewport emulation ran): NOT_RUN",
    "Forced-colors / high-contrast and prefers-reduced-motion audits: NOT_RUN",
    "Live model provider round-trips (offline synthetic provider only): NOT_RUN",
    "Release-stamped identity (real `eija serve` approval): NOT_RUN on unstamped source; use --identity release on a stamped build",
]
READING_GUIDE = (
    "How to read this report. **MEASUREMENT**: recorded from the running Studio (element geometry, axe results, focus behaviour, "
    "click-to-DOM wall-clock timings). **PREDICTION**: a population-average model (Fitts, Hick-Hyman, KLM) applied to the measured "
    "geometry and counts; it ranks alternatives and is not a measurement of any person. Timings vary run to run, so they are shown as "
    "medians with interquartile ranges; geometry and operator counts are deterministic for the same UI bytes, Chrome and fonts."
)


def build_report(raw: dict, date: str | None = None, budget_defs: list[dict] | None = None) -> dict:
    metrics = analysis.analyse(raw)
    report = {"schema": SCHEMA, "date": date, **metrics}
    report["recommendations"] = recommend.recommend(metrics)
    report["budgets"] = budgets.evaluate(report, budget_defs)
    report["limitations"] = LIMITATIONS
    report["not_run"] = NOT_RUN
    return report


def dumps(obj: dict) -> str:
    """Canonical JSON: sorted keys, 2-space indent, LF, trailing newline."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))  # bytes: never CRLF on Windows


# --- Markdown helpers ---------------------------------------------------------------------------
def _cell(x) -> str:
    return ("-" if x is None else str(x)).replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def _fmt(x, unit="") -> str:
    return "-" if x is None else f"{x}{unit}"


def _flag(condition) -> str:
    return "FLAG" if condition else "ok"


def _section(title: str, *blocks: str) -> list[str]:
    """A heading followed by blocks, each separated by one blank line."""
    out = [f"## {title}", ""]
    for block in blocks:
        out += [block, ""]
    return out


# --- Markdown sections (each is pure over the canonical report dict) ----------------------------
def _intro(rep: dict) -> list[str]:
    env = rep["environment"]
    return [
        "# HCI report: Studio UI journey",
        "",
        "> Generated by `python -m quality.hci run --publish-docs` from `docs/hci/report.snapshot.json`; "
        "re-rendered and drift-checked by `python -m quality.hci check`. Do not edit by hand.",
        "",
        "Evidence kind: **model-based prediction plus instrumented measurement on synthetic data**. Not a human study. "
        f"Identity under test: `{env['identity_source']}` (kernel-test harness stand-in, never a release identity). "
        f"Snapshot date: {rep['date'] or 'not stamped'}.",
        "",
        READING_GUIDE,
        "",
    ]


def _environment(rep: dict) -> list[str]:
    env = rep["environment"]
    rows = [
        ["Platform", env["platform"]],
        ["Browser", f"Google Chrome {env['chrome']} (headless={env['headless']})"],
        ["Playwright / axe", f"{env['playwright']} / axe-core {env['axe_core']} via axe-playwright-python {env['axe_playwright_python']}"],
        ["Viewport", f"{env['viewport']['width']}x{env['viewport']['height']} @ {env['device_scale_factor']}x"],
        ["Provider", env["provider"]],
        ["Pointer repeats (timing)", env["repeats"]],
        ["UI bytes (sha256, first 12)", ", ".join(f"{k} {v[:12]}" for k, v in sorted(env["ui_sha256"].items()))],
    ]
    return _section("Environment", _table(["Item", "Value"], rows))


def _headline_rows(rep: dict) -> list[list]:
    fit, hk, kl, wc = rep["fitts"]["summary"], rep["hick_hyman"]["summary"], rep["klm"], rep["wcag"]["summary"]
    kb, wm, dh = rep["keyboard"], rep["working_memory"]["summary"], rep["measured"]["doherty"]
    return [
        [
            "MEASUREMENT (geometry)",
            "Fitts (Shannon)",
            f"pointer moves with ID > 4 bits (centre landing; nearest-edge variant {fit['moves_id_over_4_nearest_edge']})",
            fit["moves_id_over_4"],
            "0",
            _flag(fit["moves_id_over_4"]),
        ],
        ["MEASUREMENT (geometry)", "Fitts / WCAG 2.5.8", "pointer targets with W < 24 px", fit["targets_w_under_24"], "0", _flag(fit["targets_w_under_24"])],
        ["MEASUREMENT (DOM counts)", "Hick-Hyman", "choice groups with n > 7", hk["choice_points_over_7"], "0", _flag(hk["choice_points_over_7"])],
        ["PREDICTION", "KLM-GOMS", "expert time, pointer journey (s)", kl["expert_time_pointer_s"], "-", "info"],
        ["PREDICTION", "KLM-GOMS", "expert time, keyboard-only (s)", kl["expert_time_keyboard_only_s"], "-", "info"],
        ["MEASUREMENT (wall-clock)", "Doherty", "click -> settled DOM, median (ms)", dh["settled_p50_ms"], "400", _flag((dh["settled_p50_ms"] or 0) > 400)],
        ["MEASUREMENT (wall-clock)", "Doherty", "click -> settled DOM, p95 (ms)", dh["settled_p95_ms"], "400", _flag((dh["settled_p95_ms"] or 0) > 400)],
        ["MEASUREMENT (wall-clock)", "Doherty", "click -> first DOM mutation, p95 (ms; excludes paint)", dh["first_feedback_p95_ms"], "400", _flag((dh["first_feedback_p95_ms"] or 0) > 400)],
        [
            "MEASUREMENT (axe)",
            "WCAG 2.2 AA",
            "violating rules (critical/serious/moderate/minor)",
            f"{wc['rules']} ({wc['critical']}/{wc['serious']}/{wc['moderate']}/{wc['minor']})",
            "0",
            _flag(wc["rules"]),
        ],
        ["MEASUREMENT (geometry)", "WCAG 2.5.8", "targets failing minimum size", wc["target_size_failures"], "0", _flag(wc["target_size_failures"])],
        ["MEASUREMENT (focus)", "Keyboard", "activations that dropped focus", f"{kb['focus_lost_count']}/{kb['activations']}", "0", _flag(kb["focus_lost_count"])],
        ["MEASUREMENT (proxy)", "Working memory", "max chunks visible at once", wm["max_chunks_viewport"], "9", _flag(wm["views_over_miller_9"])],
    ]


def _headline(rep: dict) -> list[str]:
    return _section("Headline", _table(["Evidence", "Law / standard", "Metric", "Value", "Threshold", "Flag"], _headline_rows(rep)))


def _recommendation_effect(x: dict) -> str:
    return x["predicted_effect"] or (f"{x['predicted_saving_s']} s" if x["predicted_saving_s"] else "-")


def _recommendation_detail(x: dict) -> list[str]:
    out = [
        f"### {x['rank']}. {x['title']}",
        "",
        f"- Change: {x['change']}",
        f"- Evidence: `{json.dumps(x['evidence'], sort_keys=True, ensure_ascii=False)}`",
    ]
    if x["targets"]:
        out.append(f"- Targets: {', '.join(f'`{t}`' for t in x['targets'][:12])}")
    if x["likely_cause"]:
        out.append(f"- Likely cause (UNVERIFIED hypothesis; the probe does not establish it): {x['likely_cause']}")
    out += [f"- Laws: {', '.join(x['laws']) or '-'}; predicted saving ({x['saving_kind']}): {x['predicted_saving_s']} s", ""]
    return out


def _recommendations(rep: dict) -> list[str]:
    recs = rep["recommendations"]
    intro = (
        "Severity 5 critical WCAG, 4 serious WCAG / focus loss / wait over 1 s, 3 moderate WCAG / 2.5.8 / wait over 400 ms, 2 law flag, 1 informational. "
        "Ties broken by predicted saving (a model output, PREDICTION), then id. These are model-ranked hypotheses, not evidence of user benefit. "
        "Applying them belongs to the visual lane's next wave."
    )
    table = _table(["#", "Sev", "Recommendation", "Category", "Predicted effect"], [[x["rank"], x["severity"], x["title"], x["category"], _recommendation_effect(x)] for x in recs])
    out = _section("Ranked recommendations", intro, table)
    for x in recs:
        out += _recommendation_detail(x)
    return out


def _budgets(rep: dict) -> list[str]:
    note = (
        "`target` is the law's threshold; `limit` is the current ratchet (`quality/hci/budgets.json`), calibrated to the values "
        "measured on the snapshot machine plus stated headroom. GAP = known shortfall within the ratchet; FAIL = regression."
    )
    table = _table(
        ["Budget", "Law", "Value", "Target", "Limit", "Status"],
        [[b["id"], b["law"], f"{_fmt(b['value'])} {b['unit']}", b["target"], b["limit"], b["status"]] for b in rep["budgets"]],
    )
    return _section("Budgets", note, table)


def _fitts_section(rep: dict) -> list[str]:
    fit = rep["fitts"]
    m, s = fit["model"], fit["summary"]
    model = (
        f"PREDICTION over measured geometry. `{m['form']}`, a = {m['a_s']} s, b = {m['b_s_per_bit']} s/bit ({m['citation']}). "
        "D = distance between consecutive pointer landing points (centre of the clickable box, which overstates D for wide targets; the last column "
        "re-computes ID to the nearest edge); W = smaller side of the target's effective box (a checkbox and its label are one target)."
    )
    header = ["Step", "Target", "D px", "W px", "ID bits", "MT s", "2.5.8", "Flags", "ID nearest edge"]
    rows = [
        [t["step"], t["target"][:38], t["distance_px"], t["w_px"], t["id_bits"], t["predicted_mt_s"], t["wcag_2_5_8"], ", ".join(t["flags"]) or "-", t.get("id_bits_nearest_edge")]
        for t in fit["targets"]
    ]
    summary = (
        f"Mean ID {s['mean_id_bits']} bits, hardest move `{s['max_id_step']}` ({s['max_id_bits']} bits), predicted pointing time {s['predicted_pointing_time_s']} s over "
        f"{s['total_distance_px']} px, {s['scrolls_needed']} scroll(s) needed (not modelled). "
        f"Moves over 4 bits: {s['moves_id_over_4']} with centre landing, {s['moves_id_over_4_nearest_edge']} with nearest-edge landing."
    )
    return _section("Fitts's law (prediction over measured geometry)", model, _table(header, rows), summary)


def _hick_section(rep: dict) -> list[str]:
    hk = rep["hick_hyman"]
    m = hk["model"]
    model = f"PREDICTION over measured counts. `{m['form']}`, b = {m['b_s_per_bit']} s/bit ({m['citation']}). {m['note']}."
    header = ["Step", "Decision", "n", "bits", "T s", "n > 7", "Screen controls", "Screen T s"]
    rows = [[d["step"], d["decision"], d["choices"], d["bits"], d["predicted_s"], _flag(d["over_7"]), d["screen_controls"], d["screen_predicted_s"]] for d in hk["decisions"]]
    summary = f"Predicted total choice time {hk['summary']['predicted_choice_time_s']} s; largest choice group {hk['summary']['max_choices']}."
    return _section("Hick-Hyman law (prediction over measured counts)", model, _table(header, rows), summary)


def _ops(operators: list[dict], step: str) -> str:
    return " ".join(o["op"] for o in operators if o["step"] == step)


def _klm_section(rep: dict) -> list[str]:
    kl, dh = rep["klm"], rep["measured"]["doherty"]
    t, pj, kj = kl["times_s"], kl["pointer_journey"], kl["keyboard_only_journey"]
    model = f"PREDICTION. Operator times (s): K {t['K']}, P {t['P']}, B {t['B']}, H {t['H']}, M {t['M']} ({kl['citation']}). {kl['placement_rules']}."
    totals = _table(
        ["Journey", "K", "P", "B", "H", "M", "Standard total s", "Fitts-refined total s"],
        [
            ["Pointer + typing", *[pj["operator_counts"][k] for k in "KPBHM"], pj["total_s"], pj["fitts_refined_total_s"]],
            ["Keyboard only (Tab, Enter, Space, arrows)", *[kj["operator_counts"][k] for k in "KPBHM"], kj["total_s"], "-"],
        ],
    )
    summary = (
        f"Expected expert time is {pj['total_s']} s pointer-driven (Fitts-refined {pj['fitts_refined_total_s']} s) and {kj['total_s']} s keyboard-only, "
        f"excluding system response (measured wait, sum of per-step medians: {dh['journey_wait_p50_sum_s']} s) and scrolling."
    )
    per_step = _table(["Step", "KLM s (pointer)", "Operators"], [[st["id"], pj["per_step_s"].get(st["id"], 0), _ops(pj["operators"], st["id"])] for st in rep["journey"]["steps"]])
    return _section("KLM-GOMS (prediction)", model, totals, summary, per_step)


def _doherty_verdict(x: dict) -> str:
    if x["median_over_400ms"]:
        return "p50"
    return "p95 only" if x["over_400ms"] else "ok"


def _doherty_section(rep: dict) -> list[str]:
    dh = rep["measured"]["doherty"]
    native = ", ".join(dh["native_control_interactions_excluded"]) or "none"
    intro = (
        "MEASUREMENT, wall-clock. The first-DOM-mutation columns time the first DOM change after the click: a JavaScript-task latency that excludes style, layout, "
        "paint and compositing. It is not perceived latency and cannot meaningfully fail a 400 ms budget. "
        f"{dh['note']}. Percentiles are {dh['method']}; {dh['interactions_measured']} interactions. "
        f"Native checkbox toggles that change no DOM ({native}) are excluded."
    )
    header = ["Step", "n", "First DOM mutation p50 ms", "p95 ms", "Settled p25 ms", "p50 ms", "p75 ms", "p95 ms", "> 400 ms"]
    rows = [
        [x["step"], x["samples"], x["first_feedback_p50_ms"], x["first_feedback_p95_ms"], x["settled_p25_ms"], x["settled_p50_ms"], x["settled_p75_ms"], x["settled_p95_ms"], _doherty_verdict(x)]
        for x in dh["steps"]
    ]
    overall = (
        f"Overall: first DOM mutation p50/p95 {dh['first_feedback_p50_ms']}/{dh['first_feedback_p95_ms']} ms; settled p25/p50/p75 "
        f"{dh['settled_p25_ms']}/{dh['settled_p50_ms']}/{dh['settled_p75_ms']} ms, p95 {dh['settled_p95_ms']} ms (max {dh['settled_max_ms']} ms). "
        f"Keyboard activations settled p50/p95 {dh['keyboard_settled_p50_ms']}/{dh['keyboard_settled_p95_ms']} ms."
    )
    return _section("Doherty threshold (measurement; varies run to run)", intro, _table(header, rows), overall)


def _wcag_violation_blocks(wc: dict) -> list[str]:
    blocks = [f"MEASUREMENT. {wc['engine']}. Views audited: {', '.join(wc['views_audited'])}."]
    if wc["violations_by_rule"]:
        rows = [[v["id"], v["impact"], v["node_count"], ", ".join(v["views"]), v["help"]] for v in wc["violations_by_rule"]]
        blocks.append(_table(["Rule", "Impact", "Nodes", "Views", "Help"], rows))
    else:
        blocks.append("No axe violations in the audited views.")
    if wc["needs_review_rules"]:
        blocks.append("Needs manual review (axe `incomplete`): " + ", ".join(f"{x['id']} ({x['impact']})" for x in wc["needs_review_rules"]) + ".")
    return blocks


def _wcag_target_blocks(wc: dict) -> list[str]:
    ts, so = wc["target_size_2_5_8"], wc["supplementary_state_only_visual"]
    blocks = [f"Target size (own audit of {ts['controls_audited']} controls): {ts['status_counts']}. Exceptions not evaluated: {', '.join(ts['exceptions_not_evaluated'])}."]
    if ts["undersized_or_failing"]:
        rows = [[f"{x['name'][:40]} `{x['selector']}`", x["status"], "x".join(map(str, x["effective_px"])), "x".join(map(str, x["raw_px"])), x["via_label"]] for x in ts["undersized_or_failing"]]
        blocks.append(_table(["Control", "Status", "Effective px", "Raw px", "Via label"], rows))
    viewport_rows = [[k, ", ".join(v["horizontal_overflow_tabs"]) or "none", v["targets_fail_2_5_8"]] for k, v in wc["reflow_and_targets_by_viewport"].items()]
    blocks.append(_table(["Viewport", "Tabs with horizontal overflow (WCAG 1.4.10)", "Targets failing 2.5.8"], viewport_rows))
    blocks.append(f"Supplementary heuristic ({so['authority']}): {so['check']}: {', '.join(f'`{e}`' for e in so['elements']) or 'none'}.")
    return blocks


def _wcag_section(rep: dict) -> list[str]:
    wc = rep["wcag"]
    return _section("WCAG 2.2 AA (measurement)", *_wcag_violation_blocks(wc), *_wcag_target_blocks(wc))


def _keyboard_section(rep: dict) -> list[str]:
    kb = rep["keyboard"]
    lost = ", ".join(kb["activations_that_lost_focus"]) or "none"
    text = (
        f"MEASUREMENT. The whole journey completed with the keyboard alone: {kb['tab_presses_total']} Tab presses; most for one target {kb['max_tab_presses_for_one_target']}; "
        f"{kb['unique_focus_stops_seen']} distinct focus stops seen; {kb['focus_lost_count']} of {kb['activations']} activations dropped focus to the page body "
        f"({lost}); {kb['tab_presses_spent_after_focus_loss']} Tab presses were spent on steps right after a focus loss; "
        f"{len(kb['stops_without_visible_focus_indicator'])} stops without a visible indicator; {kb['focus_order_regression_count']} upward focus moves. {kb['note']}."
    )
    rows = [[st["id"], kb["tab_presses_by_step"][st["id"]]] for st in rep["journey"]["steps"] if st["id"] in kb["tab_presses_by_step"]]
    return _section("Keyboard-only traversal (measurement)", text, _table(["Step", "Tab presses"], rows))


def _memory_section(rep: dict) -> list[str]:
    wm = rep["working_memory"]
    intro = f"{wm['label']}. {wm['definition']}. Citations: {'; '.join(wm['citations'])}."
    rows = [[v["view"], v["controls"], v["content_groups"], v["chunks_viewport"], v["chunks_page"], _flag(v["over_miller_9"])] for v in wm["views"]]
    return _section("Working memory (heuristic proxy)", intro, _table(["View", "Controls", "Content groups", "Chunks (viewport)", "Chunks (page)", "> 9"], rows))


def _hygiene_section(rep: dict) -> list[str]:
    errors = rep["runtime_errors"]
    http = "; ".join(f"{x['status']} {x['method']} {x['path']} during `{x['step']}`" for x in errors["http_error_responses"]) or "none"
    return _section("Runtime hygiene", f"JavaScript exceptions: {len(errors['javascript_exceptions'])}. HTTP error responses: {http}.")


def _bullets(title: str, items: list[str]) -> list[str]:
    return [f"## {title}", "", *[f"- {x}" for x in items], ""]


SECTIONS: list[Callable[[dict], list[str]]] = [
    _intro,
    _environment,
    _headline,
    _recommendations,
    _budgets,
    _fitts_section,
    _hick_section,
    _klm_section,
    _doherty_section,
    _wcag_section,
    _keyboard_section,
    _memory_section,
    _hygiene_section,
    lambda rep: _bullets("Limitations", rep["limitations"]),
    lambda rep: _bullets("NOT_RUN", rep["not_run"]),
]


def render_markdown(rep: dict) -> str:
    rep = json.loads(dumps(rep))  # render only what the canonical JSON holds (sorted keys), so in-memory and snapshot agree
    out: list[str] = []
    for section in SECTIONS:
        out += section(rep)
    return "\n".join(out)


# --- publish / drift ---------------------------------------------------------------------------
def dump_trace(raw: dict) -> str:
    """Canonical compact JSON of the raw trace (sorted keys, LF): what the snapshot is derived from."""
    return json.dumps(raw, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def publish_docs(report: dict, raw: dict) -> None:
    """Commit-ready evidence: the raw trace, the derived JSON snapshot, and the Markdown rendered from it."""
    write_text(TRACE, dump_trace(raw))
    write_text(SNAPSHOT, dumps(report))
    write_text(REPORT_MD, render_markdown(report))


def rederive_docs() -> None:
    """Rebuild snapshot and REPORT.md from the committed trace under the current laws, analysis and budgets.

    No browser and no new measurement: use it after an intentional change to laws.py, analysis, recommendations,
    the renderer or budgets.json, then review the diff."""
    raw = json.loads(TRACE.read_text(encoding="utf-8"))
    previous = json.loads(SNAPSHOT.read_text(encoding="utf-8")) if SNAPSHOT.exists() else {}
    publish_docs(build_report(raw, date=previous.get("date")), raw)


def _reproducible(snapshot_path: Path, trace_path: Path, report_path: Path) -> str | None:
    """A DRIFT message when the committed evidence does not reproduce, else None."""
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    raw = json.loads(trace_path.read_text(encoding="utf-8"))
    if trace_path.read_bytes() != dump_trace(raw).encode("utf-8"):
        return "DRIFT: docs/hci/trace.snapshot.json is not in canonical form (hand-edited?)"
    if snapshot_path.read_bytes() != dumps(build_report(raw, date=snapshot.get("date"))).encode("utf-8"):
        return (
            "DRIFT: docs/hci/report.snapshot.json is not what the committed trace yields under the current laws, analysis, "
            "recommendations and budgets.json; run `python -m quality.hci rederive` (no browser) or a fresh `run --publish-docs` and review the diff"
        )
    if report_path.read_bytes() != render_markdown(snapshot).encode("utf-8"):
        return "DRIFT: docs/hci/REPORT.md differs from render(report.snapshot.json)"
    return None


def check_docs(strict: bool = False, *, snapshot_path: Path = SNAPSHOT, trace_path: Path = TRACE, report_path: Path = REPORT_MD) -> tuple[bool, str]:
    """Drift check, no browser. Establishes that the committed evidence is internally reproducible; it does
    NOT re-measure anything, so it cannot tell whether the live UI still behaves as the trace says.

    1. snapshot == build_report(committed trace) under the CURRENT laws, analysis, recommendations and
       budgets.json (an edit to any of them without a refresh fails here);
    2. REPORT.md == render(snapshot);
    3. the snapshot's UI hashes vs the current web/* bytes: a note in the fast tier (the visual lane
       legitimately changes the UI first, then refreshes evidence), a hard failure with strict=True
       (release tier), so evidence about UI bytes that no longer exist cannot be released."""
    if not (snapshot_path.exists() and trace_path.exists() and report_path.exists()):
        return False, "docs/hci/{report.snapshot.json,trace.snapshot.json,REPORT.md} missing; run `python -m quality.hci run --publish-docs`"
    drift = _reproducible(snapshot_path, trace_path, report_path)
    if drift:
        return False, drift
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if snapshot["environment"]["ui_sha256"] == journey.ui_hashes():
        return True, "docs/hci evidence is reproducible from its committed trace and matches the current UI bytes"
    stale = (
        "the snapshot was taken on different UI bytes than the current src/eija_studio/resources/web/*; "
        "rerun `nox -s hci` and `--publish-docs` to refresh evidence"
    )
    if strict:
        return False, "STALE: " + stale
    return True, "docs/hci evidence is reproducible from its trace (informational: " + stale + ")"
