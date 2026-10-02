"""Bounded JavaScript syntax facts over captured bytes; never execute target code.

Only top-level named functions, identifier-bound function values and literal
property assignments of function values are indexed. Nested syntax contributes
to its containing fact's digest, but is not a separately resolved definition.
The versioned digest includes grammar structure and every leaf token, omitting
comments and whitespace outside tokens. It is not semantic equivalence: even
quote spelling and explicit semicolons remain significant. Raw bytes, line
endings and offsets are preserved, including inside string/template tokens.
"""

from __future__ import annotations

import base64
import json
import re
import sys
from bisect import bisect_right
from collections import Counter
from hashlib import sha256
from importlib import metadata, util
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote

METHOD = "js-tree-tokens-v1"
PARSER_VERSION = "0.26.0"
GRAMMAR_VERSION = "0.25.0"
MAX_BYTES = 2 * 1024 * 1024
MAX_SYMBOLS = 5000
FUNCTION_VALUES = frozenset({"function_expression", "generator_function", "arrow_function"})
FUNCTION_DECLARATIONS = frozenset({"function_declaration", "generator_function_declaration"})
SCOPE = (
    "Top-level syntax definitions only; no execution, call resolution, DOM meaning, "
    "complete dependency coverage or behavioral proof."
)


def _gap(reason: str, message: str) -> dict[str, str]:
    return {"reason": reason, "message": message}


def _result(status: str, symbols: list[dict[str, Any]], gaps: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "status": status,
        "method": METHOD,
        "symbols": symbols,
        "gaps": gaps,
        "parser_version": PARSER_VERSION if status != "NOT_RUN" else None,
        "grammar_version": GRAMMAR_VERSION if status != "NOT_RUN" else None,
        "scope": SCOPE,
        "semantic_complete": False,
    }


def _load_parser() -> Any:
    """Require the measured dependency pair; absence/mismatch is NOT_RUN."""
    if (metadata.version("tree-sitter"), metadata.version("tree-sitter-javascript")) != (
        PARSER_VERSION,
        GRAMMAR_VERSION,
    ):
        raise ValueError("unvalidated parser versions")
    parser_path = Path(__file__).resolve().with_name("_javascript_parser.py")
    spec = util.spec_from_file_location("_eija_javascript_parser", parser_path)
    if spec is None or spec.loader is None:
        raise ImportError("JavaScript parser loader is unavailable")
    module = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except SyntaxError:
        raise ImportError("JavaScript parser loader is invalid") from None
    return module.create_parser()


def _text(node: Any, data: bytes) -> str:
    return data[node.start_byte : node.end_byte].decode("utf-8")


def _children(node: Any) -> list[Any]:
    return [child for child in node.named_children if child.type != "comment"]


def _function_value(node: Any) -> bool:
    while node is not None and node.type == "parenthesized_expression":
        children = _children(node)
        node = children[0] if len(children) == 1 else None
    return node is not None and node.type in FUNCTION_VALUES


def _walk(node: Any):
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed(current.children))


def _syntax_digest(node: Any, data: bytes, context: str = "") -> str:
    # Structure matters: `return\nx` and `return x` have the same leaf sequence.
    digest = sha256()
    digest.update(json.dumps([METHOD, PARSER_VERSION, GRAMMAR_VERSION, context]).encode("utf-8"))

    def record(item: list[str]) -> None:
        digest.update(json.dumps(item, ensure_ascii=True, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")

    cursor = node.walk()
    while True:
        current = cursor.node
        if current.type != "comment":
            if current.child_count:
                record(["open", current.type])
                cursor.goto_first_child()
                continue
            record(["leaf", current.type, _text(current, data)])
        while not cursor.goto_next_sibling():
            if not cursor.goto_parent():
                return digest.hexdigest()
            record(["close", cursor.node.type])


def _optional(node: Any) -> bool:
    return any(child.type in {"?.", "optional_chain"} for child in node.children)


def _member_target(node: Any, data: bytes, depth: int) -> str | None:
    prop = node.child_by_field_name("property")
    if prop is None or prop.type != "property_identifier" or _optional(node):
        return None
    base = _literal_target(node.child_by_field_name("object"), data, depth + 1)
    name = _text(prop, data)
    return f"{base}.{name}" if base is not None and "\\" not in name else None


def _literal_argument(arguments: Any, data: bytes) -> str | None:
    args = _children(arguments) if arguments is not None else []
    if len(args) != 1 or args[0].type != "string":
        return None
    literal = args[0]
    if any(child.type != "string_fragment" for child in literal.named_children):
        return None
    raw = _text(literal, data)
    return "$(" + json.dumps(raw[1:-1], ensure_ascii=False) + ")"


def _call_target(node: Any, data: bytes) -> str | None:
    callee = node.child_by_field_name("function")
    if _optional(node) or callee is None or callee.type != "identifier" or _text(callee, data) != "$":
        return None
    return _literal_argument(node.child_by_field_name("arguments"), data)


def _literal_target(node: Any, data: bytes, depth: int = 0) -> str | None:
    """Normalize supported AST targets without interpreting JS string escapes."""
    if node is None or depth > 32:
        return None
    if node.type == "identifier":
        name = _text(node, data)
        return None if "\\" in name else name
    if node.type == "member_expression":
        return _member_target(node, data, depth)
    if node.type == "call_expression":
        return _call_target(node, data)
    return None


def _fact(
    path: str, name: str, kind: str, node: Any, data: bytes, line_starts: list[int], context: str = ""
) -> dict[str, Any]:
    # Avoid native Point accessors; derive exact lines from original UTF-8 bytes.
    start_line = bisect_right(line_starts, node.start_byte)
    end_line = bisect_right(line_starts, max(node.start_byte, node.end_byte - 1))
    return {
        "reference": f"repo://{quote(path, safe='/')}#js/{kind}/{quote(name, safe='')}",
        "kind": kind,
        "syntax_digest": _syntax_digest(node, data, context),
        "declaration_context": context,
        "start_line": start_line,
        "end_line": end_line,
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "source_sha256": sha256(data[node.start_byte : node.end_byte]).hexdigest(),
    }


Definition = tuple[str, str, Any, str]
Definitions = tuple[list[Definition], list[dict[str, str]]]


def _function_definition(node: Any, data: bytes, prefix: str) -> Definitions:
    name = node.child_by_field_name("name")
    if name is not None and "\\" not in _text(name, data):
        return [(_text(name, data), "function", node, prefix)], []
    return [], [_gap("UNCLASSIFIED_DEFINITION", "Function name is absent or uses unsupported escapes.")]


def _bound_functions(node: Any, data: bytes, prefix: str) -> Definitions:
    definitions, gaps = [], []
    # Bind const/let/var to each declarator's digest without unrelated siblings.
    keyword = next((c.type for c in node.children if c.type in {"const", "let", "var"}), node.type)
    context = (prefix + " " + keyword).strip()
    for declaration in _children(node):
        if not _function_value(declaration.child_by_field_name("value")):
            continue
        name = declaration.child_by_field_name("name")
        if name is not None and name.type == "identifier" and "\\" not in _text(name, data):
            definitions.append((_text(name, data), "function", declaration, context))
        else:
            gaps.append(_gap("UNCLASSIFIED_DEFINITION", "Function binding has no supported literal name."))
    return definitions, gaps


def _assignment(node: Any, data: bytes) -> Definitions:
    expressions = _children(node)
    expression = expressions[0] if len(expressions) == 1 else None
    if expression is None or expression.type != "assignment_expression":
        return [], []
    if not _function_value(expression.child_by_field_name("right")):
        return [], []
    target = expression.child_by_field_name("left")
    name = (
        _literal_target(target, data) if target is not None and target.type == "member_expression" else None
    )
    if name is not None:
        return [(name, "assignment", expression, "")], []
    return [], [
        _gap("DYNAMIC_ASSIGNMENT_TARGET", "Function assignment target is not supported literal syntax.")
    ]


def _definitions(statement: Any, data: bytes) -> Definitions:
    node = statement
    prefix = ""
    if node.type == "export_statement":
        prefix = " ".join(child.type for child in node.children if child.type in {"export", "default"})
        node = node.child_by_field_name("declaration")
        if node is None:
            return [], [_gap("UNCLASSIFIED_EXPORT", "Export has no supported named declaration.")]
    if node.type in FUNCTION_DECLARATIONS:
        return _function_definition(node, data, prefix)
    if node.type in {"lexical_declaration", "variable_declaration"}:
        return _bound_functions(node, data, prefix)
    if node.type == "expression_statement":
        return _assignment(node, data)
    if node.type in {"class_declaration", "class"}:
        return [], [
            _gap("UNCLASSIFIED_CLASS", "Class and method definitions are outside this adapter's scope.")
        ]
    return [], []


def _valid_path(path: str) -> bool:
    if not isinstance(path, str) or not path or len(path) > 1024:
        return False
    return not (
        "\\" in path
        or "\x00" in path
        or PurePosixPath(path).is_absolute()
        or any(part in {"", ".", ".."} for part in path.split("/"))
    )


def _input_problem(path: str, data: bytes) -> dict[str, Any] | None:
    if not _valid_path(path):
        return _result("NOT_RUN", [], [_gap("INVALID_PATH", "A relative POSIX source path is required.")])
    if PurePosixPath(path).suffix != ".js":
        return _result("NOT_RUN", [], [_gap("UNSUPPORTED_LANGUAGE", "Only .js files are supported.")])
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        return _result(
            "NOT_RUN", [], [_gap("SOURCE_LIMIT", "Source must be captured bytes within the 2 MiB limit.")]
        )
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return _result("NOT_RUN", [], [_gap("NON_UTF8", "Source is not exact UTF-8.")])
    return None


def _has_error(node: Any) -> bool:
    return node.has_error or any(part.is_missing for part in _walk(node))


def _candidate_facts(root: Any, path: str, data: bytes, gaps: list[dict[str, str]]):
    # Match captured-source excerpts: CRLF is one boundary; bare CR and LF also end a physical line.
    line_starts = [0] + [match.end() for match in re.finditer(rb"\r\n|\r|\n", data)]
    for statement in root.named_children:
        definitions, missing = _definitions(statement, data)
        gaps.extend(missing)
        for name, kind, node, context in definitions:
            if not _has_error(node):
                yield _fact(path, name, kind, node, data, line_starts, context)


def _tree_facts(root: Any, path: str, data: bytes) -> dict[str, Any]:
    gaps: list[dict[str, str]] = []
    if _has_error(root):
        gaps.append(
            _gap(
                "PARSE_ERROR", "Syntax contains parser errors or missing tokens; recovered facts are partial."
            )
        )
    symbols: list[dict[str, Any]] = []
    for fact in _candidate_facts(root, path, data, gaps):
        if len(symbols) >= MAX_SYMBOLS:
            gaps.append(_gap("SYMBOL_LIMIT", "The 5000-symbol output limit was reached."))
            break
        symbols.append(fact)
    if any(count > 1 for count in Counter(symbol["reference"] for symbol in symbols).values()):
        gaps.append(
            _gap(
                "DUPLICATE_REFERENCE", "Repeated definition identities are ambiguous; all sites are retained."
            )
        )
    symbols.sort(key=lambda symbol: (symbol["reference"], symbol["start_byte"]))
    unique_gaps = [
        {"reason": reason, "message": message}
        for reason, message in sorted({(gap["reason"], gap["message"]) for gap in gaps})
    ]
    return _result("PARTIAL" if unique_gaps else "EXTRACTED", symbols, unique_gaps)


def syntax_reader(path: str, data: bytes) -> dict[str, Any]:
    """Worker-only facts/gaps for one UTF-8 blob; production uses the adapter.

    EXTRACTED concerns only the declared syntax subset, never behavior. Caller
    owns Git capture and before/after pairing. Duplicate facts are retained for
    ambiguous pairing; no definition is selected arbitrarily.
    """
    invalid = _input_problem(path, data)
    if invalid is not None:
        return invalid
    try:
        parser = _load_parser()
    except (ImportError, metadata.PackageNotFoundError, ValueError, OSError, TypeError, AttributeError):
        return _result(
            "NOT_RUN", [], [_gap("PARSER_UNAVAILABLE", "The pinned parser and grammar are unavailable.")]
        )
    try:
        # The pinned parser attaches trailing comments across bare CR as if on one line.
        # Normalize its view without shifting bytes; facts and token digests still use original data.
        tree = parser.parse(re.sub(rb"\r(?!\n)", b"\n", data))
    except (ValueError, RuntimeError):
        return _result("PARTIAL", [], [_gap("PARSE_FAILED", "The parser could not produce a syntax tree.")])
    return _tree_facts(tree.root_node, path, data)


def _worker_main() -> int:
    """Fixed stdin/stdout worker protocol; the adapter owns process isolation."""
    if sys.argv[1:] != ["--worker"]:
        return 2
    raw = sys.stdin.buffer.read(MAX_BYTES * 2 + 1)
    try:
        if len(raw) > MAX_BYTES * 2:
            return 2
        payload = json.loads(raw)
        if not isinstance(payload, dict) or set(payload) != {"path", "source_base64"}:
            return 2
        data = base64.b64decode(payload["source_base64"], validate=True)
        result = syntax_reader(payload["path"], data)
    except (ValueError, TypeError):
        return 2
    sys.stdout.write(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(_worker_main())
