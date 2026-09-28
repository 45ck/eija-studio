"""Per-function cyclomatic-complexity ratchet built on radon.

radon measures; xenon (a separate nox gate) enforces module and average ranks. Neither can say "this one
legacy function may stay at 45 but nothing may get worse and nothing new may exceed 10", so this module adds
exactly that and nothing more: a checked-in debt list (`complexity_baseline.json`) of functions allowed to
exceed the default budget, each pinned at its measured value.

What it establishes: no function under the measured roots exceeds the budget, except listed debt that has
not grown. What it does NOT establish: that low cyclomatic complexity means the code is correct or readable.
The debt list can only shrink: `--update` lowers or removes entries and never records new offenders.

    python -m quality.gates.complexity_ratchet            # check (exit 1 on any violation)
    python -m quality.gates.complexity_ratchet --update   # tighten the baseline after a refactor
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from radon.complexity import cc_visit
from radon.visitors import Function

ROOT = Path(__file__).resolve().parents[2]
BASELINE = Path(__file__).with_name("complexity_baseline.json")
DEFAULT_ROOTS = ("src/eija_studio", "quality")
# Cyclomatic complexity 10 is the top of radon rank B. Rank C starts at 11.
DEFAULT_MAX = 10
UPDATE = "python -m quality.gates.complexity_ratchet --update"


def _flatten(blocks: list[Function], prefix: str = "") -> dict[str, int]:
    found: dict[str, int] = {}
    for block in blocks:
        name = f"{prefix}{block.name}"
        found[name] = block.complexity
        found.update(_flatten(list(block.closures), f"{name}."))
    return found


def _function_blocks(source: str) -> dict[str, int]:
    """Qualified function/method name -> complexity. Classes are containers, not measured themselves."""
    found: dict[str, int] = {}
    for block in cc_visit(source):
        if isinstance(block, Function):
            # radon also lists methods at top level; the Class branch below qualifies them, so skip them here
            # (unqualified names would collide across classes).
            if not block.is_method:
                found.update(_flatten([block]))
        else:
            for method in block.methods:
                found.update(_flatten([method], f"{block.name}."))
    return found


def measure(roots: tuple[str, ...] = DEFAULT_ROOTS, base: Path = ROOT) -> dict[str, int]:
    """Measure every function under `roots`; keys are `posix/relative/path.py::Qualified.name`."""
    measured: dict[str, int] = {}
    for root in roots:
        for path in sorted((base / root).rglob("*.py")):
            relative = path.relative_to(base).as_posix()
            for name, complexity in _function_blocks(path.read_text(encoding="utf-8")).items():
                measured[f"{relative}::{name}"] = complexity
    return measured


def load_baseline(path: Path = BASELINE) -> dict[str, int]:
    return {str(k): int(v) for k, v in json.loads(path.read_text(encoding="utf-8"))["debt"].items()}


def evaluate(measured: dict[str, int], debt: dict[str, int], default_max: int = DEFAULT_MAX) -> list[str]:
    """Return human-readable violations; an empty list means the ratchet holds."""
    problems = []
    for key in sorted(measured):
        allowed = debt.get(key, default_max)
        if measured[key] > allowed:
            kind = "grew beyond its recorded debt" if key in debt else f"exceeds the budget of {default_max}"
            problems.append(f"{key}: complexity {measured[key]} {kind} (allowed {allowed})")
    for key in sorted(debt):
        if key not in measured:
            problems.append(f"{key}: listed as debt but no longer exists; remove it ({UPDATE})")
        elif measured[key] < debt[key]:
            problems.append(
                f"{key}: improved to {measured[key]} (recorded {debt[key]}); tighten it ({UPDATE})"
            )
    return problems


def tightened(
    measured: dict[str, int], debt: dict[str, int], default_max: int = DEFAULT_MAX
) -> dict[str, int]:
    """The debt list after a refactor: lowered values, resolved entries dropped, no new debt ever added."""
    return {k: measured[k] for k in sorted(debt) if k in measured and measured[k] > default_max}


def write_baseline(debt: dict[str, int], path: Path = BASELINE) -> None:
    body = {"debt": dict(sorted(debt.items()))}
    path.write_bytes((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", maxsplit=1)[0])
    parser.add_argument("--update", action="store_true", help="tighten the baseline (never adds new debt)")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    args = parser.parse_args(argv)
    measured, debt = measure(), load_baseline(args.baseline)
    if args.update:
        write_baseline(tightened(measured, debt), args.baseline)
        # After tightening, anything still failing is genuinely new or grown debt: a human must fix the code.
        debt = load_baseline(args.baseline)
    problems = evaluate(measured, debt)
    for line in problems:
        print(f"FAIL {line}")
    counts = f"{len(measured)} functions, {len(debt)} recorded debt, {len(problems)} violations"
    print(f"complexity ratchet: {counts}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
