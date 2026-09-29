"""`python -m quality.mutation run [--module M ...] [--sample N] [--check] [--write-baseline]`.

Exit status: 0 gate passed / report written, 1 ratchet failed, 2 the measurement itself failed.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import report
from .engine import MutationError, engine_version
from .runner import run_all
from .targets import QUICK_MODULES, by_module

ROOT = Path(__file__).resolve().parents[2]
BASELINE = Path(__file__).with_name("baseline.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m quality.mutation", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="mutate the target modules and write reports/mutation/")
    run.add_argument("--module", action="append", dest="modules", help="repo-relative module path (repeatable)")
    run.add_argument("--quick", action="store_true", help="only the authority core (policy.py): the full-tier gate")
    run.add_argument("--sample", type=int, help="deterministic sample of N mutants per module (estimate; not gated)")
    run.add_argument("--workers", type=int, default=2)
    run.add_argument("--out", type=Path, default=ROOT / "reports" / "mutation")
    run.add_argument("--resume", action="store_true", help="reuse finished jobs whose inputs are unchanged (never in release runs)")
    run.add_argument("--check", action="store_true", help="fail when a score is below its ratchet floor")
    run.add_argument("--write-baseline", action="store_true", help="raise/establish floors from this full run")
    run.add_argument("--allow-lower", action="store_true", help="with --write-baseline: permit lowering a floor")
    args = parser.parse_args(argv)

    targets = by_module(list(QUICK_MODULES) if args.quick else args.modules)
    try:
        mutants = run_all(ROOT, targets, workers=args.workers, sample=args.sample, resume=args.resume)
    except MutationError as error:
        print(f"MUTATION ANALYSIS FAILED (measurement, not a score): {error}", file=sys.stderr)
        return 2
    summary = report.summarise(targets, mutants, engine=f"cosmic-ray {engine_version()}", workers=args.workers, sample=args.sample)
    report.write_json(args.out / "summary.json", summary)
    (args.out / "survivors.md").write_bytes(report.survivors_markdown(mutants, ROOT, summary).encode("utf-8"))
    for module, row in summary["modules"].items():
        print(f"{module}: score={row['score']} killed={row['killed']} survived={row['survived']} "
              f"timeout={row['timeout']} incompetent={row['incompetent']}")
    print(f"overall: score={summary['overall']['score']}; reports in {args.out}")

    baseline = report.load_baseline(BASELINE)
    if args.write_baseline:
        try:
            report.write_json(BASELINE, report.update_baseline(summary, baseline, allow_lower=args.allow_lower))
        except ValueError as error:
            print(f"baseline not updated: {error}", file=sys.stderr)
            return 1
        print(f"baseline written: {BASELINE}")
        return 0
    if args.check:
        failures = report.check(summary, baseline)
        for failure in failures:
            print(f"RATCHET FAIL: {failure}", file=sys.stderr)
        return 1 if failures else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
