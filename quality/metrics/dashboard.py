"""Render a metrics document as a self-contained static dashboard (HTML + inline SVG) and a Markdown snapshot.

Pure functions of the document: same input, same bytes. No scripts, no network, no fonts to fetch.
Dark and light themes share one stylesheet (prefers-color-scheme, overridable with data-theme).
Statuses are always written out (PASS / FAIL / NOT_RUN) beside a glyph, never colour alone.
"""
from __future__ import annotations

from . import svg
from .svg import esc, fmt, text

CSS = """
:root{color-scheme:light;--bg:#fcfcfb;--card:#ffffff;--ink:#0b0b0b;--muted:#52514e;--grid:#e6e5e1;--axis:#8b8a85;
--series-1:#2a78d6;--series-2:#eb6834;--series-3:#1baf7a;--good:#0b6b0b;--bad:#b3261e;--warn:#8a5a00;--line:#dcdbd6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#1a1a19;--card:#232322;--ink:#ffffff;
--muted:#c3c2b7;--grid:#34342f;--axis:#7d7c74;--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;--good:#6fcf6f;--bad:#ff8a80;--warn:#e0b040;--line:#3a3a36}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#1a1a19;--card:#232322;--ink:#ffffff;--muted:#c3c2b7;--grid:#34342f;--axis:#7d7c74;
--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;--good:#6fcf6f;--bad:#ff8a80;--warn:#e0b040;--line:#3a3a36}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1180px;margin:0 auto;padding:20px 16px 48px}h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.15rem;margin:0 0 4px}
p.sub,.note{color:var(--muted);margin:0 0 12px;font-size:.9rem}.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr))}
section.card{margin-top:0}.span{grid-column:1/-1}
section.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;min-width:0}
.kpis{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin-top:16px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}.kpi b{display:block;font-size:1.5rem}
.kpi span{color:var(--muted);font-size:.85rem}table{border-collapse:collapse;width:100%;font-size:.85rem}
th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}.wrap{overflow-x:auto}
.st{font-weight:600;white-space:nowrap}.PASS,.MEASURED{color:var(--good)}.FAIL{color:var(--bad)}.NOT_RUN,.UNKNOWN,.UNREADABLE{color:var(--warn)}
svg.chart{width:100%;height:auto;display:block}.t{fill:var(--ink);font-size:11.5px}.tick{fill:var(--muted);font-size:10.5px}
.axl{fill:var(--muted);font-size:11px}.val{fill:var(--muted);font-size:11px}.gl{stroke:var(--grid);stroke-width:1}line.axis{stroke:var(--axis);stroke-width:1}
.b1{fill:var(--series-1)}.b2{fill:var(--series-2)}.b3{fill:var(--series-3)}.bm{fill:var(--axis)}
.dot1{fill:var(--series-1);stroke:var(--card);stroke-width:2}.dot2{fill:none;stroke:var(--series-2);stroke-width:2}
.dotm{fill:var(--axis);opacity:.55}.ln1{stroke:var(--series-1);stroke-width:2;fill:none}.ln2{stroke:var(--series-2);stroke-width:2;fill:none}
.thr{stroke:var(--muted);stroke-dasharray:4 4;stroke-width:1}.zone{fill:var(--muted);font-size:10.5px;opacity:.8}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.82rem;color:var(--muted);margin:6px 0 0}
.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.banner{border-left:4px solid var(--warn);padding:8px 12px;background:var(--card);border-radius:6px;font-size:.88rem;margin-top:12px}
details{margin-top:8px}summary{cursor:pointer;color:var(--muted);font-size:.85rem}code{font-size:.85em}
"""
GLYPH = {"PASS": "✓", "FAIL": "✗", "NOT_RUN": "–", "MEASURED": "●", "UNKNOWN": "?", "UNREADABLE": "?"}


def status(s: str) -> str:
    return f'<span class="st {esc(s)}">{GLYPH.get(s, "?")} {esc(s)}</span>'


def table(headers: list[tuple[str, bool]], rows: list[list[object]], caption: str) -> str:
    head = "".join(f'<th class="{"n" if numeric else ""}" scope="col">{esc(h)}</th>' for h, numeric in headers)
    body = ""
    for row in rows:
        cells = ""
        for (h, numeric), cell in zip(headers, row):
            raw = isinstance(cell, str) and cell.startswith("<")
            cells += f'<td class="{"n" if numeric else ""}">{cell if raw else esc(fmt(cell) if isinstance(cell, (int, float)) else cell)}</td>'
        body += f"<tr>{cells}</tr>"
    return f'<div class="wrap"><table><caption class="note" style="text-align:left">{esc(caption)}</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def card(title: str, sub: str, inner: str, span: bool = False) -> str:  # `sub` is trusted markup built here
    return f'<section class="card{" span" if span else ""}"><h2>{esc(title)}</h2><p class="sub">{sub}</p>{inner}</section>'


def not_run_card(title: str, section: dict) -> str:
    return card(title, "", f'<p class="banner"><span class="st NOT_RUN">– NOT_RUN</span> {esc(section.get("reason", ""))}</p>')


# ---- charts -----------------------------------------------------------------------------------------

def martin_chart(m: dict) -> str:
    box = (52, 14, 620, 300)
    x, y = svg.linear(0, 1, box[0], box[2]), svg.linear(0, 1, box[3], box[1])
    ticks = [0, 0.25, 0.5, 0.75, 1]
    parts = [svg.axes(x, y, ticks, ticks, box, "Abstractness A", "Instability I")]
    parts.append(f'<line class="ln2" x1="{svg.num(x(0))}" y1="{svg.num(y(1))}" x2="{svg.num(x(1))}" y2="{svg.num(y(0))}" '
                 f'stroke-dasharray="6 4"><title>Main sequence: A + I = 1</title></line>')
    parts.append(text(x(0) + 8, y(0) - 8, "zone of pain", "zone"))
    parts.append(text(x(1) - 8, y(1) + 16, "zone of uselessness", "zone", "end"))
    parts.append(text(x(0.5) + 10, y(0.5) - 8, "main sequence", "zone"))
    for r in m["modules"]:
        if r["instability"] is not None:
            parts.append(f'<circle class="dotm" cx="{svg.num(x(r["abstractness"]))}" cy="{svg.num(y(r["instability"]))}" r="3.5">'
                         f'<title>{esc(r["name"])}: I={fmt(r["instability"])} A={fmt(r["abstractness"])} D={fmt(r["distance"])}</title></circle>')
    labels = []
    for r in m["layers"]:
        if r["instability"] is None:
            continue
        cx, cy = x(r["abstractness"]), y(r["instability"])
        tip = f'{r["name"]}: I={fmt(r["instability"])} A={fmt(r["abstractness"])} D={fmt(r["distance"])} ({r["zone"]})'
        parts.append(f'<circle class="dot1" cx="{svg.num(cx)}" cy="{svg.num(cy)}" r="7"><title>{esc(tip)}</title></circle>')
        labels.append((cy + 4, f'{r["name"]}  D={fmt(r["distance"])}', cx))
    placed = svg.spread_labels([(yy, lab, str(cx)) for yy, lab, cx in labels])
    for yy, lab, cx in placed:
        parts.append(text(float(cx) + 13, yy, lab, "t"))
    return svg.frame(box[3] + 44, "".join(parts), "Instability against abstractness for each layer and module")


def cc_chart(o: dict) -> str:
    rows = [(f"rank {r}  ({lo})", o["ranks"][r], "b1" if r in "AB" else "b2" if r in "CD" else "bm", f"{o['ranks'][r]} functions")
            for r, lo in zip("ABCDEF", ("CC 1-5", "6-10", "11-20", "21-30", "31-40", "41+"))]
    return svg.hbars(rows, max(o["ranks"].values()) or 1, "Number of functions per cyclomatic-complexity rank", label_w=130)


def mi_chart(mods: list[dict]) -> str:
    rows = [(m["module"], m["mi"], "b1", f'MI {m["mi"]} (rank {m["mi_rank"]}), {m["sloc"]} SLOC') for m in sorted(mods, key=lambda m: (m["mi"], m["module"]))]
    return svg.hbars(rows, 100, "Maintainability index per module, lowest first", label_w=170)


def tests_chart(layers: list[dict]) -> str:
    rows = [(r["layer"], r["tests_direct"], "b1", f'{r["tests_direct"]} tests in {r["files_direct"]} files import this layer directly; '
             f'{r["tests_transitive"]} reach it transitively') for r in layers]
    return svg.hbars(rows, max(r["tests_direct"] for r in layers) or 1, "Tests importing each layer directly", label_w=120)


def coverage_chart(layers: list[dict]) -> str:
    rows = [(r["layer"], r["line_percent"] or 0, "b3", f'{r["covered"]}/{r["statements"]} statements') for r in layers]
    return svg.hbars(rows, 100, "Line coverage percent per layer", unit="%", label_w=120)


def latency_chart(perf: dict) -> str:
    names = {"testclient": ("TestClient (in-process)", "b1"), "uvicorn": ("uvicorn (loopback socket)", "b2")}
    data = {t: {e["endpoint"]: e for e in body.get("endpoints", [])} for t, body in perf["transports"].items() if body.get("status") == "MEASURED"}
    endpoints = sorted({ep for d in data.values() for ep in d})
    if not endpoints:
        return ""
    left, right, top, row_h = 210, 600, 22, 34
    lo, hi = 1.0, 10000.0
    x = svg.log10s(lo, hi, left, right)
    parts = []
    for t in (1, 10, 100, 1000, 10000):
        parts.append(f'<line class="gl" x1="{svg.num(x(t))}" x2="{svg.num(x(t))}" y1="{top}" y2="{top + len(endpoints) * row_h}"/>')
        parts.append(text(x(t), top + len(endpoints) * row_h + 14, f"{t:,} ms", "tick", "middle"))
    for thr, label in ((100, "100 ms instant"), (400, "400 ms Doherty")):
        parts.append(f'<line class="thr" x1="{svg.num(x(thr))}" x2="{svg.num(x(thr))}" y1="{top - 6}" y2="{top + len(endpoints) * row_h}"/>')
        parts.append(text(x(thr) + (-4 if thr == 100 else 4), top - 9, label, "tick", "end" if thr == 100 else "start"))
    for i, ep in enumerate(endpoints):
        y0 = top + i * row_h
        parts.append(text(left - 8, y0 + 20, ep.replace("/api/cases/", "…/"), "t", "end"))
        for j, (t, (_, cls)) in enumerate(names.items()):
            e = data.get(t, {}).get(ep)
            if not e:
                continue
            w = max(x(max(e["p95_ms"], lo)) - left, 2)
            parts.append(f'<rect class="{cls}" x="{left}" y="{y0 + 4 + j * 12}" width="{svg.num(w)}" height="10" rx="2">'
                         f'<title>{esc(t)} {esc(ep)}: p50 {fmt(e["p50_ms"])} ms, p95 {fmt(e["p95_ms"])} ms, p99 {fmt(e["p99_ms"])} ms (n={e["n"]})</title></rect>')
            parts.append(text(left + w + 5, y0 + 13 + j * 12, f'{fmt(e["p95_ms"])} ms', "val"))
    return svg.frame(top + len(endpoints) * row_h + 26, "".join(parts), "p95 latency per endpoint on a logarithmic axis")


def scatter_fit(points: list[tuple[float, float]], fit: tuple[float, float] | None, xlabel: str, ylabel: str, label: str,
                second: list[tuple[float, float]] | None = None) -> str:
    box = (56, 14, 620, 250)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    xmax, ymax = max(xs) * 1.05, max(ys + [p[1] for p in (second or [])]) * 1.08
    x, y = svg.linear(0, xmax, box[0], box[2]), svg.linear(0, ymax, box[3], box[1])
    parts = [svg.axes(x, y, svg.nice_ticks(0, xmax), svg.nice_ticks(0, ymax), box, xlabel, ylabel)]
    if fit:
        c0, c1 = fit
        parts.append(f'<line class="ln1" x1="{svg.num(x(0))}" y1="{svg.num(y(c0))}" x2="{svg.num(x(xmax))}" y2="{svg.num(y(c0 + c1 * xmax))}"><title>least-squares line</title></line>')
    for px, py in second or []:
        parts.append(f'<circle class="dot2" cx="{svg.num(x(px))}" cy="{svg.num(y(py))}" r="5"><title>two-term prediction {fmt(py)} ms</title></circle>')
    for px, py in points:
        parts.append(f'<circle class="dot1" cx="{svg.num(x(px))}" cy="{svg.num(y(py))}" r="4.5"><title>{fmt(px)}: {fmt(py)} ms measured</title></circle>')
    return svg.frame(box[3] + 44, "".join(parts), label)


def residual_chart(points: list[tuple[float, float]], label: str, xlabel: str) -> str:
    box = (56, 10, 620, 120)
    xs, rs = [p[0] for p in points], [p[1] for p in points]
    span = max(abs(min(rs)), abs(max(rs)), 1e-6) * 1.15
    x, y = svg.linear(0, max(xs) * 1.05, box[0], box[2]), svg.linear(-span, span, box[3], box[1])
    parts = [svg.axes(x, y, svg.nice_ticks(0, max(xs) * 1.05, 4), [-span, 0, span], box, xlabel, "residual (ms)",
                      yfmt=lambda v: fmt(v, 1))]
    for px, py in points:
        parts.append(f'<circle class="dot1" cx="{svg.num(x(px))}" cy="{svg.num(y(py))}" r="4"><title>residual {fmt(py)} ms at {fmt(px)}</title></circle>')
    return svg.frame(box[3] + 44, "".join(parts), label)


# ---- page -------------------------------------------------------------------------------------------

def _legend(*items: tuple[str, str]) -> str:
    return '<div class="legend">' + "".join(f'<span><i class="{c}"></i>{esc(t)}</span>' for c, t in items) + "</div>"


def render_html(doc: dict) -> str:
    s, meta = doc["sections"], doc["meta"]
    plat, src = meta["platform"], meta["source"]
    counts = {"PASS": 0, "FAIL": 0, "NOT_RUN": 0}
    for b in doc["budgets"]:
        counts[b["status"]] += 1
    kpis = []
    if s["tests"]["status"] == "MEASURED":
        t = s["tests"]["summary"]
        kpis.append((f'{t["tests_static"]}', f'tests ({t["asserts"]} assertions)'))
    if s["coverage"]["status"] == "MEASURED":
        kpis.append((f'{fmt(s["coverage"]["summary"]["percent"], 1)}%', "line+branch coverage"))
    else:
        kpis.append(("NOT_RUN", "coverage (no report)"))
    c = s["complexity"]
    kpis.append((f'{c["overall"]["functions"]}', f'functions, mean CC {fmt(c["overall"]["mean"], 1)}'))
    kpis.append((f'{fmt(c["summary"]["sloc_weighted_mi"], 1)}', "SLOC-weighted maintainability"))
    kpis.append((f'{fmt(s["martin"]["summary"]["mean_layer_distance"])}', "mean layer distance D"))
    kpis.append((f'{counts["PASS"]}/{counts["PASS"] + counts["FAIL"] + counts["NOT_RUN"]}', f'budgets pass ({counts["FAIL"]} fail, {counts["NOT_RUN"]} not run)'))
    cards = []

    # budgets
    cards.append(card("Budgets", "Numeric limits as tests. Basis: principled rule, external threshold, or ratchet (current value plus headroom).",
                      table([("ID", False), ("Budget", False), ("Actual", True), ("Limit", True), ("Basis", False), ("Status", False)],
                            [[b["id"], b["description"], "n/a" if b["actual"] is None else b["actual"], f'{b["op"]} {fmt(b["limit"])}',
                              b["basis"], status(b["status"])] for b in doc["budgets"]], "Budget evaluation; NOT_RUN means an input section was unavailable"), True))

    # martin
    m = s["martin"]
    rows = [[r["name"], r["modules"], r["ca"], r["ce"], r["instability"], r["abstractness"], r["distance"], r["zone"]] for r in m["layers"]]
    cards.append(card("Package metrics (Martin)", "Instability I = Ce/(Ca+Ce), abstractness A = Na/Nc, distance D = |A+I-1|. Large dots are layers, small grey dots modules.",
                      martin_chart(m) + _legend(("b1", "layer"), ("bm", "module")) +
                      table([("Layer", False), ("Modules", True), ("Ca", True), ("Ce", True), ("I", True), ("A", True), ("D", True), ("Zone", False)], rows,
                            "Coupling unit is the module; only intra-project imports count") +
                      f'<p class="note">SDP violations: {len(m["summary"]["sdp_violations"])}; layer cycles: {len(m["summary"]["layer_cycles"])}; '
                      f'module cycles: {len(m["summary"]["module_cycles"])}. The domain layer is stable and concrete by construction (frozen contracts and pure rules), so D is 1.0 by the formula; '
                      f'see README.</p>', True))

    # complexity
    hot = [[h["function"], h["cc"], h["rank"]] for h in c["hotspots"]]
    cards.append(card("Cyclomatic complexity", "McCabe (1976) per function via radon; ranks A-F.", cc_chart(c["overall"]) +
                      table([("Hotspot", False), ("CC", True), ("Rank", False)], hot, "Highest-complexity functions (refactoring candidates, not defects)")))
    cards.append(card("Maintainability index", "Higher is better; radon rank A is 20 or more. Size-weighted mean above.", mi_chart(c["modules"])))

    # tests and coverage
    if s["tests"]["status"] == "MEASURED":
        t = s["tests"]
        cards.append(card("Test inventory", f'{t["summary"]["test_files"]} files; pytest collects {t["summary"]["tests_collected_by_pytest"]}. Static attribution by import (a test can count for several layers).',
                          tests_chart(t["by_layer"])))
    else:
        cards.append(not_run_card("Test inventory", s["tests"]))
    if s["coverage"]["status"] == "MEASURED":
        cards.append(card("Coverage", "coverage.py, branch mode. Executed is not verified.", coverage_chart(s["coverage"]["layers"])))
    else:
        cards.append(not_run_card("Coverage", s["coverage"]))

    # performance
    perf = s["performance"]
    lat = latency_chart(perf)
    perf_rows = []
    for tname, body in sorted(perf["transports"].items()):
        if body.get("status") != "MEASURED":
            perf_rows.append([tname, "-", "-", "-", "-", "-", status("NOT_RUN")])
            continue
        for e in body["endpoints"]:
            perf_rows.append([tname, e["endpoint"], e["n"], e["p50_ms"], e["p95_ms"], e["p99_ms"],
                              "≤100 ms" if e["p95_within_instant"] else "≤400 ms" if e["p95_within_doherty"] else "over 400 ms"])
    cards.append(card("HTTP latency (measurement)", "Measured on " + esc(plat["label"]) + ". Bars are p95 on a log axis; dashed lines are 100 ms (instant) and 400 ms (Doherty and Thadani 1982).",
                      lat + _legend(("b1", "TestClient, in-process"), ("b2", "real uvicorn on 127.0.0.1")) +
                      table([("Transport", False), ("Endpoint", False), ("n", True), ("p50 ms", True), ("p95 ms", True), ("p99 ms", True), ("p95 band", False)],
                            perf_rows, "Latency percentiles in milliseconds; p99 with n below 100 is close to the maximum"), True))
    vs = perf["verify_scaling"]
    pts = [(float(p["cells"]), p["ms"]) for p in vs["points"]]
    cards.append(card("verify() duration against matrix size (measurement)", f'T = {fmt(vs["c0_ms"])} + {fmt(vs["c1_ms_per_cell"], 3)}·cells ms, R² = {fmt(vs["r2"], 3)}. Matrix = actors × states × 5 actions.',
                      scatter_fit(pts, (vs["c0_ms"], vs["c1_ms_per_cell"]), "matrix cells", "verify_runtime (ms)", "verify duration against matrix size")))

    # scaling
    sc = s["scaling"]
    fit = sc["fit"]
    sp = [(float(p["size"]), p["ms"]) for p in sc["points"]]
    two = [(float(p["size"]), p["two_term_predicted_ms"]) for p in sc["points"]]
    cards.append(card("closure() scaling (measurement)",
                      f'T = {fmt(fit["c0_ms"], 3)} + {fmt(fit["c1_ms_per_element"] * 1000, 3)} µs·(V+E), R² = {fmt(fit["r2"], 3)}; two-term R² = {fmt(fit["two_term_r2"], 3)} '
                      f'(node {fmt(fit["two_term_cV_ms_per_node"] * 1000, 3)} µs, edge {fmt(fit["two_term_cE_ms_per_edge"] * 1000, 3)} µs); log-log exponent {fmt(fit["loglog_exponent"], 3)}; quadratic R² = {fmt(fit["alt_quadratic_r2"], 3)}.',
                      scatter_fit(sp, (fit["c0_ms"], fit["c1_ms_per_element"]), "V + E (nodes + edges)", "closure (ms)", "closure time against graph size", two) +
                      _legend(("b1", "measured, with V+E least-squares line"), ("b2", "two-term prediction (ring)")) +
                      residual_chart([(float(p["size"]), p["residual_ms"]) for p in sc["points"]], "Residuals of the V+E fit", "V + E")))

    # lane reports and yield
    lanes = s["lane_reports"]
    lane_rows = [[g["group"], g["lane"], status(g["status"]), ", ".join(r["file"] for r in g["reports"]) or g.get("reason", "")] for g in lanes["groups"]]
    cards.append(card("Other lanes' reports", "Aggregated read-only from reports/. A missing report is NOT_RUN, never a pass.",
                      table([("Group", False), ("Lane", False), ("Status", False), ("Reports / reason", False)], lane_rows, "Lane report aggregation"), True))
    y = s["verification_yield"]
    y_rows = [[t["technique"], t["kind"], t["states_explored"], "n/a" if t.get("findings") is None else t["findings"],
               "n/a" if t.get("duration_s") is None else t["duration_s"], "n/a" if t.get("states_per_s") is None else t["states_per_s"], status(t["status"])]
              for t in y["techniques"]]
    cards.append(card("Verification yield", "States explored per technique. Two are measured here; the rest are copied from lane reports when they publish a state count.",
                      table([("Technique", False), ("Source", False), ("States", True), ("Findings", True), ("Seconds", True), ("States/s", True), ("Status", False)], y_rows,
                            "Findings are counts each technique reports; they are not comparable across techniques"), True))

    head = (f'<h1>EIJA Studio metrics</h1><p class="sub">Platform: <b>{esc(plat["label"])}</b> · commit <code>{esc((src.get("commit") or "unknown")[:12])}</code>'
            f'{" (source differs from commit)" if src.get("dirty") else ""} · profile {esc(meta["profile"])}'
            f'{" · generated " + esc(meta["generated_at"]) if meta.get("generated_at") else ""}</p>'
            f'<p class="banner">{esc(meta["timing_note"])}</p>')
    kpi_html = '<div class="kpis">' + "".join(f'<div class="kpi"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for v, k in kpis) + "</div>"
    body = head + kpi_html + f'<div class="gl">{"".join(cards[:1])}</div>' + "".join(cards[1:])
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>EIJA Studio metrics</title><style>' + CSS + '</style></head><body><main>' + body + '</main></body></html>\n')


def render_markdown(doc: dict) -> str:
    s, meta = doc["sections"], doc["meta"]
    plat, src = meta["platform"], meta["source"]
    out = ["# EIJA Studio metrics snapshot", "",
           f"- Platform: **{plat['label']}** ({plat['machine']})",
           f"- Commit: `{src.get('commit')}`" + (" (source differs from commit)" if src.get("dirty") else ""),
           f"- Profile: {meta['profile']}" + (f", generated {meta['generated_at']}" if meta.get("generated_at") else ""),
           f"- Tools: " + ", ".join(f"{k} {v}" for k, v in sorted(meta["tools"].items())),
           "", f"> {meta['timing_note']}", "", "## Budgets", "",
           "| ID | Budget | Actual | Limit | Basis | Status |", "|---|---|---|---|---|---|"]
    for b in doc["budgets"]:
        out.append(f"| {b['id']} | {b['description']} | {'n/a' if b['actual'] is None else fmt(b['actual'])} | {b['op']} {fmt(b['limit'])} | {b['basis']} | {b['status']} |")
    m = s["martin"]
    out += ["", "## Package metrics (Martin)", "", "| Layer | Modules | Ca | Ce | I | A | D | Zone |", "|---|---:|---:|---:|---:|---:|---:|---|"]
    out += [f"| {r['name']} | {r['modules']} | {r['ca']} | {r['ce']} | {fmt(r['instability'])} | {fmt(r['abstractness'])} | {fmt(r['distance'])} | {r['zone']} |" for r in m["layers"]]
    out += ["", f"SDP violations {len(m['summary']['sdp_violations'])}, layer cycles {len(m['summary']['layer_cycles'])}, module cycles {len(m['summary']['module_cycles'])}."]
    c = s["complexity"]
    o = c["overall"]
    out += ["", "## Complexity and maintainability", "",
            f"{o['functions']} functions; mean CC {fmt(o['mean'])}, median {fmt(o['median'])}, p90 {fmt(o['p90'])}, max {o['max']}. "
            f"Ranks: " + ", ".join(f"{k}={v}" for k, v in o["ranks"].items()) +
            f". SLOC {c['summary']['sloc']}, SLOC-weighted MI {fmt(c['summary']['sloc_weighted_mi'])}, lowest module MI {fmt(c['summary']['min_mi'])}.",
            "", "| Hotspot | CC | Rank |", "|---|---:|---|"] + [f"| {h['function']} | {h['cc']} | {h['rank']} |" for h in c["hotspots"]]
    t = s["tests"]
    out += ["", "## Tests and coverage", ""]
    if t["status"] == "MEASURED":
        ts = t["summary"]
        out += [f"{ts['tests_static']} tests statically ({ts['tests_collected_by_pytest']} collected by pytest), {ts['asserts']} assertions, {ts['raises_blocks']} raises-blocks.", "",
                "| Layer | Test files (direct) | Tests (direct) | Tests (transitive) |", "|---|---:|---:|---:|"]
        out += [f"| {r['layer']} | {r['files_direct']} | {r['tests_direct']} | {r['tests_transitive']} |" for r in t["by_layer"]]
    else:
        out.append(f"Tests: NOT_RUN ({t['reason']})")
    cv = s["coverage"]
    out.append("")
    if cv["status"] == "MEASURED":
        out += [f"Coverage: {fmt(cv['summary']['percent'])}% ({cv['summary']['covered']}/{cv['summary']['statements']} statements, "
                f"{cv['summary']['covered_branches']}/{cv['summary']['branches']} branches).", "", "| Layer | Statements | Line % | Branch % |", "|---|---:|---:|---:|"]
        out += [f"| {r['layer']} | {r['statements']} | {fmt(r['line_percent'])} | {fmt(r['branch_percent'])} |" for r in cv["layers"]]
    else:
        out.append(f"Coverage: NOT_RUN ({cv['reason']})")
    p = s["performance"]
    out += ["", f"## HTTP latency (measured on {plat['label']})", "", "Thresholds: 100 ms instant, 400 ms Doherty. Milliseconds.", "",
            "| Transport | Endpoint | Kind | n | p50 | p95 | p99 | Band |", "|---|---|---|---:|---:|---:|---:|---|"]
    for tname, body in sorted(p["transports"].items()):
        if body.get("status") != "MEASURED":
            out.append(f"| {tname} | - | - | - | - | - | - | NOT_RUN: {body.get('reason', '')} |")
            continue
        for e in body["endpoints"]:
            band = "<=100" if e["p95_within_instant"] else "<=400" if e["p95_within_doherty"] else "over 400"
            out.append(f"| {tname} | {e['endpoint']} | {e['kind']} | {e['n']} | {fmt(e['p50_ms'])} | {fmt(e['p95_ms'])} | {fmt(e['p99_ms'])} | {band} |")
    vs = p["verify_scaling"]
    out += ["", f"verify_runtime: T = {fmt(vs['c0_ms'])} + {fmt(vs['c1_ms_per_cell'], 3)} * cells ms, R^2 = {fmt(vs['r2'], 3)} over {len(vs['points'])} matrix sizes "
            f"({min(q['cells'] for q in vs['points'])} to {max(q['cells'] for q in vs['points'])} cells)."]
    fit = s["scaling"]["fit"]
    out += ["", "## closure() scaling (measured)", "",
            f"- {fit['model']}: c0 = {fmt(fit['c0_ms'], 3)} ms, c1 = {fmt(fit['c1_ms_per_element'] * 1000, 3)} us per element, R^2 = {fmt(fit['r2'], 4)}",
            f"- {fit['two_term_model']}: cV = {fmt(fit['two_term_cV_ms_per_node'] * 1000, 3)} us, cE = {fmt(fit['two_term_cE_ms_per_edge'] * 1000, 3)} us, R^2 = {fmt(fit['two_term_r2'], 4)}",
            f"- log-log exponent {fmt(fit['loglog_exponent'], 3)} (R^2 {fmt(fit['loglog_r2'], 3)}); quadratic alternative R^2 = {fmt(fit['alt_quadratic_r2'], 3)}",
            f"- {fit['points']} points, max |residual| {fmt(fit['max_abs_residual_ms'])} ms", "", fit["reading"]]
    out += ["", "## Other lanes' reports", "", "| Group | Lane | Status | Detail |", "|---|---|---|---|"]
    out += [f"| {g['group']} | {g['lane']} | {g['status']} | {', '.join(r['file'] for r in g['reports']) or g.get('reason', '')} |" for g in s["lane_reports"]["groups"]]
    out += ["", "## Verification yield", "", "| Technique | Source | States | Findings | Seconds | States/s |", "|---|---|---:|---:|---:|---:|"]
    out += [f"| {r['technique']} | {r['kind']} | {fmt(r['states_explored'])} | {fmt(r.get('findings'))} | {fmt(r.get('duration_s'), 4)} | {fmt(r.get('states_per_s'))} |"
            for r in s["verification_yield"]["techniques"]]
    return "\n".join(out) + "\n"
