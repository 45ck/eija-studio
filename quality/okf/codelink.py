"""Deterministic links from wiki pages to code: ``repo://`` URIs and content hashes.

A ``repo://<path>[#<fragment>]`` URI names a file in this repository and, optionally, one thing inside
it. A *hash method* says how that thing is normalised before hashing, so a formatting-only edit does
not stale a page but a semantic edit does. Hashes establish that the *referenced text changed since the
page was last baselined*. They do NOT establish that the page is true, or that the code is correct.
"""
from __future__ import annotations

import ast
import csv
import functools
import io
import json
import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterator

SCHEME = "repo://"

AST_SYMBOL = "ast-v1"          # python symbol (function, class, module-level assignment)
AST_API = "ast-api-v1"         # python module public surface: signatures, fields, docstrings, no bodies
AST_SIG = "ast-sig-v1"         # one python symbol's signature view: class fields and method signatures, no bodies
FILE_LF = "lf-sha256-v1"       # whole file, CRLF folded to LF
CSV_ROW = "csv-row-v1"         # one CSV row addressed by its first column
MD_TERM = "md-bold-term-v1"    # a paragraph beginning ``**Term:**``
MD_ROW = "md-table-row-v1"     # a markdown table row addressed by the slug of any of its cells
METHODS = (AST_SYMBOL, AST_API, AST_SIG, FILE_LF, CSV_ROW, MD_TERM, MD_ROW)


class Unresolved(Exception):
    """The URI does not name anything that exists (file missing, symbol renamed, row deleted)."""


@dataclass(frozen=True)
class CodeRef:
    path: str
    fragment: str | None = None

    def uri(self) -> str:
        return SCHEME + self.path + (f"#{self.fragment}" if self.fragment else "")


def parse_uri(uri: str) -> CodeRef:
    if not isinstance(uri, str) or not uri.startswith(SCHEME):
        raise ValueError(f"not a {SCHEME} URI: {uri!r}")
    body = uri[len(SCHEME):]
    path, _, fragment = body.partition("#")
    if not path or path.startswith("/") or ".." in Path(path).parts or "\\" in path:
        raise ValueError(f"unsafe repo path: {uri!r}")
    return CodeRef(path, fragment or None)


def slug(text: str) -> str:
    """Lowercase, non-alphanumerics folded to single hyphens (``0045–0046`` -> ``0045-0046``)."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def read_text(root: Path, path: str) -> str:
    """UTF-8 text with CRLF folded to LF so a checkout's line endings never change a hash."""
    target = root / path
    if not target.is_file():
        raise Unresolved(f"file not found: {path}")
    return target.read_bytes().decode("utf-8").replace("\r\n", "\n")


@functools.lru_cache(maxsize=512)
def parse_module(text: str, filename: str = "<module>") -> ast.Module:
    """Parse once per distinct source text. Callers must treat the tree as read-only."""
    return ast.parse(text, filename=filename)


def _digest(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(blob.encode("utf-8")).hexdigest()


# ---- python AST normalisation -------------------------------------------------------------------

def canon(node: Any) -> Any:
    """Canonical JSON-able form of an AST subtree.

    Comments, formatting, positions and empty/absent fields are dropped, so the form is stable across
    Python 3.11-3.13 for the same program text. Docstrings ARE kept: they state invariants.
    """
    if isinstance(node, ast.AST):
        out: dict[str, Any] = {"_": type(node).__name__}
        for name, value in ast.iter_fields(node):
            if name == "type_comment":
                continue
            inner = canon(value)
            if inner is None or inner == []:
                continue
            out[name] = inner
        return out
    if isinstance(node, list):
        return [canon(item) for item in node]
    if node is Ellipsis:
        return {"_": "Ellipsis"}
    if isinstance(node, (bytes, complex, float)):
        return {"_": type(node).__name__, "repr": repr(node)}
    return node


def is_public(name: str) -> bool:
    return not name.startswith("_") or (name.startswith("__") and name.endswith("__"))


def public_symbols(tree: ast.Module) -> Iterator[tuple[str, str, ast.AST]]:
    """Yield ``(name, kind, node)`` for public top-level definitions of a module.

    kind is ``function``, ``class``, ``constant`` (ALL_CAPS) or ``type-alias`` (other assigned names;
    a heuristic, since Python has no declaration for either).
    """
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            yield node.name, "function", node
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            yield node.name, "class", node
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if len(targets) == 1 and isinstance(targets[0], ast.Name):
                name = targets[0].id
                if not name.startswith("_"):
                    yield name, "constant" if name.isupper() else "type-alias", node


def find_symbol(tree: ast.Module, dotted: str) -> ast.AST | None:
    """Resolve ``Name`` or ``Class.method`` among top-level statements."""
    head, _, rest = dotted.partition(".")
    for name, _kind, node in public_symbols(tree):
        if name == head:
            if not rest:
                return node
            if isinstance(node, ast.ClassDef):
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name == rest:
                        return member
            return None
    return None


def _signature_form(node: ast.AST) -> Any:
    """Signature-level view of a def/class: everything except function bodies."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return {"kind": type(node).__name__, "name": node.name, "args": canon(node.args),
                "returns": canon(node.returns), "decorators": canon(node.decorator_list),
                "doc": ast.get_docstring(node, clean=True)}
    if isinstance(node, ast.ClassDef):
        members = []
        for member in node.body:
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_public(member.name):
                members.append(_signature_form(member))
            elif isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name):
                members.append({"kind": "field", "name": member.target.id, "annotation": canon(member.annotation),
                                "value": canon(member.value)})
            elif isinstance(member, ast.Assign):
                members.append({"kind": "attribute", "node": canon(member)})
        return {"kind": "ClassDef", "name": node.name, "bases": canon(node.bases), "keywords": canon(node.keywords),
                "decorators": canon(node.decorator_list), "doc": ast.get_docstring(node, clean=True), "members": members}
    return {"kind": "assign", "node": canon(node)}


def api_form(tree: ast.Module) -> Any:
    symbols = sorted(((name, _signature_form(node)) for name, _k, node in public_symbols(tree)), key=lambda x: x[0])
    return {"module_doc": ast.get_docstring(tree, clean=True), "symbols": symbols}


# ---- non-python fragments -----------------------------------------------------------------------

_TERM = re.compile(r"^\*\*(?P<term>[^*]+?):\*\*\s*(?P<text>.*)$")


def md_terms(text: str) -> list[tuple[str, str]]:
    """Paragraphs of the form ``**Term:** definition`` as ``(term, definition)`` pairs."""
    out = []
    for paragraph in re.split(r"\n\s*\n", text):
        match = _TERM.match(" ".join(paragraph.split()))
        if match:
            out.append((match["term"].strip(), match["text"].strip()))
    return out


def md_table_rows(text: str) -> list[list[str]]:
    """Cells of every body row of every pipe table (header and separator rows excluded)."""
    rows: list[list[str]] = []
    header_seen = False
    for line in text.split("\n"):
        if not line.lstrip().startswith("|"):
            header_seen = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not header_seen:
            header_seen = True  # header row
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        rows.append(cells)
    return rows


def csv_rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text, newline="")))


# ---- resolution ---------------------------------------------------------------------------------

def digest(root: Path, ref: CodeRef, method: str) -> str:
    """Hash the thing ``ref`` names under ``method``. Raises ``Unresolved`` if it does not exist."""
    return _digest_text(read_text(root, ref.path), ref, method)


@functools.lru_cache(maxsize=2048)
def _digest_text(text: str, ref: CodeRef, method: str) -> str:
    """Pure function of (source text, reference, method); cached because every check re-derives every hash."""
    if method == FILE_LF:
        return sha256(text.encode("utf-8")).hexdigest()
    if method in (AST_SYMBOL, AST_API, AST_SIG):
        try:
            tree = parse_module(text, ref.path)
        except SyntaxError as exc:
            raise Unresolved(f"{ref.path} does not parse: {exc.msg}") from exc
        if method == AST_API:
            return _digest(api_form(tree))
        if not ref.fragment:
            raise Unresolved(f"{ref.uri()}: {method} needs a #symbol fragment")
        node = find_symbol(tree, ref.fragment)
        if node is None:
            raise Unresolved(f"symbol {ref.fragment!r} not found in {ref.path}")
        return _digest(_signature_form(node) if method == AST_SIG else canon(node))
    if not ref.fragment:
        raise Unresolved(f"{ref.uri()}: {method} needs a #fragment")
    if method == CSV_ROW:
        for row in csv_rows(text):
            if next(iter(row.values())) == ref.fragment:
                return _digest(row)
        raise Unresolved(f"row {ref.fragment!r} not found in {ref.path}")
    if method == MD_TERM:
        for term, definition in md_terms(text):
            if slug(term) == slug(ref.fragment):
                return _digest([term, " ".join(definition.split())])
        raise Unresolved(f"term {ref.fragment!r} not found in {ref.path}")
    if method == MD_ROW:
        for cells in md_table_rows(text):
            if any(slug(c.replace("`", "")) == slug(ref.fragment) for c in cells):
                return _digest(cells)
        raise Unresolved(f"table row {ref.fragment!r} not found in {ref.path}")
    raise Unresolved(f"unknown hash method {method!r}")


def resolves(root: Path, ref: CodeRef) -> bool:
    """Existence only (no hash): the file exists and, for python, the fragment names a symbol."""
    target = root / ref.path
    if not target.is_file():
        return False
    if ref.path.endswith(".py") and ref.fragment:
        try:
            return find_symbol(parse_module(read_text(root, ref.path), ref.path), ref.fragment) is not None
        except SyntaxError:
            return False
    return True
