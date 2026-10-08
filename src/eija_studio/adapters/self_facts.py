"""Syntactic facts about EIJA's own review implementation, never a conformance proof.

The caller supplies its already filtered, tracked source snapshot. This adapter neither
opens files nor imports or executes target code. It reuses weave's Python AST resolver
and normalisation; the declared reference journey remains a separate domain pack.
"""
from __future__ import annotations

import ast
import json
from collections.abc import Callable, Mapping
from hashlib import sha256
from typing import Any

from eija_studio.domain.pack import Pack
from eija_studio.weave.codelink import canon, find_symbol, parse_module

SCHEMA = "eija.source-facts.v1"
MAX_SOURCE_BYTES = 2_000_000
PREFIX = "src/eija_studio/"
SOURCE_SYMBOLS: dict[str, tuple[str, ...]] = {
    PREFIX + "domain/change_case.py": ("ChangeCase",),
    PREFIX + "domain/models.py": ("Principal.require",),
    PREFIX + "application/compiler.py": ("subject_for",),
    PREFIX + "application/service.py": (
        "Studio.create", "Studio.propose", "Studio.select", "Studio.edit", "Studio.layout",
        "Studio.save", "Studio.verify", "Studio.approve", "Studio.apply", "Studio.discard",
    ),
    PREFIX + "adapters/sqlite_store.py": ("Session.save_case", "Session.set_active"),
    PREFIX + "interfaces/mcp_server.py": ("AGENT_TOOLS", "OWNER_ONLY_OPERATIONS"),
}
# These cross-layer selectors identify the supported syntax profile, independent of a pack name.
PROFILE_BINDINGS = frozenset({
    "repo://" + PREFIX + "domain/change_case.py#ChangeCase",
    "repo://" + PREFIX + "application/service.py#Studio.apply",
    "repo://" + PREFIX + "interfaces/mcp_server.py#AGENT_TOOLS",
})


def source_profile(pack: Pack) -> Callable[[Mapping[str, bytes]], dict[str, Any]] | None:
    """Select a syntax reader from explicit source bindings; pack identity does not choose behavior."""
    bindings = {binding for term in pack.language.terms for binding in term.binds}
    if not bindings >= PROFILE_BINDINGS:
        return None

    def read(files: Mapping[str, bytes]) -> dict[str, Any]:
        return analyze_eija_source_files(files, pack_id=pack.id, pack_digest=pack.digest)

    return read


LIMITATIONS = (
    "Syntactic occurrences are extracted; reachability and successful execution are not proved.",
    "Calls, predicates, exception paths, data dependencies and concurrency stay outside Workflow guards.",
    "The finite reference journey is declared separately, not inferred from these observations.",
    "A digest identifies source bytes or syntax; it does not establish correctness or human understanding.",
)


def _hash(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _fact(kind: str, node: ast.expr | ast.stmt, value: Any) -> dict[str, Any]:
    return {"kind": kind, "line": node.lineno, "end_line": node.end_lineno, "value": value}


def _stage_writes(node: ast.AST) -> list[dict[str, Any]]:
    values: list[ast.expr] = []
    if isinstance(node, ast.Dict):
        values = [value for key, value in zip(node.keys, node.values, strict=True)
                  if isinstance(key, ast.Constant) and key.value == "stage"]
    elif isinstance(node, ast.Call):
        values = [keyword.value for keyword in node.keywords if keyword.arg == "stage"]
    return [_fact("stage_write_syntax", value, ast.unparse(value)) for value in values]


def _require_call(node: ast.AST) -> list[dict[str, Any]]:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return []
    function = node.func
    if function.attr != "require" or not isinstance(function.value, ast.Name):
        return []
    if function.value.id != "principal":
        return []
    return [_fact("principal_require_call", node, ast.unparse(node))]


def _stage_declaration(node: ast.AST) -> list[dict[str, Any]]:
    if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
        return []
    if node.target.id != "stage":
        return []
    return [_fact("stage_type_declaration", node, ast.unparse(node.annotation))]


def _syntax_facts(symbol: ast.AST) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for node in ast.walk(symbol):
        result.extend(_stage_writes(node))
        result.extend(_require_call(node))
        result.extend(_stage_declaration(node))
        if isinstance(node, (ast.If, ast.IfExp, ast.While, ast.Assert)):
            result.append(_fact("unmodeled_predicate", node.test, ast.unparse(node.test)))
    return sorted(result, key=lambda item: (item["line"], item["kind"], str(item["value"])))


def _tool_names(symbol: ast.AST) -> list[str] | None:
    if not isinstance(symbol, (ast.Assign, ast.AnnAssign)):
        return None
    try:
        value = ast.literal_eval(symbol.value) if symbol.value is not None else None
    except (ValueError, TypeError, SyntaxError, RecursionError):
        return None
    if isinstance(value, (tuple, list)) and all(isinstance(item, str) for item in value):
        return list(value)
    return None


def _symbol_record(path: str, name: str, tree: ast.Module) -> dict[str, Any]:
    reference = "repo://" + path + "#" + name
    node = find_symbol(tree, name)
    if not isinstance(node, ast.stmt):
        return {"ref": reference, "status": "UNRESOLVED", "reason": "SYMBOL_MISSING"}
    result: dict[str, Any] = {
        "ref": reference, "status": "EXTRACTED", "line": node.lineno,
        "end_line": node.end_lineno, "ast_sha256": _hash(canon(node)),
        "hash_method": "ast-v1", "facts": _syntax_facts(node),
    }
    if name in {"AGENT_TOOLS", "OWNER_ONLY_OPERATIONS"}:
        names = _tool_names(node)
        result["literal_names"] = names
        if names is None:
            result["status"] = "UNRESOLVED"
            result["reason"] = "NON_LITERAL_TOOL_DECLARATION"
    return result


def _source_record(path: str, data: bytes | None) -> tuple[dict[str, Any], ast.Module | None]:
    if data is None:
        return {"path": path, "status": "UNRESOLVED", "reason": "SOURCE_NOT_IN_SNAPSHOT"}, None
    record: dict[str, Any] = {"path": path, "sha256": sha256(data).hexdigest()}
    if len(data) > MAX_SOURCE_BYTES:
        return record | {"status": "UNRESOLVED", "reason": "SOURCE_TOO_LARGE"}, None
    try:
        tree = parse_module(data.decode("utf-8-sig"), path)
    except (UnicodeDecodeError, SyntaxError, RecursionError, ValueError):
        return record | {"status": "UNRESOLVED", "reason": "SOURCE_UNPARSEABLE"}, None
    return record | {"status": "PARSED"}, tree


def analyze_eija_source_files(files: Mapping[str, bytes], *, pack_id: str | None = None,
                              pack_digest: str | None = None) -> dict[str, Any]:
    """Extract declared syntax from a safe captured snapshot; missing evidence stays visible.

    This report intentionally contains no PASS status. It does not establish equivalence
    between the declared pack and implementation, nor validate the authority of a caller.
    """
    sources: list[dict[str, Any]] = []
    symbols: list[dict[str, Any]] = []
    for path, names in sorted(SOURCE_SYMBOLS.items()):
        source, tree = _source_record(path, files.get(path))
        sources.append(source)
        if tree is not None:
            symbols.extend(_symbol_record(path, name, tree) for name in names)
    gaps = [item for item in sources + symbols if item["status"] == "UNRESOLVED"]
    return {
        "schema": SCHEMA,
        "extraction": {"status": "PARTIAL" if gaps else "EXTRACTED", "method": "python_ast",
                       "executes_target": False, "limitations": list(LIMITATIONS)},
        "source_digest": _hash(sources), "sources": sources, "symbols": symbols, "gaps": gaps,
        "declared_model": {
            "pack_id": pack_id, "pack_digest": pack_digest,
            "status": "DECLARED_REFERENCE_JOURNEY" if pack_id is not None else "UNBOUND",
            "scope": "A synthetic, bounded review simulation, not the complete Studio lifecycle.",
        },
        "conformance": {
            "status": "NOT_RUN",
            "reason": "Source occurrences and declared laws do not prove implementation equivalence.",
        },
    }
