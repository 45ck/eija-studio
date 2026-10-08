"""Frozen pre-refactor Python adapter oracle, outside production.

Function bodies are retained verbatim from the repository_changes.py whose
SHA-256 is 5025c008ab848fd1e17f4a7f66b0d0a4764f12a65f9126cb96784de41fcf98c1. Do not refactor this oracle with
the implementation: it preserves the original filesystem extraction route.
"""
from __future__ import annotations

import ast
import re
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import quote

from eija_studio.weave import codelink
from eija_studio.weave.codelink import parse_module
from eija_studio.weave.extract_python import FileFacts, Gap, extract_file

MAX_SYMBOLS = 1024
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SyntaxReader = Callable[[str, bytes], dict[str, Any]]


def _python_facts(path: str, data: bytes) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eija-change-syntax-") as directory:
        mirror = Path(directory)
        target = mirror / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        facts = extract_file(mirror, path)
    if isinstance(facts, Gap):
        return {"status": "PARTIAL", "method": "python_ast", "symbols": [],
                "gaps": [{"reason": "SOURCE_UNPARSEABLE", "message": "Python syntax could not be extracted."}]}
    tree = parse_module(data.decode("utf-8").replace("\r\n", "\n"), path)
    symbols = _python_symbols(path, tree, facts)
    duplicate = len({item["reference"] for item in symbols}) != len(symbols)
    gaps = [{"reason": "DUPLICATE_REFERENCE", "message": "Multiple Python definitions share a source reference; no single definition is selected."}] if duplicate else []
    return {"status": "PARTIAL" if duplicate else "EXTRACTED", "method": "python_ast_ast-v2", "symbols": symbols, "gaps": gaps,
            "python_version": ".".join(map(str, sys.version_info[:3]))}



def _python_definitions(tree: ast.Module) -> dict[str, list[tuple[ast.stmt, ast.ClassDef | None]]]:
    definitions: dict[str, list[tuple[ast.stmt, ast.ClassDef | None]]] = {}
    for name, _kind, node in codelink.public_symbols(tree):
        if not isinstance(node, ast.stmt):
            continue
        definitions.setdefault(name, []).append((node, None))
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and codelink.is_public(member.name):
                    definitions.setdefault(f"{name}.{member.name}", []).append((member, node))
    return definitions



def _python_symbols(path: str, tree: ast.Module, facts: FileFacts) -> list[dict[str, Any]]:
    definitions = _python_definitions(tree)
    symbols = []
    for fact in facts.symbols:
        matches = definitions.get(fact.fragment, [])
        for node, owner in matches:
            # The existing extractor resolves one definition by name. Keep all ranges for
            # duplicates and reuse its AST closure digest primitive for each actual node.
            digest = fact.digest if len(matches) == 1 else codelink._digest(codelink.closure_form(tree, node, owner))
            first = min([node.lineno, *(value.lineno for value in getattr(node, "decorator_list", []))])
            symbols.append({"reference": "repo://" + quote(path, safe="/") + "#" + quote(fact.fragment, safe="."), "kind": fact.kind,
                            "syntax_digest": digest, "start_line": first,
                            "end_line": node.end_lineno or node.lineno})
    return symbols



def _validated_symbol(path: str, item: dict[str, Any], lines: int) -> dict[str, Any]:
    reference = item["reference"]
    start, end = item["start_line"], item["end_line"]
    digest = item["syntax_digest"]
    if not isinstance(reference, str) or not reference.startswith("repo://" + quote(path, safe="/") + "#"):
        raise ValueError("invalid syntax reference")
    if type(start) is not int or type(end) is not int or not 1 <= start <= end <= lines:
        raise ValueError("invalid syntax range")
    # Existing Python extractor has an explicit coarse fallback for lone surrogates.
    plain_digest = digest.removeprefix("ast-dump-v0:") if isinstance(digest, str) else ""
    if SHA256.fullmatch(plain_digest) is None:
        raise ValueError("invalid syntax digest")
    return {key: item[key] for key in ("reference", "kind", "syntax_digest", "start_line", "end_line")}



def _validated_facts(path: str, data: bytes, facts: dict[str, Any]) -> dict[str, Any]:
    symbols = facts.get("symbols", [])
    if facts.get("status") not in {"EXTRACTED", "PARTIAL", "NOT_RUN"} or not isinstance(symbols, list):
        raise ValueError("invalid syntax result")
    lines = max(1, len(_physical_lines(data.decode("utf-8"))))
    validated = [] if len(symbols) > MAX_SYMBOLS else [_validated_symbol(path, item, lines) for item in symbols]
    gaps = [{"reason": str(gap.get("reason", "SYNTAX_GAP")), "message": str(gap.get("message", "Syntax gap"))}
            for gap in facts.get("gaps", [])]
    status = facts["status"]
    if len(symbols) > MAX_SYMBOLS:
        status = "PARTIAL"
        gaps.append({"reason": "SYMBOL_LIMIT", "message": "The source exceeds the bounded symbol inventory; no symbol is selectable."})
    versions: dict[str, Any] = {key: None if facts[key] is None else str(facts[key])[:120]
                for key in ("parser_version", "grammar_version", "python_version") if key in facts}
    return {"status": status, "method": str(facts.get("method", "unknown")),
            "symbols": sorted(validated, key=lambda value: (value["reference"], value["start_line"])), "gaps": gaps,
            **versions}



def _physical_lines(text: str) -> list[str]:
    # Python source positions count CR, LF and CRLF, not Unicode separators or
    # other string whitespace. Keep the original terminators and unterminated tail.
    return [line for line in re.findall(r"[^\r\n]*(?:\r\n|\r|\n|$)", text) if line]



def _facts(path: str, data: bytes, reader: SyntaxReader | None) -> dict[str, Any]:
    try:
        if path.endswith(".py"):
            result = _python_facts(path, data)
        elif reader is not None and path.endswith(".js"):
            result = reader(path, data)
        else:
            result = {"status": "NOT_RUN", "method": "file_only", "symbols": [],
                      "gaps": [{"reason": "SYNTAX_ADAPTER_NOT_CONFIGURED", "message": "File diff only; no syntax adapter configured."}]}
        return _validated_facts(path, data, result)
    except (OSError, ValueError, TypeError, KeyError, SyntaxError, UnicodeError, RecursionError):
        return {"status": "PARTIAL", "method": "unavailable", "symbols": [],
                "gaps": [{"reason": "SYNTAX_EXTRACTION_UNAVAILABLE", "message": "Syntax facts could not be validated."}]}
