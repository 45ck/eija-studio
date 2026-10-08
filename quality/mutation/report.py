"""Turn mutants into `summary.json`, `survivors.md` and a ratchet verdict. Deterministic: sorted, no timestamps."""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any

from .model import EQUIVALENT, INCOMPETENT, SURVIVED, Mutant, tally
from .targets import OPERATORS, Target

SUMMARY_SCHEMA = "eija.mutation-summary.v1"
BASELINE_SCHEMA = "eija.mutation-baseline.v1"
MAX_INCOMPETENT_SHARE = 0.20  # above this the tool is not exercising the code and the score means nothing


def platform_label() -> str:
    return f"{sys.platform} {platform.system()} {platform.release()}, CPython {platform.python_version()}"


def summarise(targets: tuple[Target, ...], mutants: list[Mutant], *, engine: str, workers: int, sample: int | None) -> dict[str, Any]:
    """Per-module and overall counts. `score` = (killed + timeout) / (killed + timeout + survived)."""
    modules = {}
    for target in sorted(targets, key=lambda t: t.module):
        own = [m for m in mutants if m.module == target.module]
        modules[target.module] = {**tally(own), "tests": list(target.tests)}
    return {"schema": SUMMARY_SCHEMA, "engine": engine, "platform": platform_label(), "workers": workers,
            "sample": sample, "operators": list(OPERATORS), "modules": modules, "overall": tally(mutants)}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))


_ADVICE = (
    ("ReplaceStringLiteral", "Assert the exact value of {snippet} where a caller can observe it (role, state, effect, error code or key). A wrong literal must fail an assertion, not just a type check."),
    ("ReplaceReturnValue", "Assert on the value returned by `{function}`; today no test would notice it returning None."),
    ("ReplaceComparisonOperator_Eq_NotEq", "Add one case where the operands are equal and one where they differ; assert the branch taken."),
    ("ReplaceComparisonOperator_NotEq_Eq", "Add one case where the operands are equal and one where they differ; assert the branch taken."),
    ("ReplaceComparisonOperator_Is", "Assert identity versus equality where it matters, with a case that distinguishes them."),
    ("ReplaceMembership", "Add a member and a non-member case and assert the branch taken."),
    ("ReplaceComparisonOperator", "Add a boundary test at equality and one on each side of it; assert the outcome of each."),
    ("ReplaceBinaryOperator", "Assert the computed value with operands that make the operators distinguishable (not 0/1/equal)."),
    ("AddNot", "Cover both truth values of this condition and assert the different outcomes."),
    ("ReplaceTrueWithFalse", "Assert the observable effect of this flag being True; nothing depends on it today."),
    ("ReplaceFalseWithTrue", "Assert the observable effect of this flag being False; nothing depends on it today."),
    ("ReplaceOrWithAnd", "Add a case where exactly one operand is true (each operand alone) and assert the outcome."),
    ("ReplaceAndWithOr", "Add a case where exactly one operand is true (each operand alone) and assert the outcome."),
    ("ReplaceContinueWithBreak", "Add an input where an item that hits `continue` is followed by more items; assert the later items are still processed."),
    ("ReplaceBreakWithContinue", "Add an input where processing must stop at the first hit; assert nothing after it is processed."),
    ("NumberReplacer", "Assert the exact number (a count, version, limit or index) with a value that differs from the mutant by one."),
    ("ExceptionReplacer", "Assert the specific exception type (`pytest.raises(<type>)`), not a superclass."),
    ("ZeroIterationForLoop", "Assert an effect of the loop body with a non-empty iterable."),
    ("RemoveDecorator", "Assert the behaviour the decorator provides."),
    ("ReplaceUnaryOperator_Delete_Not", "Cover both truth values of the negated condition and assert the different outcomes."),
)


def suggest_test(mutant: Mutant, source_lines: list[str]) -> str:
    """A concrete, oracle-first hint. It is a suggestion for a human or agent to write, not a generated test."""
    line = source_lines[mutant.start[0] - 1] if 0 < mutant.start[0] <= len(source_lines) else ""
    snippet = line[mutant.start[1]:mutant.end[1]] if mutant.start[0] == mutant.end[0] else line.strip()
    function = mutant.function or "the module-level code"
    name = mutant.operator.split("/", 1)[-1]
    for prefix, advice in _ADVICE:
        if name.startswith(prefix):
            return advice.format(snippet=f"`{snippet}`", function=function)
    return f"Add a test that fails when `{snippet}` in `{function}` is changed."


def _hunk(diff: str) -> str:
    lines = diff.splitlines()
    start = next((i for i, x in enumerate(lines) if x.startswith("@@")), 0)
    return "\n".join(lines[start:]).rstrip()


def survivors_markdown(mutants: list[Mutant], root: Path, summary: dict[str, Any]) -> str:
    """Every survivor with its diff and a suggested test. Also lists `incompetent` mutants: they hide risk."""
    out = ["# Surviving mutants", "",
           f"Engine: {summary['engine']}. Platform: {summary['platform']}. Sample: {summary['sample'] or 'all mutants'}.", "",
           "A survivor is a behavioural change that the selected tests did not detect. It is a finding about the",
           "tests, not necessarily a bug: an equivalent mutant (same behaviour) cannot be killed and must be",
           "listed under `quality/mutation/equivalents.py` with a reason. Suggested tests are hints, not generated tests.", "",
           "| Module | Score | Killed | Survived | Timeout | Incompetent | Equivalent |", "|---|---|---|---|---|---|---|"]
    for module, row in summary["modules"].items():
        shown = "n/a" if row["score"] is None else f"{row['score']:.1%}"
        out.append(f"| `{module}` | {shown} | {row['killed']} | {row['survived']} | {row['timeout']} | {row['incompetent']} | {row['equivalent']} |")
    for module in summary["modules"]:
        interesting = [m for m in mutants if m.module == module and m.status in {SURVIVED, INCOMPETENT, EQUIVALENT}]
        if interesting:
            out += _module_section(module, interesting, root)
    return "\n".join(out) + "\n"


def _mutant_note(m: Mutant, source: list[str]) -> str:
    """The sentence under one reported mutant, by status."""
    if m.status == SURVIVED:
        return f"Suggested test: {suggest_test(m, source)}"
    if m.status == EQUIVALENT:
        return f"Accepted as equivalent, excluded from the score: {m.equivalent_reason}. Reject this in review if it is wrong."
    return "Not exercised (import or collection failure); excluded from the score. Check that this is not hiding a gap."


def _module_section(module: str, interesting: list[Mutant], root: Path) -> list[str]:
    source = (root / module).read_text(encoding="utf-8").splitlines()
    out = ["", f"## `{module}`"]
    for m in interesting:
        out += ["", f"### {m.status}: line {m.start[0]}, col {m.start[1]}: `{m.operator}` in `{m.function or '<module>'}`", "",
                "```diff", _hunk(m.diff), "```", ""]
        out.append(_mutant_note(m, source))
    return out


def load_baseline(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema": BASELINE_SCHEMA, "modules": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != BASELINE_SCHEMA:
        raise ValueError(f"{path}: unexpected schema {data.get('schema')!r}")
    return data


def check(summary: dict[str, Any], baseline: dict[str, Any]) -> list[str]:
    """Ratchet verdict: a list of failures (empty means the gate passes).

    Fails when a module's score falls below its stored floor, when a measured module has no floor, when too
    many mutants were not exercisable (a tool failure must not read as a score), or when the run was sampled
    (a sampled score is an estimate over a subset and is never compared with a full-run floor).
    """
    failures = []
    if summary["sample"] is not None:
        failures.append("sampled runs are estimates and are not gated; rerun without --sample")
    for module, row in summary["modules"].items():
        floor = baseline["modules"].get(module)
        if row["total"] == 0:
            failures.append(f"{module}: no mutants were generated (operator set, module path or filter broken)")
            continue
        if row["incompetent"] / row["total"] > MAX_INCOMPETENT_SHARE:
            failures.append(f"{module}: {row['incompetent']}/{row['total']} mutants were not exercisable; the analysis is not trustworthy")
        if floor is None:
            failures.append(f"{module}: no baseline floor; establish one with `python -m quality.mutation baseline`")
        elif row["score"] is None or row["score"] < floor["score"]:
            failures.append(f"{module}: mutation score {row['score']} is below the ratchet floor {floor['score']}")
    return failures


def update_baseline(summary: dict[str, Any], baseline: dict[str, Any], *, allow_lower: bool = False) -> dict[str, Any]:
    """Raise (or establish) floors from a full run. Lowering a floor requires an explicit, reviewed override."""
    if summary["sample"] is not None:
        raise ValueError("a floor must come from a full run, not a sample")
    modules = dict(baseline["modules"])
    for module, row in summary["modules"].items():
        if row["score"] is None:
            raise ValueError(f"{module}: nothing was assessed")
        old = modules.get(module)
        if old is not None and row["score"] < old["score"] and not allow_lower:
            raise ValueError(f"{module}: {row['score']} would lower the floor {old['score']}; fix the tests or pass --allow-lower")
        modules[module] = {"score": row["score"], "total": row["total"], "survived": row["survived"]}
    return {"schema": BASELINE_SCHEMA, "engine": summary["engine"], "platform": summary["platform"],
            "modules": dict(sorted(modules.items()))}

