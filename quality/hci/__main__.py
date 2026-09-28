"""CLI: python -m quality.hci {prereq|run|check}.

Exit codes: 0 ok, 1 budget regression / drift / journey failure, 2 misuse, 3 NOT_RUN (missing prerequisite; never a pass).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import journey, report

ROOT = Path(__file__).resolve().parents[2]
NOT_RUN = 3


def cmd_prereq(_: argparse.Namespace) -> int:
    ok, detail = journey.prerequisites()
    print(("READY: Google Chrome " + detail) if ok else "NOT_RUN: " + detail)
    return 0 if ok else NOT_RUN


def cmd_run(args: argparse.Namespace) -> int:
    ok, detail = journey.prerequisites()
    if not ok:
        print("NOT_RUN: " + detail)
        return NOT_RUN
    try:
        raw = journey.collect(repeats=args.repeats, headless=not args.headed, identity=args.identity)
    except journey.ReleaseIdentityUnavailable as exc:
        print("NOT_RUN: " + str(exc))
        return NOT_RUN
    except journey.JourneyError as exc:
        print("FAIL: the journey did not complete: " + str(exc))
        return 1
    rep = report.build_report(raw, date=args.date)
    out = Path(args.out)
    report.write_text(out / "report.json", report.dumps(rep))
    report.write_text(out / "REPORT.md", report.render_markdown(rep))
    report.write_text(out / "trace.json", report.dump_trace(raw))
    if args.publish_docs:
        report.publish_docs(rep, raw)
    fails = [b for b in rep["budgets"] if b["status"] == "FAIL"]
    gaps = [b for b in rep["budgets"] if b["status"] == "GAP"]
    print(f"HCI report written to {out} ({len(rep['recommendations'])} recommendations; budgets: "
          f"{sum(b['status'] == 'PASS' for b in rep['budgets'])} PASS, {len(gaps)} GAP, {len(fails)} FAIL)")
    for b in fails:
        print(f"FAIL {b['id']}: {b['value']} {b['unit']} > limit {b['limit']}")
    return 1 if fails else 0


def cmd_check(args: argparse.Namespace) -> int:
    ok, message = report.check_docs(strict=args.strict)
    print(("OK: " if ok else "FAIL: ") + message)
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m quality.hci", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prereq", help="report whether Chrome + Playwright + axe are usable (NOT_RUN if not)").set_defaults(func=cmd_prereq)
    run = sub.add_parser("run", help="run the journey and write reports/hci")
    run.add_argument("--out", default=str(ROOT / "reports" / "hci"))
    run.add_argument("--repeats", type=int, default=3, help="pointer journeys for timing (first is fully audited)")
    run.add_argument("--headed", action="store_true")
    run.add_argument("--identity", choices=["harness", "release"], default="harness")
    run.add_argument("--date", default=None, help="stamp the report (default: no timestamp, for determinism)")
    run.add_argument("--publish-docs", action="store_true", help="also write docs/hci/report.snapshot.json and REPORT.md")
    run.set_defaults(func=cmd_run)
    check = sub.add_parser("check", help="drift check, no browser: snapshot == derive(committed trace, current laws + budgets); REPORT.md == render(snapshot)")
    check.add_argument("--strict", action="store_true", help="also fail when the snapshot was taken on different UI bytes (release gate)")
    check.set_defaults(func=cmd_check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
