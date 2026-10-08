"""Independent re-derivation of the rule catalogue's strata (graph/rules/catalogue.json, owned by the rules aspect).

The catalogue declares, per rule, the relations it reads (positive and negative) and a stratum computed by the
formula it states:

    stratum(rule) = max(0, max over positive reads of stratum(rel), max over negative reads of stratum(rel) + 1)

The rules aspect validates this in ``graph/rules/check_catalogue.py``. This module recomputes it separately,
and additionally builds the predicate dependency graph of the whole catalogue and feeds it to the formal lane's
stratifier (``rules.stratify``), which rejects negation inside recursion by a different route (SCC labels).

Two things are checked and both are static: (1) each rule's declared stratum equals the recomputed one, and each
negative read is over a relation of strictly lower stratum; (2) the catalogue as a program is stratifiable.
Polarity itself (that a rule declared positive really is monotone) is not decidable from the catalogue; it is a
property of the rule's query text, tested elsewhere (property tests on the rule implementations).
"""
from __future__ import annotations

import re

from . import rules as R


def relation_stratum(name: str, catalogue: dict) -> int | None:
    rels = {r["name"]: r["stratum"] for r in catalogue["relations"]}
    if name in rels:
        return rels[name]
    base, _, _ = name.partition(".")
    pattern = f"{base}.<"
    for key, text in catalogue["relation_patterns"].items():
        if key.startswith(pattern):
            m = re.search(r"stratum (\d+)", text)
            return int(m.group(1)) if m else 0
    return None


def recompute(catalogue: dict) -> dict:
    problems: list[str] = []
    checked = 0
    for rule in sorted(catalogue["rules"], key=lambda r: r["id"]):
        reads = rule["reads"] or {}
        levels = [0]
        for name in reads.get("pos") or []:
            s = relation_stratum(name, catalogue)
            if s is None:
                problems.append(f"{rule['id']}: unknown relation {name}")
            else:
                levels.append(s)
        for name in reads.get("neg") or []:
            s = relation_stratum(name, catalogue)
            if s is None:
                problems.append(f"{rule['id']}: unknown relation {name}")
            else:
                levels.append(s + 1)
                if s >= rule["stratum"]:
                    problems.append(f"{rule['id']}: negative read of {name} at stratum {s} is not below the rule's stratum {rule['stratum']}")
        want = max(levels)
        checked += 1
        if want != rule["stratum"]:
            problems.append(f"{rule['id']}: declared stratum {rule['stratum']}, recomputed {want}")
    return {"rules": checked, "problems": problems}


def as_program(catalogue: dict) -> list[R.Rule]:
    """The catalogue as a stratified-Datalog program over the IR: one predicate per rule output, positive and negative
    body atoms per declared read, and ``finding`` fed by the rules of strata 0 to 2 (stratum-3 rules feed ``finding3``,
    which nothing reads: the catalogue's stated reason why WV-045 reading ``finding`` negatively is not recursion)."""
    program: list[R.Rule] = []

    def pred(name: str) -> str:
        return "r_" + re.sub(r"[^a-z0-9]", "_", name.lower())

    for rule in sorted(catalogue["rules"], key=lambda r: r["id"]):
        reads = rule["reads"] or {}
        body = [R.Atom(pred(n), ("X",)) for n in reads.get("pos") or []]
        body += [R.Atom(pred(n), ("X",), True) for n in reads.get("neg") or []]
        body.append(R.Atom("universe", ("X",)))  # keeps every rule safe
        out = "out_" + re.sub(r"[^a-z0-9]", "_", rule["id"].lower())
        program.append(R.Rule(rule["id"], R.Atom(out, ("X",)), tuple(body)))
        program.append(R.Rule(rule["id"] + "-f", R.Atom("r_finding" if rule["stratum"] <= 2 else "r_finding3", ("X",)),
                              (R.Atom(out, ("X",)),)))
    return program


def stratify_catalogue(catalogue: dict) -> dict[str, int]:
    return R.stratify(as_program(catalogue))
