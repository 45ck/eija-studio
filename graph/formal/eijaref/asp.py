"""Optional bridge from the rule IR to clingo (Answer Set Programming, MIT): a third evaluator and a fixture synthesiser.

Needs the ``clingo`` wheel; when it is absent every function here raises ``Unavailable`` and the callers
report NOT_RUN. clingo is a TEST-TIME tool of the formal lane: it is never in the trust path of a verdict.

Two uses, both validated against ``rules.evaluate`` (the definition):

* ``evaluate_asp``: evaluate the IR on given base facts. For a stratified program the intended semantics is
  the perfect model computed by ``rules.evaluate``; that clingo returns exactly that model is UNVERIFIED as a
  theorem in this lane's sources and is tested by differential runs instead.
* ``synthesise``: search a bounded universe for the smallest base fact set that makes a target predicate
  non-empty (a positive fixture), or report that none exists within the bound (a dead-rule alarm that is
  bounded, not a proof). Every fixture found is replayed through ``rules.evaluate`` by the caller before it
  is used, so a translation bug in either direction is caught: the solver's answer is a witness, checked by
  the reference.
"""
from __future__ import annotations

from typing import Iterable

from . import rules as R

try:
    import clingo
except ImportError:  # optional
    clingo = None


class Unavailable(RuntimeError):
    pass


def available() -> bool:
    return clingo is not None


def _atom(a: R.Atom) -> str:
    if a.pred == "neq":
        return f"{a.terms[0]} != {a.terms[1]}"
    args = ",".join(a.terms)
    return ("not " if a.neg else "") + (f"{a.pred}({args})" if args else a.pred)


def to_asp(rules: Iterable[R.Rule]) -> str:
    lines = []
    for r in sorted(rules, key=lambda r: r.id):
        head = f"{r.head.pred}({','.join(r.head.terms)})"
        lines.append(f"{head} :- {', '.join(_atom(a) for a in r.body)}.")
    return "\n".join(lines) + "\n"


def _solve(program: str, optimise: bool = False) -> list[frozenset[str]]:
    """Stable models of ``program``. With ``optimise`` the last model reported is an optimal one."""
    ctl = clingo.Control(["--opt-mode=opt" if optimise else "--models=1", "--parallel-mode=1", "--seed=0"],
                         logger=lambda code, message: None)  # "atom does not occur in any rule head" is expected here
    ctl.add("base", [], program)
    ctl.ground([("base", [])])
    out: list[frozenset[str]] = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            out.append(frozenset(str(sym) for sym in model.symbols(atoms=True)))
    return out


def _parse_atom(text: str) -> tuple[str, tuple[str, ...]]:
    if "(" not in text:
        return text, ()
    name, rest = text.split("(", 1)
    return name, tuple(rest[:-1].split(","))


def _facts_from(model: frozenset[str], only: set[str] | None = None) -> R.Facts:
    out: R.Facts = {}
    for text in sorted(model):
        name, args = _parse_atom(text)
        if only is None or name in only:
            out.setdefault(name, set()).add(args)
    return out


def evaluate_asp(rules: list[R.Rule], base: R.Facts) -> R.Facts:
    if clingo is None:
        raise Unavailable("clingo is not installed")
    facts = "".join(f"{p}({','.join(t)}).\n" for p, ts in sorted(base.items()) for t in sorted(ts))
    models = _solve(facts + to_asp(rules))
    if len(models) != 1:
        raise R.RuleError("a stratified program must have exactly one stable model")
    return _facts_from(models[0])


def synthesise(rules: list[R.Rule], base_arity: dict[str, int], universe: list[str], target: str,
               target_arity: int, max_facts: int) -> R.Facts | None:
    """Smallest set of base facts over ``universe`` such that ``target`` is non-empty, or None if there is none
    with at most ``max_facts`` facts."""
    if clingo is None:
        raise Unavailable("clingo is not installed")
    program = "".join(f"dom({c}).\n" for c in universe)
    terms = []
    for p, k in sorted(base_arity.items()):
        vs = ",".join(f"V{i}" for i in range(k))
        doms = ",".join(f"dom(V{i})" for i in range(k))
        program += f"{{ {p}({vs}) : {doms} }}.\n"
        terms.append(f"1,{p},{vs} : {p}({vs})")
    program += to_asp(rules)
    program += f":- #sum {{ {'; '.join(terms)} }} > {max_facts}.\n"
    program += f"has_target :- {target}({','.join('_' for _ in range(target_arity))}).\n:- not has_target.\n"
    program += f"#minimize {{ {'; '.join(terms)} }}.\n"
    models = _solve(program, optimise=True)
    return _facts_from(models[-1], set(base_arity)) if models else None
