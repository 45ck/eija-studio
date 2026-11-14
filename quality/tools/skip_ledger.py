"""A ledger of the tests the fast tier skips, so a new skip cannot pass unnoticed.

    python -m quality.tools.skip_ledger reports/testing/pytest-fast.xml            # check (the `tests` session runs it)
    python -m quality.tools.skip_ledger reports/testing/pytest-fast.xml --update   # rewrite the ledger after review

nox reports a skipped *session* (quality/tools/nox_report.py), but a skipped *test* inside a green session is
invisible: on 2026-11-13 two tests that need the `smt` extra had been red on `main` for a day while every local run
without z3 skipped them, and four build-hook tests needed setuptools that no gate environment had. The ledger
(`skip_ledger.json`) counts skips per test file and reason, measured with every extra the hosted job installs and no
fetched jar or opt-in variable. The check fails when a (file, reason) pair skips more often than its ledger count,
which is how a missing extra, a new `importorskip` or a test that started skipping shows up. Fewer skips than the
ledger is fine (a fetched jar, an opt-in run); `--update` then lowers the counts, as with any ratchet. Accepting a
new skip is a reviewed diff of the ledger. EIJA_ALLOW_NOT_RUN=1 turns a failure into a NOT_RUN warning.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = Path(__file__).with_name("skip_ledger.json")
SCHEMA = "eija.skip-ledger.v1"


def _file(classname: str) -> str:
    """`tests.graph.test_x.TestClass` -> `tests/graph/test_x.py`: the longest dotted prefix that is a file here."""
    parts = classname.split(".")
    for end in range(len(parts), 0, -1):
        candidate = "/".join(parts[:end]) + ".py"
        if (ROOT / candidate).is_file():
            return candidate
    return classname


def skips(junit: Path) -> Counter[str]:
    """`file: reason` -> count for every skipped test case (xfail is not a skip)."""
    counts: Counter[str] = Counter()
    for case in ET.parse(junit).getroot().iter("testcase"):  # noqa: S314 - our own pytest output
        skipped = case.find("skipped")
        if skipped is None or skipped.get("type") == "pytest.xfail":
            continue
        where = _file(case.get("classname", ""))
        reason = (skipped.get("message") or "").removeprefix("Skipped: ").strip()
        counts[f"{where}: {reason}"] += 1
    return counts


def load(path: Path = LEDGER) -> Counter[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise SystemExit(f"{path}: not a {SCHEMA} file")
    return Counter(data["skips"])


def compare(current: Counter[str], ledger: Counter[str]) -> tuple[list[str], list[str]]:
    """(new or grown skips, entries now skipping less than recorded)."""
    grown = [f"{key} (skipped {n}, ledger {ledger[key]})" for key, n in sorted(current.items()) if n > ledger[key]]
    shrunk = [f"{key} (skipped {current[key]}, ledger {n})" for key, n in sorted(ledger.items()) if current[key] < n]
    return grown, shrunk


def write(current: Counter[str], path: Path = LEDGER) -> None:
    body = {"schema": SCHEMA, "skips": dict(sorted(current.items()))}
    path.write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m quality.tools.skip_ledger")
    parser.add_argument("junit", type=Path)
    parser.add_argument("--update", action="store_true", help="rewrite the ledger with this run's skips")
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    args = parser.parse_args(argv)
    current = skips(args.junit)
    if args.update:
        write(current, args.ledger)
        sys.stdout.write(f"skip ledger written: {sum(current.values())} skips in {len(current)} groups\n")
        return 0
    grown, shrunk = compare(current, load(args.ledger))
    out = [f"skip ledger: {sum(current.values())} skips"]
    out += [f"  fewer skips than recorded (lower the ledger with --update): {line}" for line in shrunk]
    out += [f"  NEW SKIP: {line}" for line in grown]
    if grown:
        out.append("A test that skips where it used to run is NOT_RUN, never a pass. Install the missing extra, fix the test, "
                   "or accept the skip by reviewing `--update`'s diff of quality/tools/skip_ledger.json.")
    sys.stdout.write("\n".join(out) + "\n")
    if grown and os.environ.get("EIJA_ALLOW_NOT_RUN") != "1":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
