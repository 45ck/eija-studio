"""Vocabulary fitness gate (WBS 1.5): generic code names no domain.

Tokens are read from every pack under ``packs/`` (pack and model ids, states, roles, actions, transition ids, effect
ids and their bare names, meaning ids, law ids, fixture actor ids). Every text file in the scanned roots is searched for
each token as a whole word (case-sensitive; a token is delimited by anything that is not a letter, digit or ``_``).
A hit is a finding unless the file is under ``packs/``, is GENERATED-headed, or is on the justified ALLOWLIST below.
Separately, any ``Literal[...]`` in scanned Python code that contains a pack token is a finding even in an
allowlisted file: a type that names a domain value is a closed kernel, whatever the file's other debt.

    python -m quality.gates.vocabulary            # gate: exit 1 on any finding
    python -m quality.gates.vocabulary --report   # counts per file, allowlisted files included (MEASUREMENT)
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKS = ROOT / "packs"
SCANNED = ("src", "verification", "quality", "scripts", "contracts")
SUFFIXES = frozenset({".py", ".js", ".html", ".css", ".json", ".toml", ".md", ".txt", ".yaml", ".yml", ".tla", ".bend", ".cfg"})
GENERATED_MARK = "GENERATED"
# A pack token that is also an ordinary English word (docstrings: "Return ...") or a generic modelling term (a UML class
# "Member") cannot be told apart by a word search; it is not searched. Kept tiny and explicit; each costs detection.
COMMON_WORDS = frozenset({"unsupported", "Return", "Member"})
# A line carrying this marker is exempt (one line only, with its reason written next to the marker).
LINE_MARK = "vocab-ok:"

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
        yield from (t.get("id", ""), t.get("action", ""), t.get("role", ""), t.get("from_state", ""), t.get("to_state", ""))
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


def pack_tokens(packs: Path = PACKS) -> dict[str, set[str]]:
    """token -> the packs that use it."""
    out: dict[str, set[str]] = {}
    for path in sorted(packs.glob("*/pack.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for value in _pack_values(doc):
            for token in _expand(value):
                if len(token) >= 3 and token not in COMMON_WORDS:
                    out.setdefault(token, set()).add(path.parent.name)
    return out


# ---- scanning ----------------------------------------------------------------------------------------------------

def _pattern(tokens: Iterable[str]) -> re.Pattern[str]:
    alternatives = "|".join(re.escape(t) for t in sorted(tokens, key=lambda t: (-len(t), t)))
    return re.compile(rf"(?<![A-Za-z0-9_])(?:{alternatives})(?![A-Za-z0-9_])")


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
            if path.is_file() and path.suffix in SUFFIXES and not parts & {"__pycache__", "node_modules", ".pytest_cache"}:
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
    return (isinstance(target, ast.Name) and target.id == "Literal") or (isinstance(target, ast.Attribute) and target.attr == "Literal")


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


def scan(root: Path = ROOT, tokens: dict[str, set[str]] | None = None, include_allowlisted: bool = False) -> list[Finding]:
    tokens = pack_tokens(root / "packs") if tokens is None else tokens
    pattern = _pattern(tokens)
    found: list[Finding] = []
    for path in files(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".py":
            found += [Finding(rel, n, t, "literal") for n, t in literal_hits(text, set(tokens))]
        if _generated(text) or (allowlisted(rel) and not include_allowlisted):
            continue
        found += [Finding(rel, n, t, "word") for n, t in word_hits(text, pattern)]
    return found


def report(findings: list[Finding]) -> dict[str, Any]:
    by_file: dict[str, int] = {}
    for f in findings:
        by_file[f.path] = by_file.get(f.path, 0) + 1
    outside = {p: n for p, n in by_file.items() if allowlisted(p) is None}
    return {"findings": len(findings), "files": len(by_file), "outside_allowlist": sum(outside.values()),
            "outside_allowlist_files": len(outside), "by_file": dict(sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0])))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m quality.gates.vocabulary", description=__doc__)
    ap.add_argument("--report", action="store_true", help="print counts per file (allowlisted files included)")
    ap.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    args = ap.parse_args(argv)
    if args.report:
        print(json.dumps(report(scan(args.root, include_allowlisted=True)), indent=2))
        return 0
    findings = scan(args.root)
    for f in findings:
        print(f.render())
    tokens = pack_tokens(args.root / "packs")
    print(f"vocabulary: {len(tokens)} pack tokens, {len(findings)} finding(s) outside packs/, GENERATED files and the allowlist")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
