"""`python -m verification.smt` -- run the Z3 policy-soundness proof and write reports/formal/smt.json.

Exit status: 0 PASS, 1 FAIL, 3 NOT_RUN (a prerequisite such as z3-solver is missing).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from verification import formal_report as fr

NOT_RUN_EXIT = 3
SUBJECT_FILES = ("domain/models.py", "domain/policy.py")
SUBJECT_FUNCTION = "eija_studio.domain.policy.check_policy"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m verification.smt", description=__doc__)
    ap.add_argument("--out", type=Path, default=fr.ROOT / "reports" / "formal" / "smt.json")
    ap.add_argument("--differential-mutants", type=int, default=1500, help="seeded random multi-field mutants")
    ap.add_argument("--differential-fresh", type=int, default=500, help="seeded fully random candidates")
    ap.add_argument("--seed", type=int, default=20260928)
    ap.add_argument("--write-snapshot", action="store_true", help="regenerate verification/smt/accepted_set.json")
    args = ap.parse_args(argv)

    try:
        import z3  # noqa: F401
    except ImportError:
        report = fr.not_run("smt_proof", "z3-solver is not installed; run `pip install -e .[smt]`",
                            fr.kernel_subject(*SUBJECT_FILES, function=SUBJECT_FUNCTION))
        fr.write(args.out, report)
        print("NOT_RUN: z3-solver is not installed (pip install -e .[smt])", file=sys.stderr)
        return NOT_RUN_EXIT

    from . import prove

    if args.write_snapshot:
        prove.SNAPSHOT.write_bytes(prove.snapshot_text(prove.enumerate_accepted()).encode("utf-8"))
        print(f"wrote {prove.SNAPSHOT}")
    report = prove.build_report(args.differential_mutants, args.differential_fresh, args.seed)
    fr.write(args.out, report)
    for check in report["checks"]:
        print(f"{check['status']:4} {check['id']}: {check['detail']}")
    print(f"{report['verdict']}  {args.out}  ({report['measurements']['seconds_total']} s, z3 {report['tool']['z3']})")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
