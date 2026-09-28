"""Robert C. Martin package metrics from the import graph (grimp) and the syntax tree (ast).

Sources: R. C. Martin, "OO Design Quality Metrics: An Analysis of Dependencies" (1994) and
"Agile Software Development: Principles, Patterns, and Practices" (2003), ch. 20.

    Ca  afferent couplings   distinct OTHER modules that import something in the package
    Ce  efferent couplings   distinct OTHER modules that the package imports
    I   instability          Ce / (Ca + Ce)         0 = maximally stable, 1 = maximally unstable
    A   abstractness         Na / Nc                abstract classes (Protocol/ABC) over all classes
    D   distance             |A + I - 1|            distance from the "main sequence"

Deviations from the paper, all deliberate and stated in docs/metrics/README.md: the coupling unit is
the MODULE (Python's compilation unit) rather than the class; only intra-project imports count
(third-party imports are reported separately as `third_party_imports`); a package with no imports in
either direction has undefined instability (reported as null, excluded from D).

What this does NOT establish: that the design is good. D measures balance between abstraction and
stability; a small stable value-object layer is legitimately concrete (see `zone` and the README).
"""
from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

import grimp

from . import SRC
from .common import measured, r3

PACKAGE = "eija_studio"
STDLIB = frozenset(sys.stdlib_module_names) | {"__future__"}
ABSTRACT_BASES = {"Protocol", "ABC"}
ABSTRACT_DECORATORS = {"abstractmethod", "abstractproperty", "abstractclassmethod", "abstractstaticmethod"}


def layer_of(module: str) -> str:
    """First path component under `eija_studio`: a layer package (domain, ...) or a top-level module
    (bootstrap, __main__), which is then its own single-module package."""
    parts = module.split(".")
    return parts[1] if len(parts) >= 2 else PACKAGE


def _name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):  # Protocol[T]
        return _name(node.value)
    return ""


def is_abstract(cls: ast.ClassDef) -> bool:
    """A class is abstract when it declares a Protocol/ABC base, ABCMeta, or an abstract method."""
    if any(_name(b) in ABSTRACT_BASES for b in cls.bases):
        return True
    if any(k.arg == "metaclass" and _name(k.value) == "ABCMeta" for k in cls.keywords):
        return True
    for item in cls.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(_name(d.func if isinstance(d, ast.Call) else d) in ABSTRACT_DECORATORS for d in item.decorator_list):
                return True
    return False


def class_counts(path: Path) -> tuple[int, int]:
    """(total classes, abstract classes) in one file, including nested classes."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    return len(classes), sum(is_abstract(c) for c in classes)


def module_path(module: str) -> Path:
    rel = Path(*module.split(".")[1:])
    file = SRC / rel.with_suffix(".py")
    return file if file.exists() else SRC / rel / "__init__.py"


def instability(ca: int, ce: int) -> float | None:
    """I = Ce / (Ca + Ce); undefined (None) for a package nobody imports and that imports nobody."""
    return None if ca + ce == 0 else ce / (ca + ce)


def abstractness(nc: int, na: int) -> float:
    """A = Na / Nc; a package with no classes has A = 0 (nothing abstract)."""
    return 0.0 if nc == 0 else na / nc


def distance(i: float | None, a: float) -> float | None:
    """D = |A + I - 1|."""
    return None if i is None else abs(a + i - 1)


def zone(i: float | None, a: float) -> str:
    """Martin's regions of the A/I plane (informative labels; the numbers are the evidence)."""
    d = distance(i, a)
    if i is None or d is None:
        return "undefined"
    if d <= 0.25:
        return "main sequence"
    if d <= 0.5:
        return "near main sequence"
    if a + i < 1:
        return "zone of pain (stable, concrete)" if i < 0.5 else "concrete, unstable"
    return "zone of uselessness (abstract, unstable)"


def _row(name: str, ca: int, ce: int, nc: int, na: int) -> dict:
    i, a = instability(ca, ce), abstractness(nc, na)
    d = distance(i, a)
    return {"name": name, "ca": ca, "ce": ce, "classes": nc, "abstract_classes": na,
            "instability": None if i is None else r3(i), "abstractness": r3(a),
            "distance": None if d is None else r3(d), "zone": zone(i, a)}


def cycles(edges: dict[str, set[str]]) -> list[list[str]]:
    """Strongly connected components with more than one member (Tarjan). Empty means acyclic."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on: set[str] = set()
    out: list[list[str]] = []
    counter = [0]

    def visit(v: str) -> None:
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in sorted(edges.get(v, ())):
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                out.append(sorted(comp))

    for node in sorted(edges):
        if node not in index:
            visit(node)
    return sorted(out)


def sdp_violations(edges: list[dict], inst: dict[str, float | None]) -> list[dict]:
    """Stable Dependencies Principle: a package should depend only on packages at most as unstable."""
    out = []
    for e in edges:
        a, b = inst.get(e["from"]), inst.get(e["to"])
        if a is not None and b is not None and b > a:
            out.append({"from": e["from"], "to": e["to"], "i_from": a, "i_to": b})
    return out


def collect() -> dict:
    graph = grimp.build_graph(PACKAGE, include_external_packages=False, cache_dir=None)
    external = grimp.build_graph(PACKAGE, include_external_packages=True, cache_dir=None)
    modules = sorted(m for m in graph.modules if m != PACKAGE)
    leaves = [m for m in modules if not graph.find_children(m)]
    layers = sorted({layer_of(m) for m in modules})

    imports_of: dict[str, set[str]] = {m: set(graph.find_modules_directly_imported_by(m)) - {m} for m in modules}
    imported_by: dict[str, set[str]] = defaultdict(set)
    for src, dsts in imports_of.items():
        for dst in dsts:
            imported_by[dst].add(src)
    counts = {m: class_counts(module_path(m)) for m in leaves}

    module_rows = []
    for m in leaves:
        row = _row(m.removeprefix(PACKAGE + "."), len(imported_by[m]), len(imports_of[m]), *counts[m])
        row["layer"] = layer_of(m)
        module_rows.append(row)

    layer_rows: list[dict] = []
    layer_edges: dict[tuple[str, str], int] = defaultdict(int)
    for layer in layers:
        inside = {m for m in modules if layer_of(m) == layer}
        ce_mods = {d for m in inside for d in imports_of[m] if layer_of(d) != layer}
        ca_mods = {s for m in inside for s in imported_by[m] if layer_of(s) != layer}
        nc = sum(counts[m][0] for m in inside if m in counts)
        na = sum(counts[m][1] for m in inside if m in counts)
        row = _row(layer, len(ca_mods), len(ce_mods), nc, na)
        row["modules"] = sum(1 for m in inside if m in counts)
        row["third_party_imports"] = sorted({d.split(".")[0] for m in inside
                                             for d in external.find_modules_directly_imported_by(m)
                                             if d.split(".")[0] not in STDLIB | {PACKAGE}})
        layer_rows.append(row)
        for m in inside:
            for d in imports_of[m]:
                if layer_of(d) != layer:
                    layer_edges[(layer, layer_of(d))] += 1

    inst = {r["name"]: r["instability"] for r in layer_rows}
    edges = [{"from": a, "to": b, "imports": n} for (a, b), n in sorted(layer_edges.items())]
    adjacency: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        adjacency[e["from"]].add(e["to"])
    defined = [r["distance"] for r in layer_rows if r["distance"] is not None]
    return measured(
        method="grimp import graph (project modules only) + ast class census; unit of coupling = module",
        source="Martin 1994; Martin 2003 ch.20",
        not_measured=["class-level coupling", "runtime/dynamic imports", "third-party coupling (listed per layer)",
                      "design quality: D is a balance heuristic, not a verdict"],
        layers=layer_rows, modules=module_rows, layer_edges=edges,
        summary={"layers": len(layer_rows), "modules": len(module_rows),
                 "mean_layer_distance": r3(sum(defined) / len(defined)) if defined else None,
                 "max_layer_distance": max(defined) if defined else None,
                 "sdp_violations": sdp_violations(edges, inst), "layer_cycles": cycles(adjacency),
                 "module_cycles": cycles({m: {d for d in imports_of[m] if d in imports_of} for m in modules})})
