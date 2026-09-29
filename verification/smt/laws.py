"""`python -m verification.smt.laws [--pack DIR ...]` -- the generated-law SMT gate (WBS 1.4).

For each pack (default: every directory under packs/): the generic proof over the pack's generated encoding and, where
the pack keeps a hand-written encoding, the hand <=> generated equivalence gate with its planted-defect controls.
Writes reports/formal/smt-laws-<pack>.json. Exit status: 0 PASS, 1 FAIL, 3 NOT_RUN (z3-solver missing).
"""
from __future__ import annotations

# ruff: noqa: PLC0415 (z3 is an optional extra: it is imported lazily so that its absence reports NOT_RUN)
import argparse
import importlib.util
import sys
from pathlib import Path

from eija_studio.domain.pack import PACKS_ROOT, load_pack
from verification import formal_report as fr

NOT_RUN_EXIT = 3


def _packs(given: list[Path]) -> list[Path]:
    return given or sorted(p for p in PACKS_ROOT.iterdir() if (p / "pack.json").is_file())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m verification.smt.laws", description=__doc__)
    ap.add_argument("--pack", type=Path, action="append", default=[], help="pack directory (repeatable; default: all)")
    ap.add_argument("--out-dir", type=Path, default=fr.ROOT / "reports" / "formal")
    ap.add_argument("--random-mutants", type=int, default=300, help="seeded multi-field mutants in the differential")
    args = ap.parse_args(argv)
    if importlib.util.find_spec("z3") is None:
        sys.stderr.write("NOT_RUN: z3-solver is not installed (pip install -e .[smt])\n")
        return NOT_RUN_EXIT
    from .laws_gate import build_report

    verdicts = []
    for location in _packs(args.pack):
        pack = load_pack(location)
        report = build_report(pack, args.random_mutants)
        fr.write(args.out_dir / f"smt-laws-{pack.id}.json", report)
        verdicts.append(report["verdict"])
        sys.stdout.write(_summary(report) + "\n")
    return 0 if verdicts and all(v == "PASS" for v in verdicts) else 1


def _summary(report: dict) -> str:
    proof, eq = report["generic_proof"], report["equivalence"]
    diff = proof["differential"]
    line = (f"{report['verdict']:4} {report['pack']}: {proof['encoded_laws']} laws encoded, {len(proof['not_encoded'])} NOT_RUN; "
            f"differential {diff['candidates']} candidates, {len(diff['disagreements'])} disagreements; "
            f"planted clause deletion detected={proof['negative_control']['detected']}")
    if "codes" in eq:
        controls = eq["negative_controls"]
        line += (f"; hand<=>generated {eq['codes_equivalent']}/{eq['codes_total']} codes equivalent, "
                 f"{sum(c['detected'] for c in controls)}/{len(controls)} planted pack defects detected")
    else:
        line += f"; equivalence NOT_RUN ({eq['reason']})"
    return line


if __name__ == "__main__":
    raise SystemExit(main())
