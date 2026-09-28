"""Command line: `python -m quality.metrics <command>`.

    collect   measure everything and write reports/metrics.json (--profile quick|full)
    coverage  run the test suite under coverage.py -> reports/coverage/coverage.json
    check     evaluate budgets on a metrics document; exit 1 when any budget FAILs (NOT_RUN is shown, not failed)
    render    write the dashboard and Markdown snapshot from a metrics document
    drift     verify docs/metrics/{index.html,latest.md} are exactly what docs/metrics/snapshot.json renders to
    snapshot  collect (full profile) and render into docs/metrics/ (the committed, platform-labelled snapshot)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import ROOT
from . import budgets, collect as collector, dashboard, inventory
from .common import dumps, write_text

DOCS = ROOT / "docs" / "metrics"
SNAPSHOT = DOCS / "snapshot.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _render(doc: dict, out_dir: Path) -> list[Path]:
    targets = {out_dir / "index.html": dashboard.render_html(doc), out_dir / "latest.md": dashboard.render_markdown(doc)}
    for path, content in targets.items():
        write_text(path, content)
    return list(targets)


def cmd_collect(a) -> int:
    doc = collector.collect(a.profile, generated_at=a.generated_at, real_server=not a.no_real_server)
    collector.write(doc, a.out)
    print(f"wrote {a.out} ({a.profile} profile); budgets: {budgets.summary(doc['budgets'])}")
    return 0


def cmd_coverage(_a) -> int:
    result = inventory.run_coverage()
    print(json.dumps(result))
    return 0 if result["status"] == "MEASURED" and result.get("pytest_returncode") == 0 else 1


def cmd_check(a) -> int:
    doc = _load(a.input)
    results = budgets.evaluate(doc)  # re-evaluate: the budgets in code are the source of truth
    for r in results:
        detail = r.get("reason", "") if r["status"] == "NOT_RUN" else f"{r['actual']} {r['op']} {r['limit']}"
        print(f"{r['status']:8} {r['id']:9} {r['description']} [{detail}]")
    counts = budgets.summary(results)
    print(counts)
    return 1 if counts["FAIL"] else 0


def cmd_render(a) -> int:
    for p in _render(_load(a.input), a.out_dir):
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return 0


def cmd_drift(_a) -> int:
    if not SNAPSHOT.exists():
        print("NOT_RUN: docs/metrics/snapshot.json missing")
        return 1
    doc = _load(SNAPSHOT)
    bad = []
    for name, content in (("index.html", dashboard.render_html(doc)), ("latest.md", dashboard.render_markdown(doc))):
        path = DOCS / name
        if not path.exists() or path.read_bytes() != content.encode("utf-8"):
            bad.append(name)
    if bad:
        print("DRIFT: docs/metrics/" + ", ".join(bad) + " differ from what snapshot.json renders to; run `python -m quality.metrics render --input docs/metrics/snapshot.json --out-dir docs/metrics`")
        return 1
    stale = [k for k, v in collector.structural_sections(pytest_collection=False).items()
             if k in ("martin", "complexity") and v != doc["sections"].get(k)]
    print("OK: dashboard and latest.md match snapshot.json" +
          (f"; NOTE: source has changed since the snapshot in sections {stale} (re-run `snapshot` on the reference machine)" if stale else ""))
    return 0


def cmd_snapshot(a) -> int:
    doc = collector.collect("full", generated_at=a.generated_at)
    write_text(SNAPSHOT, dumps(doc))
    collector.write(doc)
    _render(doc, DOCS)
    print("wrote docs/metrics/{snapshot.json,index.html,latest.md}; budgets:", budgets.summary(doc["budgets"]))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m quality.metrics", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--profile", choices=("quick", "full"), default="quick")
    c.add_argument("--out", type=Path, default=collector.REPORT)
    c.add_argument("--generated-at", default=None, help="ISO date/time to record; omitted by default so output is timestamp-free")
    c.add_argument("--no-real-server", action="store_true", help="skip the uvicorn transport (reports NOT_RUN for it)")
    c.set_defaults(fn=cmd_collect)
    sub.add_parser("coverage").set_defaults(fn=cmd_coverage)
    k = sub.add_parser("check")
    k.add_argument("--input", type=Path, default=collector.REPORT)
    k.set_defaults(fn=cmd_check)
    r = sub.add_parser("render")
    r.add_argument("--input", type=Path, default=collector.REPORT)
    r.add_argument("--out-dir", type=Path, default=ROOT / "reports" / "metrics")
    r.set_defaults(fn=cmd_render)
    sub.add_parser("drift").set_defaults(fn=cmd_drift)
    s = sub.add_parser("snapshot")
    s.add_argument("--generated-at", default=None)
    s.set_defaults(fn=cmd_snapshot)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
