"""Equivalent mutants: changes that cannot alter behaviour, so no test could ever kill them.

An equivalent mutant is excluded from the score instead of being left to drag it down or hidden with a
`# pragma: no mutate` comment inside production code (this lane does not edit production code). Two rules
keep the exclusion honest:

* Only a mutant that *survived* can be reclassified. If a test kills it, it was not equivalent.
* Each exclusion states why. Generic rules are structural (below); the rest are listed one by one in
  `ACCEPTED`, matched on module, function and the exact original text, so a code move that changes
  the text re-exposes the mutant instead of silently keeping the exclusion.

Every accepted equivalent appears in `survivors.md` with its reason so a reviewer can reject it.

Postponed function annotations are excluded from executable-body mutation scope only. Their type
hints and introspection results can change; this exclusion does not establish annotation-contract
equivalence. The current quick target review is recorded in docs/quality/policy-mutation-review.md.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

from .model import Mutant

_SRC = "src/eija_studio"


@dataclass(frozen=True)
class Accepted:
    """A reviewed equivalent mutant: module, enclosing function, original text at the mutation, reason."""

    module: str
    function: str | None
    snippet: str
    becomes: str  # the exact replacement text the mutant substitutes; other replacements of the same text are not covered
    reason: str


ACCEPTED: tuple[Accepted, ...] = (
    Accepted(f"{_SRC}/domain/models.py", "semantic_hash", '"json"', '"XXjsonXX"',
             "Workflow holds only str, int and tuple fields, which serialise identically in python and json dump modes"),
)


def _defers_annotations(tree: ast.Module) -> bool:
    """True when the module has `from __future__ import annotations`."""
    return any(isinstance(n, ast.ImportFrom) and n.module == "__future__" and any(a.name == "annotations" for a in n.names) for n in tree.body)


def _function_annotations(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.expr]:
    """Every argument annotation and the return annotation of one function."""
    args = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs, node.args.vararg, node.args.kwarg)
    annotated = [a.annotation for a in args if a and a.annotation]
    return [annotation for annotation in (*annotated, node.returns) if annotation is not None]


def _annotation_ranges(tree: ast.Module) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Positions of function annotations deferred until an annotation consumer resolves them."""
    if not _defers_annotations(tree):
        return []
    return [((a.lineno, a.col_offset), (a.end_lineno, a.end_col_offset))
            for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            for a in _function_annotations(node)]


def _text(lines: list[str], mutant: Mutant) -> str:
    (l1, c1), (l2, c2) = mutant.start, mutant.end
    if l1 == l2:
        return lines[l1 - 1][c1:c2]
    return "\n".join([lines[l1 - 1][c1:], *lines[l1:l2 - 1], lines[l2 - 1][:c2]])


def _changed_lines(diff: str) -> tuple[list[str], list[str]]:
    """(removed, added) lines of a unified diff, without the marker and without the file headers."""
    lines = diff.splitlines()
    removed = [x[1:] for x in lines if x.startswith("-") and not x.startswith("---")]
    added = [x[1:] for x in lines if x.startswith("+") and not x.startswith("+++")]
    return removed, added


def _produces(mutant: Mutant, lines: list[str], becomes: str) -> bool:
    """True when the diff is exactly the original line with the mutated text replaced by `becomes`."""
    (l1, c1), (l2, c2) = mutant.start, mutant.end
    removed, added = _changed_lines(mutant.diff)
    if l1 != l2 or len(removed) != 1 or len(added) != 1:
        return False
    return removed[0] == lines[l1 - 1] and added[0] == lines[l1 - 1][:c1] + becomes + lines[l1 - 1][c2:]


def reason(mutant: Mutant, source: str) -> str | None:
    """Why this surviving mutant cannot change behaviour, or `None` if it may."""
    lines = source.splitlines()
    text = _text(lines, mutant)
    if any(start <= mutant.start and mutant.end <= end for start, end in _annotation_ranges(ast.parse(source))):
        return "inside a postponed function annotation; excluded from executable-body scope, not a claim about type-hint consumers"
    for accepted in ACCEPTED:
        if (accepted.module, accepted.function, accepted.snippet) == (mutant.module, mutant.function, text) and _produces(mutant, lines, accepted.becomes):
            return accepted.reason
    return None
