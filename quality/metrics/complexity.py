"""Cyclomatic complexity, maintainability index and raw size via radon.

Sources: T. J. McCabe, "A Complexity Measure", IEEE TSE SE-2(4), 1976 (cyclomatic complexity, CC);
Oman & Hagemeister 1992 / Coleman et al. 1994 (maintainability index, MI, as implemented by radon:
MI = max(0, 100 * (171 - 5.2 ln V - 0.23 G - 16.2 ln L + 50 sin sqrt(2.4 C)) / 171) with Halstead volume V,
CC G, lines L and comment ratio C).

Ranks are radon's: CC A 1-5, B 6-10, C 11-20, D 21-30, E 31-40, F 41+; MI A >= 20, B 10-19, C < 10.

What this does NOT establish: that low complexity means correct code, or that a high CC function is
wrong. CC counts independent paths in one function; module-level statements are not counted by radon.
"""
from __future__ import annotations

import statistics
from pathlib import Path

from radon.complexity import cc_rank, cc_visit
from radon.metrics import mi_rank, mi_visit
from radon.raw import analyze

from . import SRC
from .common import measured, percentile, r3
from .structure import PACKAGE, layer_of

RANKS = ("A", "B", "C", "D", "E", "F")


def _flatten(blocks) -> list[tuple[str, int, int]]:
    """(qualified name, line, complexity) for every function, method and closure.

    radon already lists methods as flat `Function` blocks (with `classname`) next to their `Class`
    block, so `Class` blocks are skipped: counting both would count each method twice.
    """
    out: list[tuple[str, int, int]] = []

    def add(block, prefix: str = "") -> None:
        if type(block).__name__ == "Class":
            return
        name = f"{prefix}{block.classname + '.' if getattr(block, 'classname', None) else ''}{block.name}"
        out.append((name, block.lineno, block.complexity))
        for closure in getattr(block, "closures", ()):
            add(closure, name + ".")

    for b in blocks:
        add(b)
    return out


def source_files() -> list[Path]:
    return sorted(p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts)


def module_name(path: Path) -> str:
    parts = path.relative_to(SRC).with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join((PACKAGE, *parts))


def _stats(values: list[int]) -> dict:
    if not values:
        return {"functions": 0, "mean": None, "median": None, "p90": None, "max": None,
                "ranks": dict.fromkeys(RANKS, 0)}
    s = sorted(values)
    ranks = dict.fromkeys(RANKS, 0)
    for v in s:
        ranks[cc_rank(v)] += 1
    return {"functions": len(s), "mean": r3(statistics.fmean(s)), "median": r3(percentile(s, 50)),
            "p90": r3(percentile(s, 90)), "max": s[-1], "ranks": ranks}


def _analyse_module(path: Path) -> tuple[str, list[tuple[str, int, int]], dict]:
    """(layer, functions, module row) for one source file."""
    text = path.read_text(encoding="utf-8")
    module = module_name(path)
    raw = analyze(text)
    mi = mi_visit(text, True)
    funcs = _flatten(cc_visit(text))
    row = {"module": module.removeprefix(PACKAGE + "."), "layer": layer_of(module), "loc": raw.loc, "sloc": raw.sloc,
           "lloc": raw.lloc, "comments": raw.comments + raw.single_comments, "blank": raw.blank,
           "mi": r3(mi), "mi_rank": mi_rank(mi),
           "functions": len(funcs), "max_cc": max((f[2] for f in funcs), default=0)}
    return row["layer"], funcs, row


def _summary(modules: list[dict]) -> dict:
    total_sloc = sum(m["sloc"] for m in modules)
    weighted_mi = sum(m["mi"] * m["sloc"] for m in modules) / total_sloc if total_sloc else None
    return {"files": len(modules), "sloc": total_sloc, "sloc_weighted_mi": None if weighted_mi is None else r3(weighted_mi),
            "min_mi": min((m["mi"] for m in modules), default=None),
            "modules_below_mi_rank_a": sorted(m["module"] for m in modules if m["mi_rank"] != "A")}


def collect(top: int = 10) -> dict:
    per_layer: dict[str, list[int]] = {}
    hotspots: list[dict] = []
    modules: list[dict] = []
    for path in source_files():
        layer, funcs, row = _analyse_module(path)
        modules.append(row)
        for name, line, cc in funcs:
            per_layer.setdefault(layer, []).append(cc)
            hotspots.append({"function": f"{row['module']}:{name}", "line": line, "cc": cc, "rank": cc_rank(cc)})
    hotspots.sort(key=lambda h: (-h["cc"], h["function"]))
    everything = [cc for values in per_layer.values() for cc in values]
    layers = [{"layer": layer, **_stats(values)} for layer, values in sorted(per_layer.items())]
    return measured(
        method="radon cc_visit / mi_visit(multi=True) / raw.analyze over src/eija_studio/**/*.py",
        source="McCabe 1976; Oman & Hagemeister 1992; radon 6.0.1 rank tables",
        not_measured=["module-level statement complexity (radon omits it)", "cognitive complexity", "test-code complexity"],
        overall=_stats(everything), layers=layers, hotspots=hotspots[:top], modules=sorted(modules, key=lambda m: m["module"]),
        summary=_summary(modules))
