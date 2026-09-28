"""Shared plumbing for the `smt` and `bmc` evidence reports (no third-party imports).

Reports are JSON with sorted keys and LF endings. Wall-clock numbers live only under `measurements`,
so everything else is reproducible byte-for-byte for the same sources, seed and bounds.
"""
from __future__ import annotations

import ast
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "src" / "eija_studio"


def lf_sha256(path: Path) -> str:
    """SHA-256 of the file with CRLF normalised, so a Windows checkout hashes like a Linux one."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


_IGNORED_FIELDS = frozenset({"type_comment", "kind", "type_params", "ctx"})
_ANNOTATION_ONLY_MODULES = frozenset({"typing", "__future__", "collections.abc"})


class _Normalise(ast.NodeTransformer):
    """Drop what cannot change behaviour: docstrings, typing imports and (optionally) annotations."""

    def __init__(self, strip_annotations: bool) -> None:
        self.strip_annotations = strip_annotations

    def _body(self, node: ast.AST) -> ast.AST:
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr)                 and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
        return self.generic_visit(node)

    visit_Module = visit_ClassDef = visit_FunctionDef = visit_AsyncFunctionDef = _body

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST | None:
        return None if node.module in _ANNOTATION_ONLY_MODULES else node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        if self.strip_annotations:
            node.annotation = None
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AST | None:
        if not self.strip_annotations:
            return self.generic_visit(node)
        if node.value is None:
            return None
        return ast.Assign(targets=[node.target], value=self.visit(node.value))

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if self.strip_annotations and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            node.returns = None
        return super().generic_visit(node)


def _canonical(node: object) -> object:
    """A Python-version-independent tree: node names and fields, without positions or empty optional fields."""
    if isinstance(node, ast.AST):
        fields = {name: _canonical(value) for name, value in ast.iter_fields(node)
                  if name not in _IGNORED_FIELDS and value not in (None, [])}
        return [type(node).__name__, fields]
    if isinstance(node, list):
        return [_canonical(item) for item in node]
    return repr(node)


def semantic_sha256(path: Path, *, strip_annotations: bool) -> str:
    """SHA-256 of the parsed program, so formatting, comments, docstrings and typing-only edits do not change it.

    What it establishes: two files with the same digest parse to the same executable structure (up to the
    normalisation above). What it does NOT establish: that the code is correct, or that two different digests
    differ in behaviour. With `strip_annotations=True` annotation edits are invisible, so use it only for
    modules whose annotations carry no runtime meaning (pydantic models are NOT such a module)."""
    tree = _Normalise(strip_annotations).visit(ast.parse(path.read_text(encoding="utf-8")))
    return hashlib.sha256(json.dumps(_canonical(tree), sort_keys=True).encode("utf-8")).hexdigest()


def kernel_subject(*relative: str, function: str, plain_modules: tuple[str, ...] = ()) -> dict[str, Any]:
    """Identify the kernel code a report is about. A hash names the bytes; it does not vouch for them.

    `sources_sha256_lf` changes on any byte edit (measurement only). `sources_semantic_sha256` ignores
    formatting, comments, docstrings and typing-only changes, and is what a committed snapshot may embed:
    annotations are stripped except for `plain_modules`, whose annotations are behaviour (pydantic fields)."""
    return {"function": function,
            "sources_sha256_lf": {r: lf_sha256(KERNEL / r) for r in sorted(relative)},
            "sources_semantic_sha256": {r: semantic_sha256(KERNEL / r, strip_annotations=r not in plain_modules)
                                        for r in sorted(relative)}}


def platform_info() -> dict[str, str]:
    """OS tag and interpreter version. `platform.platform()` is avoided: on Windows it issues slow WMI queries."""
    return {"platform": sys.platform, "python": platform.python_version()}


def dumps(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(dumps(document).encode("utf-8"))


def not_run(kind: str, reason: str, subject: dict[str, Any]) -> dict[str, Any]:
    """A missing prerequisite is NOT_RUN, never PASS."""
    return {"schema": "eija.formal-report/v1", "kind": kind, "verdict": "NOT_RUN", "reason": reason,
            "subject": subject, "measurements": platform_info()}
