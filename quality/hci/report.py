"""Canonical JSON report, deterministic Markdown rendering, snapshot publishing and the drift check.

`build_report` is pure over a `journey.collect()` result (the raw trace). The raw trace is committed
beside the snapshot (docs/hci/trace.snapshot.json), so `python -m quality.hci check` can re-derive the
snapshot from trace + current laws + current budgets and re-render REPORT.md, byte for byte, without
a browser. Consequence: an edit to laws.py, analysis/recommend code or budgets.json that is not
followed by a refresh is a drift failure in the fast tier.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import analysis, budgets, recommend

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
    "Doherty timings are wall-clock on one shared Windows PC, headless Chrome, loopback server; they exclude OS/input latency and are sensitive to load (the settled p95 varied between about 1.4 and 2.5 s across runs).",
    "'First feedback' is the first DOM mutation after the click (a JavaScript-task latency). It excludes style, layout, paint and compositing, so it is not perceived latency.",
    "Fitts D lands at the centre of the effective box, which overstates D for wide targets; the report also gives a nearest-edge variant so the flag count is a range. Geometry-based budgets are specific to this Chrome build and font set.",
    "Only uncaught page exceptions and HTTP error responses are counted as runtime hygiene; console.error and console.warn messages are not.",
    "Hick b and the KLM operator times came from secondary sources (Card, Moran & Newell as cited in the literature); only the Fitts constants were checked against the primary paper text.",
    "axe-core detects only a subset of WCAG failures; a clean axe run is not conformance. Exceptions to 2.5.8 other than spacing are not evaluated.",
    "The working-memory number is a visibility-based heuristic proxy for Miller/Cowan chunk limits, not a measure of anyone's memory.",
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


# --- Markdown -----------------------------------------------------------------------------------
def _table(headers: list[str], rows: list[list]) -> str:
    def cell(x) -> str:
        return ("-" if x is None else str(x)).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(cell(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def _fmt(x, unit="") -> str:
    return "-" if x is None else f"{x}{unit}"


def render_markdown(rep: dict) -> str:
    rep = json.loads(dumps(rep))  # render only what the canonical JSON holds (sorted keys), so in-memory and snapshot agree
    env = rep["environment"]
    fit, hk, kl, wc, kb, wm, dh = (rep["fitts"], rep["hick_hyman"], rep["klm"], rep["wcag"], rep["keyboard"],
                                   rep["working_memory"], rep["measured"]["doherty"])
    out: list[str] = []
    add = out.append
    add("# HCI report: Studio UI journey")
    add("")
    add("> Generated by `python -m quality.hci run --publish-docs` from `docs/hci/report.snapshot.json`; "
        "re-rendered and drift-checked by `python -m quality.hci check`. Do not edit by hand.")
    add("")
    add(f"Evidence kind: **model-based prediction plus instrumented measurement on synthetic data**. Not a human study. "
        f"Identity under test: `{env['identity_source']}`. Snapshot date: {rep['date'] or 'not stamped'}.")
    add("")
    add("## Environment")
    add("")
    add(_table(["Item", "Value"], [
        ["Platform", env["platform"]], ["Browser", f"Google Chrome {env['chrome']} (headless={env['headless']})"],
        ["Playwright / axe", f"{env['playwright']} / axe-core {env['axe_core']} via axe-playwright-python {env['axe_playwright_python']}"],
        ["Viewport", f"{env['viewport']['width']}x{env['viewport']['height']} @ {env['device_scale_factor']}x"],
        ["Provider", env["provider"]], ["Pointer repeats (timing)", env["repeats"]],
        ["UI bytes (sha256, first 12)", ", ".join(f"{k} {v[:12]}" for k, v in sorted(env["ui_sha256"].items()))]]))
    add("")
    add("## Headline")
    add("")
    add(_table(["Law / standard", "Metric", "Value", "Threshold", "Flag"], [
        ["Fitts (Shannon)", "pointer moves with ID > 4 bits (centre landing; nearest-edge variant "
         + str(fit["summary"]["moves_id_over_4_nearest_edge"]) + ")", fit["summary"]["moves_id_over_4"], "0", "FLAG" if fit["summary"]["moves_id_over_4"] else "ok"],
        ["Fitts / WCAG 2.5.8", "pointer targets with W < 24 px", fit["summary"]["targets_w_under_24"], "0", "FLAG" if fit["summary"]["targets_w_under_24"] else "ok"],
        ["Hick-Hyman", "choice groups with n > 7", hk["summary"]["choice_points_over_7"], "0", "FLAG" if hk["summary"]["choice_points_over_7"] else "ok"],
        ["KLM-GOMS", "predicted expert time, pointer journey (s)", kl["expert_time_pointer_s"], "-", "info"],
        ["KLM-GOMS", "predicted expert time, keyboard-only (s)", kl["expert_time_keyboard_only_s"], "-", "info"],
        ["Doherty", "click -> settled DOM p95 (ms)", dh["settled_p95_ms"], "400", "FLAG" if (dh["settled_p95_ms"] or 0) > 400 else "ok"],
        ["Doherty", "click -> first DOM mutation p95 (ms; excludes paint)", dh["first_feedback_p95_ms"], "400", "FLAG" if (dh["first_feedback_p95_ms"] or 0) > 400 else "ok"],
        ["WCAG 2.2 AA (axe)", "violating rules (critical/serious/moderate/minor)",
         f"{wc['summary']['rules']} ({wc['summary']['critical']}/{wc['summary']['serious']}/{wc['summary']['moderate']}/{wc['summary']['minor']})", "0",
         "FLAG" if wc["summary"]["rules"] else "ok"],
        ["WCAG 2.5.8", "targets failing minimum size", wc["summary"]["target_size_failures"], "0", "FLAG" if wc["summary"]["target_size_failures"] else "ok"],
        ["Keyboard", "activations that dropped focus", f"{kb['focus_lost_count']}/{kb['activations']}", "0", "FLAG" if kb["focus_lost_count"] else "ok"],
        ["Working memory (proxy)", "max chunks visible at once", wm["summary"]["max_chunks_viewport"], "9", "FLAG" if wm["summary"]["views_over_miller_9"] else "ok"],
    ]))
    add("")
    add("## Ranked recommendations")
    add("")
    add("Severity 5 critical WCAG, 4 serious WCAG / focus loss / wait over 1 s, 3 moderate WCAG / 2.5.8 / wait over 400 ms, 2 law flag, 1 informational. "
        "Ties broken by predicted saving (a model output), then id. Applying these belongs to the visual lane's next wave.")
    add("")
    add(_table(["#", "Sev", "Recommendation", "Category", "Predicted effect"],
               [[x["rank"], x["severity"], x["title"], x["category"], x["predicted_effect"] or (f"{x['predicted_saving_s']} s" if x["predicted_saving_s"] else "-")]
                for x in rep["recommendations"]]))
    add("")
    for x in rep["recommendations"]:
        add(f"### {x['rank']}. {x['title']}")
        add("")
        add(f"- Change: {x['change']}")
        add(f"- Evidence: `{json.dumps(x['evidence'], sort_keys=True, ensure_ascii=False)}`")
        if x["targets"]:
            add(f"- Targets: {', '.join(f'`{t}`' for t in x['targets'][:12])}")
        if x["likely_cause"]:
            add(f"- Likely cause (UNVERIFIED hypothesis; the probe does not establish it): {x['likely_cause']}")
        add(f"- Laws: {', '.join(x['laws']) or '-'}; predicted saving ({x['saving_kind']}): {x['predicted_saving_s']} s")
        add("")
    add("## Budgets")
    add("")
    add("`target` is the law's threshold; `limit` is the current ratchet (`quality/hci/budgets.json`). GAP = known shortfall within the ratchet; FAIL = regression.")
    add("")
    add(_table(["Budget", "Law", "Value", "Target", "Limit", "Status"],
               [[b["id"], b["law"], f"{_fmt(b['value'])} {b['unit']}", b["target"], b["limit"], b["status"]] for b in rep["budgets"]]))
    add("")
    add("## Fitts's law")
    add("")
    m = fit["model"]
    add(f"`{m['form']}`, a = {m['a_s']} s, b = {m['b_s_per_bit']} s/bit ({m['citation']}). D = distance between consecutive pointer landing points "
        f"(centre of the clickable box, which overstates D for wide targets; the last column re-computes ID to the nearest edge); W = smaller side of the target's effective box (a checkbox and its label are one target).")
    add("")
    add(_table(["Step", "Target", "D px", "W px", "ID bits", "MT s", "2.5.8", "Flags", "ID nearest edge"],
               [[t["step"], t["target"][:38], t["distance_px"], t["w_px"], t["id_bits"], t["predicted_mt_s"], t["wcag_2_5_8"], ", ".join(t["flags"]) or "-",
                 t.get("id_bits_nearest_edge")] for t in fit["targets"]]))
    add("")
    s = fit["summary"]
    add(f"Mean ID {s['mean_id_bits']} bits, hardest move `{s['max_id_step']}` ({s['max_id_bits']} bits), predicted pointing time {s['predicted_pointing_time_s']} s over "
        f"{s['total_distance_px']} px, {s['scrolls_needed']} scroll(s) needed (not modelled). Moves over 4 bits: {s['moves_id_over_4']} with centre landing, "
        f"{s['moves_id_over_4_nearest_edge']} with nearest-edge landing.")
    add("")
    add("## Hick-Hyman law")
    add("")
    add(f"`{hk['model']['form']}`, b = {hk['model']['b_s_per_bit']} s/bit ({hk['model']['citation']}). {hk['model']['note']}.")
    add("")
    add(_table(["Step", "Decision", "n", "bits", "T s", "n > 7", "Screen controls", "Screen T s"],
               [[d["step"], d["decision"], d["choices"], d["bits"], d["predicted_s"], "FLAG" if d["over_7"] else "ok", d["screen_controls"], d["screen_predicted_s"]] for d in hk["decisions"]]))
    add("")
    add(f"Predicted total choice time {hk['summary']['predicted_choice_time_s']} s; largest choice group {hk['summary']['max_choices']}.")
    add("")
    add("## KLM-GOMS")
    add("")
    t = kl["times_s"]
    add(f"Operator times (s): K {t['K']}, P {t['P']}, B {t['B']}, H {t['H']}, M {t['M']} ({kl['citation']}). {kl['placement_rules']}.")
    add("")
    pj, kj = kl["pointer_journey"], kl["keyboard_only_journey"]
    add(_table(["Journey", "K", "P", "B", "H", "M", "Standard total s", "Fitts-refined total s"], [
        ["Pointer + typing", *[pj["operator_counts"][k] for k in "KPBHM"], pj["total_s"], pj["fitts_refined_total_s"]],
        ["Keyboard only (Tab, Enter, Space, arrows)", *[kj["operator_counts"][k] for k in "KPBHM"], kj["total_s"], "-"]]))
    add("")
    add(f"Expected expert time is {pj['total_s']} s pointer-driven (Fitts-refined {pj['fitts_refined_total_s']} s) and {kj['total_s']} s keyboard-only, excluding system response "
        f"(measured wait, sum of per-step p50: {dh['journey_wait_p50_sum_s']} s) and scrolling.")
    add("")
    add(_table(["Step", "KLM s (pointer)", "Operators"], [[st["id"], pj["per_step_s"].get(st["id"], 0), _ops(pj["operators"], st["id"])] for st in rep["journey"]["steps"]]))
    add("")
    add("## Doherty threshold (measured; varies run to run)")
    add("")
    add("First feedback = first DOM mutation after the click: a JavaScript-task latency that excludes style, layout, paint and compositing. "
        "It is not perceived latency and cannot meaningfully fail a 400 ms budget.")
    add("")
    add(f"{dh['note']}. Percentiles are {dh['method']}; {dh['interactions_measured']} interactions. Native checkbox toggles that change no DOM "
        f"({', '.join(dh['native_control_interactions_excluded']) or 'none'}) are excluded.")
    add("")
    add(_table(["Step", "n", "First DOM mutation p50 ms", "p95 ms", "Settled p50 ms", "p95 ms", "> 400 ms"],
               [[x["step"], x["samples"], x["first_feedback_p50_ms"], x["first_feedback_p95_ms"], x["settled_p50_ms"], x["settled_p95_ms"], ("p50" if x["median_over_400ms"] else "p95 only" if x["over_400ms"] else "ok")] for x in dh["steps"]]))
    add("")
    add(f"Overall: first DOM mutation p50/p95 {dh['first_feedback_p50_ms']}/{dh['first_feedback_p95_ms']} ms; settled p50/p95 {dh['settled_p50_ms']}/{dh['settled_p95_ms']} ms "
        f"(max {dh['settled_max_ms']} ms). Keyboard activations settled p50/p95 {dh['keyboard_settled_p50_ms']}/{dh['keyboard_settled_p95_ms']} ms.")
    add("")
    add("## WCAG 2.2 AA")
    add("")
    add(f"{wc['engine']}. Views audited: {', '.join(wc['views_audited'])}.")
    add("")
    if wc["violations_by_rule"]:
        add(_table(["Rule", "Impact", "Nodes", "Views", "Help"], [[v["id"], v["impact"], v["node_count"], ", ".join(v["views"]), v["help"]] for v in wc["violations_by_rule"]]))
    else:
        add("No axe violations in the audited views.")
    add("")
    if wc["needs_review_rules"]:
        add("Needs manual review (axe `incomplete`): " + ", ".join(f"{x['id']} ({x['impact']})" for x in wc["needs_review_rules"]) + ".")
        add("")
    ts = wc["target_size_2_5_8"]
    add(f"Target size (own audit of {ts['controls_audited']} controls): {ts['status_counts']}. Exceptions not evaluated: {', '.join(ts['exceptions_not_evaluated'])}.")
    add("")
    if ts["undersized_or_failing"]:
        add(_table(["Control", "Status", "Effective px", "Raw px", "Via label"],
                   [[f"{x['name'][:40]} `{x['selector']}`", x["status"], "x".join(map(str, x["effective_px"])), "x".join(map(str, x["raw_px"])), x["via_label"]] for x in ts["undersized_or_failing"]]))
        add("")
    add(_table(["Viewport", "Tabs with horizontal overflow (WCAG 1.4.10)", "Targets failing 2.5.8"],
               [[k, ", ".join(v["horizontal_overflow_tabs"]) or "none", v["targets_fail_2_5_8"]] for k, v in wc["reflow_and_targets_by_viewport"].items()]))
    add("")
    so = wc["supplementary_state_only_visual"]
    add(f"Supplementary heuristic ({so['authority']}): {so['check']}: {', '.join(f'`{e}`' for e in so['elements']) or 'none'}.")
    add("")
    add("## Keyboard-only traversal")
    add("")
    add(f"The whole journey completed with the keyboard alone: {kb['tab_presses_total']} Tab presses; most for one target {kb['max_tab_presses_for_one_target']}; "
        f"{kb['unique_focus_stops_seen']} distinct focus stops seen; {kb['focus_lost_count']} of {kb['activations']} activations dropped focus to the page body "
        f"({', '.join(kb['activations_that_lost_focus']) or 'none'}); {kb['tab_presses_spent_after_focus_loss']} Tab presses were spent on steps right after a focus loss; "
        f"{len(kb['stops_without_visible_focus_indicator'])} stops without a visible indicator; {kb['focus_order_regression_count']} upward focus moves. {kb['note']}.")
    add("")
    add(_table(["Step", "Tab presses"], [[st["id"], kb["tab_presses_by_step"][st["id"]]] for st in rep["journey"]["steps"] if st["id"] in kb["tab_presses_by_step"]]))
    add("")
    add("## Working memory (heuristic proxy)")
    add("")
    add(f"{wm['label']}. {wm['definition']}. Citations: {'; '.join(wm['citations'])}.")
    add("")
    add(_table(["View", "Controls", "Content groups", "Chunks (viewport)", "Chunks (page)", "> 9"],
               [[v["view"], v["controls"], v["content_groups"], v["chunks_viewport"], v["chunks_page"], "FLAG" if v["over_miller_9"] else "ok"] for v in wm["views"]]))
    add("")
    add("## Runtime hygiene")
    add("")
    re_ = rep["runtime_errors"]
    add(f"JavaScript exceptions: {len(re_['javascript_exceptions'])}. HTTP error responses: "
        + ("; ".join(f"{x['status']} {x['method']} {x['path']} during `{x['step']}`" for x in re_["http_error_responses"]) or "none") + ".")
    add("")
    add("## Limitations")
    add("")
    out += [f"- {x}" for x in rep["limitations"]]
    add("")
    add("## NOT_RUN")
    add("")
    out += [f"- {x}" for x in rep["not_run"]]
    add("")
    return "\n".join(out)


def _ops(operators: list[dict], step: str) -> str:
    return " ".join(o["op"] for o in operators if o["step"] == step)


# --- publish / drift ---------------------------------------------------------------------------
def dump_trace(raw: dict) -> str:
    """Canonical compact JSON of the raw trace (sorted keys, LF): what the snapshot is derived from."""
    return json.dumps(raw, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def publish_docs(report: dict, raw: dict) -> None:
    """Commit-ready evidence: the raw trace, the derived JSON snapshot, and the Markdown rendered from it."""
    write_text(TRACE, dump_trace(raw))
    write_text(SNAPSHOT, dumps(report))
    write_text(REPORT_MD, render_markdown(report))


def check_docs(strict: bool = False, *, snapshot_path: Path = SNAPSHOT, trace_path: Path = TRACE,
               report_path: Path = REPORT_MD) -> tuple[bool, str]:
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
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    raw = json.loads(trace_path.read_text(encoding="utf-8"))
    if trace_path.read_bytes() != dump_trace(raw).encode("utf-8"):
        return False, "DRIFT: docs/hci/trace.snapshot.json is not in canonical form (hand-edited?)"
    if snapshot_path.read_bytes() != dumps(build_report(raw, date=snapshot.get("date"))).encode("utf-8"):
        return False, ("DRIFT: docs/hci/report.snapshot.json is not what the committed trace yields under the current laws, analysis, "
                       "recommendations and budgets.json; rerun `python -m quality.hci run --publish-docs` and review the diff")
    if report_path.read_bytes() != render_markdown(snapshot).encode("utf-8"):
        return False, "DRIFT: docs/hci/REPORT.md differs from render(report.snapshot.json)"
    from .journey import ui_hashes
    if snapshot["environment"]["ui_sha256"] != ui_hashes():
        stale = ("the snapshot was taken on different UI bytes than the current src/eija_studio/resources/web/*; "
                 "rerun `nox -s hci` and `--publish-docs` to refresh evidence")
        if strict:
            return False, "STALE: " + stale
        return True, "docs/hci evidence is reproducible from its trace (informational: " + stale + ")"
    return True, "docs/hci evidence is reproducible from its committed trace and matches the current UI bytes"
