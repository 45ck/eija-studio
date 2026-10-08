"""Captured-byte syntax and partial impact adapted to existing Weave primitives.

Python uses codelink's existing parser, symbol resolver and closure digests over
the supplied bytes. JavaScript runs the existing pinned parser in its bounded
worker. Neither path executes target code or supplies a behavioral proof.
"""
from __future__ import annotations

import ast
import base64
import hashlib
import json
import os
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import quote

from eija_studio.domain.pack import Pack
from eija_studio.weave import codelink, extract_javascript
from eija_studio.weave.impact import UnknownTarget, impact
from eija_studio.weave.metamodel import WeaveUnavailable

from .providers.process import CliOutputLimit, CliTimeout, run_bounded
from .repository import _build
from .repository_capture import _Unavailable
from .repository_change_snapshot import _Side, _physical_lines

MAX_OUTPUT_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 10.0
MAX_SYMBOLS = 1024
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SyntaxReader = Callable[[str, bytes], dict[str, Any]]


def _unavailable(reason: str) -> dict[str, Any]:
    return {
        "status": "NOT_RUN",
        "method": extract_javascript.METHOD,
        "symbols": [],
        "gaps": [{"reason": reason, "message": "JavaScript syntax extraction did not complete."}],
        "parser_version": None,
        "grammar_version": None,
        "scope": extract_javascript.SCOPE,
        "semantic_complete": False,
    }


def _response(stdout: str) -> dict[str, Any]:
    try:
        response = json.loads(stdout)
    except (ValueError, TypeError):
        return _unavailable("PARSER_RESPONSE_INVALID")
    if (
        not isinstance(response, dict)
        or response.get("method") != extract_javascript.METHOD
        or response.get("status") not in {"EXTRACTED", "PARTIAL", "NOT_RUN"}
        or not isinstance(response.get("symbols"), list)
        or not isinstance(response.get("gaps"), list)
    ):
        return _unavailable("PARSER_RESPONSE_INVALID")
    return response


def _worker_environment() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key.upper() in {"SYSTEMROOT", "WINDIR"}}


def syntax_reader(path: str, data: bytes) -> dict[str, Any]:
    """Production hook: parse supplied bytes in a fixed, bounded worker process.

    No target path is opened. No target code is executed. The child receives no
    provider credentials or Python startup customizations. This limits a native
    parser failure to the child; it is not an OS sandbox or parser-correctness claim.
    """
    if not isinstance(path, str) or len(path) > 1024 or not isinstance(data, bytes):
        return _unavailable("INVALID_SOURCE")
    if len(data) > extract_javascript.MAX_BYTES:
        return _unavailable("SOURCE_LIMIT")
    payload = json.dumps({"path": path, "source_base64": base64.b64encode(data).decode("ascii")})
    script = Path(extract_javascript.__file__).resolve()
    try:
        result = run_bounded(
            [sys.executable, "-I", "-B", str(script), "--worker"],
            input=payload,
            env=_worker_environment(),
            timeout=TIMEOUT_SECONDS,
            cwd=str(script.parent),
            max_bytes=MAX_OUTPUT_BYTES,
        )
    except CliTimeout:
        return _unavailable("PARSER_TIMEOUT")
    except CliOutputLimit:
        return _unavailable("PARSER_OUTPUT_LIMIT")
    except (OSError, ValueError):
        return _unavailable("PARSER_UNAVAILABLE")
    if result.returncode != 0:
        return _unavailable("PARSER_PROCESS_FAILED")
    return _response(result.stdout)


def _python_digest(text: str, path: str, fragment: str | None, node: ast.AST, method: str) -> str:
    try:
        return codelink._digest_text(text, codelink.CodeRef(path, fragment), method)
    except UnicodeEncodeError:
        # Preserve the existing extractor's coarse, explicitly tagged fallback.
        return "ast-dump-v0:" + hashlib.sha256(ast.dump(node).encode("utf-8", "surrogatepass")).hexdigest()


def _python_definitions(tree: ast.Module) -> dict[str, list[tuple[str, ast.stmt, ast.ClassDef | None]]]:
    definitions: dict[str, list[tuple[str, ast.stmt, ast.ClassDef | None]]] = {}
    for name, kind, node in codelink.public_symbols(tree):
        if not isinstance(node, ast.stmt):
            continue
        definitions.setdefault(name, []).append((kind, node, None))
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and codelink.is_public(member.name):
                    definitions.setdefault(f"{name}.{member.name}", []).append(("method", member, node))
    return definitions


def _python_resolved(text: str, path: str, tree: ast.Module,
                     definitions: dict[str, list[tuple[str, ast.stmt, ast.ClassDef | None]]]) -> dict[str, tuple[str, str]]:
    # The original file extractor resolves each distinct name once. Keep that
    # validation (including unresolved rebindings) before projecting duplicates.
    _python_digest(text, path, None, tree, codelink.AST_API)
    resolved = {}
    for fragment, matches in definitions.items():
        kind, node, _owner = matches[0]
        if kind == "function" and path.startswith(("tests/", "scripts/")) and fragment.startswith("test"):
            kind = "test"
        resolved[fragment] = kind, _python_digest(text, path, fragment, node, codelink.AST_CLOSURE)
    return resolved


def _python_symbols(path: str, tree: ast.Module,
                    definitions: dict[str, list[tuple[str, ast.stmt, ast.ClassDef | None]]],
                    resolved: dict[str, tuple[str, str]]) -> list[dict[str, Any]]:
    symbols = []
    for fragment in sorted(resolved):
        kind, first_digest = resolved[fragment]
        matches = definitions[fragment]
        for _kind, node, owner in matches:
            digest = first_digest if len(matches) == 1 else codelink._digest(codelink.closure_form(tree, node, owner))
            first = min([node.lineno, *(value.lineno for value in getattr(node, "decorator_list", []))])
            symbols.append({"reference": "repo://" + quote(path, safe="/") + "#" + quote(fragment, safe="."), "kind": kind,
                            "syntax_digest": digest, "start_line": first,
                            "end_line": node.end_lineno or node.lineno})
    return symbols


def _python_facts(path: str, data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8").replace("\r\n", "\n")
        tree = codelink.parse_module(text, path)
        definitions = _python_definitions(tree)
        resolved = _python_resolved(text, path, tree, definitions)
    except (codelink.Unresolved, SyntaxError, UnicodeDecodeError, OSError, RecursionError, ValueError):
        return {"status": "PARTIAL", "method": "python_ast", "symbols": [],
                "gaps": [{"reason": "SOURCE_UNPARSEABLE", "message": "Python syntax could not be extracted."}]}
    symbols = _python_symbols(path, tree, definitions, resolved)
    duplicate = len({item["reference"] for item in symbols}) != len(symbols)
    gaps = [{"reason": "DUPLICATE_REFERENCE", "message": "Multiple Python definitions share a source reference; no single definition is selected."}] if duplicate else []
    return {"status": "PARTIAL" if duplicate else "EXTRACTED", "method": "python_ast_ast-v2", "symbols": symbols, "gaps": gaps,
            "python_version": ".".join(map(str, sys.version_info[:3]))}


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



def known_impact(side: _Side, reference: str, pack: Pack, root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "PARTIAL", "complete": False,
                              "scope": "Changed-file syntax and the configured pack only; unmodified files and runtime dependencies are omitted.",
                              "uncaptured_inventory_count": len(side.inventory) - len(side.capture.files),
                              "captured_source_hash": side.capture.source_hash}
    try:
        graph = _build(side.capture, pack, root)
        result.update({"graph_hash": graph.root_hash, "gaps": graph.gaps})
        result["impact"] = impact(graph, reference)
    except UnknownTarget:
        result.update({"status": "UNKNOWN_TARGET", "reason": "No declared graph target for this syntax reference."})
    except (_Unavailable, WeaveUnavailable, ValueError, UnicodeError, RecursionError):
        result.update({"status": "NOT_RUN", "reason": "Known graph analysis is unavailable."})
    return result
