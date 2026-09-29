"""Cyclomatic complexity, maintainability index and raw size.

One collector per metric. Per-function cyclomatic complexity (CC) is NOT measured here a second time: it
comes from `quality.gates.complexity_ratchet.measure`, the function the quality lane's ratchet gate runs, so
the dashboard and the gate can never disagree about a function. What this module adds, and the ratchet does
not have, is the maintainability index (MI) and raw size per module (radon `mi_visit` / `raw.analyze`), and
the per-layer aggregation.

Sources: T. J. McCabe, "A Complexity Measure", IEEE TSE SE-2(4), 1976 (CC); Oman & Hagemeister 1992 /
Coleman et al. 1994 (MI, as implemented by radon:
MI = max(0, 100 * (171 - 5.2 ln V - 0.23 G - 16.2 ln L + 50 sin sqrt(2.4 C)) / 171) with Halstead volume V,
CC G, lines L and comment ratio C).

Ranks are radon's: CC A 1-5, B 6-10, C 11-20, D 21-30, E 31-40, F 41+; MI A >= 20, B 10-19, C < 10.

What this does NOT establish: that low complexity means correct code, or that a high CC function is
wrong. CC counts independent paths in one function; module-level statements are not counted by radon.
"""
from __future__ import annotations

import statistics
from collections import defaultdict
from pathlib import Path

from radon.complexity import cc_rank
from radon.metrics import mi_rank, mi_visit
from radon.raw import analyze

from quality.gates import complexity_ratchet
from quality.hci import laws

from . import ROOT, SRC
from .common import measured, r3
from .structure import PACKAGE, layer_of

RANKS = ("A", "B", "C", "D", "E", "F")
SRC_ROOT = SRC.relative_to(ROOT).as_posix()  # "src/eija_studio", the kernel tree the ratchet also measures


def source_files() -> list[Path]:
    return sorted(p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts)


def module_name(path: Path) -> str:
    parts = path.relative_to(SRC).with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join((PACKAGE, *parts))


def function_complexities() -> dict[str, dict[str, int]]:
    """module (dotted, `eija_studio.x.y`) -> {qualified function name: CC}, from the quality lane's collector."""
    per_module: dict[str, dict[str, int]] = defaultdict(dict)
    for key, cc in complexity_ratchet.measure((SRC_ROOT,), ROOT).items():
        path, name = key.split("::", 1)
        per_module[module_name(ROOT / path)][name] = cc
    return per_module


def _stats(values: list[int]) -> dict:
    ranks = dict.fromkeys(RANKS, 0)
    if not values:
        return {"functions": 0, "mean": None, "median": None, "p90": None, "max": None, "ranks": ranks}
    s = sorted(values)
    for v in s:
        ranks[cc_rank(v)] += 1
    return {"functions": len(s), "mean": r3(statistics.fmean(s)), "median": r3(laws.percentile(s, 50) or 0),
            "p90": r3(laws.percentile(s, 90) or 0), "max": s[-1], "ranks": ranks}


def _module_row(path: Path, funcs: dict[str, int]) -> dict:
    text = path.read_text(encoding="utf-8")
    module = module_name(path)
    raw = analyze(text)
    mi = mi_visit(text, True)
    return {"module": module.removeprefix(PACKAGE + "."), "layer": layer_of(module), "loc": raw.loc, "sloc": raw.sloc,
            "lloc": raw.lloc, "comments": raw.comments + raw.single_comments, "blank": raw.blank,
            "mi": r3(mi), "mi_rank": mi_rank(mi), "functions": len(funcs), "max_cc": max(funcs.values(), default=0)}


def collect(top: int = 10) -> dict:
    per_module = function_complexities()
    modules = [_module_row(p, per_module.get(module_name(p), {})) for p in source_files()]
    per_layer: dict[str, list[int]] = defaultdict(list)
    hotspots = []
    for module, funcs in per_module.items():
        for name, cc in funcs.items():
            per_layer[layer_of(module)].append(cc)
            hotspots.append({"function": f"{module.removeprefix(PACKAGE + '.')}:{name}", "cc": cc, "rank": cc_rank(cc)})
    hotspots.sort(key=lambda h: (-h["cc"], h["function"]))
    everything = [cc for values in per_layer.values() for cc in values]
    total_sloc = sum(m["sloc"] for m in modules)
    weighted_mi = sum(m["mi"] * m["sloc"] for m in modules) / total_sloc if total_sloc else None
    return measured(
        method=("per-function CC from quality.gates.complexity_ratchet.measure (the ratchet gate's own collector); "
                "radon mi_visit(multi=True) and raw.analyze per module over src/eija_studio/**/*.py"),
        source="McCabe 1976; Oman & Hagemeister 1992; radon 6.0.1 rank tables",
        not_measured=["module-level statement complexity (radon omits it)", "cognitive complexity", "test-code complexity"],
        overall=_stats(everything), layers=[{"layer": k, **_stats(v)} for k, v in sorted(per_layer.items())],
        hotspots=hotspots[:top], modules=sorted(modules, key=lambda m: m["module"]),
        summary={"files": len(modules), "sloc": total_sloc, "sloc_weighted_mi": None if weighted_mi is None else r3(weighted_mi),
                 "min_mi": min((m["mi"] for m in modules), default=None),
                 "modules_below_mi_rank_a": sorted(m["module"] for m in modules if m["mi_rank"] != "A")})
