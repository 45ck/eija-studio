"""Equivalent mutants: changes that cannot alter behaviour, so no test could ever kill them.

An equivalent mutant is excluded from the score instead of being left to drag it down or hidden with a
`# pragma: no mutate` comment inside production code (this lane does not edit production code). Two rules
keep the exclusion honest:

* Only a mutant that *survived* can be reclassified. If a test kills it, it was not equivalent.
* Each exclusion states why. Generic rules are structural (below); the rest are listed one by one in
  `ACCEPTED`, matched on module, function and the exact original text, so a code move that changes
  the text re-exposes the mutant instead of silently keeping the exclusion.

Every accepted equivalent appears in `survivors.md` with its reason so a reviewer can reject it.
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
    Accepted(f"{_SRC}/application/runtime.py", "execute", '"case"', '"XXcaseXX"',
             "dictionary key label inside the operation binding: the binding is computed identically when recorded and when compared, so renaming a key changes the hash consistently and nothing observes it"),
    Accepted(f"{_SRC}/application/runtime.py", "execute", '"subject"', '"XXsubjectXX"',
             "dictionary key label inside the operation binding (see \"case\")"),
    Accepted(f"{_SRC}/application/runtime.py", "execute", '"command"', '"XXcommandXX"',
             "dictionary key label inside the operation binding (see \"case\")"),
    Accepted(f"{_SRC}/domain/models.py", "semantic_hash", '"json"', '"XXjsonXX"',
             "Workflow holds only str, int and tuple fields, which serialise identically in python and json dump modes"),
    Accepted(f"{_SRC}/domain/models.py", "Proposal", "4", "5",
             "at most four alternatives can exist anyway: `Interpretation` has four values and duplicates are rejected by the validator"),
)


def _annotation_ranges(tree: ast.Module) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Positions of function argument and return annotations (never evaluated under `from __future__ import annotations`)."""
    if not any(isinstance(n, ast.ImportFrom) and n.module == "__future__" and any(a.name == "annotations" for a in n.names) for n in tree.body):
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            annotated = [a.annotation for a in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs, node.args.vararg, node.args.kwarg) if a and a.annotation]
            for annotation in (*annotated, node.returns):
                if annotation is not None:
                    found.append(((annotation.lineno, annotation.col_offset), (annotation.end_lineno, annotation.end_col_offset)))
    return found


def _text(lines: list[str], mutant: Mutant) -> str:
    (l1, c1), (l2, c2) = mutant.start, mutant.end
    if l1 == l2:
        return lines[l1 - 1][c1:c2]
    return "\n".join([lines[l1 - 1][c1:], *lines[l1:l2 - 1], lines[l2 - 1][:c2]])


def _produces(mutant: Mutant, lines: list[str], becomes: str) -> bool:
    """True when the diff is exactly the original line with the mutated text replaced by `becomes`."""
    (l1, c1), (l2, c2) = mutant.start, mutant.end
    removed = [x[1:] for x in mutant.diff.splitlines() if x.startswith("-") and not x.startswith("---")]
    added = [x[1:] for x in mutant.diff.splitlines() if x.startswith("+") and not x.startswith("+++")]
    if l1 != l2 or len(removed) != 1 or len(added) != 1:
        return False
    return removed[0] == lines[l1 - 1] and added[0] == lines[l1 - 1][:c1] + becomes + lines[l1 - 1][c2:]


def _bare_keyword_only_star(lines: list[str], mutant: Mutant) -> bool:
    """The `*` separating keyword-only parameters is not multiplication; `cosmic-ray` mutates it as if it were."""
    if _text(lines, mutant) != "*":
        return False
    line = lines[mutant.start[0] - 1]
    before, after = line[:mutant.start[1]].rstrip(), line[mutant.end[1]:].lstrip()
    return before[-1:] in {",", "("} and after[:1] == ","


def reason(mutant: Mutant, source: str) -> str | None:
    """Why this surviving mutant cannot change behaviour, or `None` if it may."""
    lines = source.splitlines()
    text = _text(lines, mutant)
    if any(start <= mutant.start and mutant.end <= end for start, end in _annotation_ranges(ast.parse(source))):
        return "inside a function annotation, which is never evaluated (`from __future__ import annotations`)"
    if _bare_keyword_only_star(lines, mutant):
        return "the bare `*` that makes later parameters keyword-only is syntax, not multiplication"
    for accepted in ACCEPTED:
        if (accepted.module, accepted.function, accepted.snippet) == (mutant.module, mutant.function, text) and _produces(mutant, lines, accepted.becomes):
            return accepted.reason
    return None
