"""`python -m verification.bmc` -- bounded model check of the real runtime; writes a `bounded_model_check` report.

Exit status: 0 PASS, 1 FAIL (counterexample or failed check), 2 INCONCLUSIVE (time cap hit),
4 PARTIAL (no violation, but the drift check or the self-test could not run: not a PASS).
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from verification import formal_report as fr

from . import report
from .explorer import ALL_TOGGLES, CORE_TOGGLES, Config


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m verification.bmc", description=__doc__)
    ap.add_argument("--depth", type=int, default=6, help="maximum number of moves (commands + environment moves)")
    ap.add_argument("--tier", choices=("full", "release"), default="full")
    ap.add_argument("--out", type=Path, default=None, help="default reports/formal/bmc.json (bmc_deep.json for --tier release)")
    ap.add_argument("--workdir", type=Path, default=fr.ROOT / ".tmp" / "bmc", help="sandbox parent directory (kept off the system temp drive)")
    ap.add_argument("--max-seconds", type=float, default=None, help="wall-clock cap per model; exceeding it is INCONCLUSIVE")
    ap.add_argument("--models", nargs="*", default=None, choices=sorted(report.workflows()),
                    help="workflow variants to check (default: the two most-used for --tier full, all three for --tier release)")
    ap.add_argument("--toggles", choices=("core", "all"), default="core",
                    help="environment moves: core = teacher-assigned active/assigned + registrar active; all adds the other two actors")
    ap.add_argument("--no-self-test", action="store_true", help="skip the seeded-fault (mutant) detection check")
    ap.add_argument("--self-test-depth", type=int, default=3)
    ap.add_argument("--write-snapshot", action="store_true", help="record deterministic statistics into expected_statistics.json")
    args = ap.parse_args(argv)

    cfg = replace(Config(), depth=args.depth, max_seconds=args.max_seconds,
                  toggles=ALL_TOGGLES if args.toggles == "all" else CORE_TOGGLES)
    out = args.out or fr.ROOT / "reports" / "formal" / ("bmc_deep.json" if args.tier == "release" else "bmc.json")
    doc = report.build_report(cfg, args.workdir, run_self_test=not args.no_self_test, self_test_depth=args.self_test_depth,
                              tier=args.tier, model_names=tuple(args.models) if args.models else report.DEFAULT_MODELS[args.tier],
                              check_drift=not args.write_snapshot)
    if args.write_snapshot and doc["verdict"] != "PASS":  # the drift check is excluded on purpose here, so PASS means everything else ran
        print(f"refusing --write-snapshot: the run is {doc['verdict']}; statistics are never recorded over a counterexample, "
              "a cut-off search, or a run whose self-test did not execute")
    elif args.write_snapshot:
        stats = report.deterministic_stats(doc["results"]["models"])
        report.write_snapshot(cfg.depth, stats, cfg.describe())
        print(f"wrote {report.SNAPSHOT}")
    fr.write(out, doc)
    for check in doc["checks"]:
        print(f"{check['status']:4} {check['id']}: {check['detail']}")
    for name, cexs in doc["results"]["counterexamples"].items():
        for c in cexs:
            print(f"COUNTEREXAMPLE [{name}] {c['invariant']} in {c['length']} moves: {c['detail']}\n  " + "\n  ".join(c["trace"]))
    print(f"{doc['verdict']}  {out}  ({doc['measurements']['seconds_total']} s)")
    return {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2, "PARTIAL": 4}[doc["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
