"""Vocabulary fitness gate (WBS 1.5): generic code names no domain.

Tokens are read from every pack under ``packs/`` (pack and model ids, states, roles, actions, transition ids, effect
ids and their bare names, meaning ids, law ids, fixture actor ids). Every text file in the scanned roots is searched for
each token as a whole word (case-sensitive; a token is delimited by anything that is not a letter, digit or ``_``).
A plain single word (``Active``, ``support``) is also an ordinary English word, so it is searched only where it names
something in code: in Python, a whole string literal or an identifier. Its use in prose, comments, docstrings, JavaScript,
JSON and UI copy is not a finding; that is the trade for letting packs use ordinary domain words. A compound or delimited token (``FundsCaptured``,
``library-loan``) cannot be mistaken for prose, so it is searched as a whole word in every scanned file.
A hit is a finding unless the file is under ``packs/``, is GENERATED-headed, or is on the justified ALLOWLIST below.
A pack can refer to EIJA's own lifecycle vocabulary by binding an explicit kernel export. Its declared names are
resolved from the source AST; this discounts only that pack's grounded token provenance, never another pack's use.
Separately, any ``Literal[...]`` in scanned Python code that contains a pack token is a finding even in an
allowlisted file: a type that names a domain value is a closed kernel, whatever the file's other debt.

    python -m quality.gates.vocabulary            # gate: exit 1 on any finding
    python -m quality.gates.vocabulary --report   # counts per file, allowlisted files included (MEASUREMENT)
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quality.okf.codelink import find_symbol, parse_module

ROOT = Path(__file__).resolve().parents[2]
PACKS = ROOT / "packs"
SCANNED = ("src", "verification", "quality", "scripts", "contracts")
SUFFIXES = frozenset(
    {".py", ".js", ".html", ".css", ".json", ".toml", ".md", ".txt", ".yaml", ".yml", ".tla", ".bend", ".cfg"}
)
GENERATED_MARK = "GENERATED"
# A pack token that is also an ordinary English word (docstrings: "Return ...") or a generic modelling term (a UML class
# "Member") cannot be told apart by a word search; it is not searched. Kept tiny and explicit; each costs detection.
COMMON_WORDS = frozenset({"unsupported", "Return", "Member"})
# A line carrying this marker is exempt (one line only, with its reason written next to the marker).
LINE_MARK = "vocab-ok:"

# These are EIJA's own public lifecycle/capability contracts, not vocabulary from a supplied domain.
# Values are recovered from parsed declarations, never copied here. A pack must bind the exact
# export before its use of a token is discounted; another pack's unbound use remains enforceable.
KERNEL_EXPORTS = {
    "src/eija_studio/domain/change_case.py#ChangeCase": "stage_enum",
    "src/eija_studio/application/service.py#Studio": "method_labels",
    "src/eija_studio/domain/models.py#OWNER": "symbol_label",
    "src/eija_studio/domain/models.py#AGENT": "symbol_label",
}

# path (POSIX, relative to the root) or directory prefix ending in "/" -> why it may name a pack's vocabulary.
ALLOWLIST: dict[str, str] = {
    "verification/excursion_pack.py": "the hand-encoded formal models' view of the excursion pack (by design)",
    "verification/smt/vocabulary.py": "hand-written SMT encoding of the excursion pack (debt; equivalence-gated by smt/laws_gate.py)",
    "verification/smt/encoding.py": "hand-written SMT encoding of the excursion pack (debt; equivalence-gated)",
    "verification/smt/prove.py": "hand-written SMT proof report of the excursion pack (debt)",
    "verification/smt/differential.py": "hand-written SMT faithfulness test of the excursion pack (debt)",
    "verification/smt/accepted_set.json": "committed snapshot of the hand-written excursion proof",
    "verification/bmc/": "BMC harness explores the excursion workflows and fixture actors (debt; FUTURE-WORK: BMC over a new pack)",
    "verification/bend/": "hand-written Bend model, laws and proofs of the excursion pack (debt; FUTURE-WORK: generate Bend laws)",
    "verification/tla/": "hand-written TLA+ model of the excursion pack (debt; FUTURE-WORK: generate TLA+ laws)",
    "quality/hci/": "HCI budgets and journey evidence measured on the excursion demo (re-baselined per pack in WBS 2.6)",
    "quality/mutation/": "mutation-testing evidence recorded on the excursion kernel run (evidence, not code)",
    "quality/metrics/": "metrics snapshots recorded on the excursion build (evidence, not code)",
    "quality/okf/tests/": "OKF tool tests use recorded symbol names as fixtures",
    "quality/gates/vocabulary.py": "this gate names its planted-token negative control",
    "src/eija_studio/resources/web/vendor/": "third-party vendored code (Mermaid); its words are not ours",
    "src/eija_studio/domain/formal_smt.py": "kernel admissibility of the HAND-WRITTEN excursion SMT artifact: its required named "
    "controls (debt; WBS 1.7 moves them into pack-declared controls)",
    "src/eija_studio/domain/formal_bend.py": "kernel admissibility of the HAND-WRITTEN excursion Bend artifact: its required "
    "controls and witnesses (debt; WBS 1.7 moves them into pack-declared controls)",
    "scripts/browser_smoke.py": "drives the default pack's demo journey in a browser (debt; WBS 1.10 e2e runs both packs)",
    "scripts/browser_component_smoke.py": "drives the default pack's demo journey in a browser (debt; WBS 1.10)",
    "scripts/http_smoke.py": "drives the default pack's demo journey over HTTP (debt; WBS 1.10)",
    "scripts/capture_visual_screenshots.py": "captures the default pack's demo screenshots for the docs (debt; WBS 2.6)",
    "scripts/gen_readme_diagram.py": "renders the README's before/after diagram of the default demo pack (README is written for it)",
    "scripts/wheel_smoke.py": "installed-wheel smoke over the committed example files of the default pack (debt; WBS 1.10)",
    "src/eija_studio/resources/trusted_build.json": "owner-stamped release fixture (owner-only file; never edited by agents)",
    "scripts/stamp_release.py": "owner-only release stamping script",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    token: str
    kind: str  # "word" | "literal"

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.kind} {self.token!r}"


# ---- tokens ------------------------------------------------------------------------------------------------------


def _pack_values(doc: dict[str, Any]) -> Iterator[str]:
    model = doc.get("model", {})
    yield from (doc.get("pack", {}).get("id", ""), model.get("id", ""))
    yield from model.get("states", ())
    for t in model.get("transitions", ()):
        yield from (
            t.get("id", ""),
            t.get("action", ""),
            t.get("role", ""),
            t.get("from_state", ""),
            t.get("to_state", ""),
        )
    yield from (r.get("id", "") for r in doc.get("roles", ()))
    for a in doc.get("actions", ()):
        yield a.get("id", "")
        yield from a.get("required_effects", ())
    effects = doc.get("effects", {})
    yield from (e.get("id", "") for e in effects.get("catalog", ()))
    yield from effects.get("forbidden", ())
    yield from (m.get("id", "") for m in doc.get("meanings", ()))
    yield from (x.get("id", "") for x in doc.get("laws", ()))
    yield from (a.get("id", "") for a in doc.get("fixtures", {}).get("actors", ()))


def _expand(value: str) -> list[str]:
    """An effect id ``Audit:X`` is also the bare name ``X``."""
    return [value, value.rsplit(":", 1)[-1]] if ":" in value else [value]


def _stage_field(node: ast.AST) -> bool:
    return isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "stage"


def _stage_exports(node: ast.AST) -> set[str]:
    if not isinstance(node, ast.ClassDef):
        return set()
    fields = [member for member in node.body if _stage_field(member)]
    return {
        value.value
        for field in fields
        for literal in ast.walk(field.annotation)
        if isinstance(literal, ast.Subscript) and _is_literal(literal)
        for value in _literal_strings(literal)
    }


def _export_values(ref: str, mode: str, node: ast.AST) -> dict[str, set[str]]:
    if mode == "stage_enum":
        return {ref: _stage_exports(node)}
    if mode == "method_labels" and isinstance(node, ast.ClassDef):
        return {
            ref + "." + member.name: {member.name[:1].upper() + member.name[1:]}
            for member in node.body
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and not member.name.startswith("_")
        }
    if mode == "symbol_label" and isinstance(node, (ast.Assign, ast.AnnAssign)):
        return {ref: {ref.rsplit("#", 1)[1].title()}}
    return {}


def kernel_exports(root: Path) -> dict[str, set[str]]:
    """Resolve a small reviewed contract surface without importing or executing target code.

    Missing/unparseable declarations export nothing, so their pack tokens stay subject to the gate.
    Arbitrary strings in function bodies and arbitrary pack bindings are never export authority.
    """
    out: dict[str, set[str]] = {}
    for binding, mode in KERNEL_EXPORTS.items():
        relative, symbol = binding.split("#", 1)
        target = root / relative
        if not target.resolve().is_relative_to(root.resolve()):
            continue
        try:
            node = find_symbol(parse_module(target.read_text(encoding="utf-8"), relative), symbol)
        except (OSError, UnicodeError, SyntaxError, ValueError, RecursionError):
            continue
        if node is not None:
            out.update(_export_values("repo://" + binding, mode, node))
    return out


def _bound_kernel_tokens(doc: dict[str, Any], exports: dict[str, set[str]]) -> set[str]:
    bindings = {
        binding for term in doc.get("language", {}).get("terms", ()) for binding in term.get("binds", ())
    }
    return {token for binding in bindings for token in exports.get(binding, ())}


def pack_tokens(packs: Path = PACKS) -> dict[str, set[str]]:
    """Token -> packs whose token is not already grounded in a bound kernel export.

    Provenance is retained per pack: a self-reference cannot exempt a foreign domain's token.
    """
    out: dict[str, set[str]] = {}
    exports = kernel_exports(packs.parent)
    for path in sorted(packs.glob("*/pack.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        bound = _bound_kernel_tokens(doc, exports)
        for value in _pack_values(doc):
            for token in _expand(value):
                if len(token) >= 3 and token not in COMMON_WORDS and token not in bound:
                    out.setdefault(token, set()).add(path.parent.name)
    return out


# ---- scanning ----------------------------------------------------------------------------------------------------


def _pattern(tokens: Iterable[str]) -> re.Pattern[str]:
    alternatives = "|".join(re.escape(t) for t in sorted(tokens, key=lambda t: (-len(t), t)))
    return re.compile(rf"(?<![A-Za-z0-9_])(?:{alternatives})(?![A-Za-z0-9_])")


# A plain word: at most an initial capital and nothing else (``Active``, ``support``). Anything else is compound or delimited.
PLAIN_WORD = re.compile(r"[A-Z]?[a-z]+")
# Plain words are read only from Python, where a string literal or identifier is domain logic (an enum, a dispatch value).
# JavaScript and JSON carry UI labels and schema titles, which are ordinary English (``"Owner"`` on a button).
CODE_SUFFIXES = frozenset({".py"})


def _plain(token: str) -> bool:
    return PLAIN_WORD.fullmatch(token) is not None


def allowlisted(rel: str) -> str | None:
    for key, why in ALLOWLIST.items():
        if rel == key or (key.endswith("/") and rel.startswith(key)):
            return why
    return None


def _generated(text: str) -> bool:
    return GENERATED_MARK in "\n".join(text.splitlines()[:3])


def files(root: Path = ROOT, scanned: Iterable[str] = SCANNED) -> Iterator[Path]:
    for top in scanned:
        base = root / top
        for path in sorted(base.rglob("*")) if base.is_dir() else ():
            parts = set(path.relative_to(root).parts)
            if (
                path.is_file()
                and path.suffix in SUFFIXES
                and not parts & {"__pycache__", "node_modules", ".pytest_cache"}
                and not any(part.endswith(".egg-info") for part in parts)  # gitignored install metadata
            ):
                yield path


def word_hits(text: str, pattern: re.Pattern[str]) -> Iterator[tuple[int, str]]:
    for number, line in enumerate(text.splitlines(), start=1):
        if LINE_MARK in line:
            continue
        for match in pattern.finditer(line):
            yield number, match.group(0)


def _literal_strings(node: ast.Subscript) -> Iterator[ast.Constant]:
    for child in ast.walk(node.slice):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            yield child


def _is_literal(node: ast.AST) -> bool:
    target = node.value if isinstance(node, ast.Subscript) else None
    return (isinstance(target, ast.Name) and target.id == "Literal") or (
        isinstance(target, ast.Attribute) and target.attr == "Literal"
    )


def literal_hits(text: str, tokens: set[str]) -> Iterator[tuple[int, str]]:
    """``Literal[...]`` members that are pack tokens (a string member is judged whole, and by its bare effect name)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and _is_literal(node):
            for const in _literal_strings(node):
                if set(_expand(const.value)) & tokens:
                    yield const.lineno, const.value


def _named_word(tok: tokenize.TokenInfo, plain: set[str]) -> str | None:
    """The plain pack word that a Python identifier or whole string literal names, if any."""
    if tok.type == tokenize.NAME:
        return tok.string if tok.string in plain else None
    if tok.type != tokenize.STRING:
        return None
    try:
        value = ast.literal_eval(tok.string)
    except (ValueError, SyntaxError):
        return None
    return value if isinstance(value, str) and value in plain else None


def code_hits(path: Path, text: str, plain: set[str]) -> Iterator[tuple[int, str]]:
    """Plain pack words that name something in code: a whole string literal, or in Python an identifier.

    Comments and docstrings are not read (tokenize yields them as comments or as a string that is not the whole word).
    Only ``CODE_SUFFIXES`` are read at all.
    """
    if path.suffix not in CODE_SUFFIXES or not plain:
        return
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError):
        return
    lines = text.splitlines()
    for tok in tokens:
        hit = _named_word(tok, plain)
        if hit is not None and LINE_MARK not in lines[tok.start[0] - 1]:
            yield tok.start[0], hit


def _file_findings(
    path: Path,
    rel: str,
    text: str,
    pattern: re.Pattern[str] | None,
    plain: set[str],
    tokens: dict[str, set[str]],
    include_allowlisted: bool,
) -> list[Finding]:
    found: list[Finding] = []
    if path.suffix == ".py":
        found += [Finding(rel, n, t, "literal") for n, t in literal_hits(text, set(tokens))]
    if _generated(text) or (allowlisted(rel) and not include_allowlisted):
        return found
    if pattern is not None:
        found += [Finding(rel, n, t, "word") for n, t in word_hits(text, pattern)]
    found += [Finding(rel, n, t, "word") for n, t in code_hits(path, text, plain)]
    return found


def scan(
    root: Path = ROOT, tokens: dict[str, set[str]] | None = None, include_allowlisted: bool = False
) -> list[Finding]:
    tokens = pack_tokens(root / "packs") if tokens is None else tokens
    compound = {t for t in tokens if not _plain(t)}
    plain = set(tokens) - compound
    pattern = _pattern(compound) if compound else None
    found: list[Finding] = []
    for path in files(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        found += _file_findings(path, rel, text, pattern, plain, tokens, include_allowlisted)
    return found


def report(findings: list[Finding]) -> dict[str, Any]:
    by_file: dict[str, int] = {}
    for f in findings:
        by_file[f.path] = by_file.get(f.path, 0) + 1
    outside = {p: n for p, n in by_file.items() if allowlisted(p) is None}
    return {
        "findings": len(findings),
        "files": len(by_file),
        "outside_allowlist": sum(outside.values()),
        "outside_allowlist_files": len(outside),
        "by_file": dict(sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m quality.gates.vocabulary", description=__doc__)
    ap.add_argument(
        "--report", action="store_true", help="print counts per file (allowlisted files included)"
    )
    ap.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    args = ap.parse_args(argv)
    if args.report:
        print(json.dumps(report(scan(args.root, include_allowlisted=True)), indent=2))
        return 0
    findings = scan(args.root)
    for f in findings:
        print(f.render())
    tokens = pack_tokens(args.root / "packs")
    print(
        f"vocabulary: {len(tokens)} pack tokens, {len(findings)} finding(s) outside packs/, GENERATED files and the allowlist"
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
