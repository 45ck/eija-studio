"""Rule IR for the compiler-and-linter layer: safety, stratification, a naive reference evaluator, a SQL backend.

A rule is Datalog with stratified negation and inequality over base relations (design document section 5):

    head(X, ...) :- body atoms, where an atom is (predicate, terms, negated) and a term is a variable
    (a string starting with an upper-case letter) or a constant (any other string). The built-in
    predicate ``neq`` takes two terms. A finding is a derived ``violation`` tuple.

Semantics = the perfect model of the stratified program: strata are evaluated in order, each to its least
fixed point by naive iteration, and negation only looks at strata that are already complete. This file
IS the definition: the SQL rules of the production runner must agree with it (differential test), and
formal models are generated from the same IR.

Safety (range restriction): every variable of the head, of a negated atom, and of a ``neq`` occurs in a
positive, non-built-in body atom. Stratification: no cycle of the predicate dependency graph contains a
negative edge (checked with the SCC code in ``order``). Both are decidable in linear time.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass

from .order import scc_labels

Fact = tuple[str, ...]
Facts = dict[str, set[Fact]]


@dataclass(frozen=True)
class Atom:
    pred: str
    terms: tuple[str, ...]
    neg: bool = False


@dataclass(frozen=True)
class Rule:
    id: str
    head: Atom
    body: tuple[Atom, ...]


class RuleError(ValueError):
    pass


def is_var(t: str) -> bool:
    return t[:1].isupper()


def check_safety(rules: Iterable[Rule]) -> None:
    for r in rules:
        bound = {t for a in r.body if not a.neg and a.pred != "neq" for t in a.terms if is_var(t)}
        need = {t for t in r.head.terms if is_var(t)} | {t for a in r.body if a.neg or a.pred == "neq"
                                                          for t in a.terms if is_var(t)}
        if need - bound:
            raise RuleError(f"{r.id}: unsafe variables {sorted(need - bound)}")
        if r.head.neg:
            raise RuleError(f"{r.id}: negated head")


def dependency_edges(rules: Iterable[Rule]) -> set[tuple[str, str, bool]]:
    return {(a.pred, r.head.pred, a.neg) for r in rules for a in r.body if a.pred != "neq"}


def stratify(rules: list[Rule]) -> dict[str, int]:
    """Stratum per predicate (base predicates are stratum 0). Raises RuleError on negation inside recursion."""
    check_safety(rules)
    edges = dependency_edges(rules)
    preds = sorted({p for e in edges for p in e[:2]} | {r.head.pred for r in rules})
    label = scc_labels(preds, [(a, b) for a, b, _ in edges])
    for a, b, neg in sorted(edges):
        if neg and label[a] == label[b]:
            raise RuleError(f"negation inside recursion: {a} -> {b}")
    stratum = dict.fromkeys(preds, 0)
    for _ in range(len(preds) + 1):  # longest path in the condensation, negative edges count one
        changed = False
        for a, b, neg in sorted(edges):
            need = stratum[a] + (1 if neg else 0)
            if label[a] != label[b] and stratum[b] < need:
                stratum[b], changed = need, True
            elif label[a] == label[b] and stratum[b] != stratum[a]:
                stratum[b] = stratum[a] = max(stratum[a], stratum[b])
                changed = True
        if not changed:
            return stratum
    raise RuleError("stratification did not converge")  # unreachable for a finite dependency graph


def _matches(atom: Atom, facts: Facts, env: dict[str, str]):
    for tup in sorted(facts.get(atom.pred, ())):
        if len(tup) != len(atom.terms):
            continue
        new = dict(env)
        ok = True
        for term, val in zip(atom.terms, tup, strict=False):
            if is_var(term):
                if new.setdefault(term, val) != val:
                    ok = False
                    break
            elif term != val:
                ok = False
                break
        if ok:
            yield new


def _rule_facts(rule: Rule, facts: Facts) -> set[Fact]:
    envs: list[dict[str, str]] = [{}]
    for a in sorted((a for a in rule.body if not a.neg and a.pred != "neq"), key=lambda a: (a.pred, a.terms)):
        envs = [e2 for e in envs for e2 in _matches(a, facts, e)]
    out: set[Fact] = set()
    for env in envs:
        def val(t: str) -> str:
            return env[t] if is_var(t) else t
        ok = True
        for a in rule.body:
            if a.pred == "neq":
                ok &= val(a.terms[0]) != val(a.terms[1])
            elif a.neg:
                ok &= tuple(val(t) for t in a.terms) not in facts.get(a.pred, set())
        if ok:
            out.add(tuple(val(t) for t in rule.head.terms))
    return out


def evaluate(rules: list[Rule], base: Facts) -> Facts:
    """Perfect model by strata. Deterministic: iteration over sorted data only."""
    strata = stratify(rules)
    facts: Facts = {p: set(t) for p, t in base.items()}
    for level in sorted(set(strata.values())):
        active = [r for r in rules if strata[r.head.pred] == level]
        while True:
            added = False
            for r in sorted(active, key=lambda r: r.id):
                new = _rule_facts(r, facts) - facts.get(r.head.pred, set())
                if new:
                    facts.setdefault(r.head.pred, set()).update(new)
                    added = True
            if not added:
                break
    return facts


# ---- SQL backend used by the differential test (naive iteration executed by SQLite) ----------------

def _cols(n: int) -> str:
    return ", ".join(f"c{i} TEXT" for i in range(n))


def compile_sql(rule: Rule) -> tuple[str, list[str]]:
    pos = [a for a in rule.body if not a.neg and a.pred != "neq"]
    binding: dict[str, str] = {}
    where: list[str] = []
    params: list[str] = []
    for i, a in enumerate(pos):
        for j, t in enumerate(a.terms):
            ref = f"t{i}.c{j}"
            if is_var(t):
                if t in binding:
                    where.append(f"{ref} = {binding[t]}")
                else:
                    binding[t] = ref
            else:
                where.append(f"{ref} = ?")
                params.append(t)

    def term(t: str) -> tuple[str, list[str]]:
        return (binding[t], []) if is_var(t) else ("?", [t])

    for a in rule.body:
        if a.pred == "neq":
            (x, px), (y, py) = term(a.terms[0]), term(a.terms[1])
            where.append(f"{x} <> {y}")
            params += px + py
        elif a.neg:
            conds, ps = [], []
            for j, t in enumerate(a.terms):
                x, p = term(t)
                conds.append(f"n.c{j} = {x}")
                ps += p
            where.append(f"NOT EXISTS (SELECT 1 FROM {a.pred} AS n WHERE {' AND '.join(conds) or '1'})")
            params += ps
    sel, sel_params = [], []
    for t in rule.head.terms:
        x, p = term(t)
        sel.append(x)
        sel_params += p
    frm = ", ".join(f"{a.pred} AS t{i}" for i, a in enumerate(pos)) or "(SELECT 1) AS t0"
    sql = f"SELECT DISTINCT {', '.join(sel)} FROM {frm}" + (f" WHERE {' AND '.join(where)}" if where else "")
    return sql, sel_params + params


def evaluate_sql(rules: list[Rule], base: Facts, arity: dict[str, int]) -> Facts:
    strata = stratify(rules)
    db = sqlite3.connect(":memory:")
    preds = sorted(set(base) | {r.head.pred for r in rules} | {a.pred for r in rules for a in r.body if a.pred != "neq"})
    for p in preds:
        db.execute(f"CREATE TABLE {p} ({_cols(arity[p])}, UNIQUE ({', '.join(f'c{i}' for i in range(arity[p]))}))")
    for p, tuples in sorted(base.items()):
        for t in sorted(tuples):
            db.execute(f"INSERT INTO {p} VALUES ({', '.join('?' * len(t))})", t)
    for level in sorted(set(strata.values())):
        active = sorted((r for r in rules if strata[r.head.pred] == level), key=lambda r: r.id)
        while True:
            changed = False
            for r in active:
                sql, params = compile_sql(r)
                rows = sorted(db.execute(sql, params).fetchall())
                for row in rows:
                    cur = db.execute(f"INSERT OR IGNORE INTO {r.head.pred} VALUES ({', '.join('?' * len(row))})", row)
                    changed |= cur.rowcount > 0
            if not changed:
                break
    out: Facts = {}
    for p in preds:
        rows = db.execute(f"SELECT * FROM {p} ORDER BY " + ", ".join(str(i + 1) for i in range(arity[p]))).fetchall()
        if rows:
            out[p] = {tuple(r) for r in rows}
    db.close()
    return out


def parse(text: str) -> list[Rule]:
    """Tiny text form for tests and docs:  ID: head(X) :- p(X, Y), not q(Y), neq(X, Y).  One rule per line."""
    rules = []
    for line in [ln.strip() for ln in text.strip().splitlines() if ln.strip() and not ln.strip().startswith("#")]:
        rid, rest = line.split(":", 1)
        head_s, body_s = rest.split(":-")

        def atom(s: str) -> Atom:
            s = s.strip()
            neg = s.startswith("not ")
            if neg:
                s = s[4:].strip()
            name, args = s.split("(")
            return Atom(name.strip(), tuple(x.strip() for x in args.rstrip(").").split(",") if x.strip()), neg)

        atoms, depth, cur = [], 0, ""
        for ch in body_s.rstrip("."):
            depth += ch == "("
            depth -= ch == ")"
            if ch == "," and depth == 0:
                atoms.append(cur)
                cur = ""
            else:
                cur += ch
        atoms.append(cur)
        rules.append(Rule(rid.strip(), atom(head_s), tuple(atom(a) for a in atoms)))
    return rules
