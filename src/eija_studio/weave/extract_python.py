"""Python facts for the weave index: modules, public symbols, tests and their ``@pytest.mark.eija(law=...)`` marks.

Stdlib ``ast`` only, through the lifted ``codelink`` (which defines what a symbol is and how it is hashed). Files that
cannot be read or parsed become GAPS, never silent omissions: the index records them and the lint says so.
Other languages are not parsed; a file of any language is bound at file level (see ``index``).
"""
from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from . import codelink

SKIP_DIRS = frozenset({"node_modules", "build", "dist", "__pycache__", "site-packages", "htmlcov"})
TEST_ROOTS = ("tests/", "scripts/")


@dataclass(frozen=True)
class SymbolFact:
    fragment: str          # ``name`` or ``Class.method``
    kind: str              # function | class | constant | type-alias | method | test
    digest: str            # ast-v2: the symbol plus the private helpers it reaches
    laws: tuple[str, ...] = ()


@dataclass(frozen=True)
class FileFacts:
    path: str
    module_digest: str     # ast-api-v1
    symbols: tuple[SymbolFact, ...]


@dataclass(frozen=True)
class Gap:
    path: str
    reason: str


def _skipped(name: str) -> bool:
    return name.startswith(".") or name in SKIP_DIRS or name.endswith(".egg-info")


def walk_files(root: Path, suffixes: tuple[str, ...]) -> list[str]:
    """POSIX-relative paths of files under ``root`` with one of ``suffixes``, sorted; hidden and build directories pruned."""
    found: list[str] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not _skipped(d))
        base = Path(current).relative_to(root)
        found += [(base / f).as_posix() for f in files if f.endswith(suffixes)]
    return sorted(found)


def python_files(root: Path) -> list[str]:
    return walk_files(root, (".py",))


def _law_values(node: ast.expr) -> tuple[str, ...]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return (node.value,)
    if isinstance(node, (ast.Tuple, ast.List)):
        return tuple(e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str))
    return ()


def _is_eija_mark(call: ast.Call) -> bool:
    func = call.func
    return isinstance(func, ast.Attribute) and func.attr == "eija" and isinstance(func.value, ast.Attribute) and func.value.attr == "mark"


def marked_laws(node: ast.AST) -> tuple[str, ...]:
    """Law ids named by ``@pytest.mark.eija(law="id")`` or ``law=("a", "b")`` on a function, sorted and unique."""
    laws: list[str] = []
    for decorator in getattr(node, "decorator_list", ()):
        if isinstance(decorator, ast.Call) and _is_eija_mark(decorator):
            for keyword in decorator.keywords:
                if keyword.arg == "law":
                    laws += _law_values(keyword.value)
    return tuple(sorted(set(laws)))


def _is_test(path: str, fragment: str, kind: str) -> bool:
    return kind == "function" and path.startswith(TEST_ROOTS) and fragment.startswith("test")


def _members(node: ast.AST) -> list[tuple[str, ast.AST]]:
    if not isinstance(node, ast.ClassDef):
        return []
    return [(f"{node.name}.{m.name}", m) for m in node.body
            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and codelink.is_public(m.name)]


FALLBACK = "ast-dump-v0:"


def safe_digest(root: Path, ref: codelink.CodeRef, method: str, node: ast.AST) -> str:
    """``codelink.digest``, except for source that cannot be UTF-8 encoded after normalisation (a string literal holding a
    lone surrogate): those get a coarser, clearly labelled ``ast-dump-v0`` digest instead of vanishing from the index."""
    try:
        return codelink.digest(root, ref, method)
    except UnicodeEncodeError:
        return FALLBACK + sha256(ast.dump(node).encode("utf-8", "surrogatepass")).hexdigest()


def _fact(root: Path, path: str, fragment: str, kind: str, node: ast.AST) -> SymbolFact:
    digest = safe_digest(root, codelink.CodeRef(path, fragment), codelink.AST_CLOSURE, node)
    return SymbolFact(fragment, "test" if _is_test(path, fragment, kind) else kind, digest, marked_laws(node))


def _facts(root: Path, path: str, tree: ast.Module) -> tuple[SymbolFact, ...]:
    seen: set[str] = set()
    out: list[SymbolFact] = []
    for name, kind, node in codelink.public_symbols(tree):
        for fragment, k, n in [(name, kind, node)] + [(f, "method", m) for f, m in _members(node)]:
            if fragment not in seen:  # codelink resolves the first definition; a redefinition is the same id
                seen.add(fragment)
                out.append(_fact(root, path, fragment, k, n))
    return tuple(sorted(out, key=lambda s: s.fragment))


def extract_file(root: Path, path: str) -> FileFacts | Gap:
    try:
        text = codelink.read_text(root, path)
        tree = codelink.parse_module(text, path)
        module_digest = safe_digest(root, codelink.CodeRef(path), codelink.AST_API, tree)
        return FileFacts(path, module_digest, _facts(root, path, tree))
    except codelink.Unresolved as error:
        return Gap(path, str(error))
    except SyntaxError as error:
        return Gap(path, f"does not parse: {error.msg}")
    except (UnicodeDecodeError, OSError, RecursionError, ValueError) as error:
        return Gap(path, f"cannot be read ({type(error).__name__})")


def extract_all(root: Path) -> tuple[list[FileFacts], list[Gap]]:
    facts: list[FileFacts] = []
    gaps: list[Gap] = []
    for path in python_files(root):
        result = extract_file(root, path)
        (gaps if isinstance(result, Gap) else facts).append(result)  # type: ignore[arg-type]
    return facts, gaps
