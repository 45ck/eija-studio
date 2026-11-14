"""Gates over the generated SMT laws (WBS 1.4): hand <=> generated equivalence, and the generic per-pack proof.

``equivalence``   (a pack with a hand-written encoding): over the HAND grammar, for every error code, the hand clause
                  set and the generated clause set are equivalent (``hand XOR generated`` is UNSAT); the generated
                  policy implies every hand-written authority invariant; the hand policy implies every generated law.
                  Negative controls: a pack with a law deleted, a law weakened, or its forbidden effects dropped
                  must each make the gate FAIL.
``pack_proof``    (any pack): the generated policy admits some candidate; every encoded law is falsifiable in the
                  grammar (not vacuous); per law, whether the others already imply it (leave-one-out, reported);
                  a seeded differential against the REAL ``check_policy`` (measured counts), with a planted-defect
                  control (one clause deleted) that the differential must detect.

MEASUREMENT: every count in the report is computed by the run. Bounds: one slot per declared action, enumerated
vocabulary plus one OTHER value per sort, as in ``encoding.py``.
"""
from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import z3

from eija_studio.domain.laws import ActionSourceIn
from eija_studio.domain.models import Transition, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import check_policy

from . import encoding as E
from . import laws_gen as G
from . import vocabulary as V  # the hand-written grammar's vocabulary (used only for a hand-encoded pack)

TIMEOUT_MS = 60_000
FOREIGN = {"role": "<foreign-role>", "state": "<foreign-state>", "effect": "<foreign-effect>", "action": "<ForeignAction>"}


def _solver(*constraints: z3.BoolRef) -> z3.Solver:
    s = z3.Solver()
    s.set(timeout=TIMEOUT_MS)
    s.add(*constraints)
    return s


def _name(result: z3.CheckSatResult, unsat: str, sat: str) -> str:
    """Z3 results are not hashable: name them explicitly (a timeout is ``unknown``, never a pass)."""
    if result == z3.unsat:
        return unsat
    return sat if result == z3.sat else "unknown"


def _status(result: z3.CheckSatResult) -> str:
    return _name(result, "proved", "refuted")


# ---- hand <=> generated -------------------------------------------------------------------------------------

def _hand_grammar(pack: Pack, w: E.SymWorkflow) -> G.Grammar:
    return G.over_hand_grammar(pack, w, E.ROLE, E.STATE, V.GUARDS, V.EFFECT_ATOMS)


def _code_rows(w: E.SymWorkflow, hand: dict[str, z3.BoolRef], gen: dict[str, z3.BoolRef]) -> list[dict[str, Any]]:
    rows = []
    for code in sorted(set(hand) | set(gen)):
        r = _solver(w.canonical(), z3.Xor(hand.get(code, E.FALSE), gen.get(code, E.FALSE))).check()
        rows.append({"code": code, "status": _name(r, "equivalent", "differs")})
    return rows


def _implied(w: E.SymWorkflow, admits: z3.BoolRef, invariants: list[E.Invariant]) -> list[dict[str, str]]:
    return [{"id": i.id, "status": _status(_solver(w.canonical(), admits, z3.Not(i.formula)).check())} for i in invariants]


def equivalence(pack: Pack) -> dict[str, Any]:
    """Compare the generated encoding of ``pack`` with the hand-written one, over the hand grammar."""
    w = E.new_workflow("eqv")
    g = _hand_grammar(pack, w)
    hand_clauses, gen_clauses = E.policy_clauses(w), G.policy_clauses(g, pack)
    hand_admits, gen_admits = E.admits(hand_clauses), E.admits(gen_clauses)
    codes = _code_rows(w, E.error_formulas(hand_clauses), E.error_formulas(gen_clauses))
    admits = _status(_solver(w.canonical(), z3.Xor(hand_admits, gen_admits)).check())
    hand_inv = _implied(w, gen_admits, E.authority_invariants(w))
    gen_inv = _implied(w, hand_admits, G.law_invariants(g, pack))
    ok = (admits == "proved" and all(r["status"] == "equivalent" for r in codes)
          and all(r["status"] == "proved" for r in hand_inv + gen_inv))
    return {"verdict": "PASS" if ok else "FAIL", "admits_equivalent": admits, "codes": codes,
            "codes_equivalent": sum(r["status"] == "equivalent" for r in codes), "codes_total": len(codes),
            "hand_invariants_implied_by_generated_policy": hand_inv, "generated_laws_implied_by_hand_policy": gen_inv}


def without_law(pack: Pack, law_id: str) -> Pack:
    return pack.model_copy(update={"laws": tuple(x for x in pack.laws if x.id != law_id)})


def weaken_source_law(pack: Pack, law_id: str) -> Pack:
    """``law_id`` (an ``action_source_in`` law) admitting every state of the baseline as a source."""
    def widen(law: Any) -> Any:
        if law.id != law_id or not isinstance(law, ActionSourceIn):
            return law
        return law.model_copy(update={"states": tuple(dict.fromkeys((*law.states, *pack.model.states)))})
    return pack.model_copy(update={"laws": tuple(widen(x) for x in pack.laws)})


def without_forbidden_effects(pack: Pack) -> Pack:
    return pack.model_copy(update={"effects": pack.effects.model_copy(update={"forbidden": ()})})


def planted_defects(pack: Pack) -> dict[str, Pack]:
    """Every law deleted in turn, every source law widened in turn, and the forbidden effects dropped."""
    planted = {f"delete law {x.id}": without_law(pack, x.id) for x in pack.laws}
    planted |= {f"weaken law {x.id}": weaken_source_law(pack, x.id) for x in pack.laws if isinstance(x, ActionSourceIn)}
    planted["drop the forbidden effects"] = without_forbidden_effects(pack)
    return planted


def equivalence_controls(pack: Pack) -> list[dict[str, Any]]:
    """Planted defects in the PACK: each must make the equivalence gate FAIL (else the gate cannot see a lost law)."""
    out = []
    for name, broken in planted_defects(pack).items():
        result = equivalence(broken)
        refuted = sorted(r["id"] for r in result["hand_invariants_implied_by_generated_policy"] if r["status"] == "refuted")
        out.append({"control": name, "gate_verdict": result["verdict"], "detected": result["verdict"] == "FAIL",
                    "codes_that_differ": [r["code"] for r in result["codes"] if r["status"] != "equivalent"],
                    "hand_invariants_refuted": refuted})
    return out


# ---- the generic per-pack proof -------------------------------------------------------------------------------

def _falsifiable(g: G.Grammar, inv: E.Invariant) -> bool:
    return _solver(g.canonical(), z3.Not(inv.formula)).check() == z3.sat


def independence(g: G.Grammar, pack: Pack) -> list[dict[str, str]]:
    """Per law: does the policy WITHOUT that law's clause still imply it? ``implied_by_others`` is reported, not failed."""
    clauses = G.policy_clauses(g, pack)
    rows = []
    for inv in G.law_invariants(g, pack):
        rest = E.admits(clauses, frozenset(c.id for c in clauses if c.name == "law:" + inv.id[len("LAW:"):]))
        r = _solver(g.canonical(), rest, z3.Not(inv.formula)).check()
        rows.append({"law": inv.id, "status": _name(r, "implied_by_others", "independent")})
    return rows


@dataclass
class Differential:
    candidates: int = 0
    admitted: int = 0
    unvalidated: int = 0
    admission_only: int = 0  # candidates with an undeclared action: the grammar models it as one flag, so only admission is compared
    disagreements: list[dict[str, Any]] = field(default_factory=list)
    fired: dict[str, int] = field(default_factory=dict)
    silent: dict[str, int] = field(default_factory=dict)


class Evaluator:
    """The generated clauses evaluated on a concrete workflow by Z3 itself (one persistent solver, assumption literals)."""

    def __init__(self, pack: Pack, drop: frozenset[str] = frozenset()) -> None:
        self.g = G.grammar(pack, "diff")
        self.clauses = [c if c.id not in drop else E.Clause(c.code, c.name, E.FALSE) for c in G.policy_clauses(self.g, pack)]
        self.fired = {c.id: z3.Bool("fired/" + c.id) for c in self.clauses}
        self.solver = z3.Solver()
        self.solver.add(*(self.fired[c.id] == c.formula for c in self.clauses))

    def __call__(self, wf: Workflow) -> dict[str, bool]:
        literals = [v == x for v, x in G.assignment(self.g, wf)]
        if self.solver.check(*literals) != z3.sat:  # pragma: no cover - a total assignment is satisfiable
            raise RuntimeError("concrete assignment unsatisfiable")
        m = self.solver.model()
        return {k: z3.is_true(m.eval(f, model_completion=True)) for k, f in self.fired.items()}


def _encoded_only(pack: Pack) -> Pack:
    """The pack without the laws the generator does not encode: the differential compares like with like."""
    kept = {law.id for law in G.encoded_laws(pack)}
    return pack.model_copy(update={"laws": tuple(x for x in pack.laws if x.id in kept)})


def _agree(z3_codes: list[str], real: list[str], undeclared: bool) -> bool:
    """Exact codes, except that an undeclared action's own fields are outside the grammar (one flag): then both sides
    must refuse and both must name UNSUPPORTED_ACTION."""
    if not undeclared:
        return z3_codes == real
    return "UNSUPPORTED_ACTION" in z3_codes and "UNSUPPORTED_ACTION" in real


def differential(pack: Pack, seed: int = 20260929, random_mutants: int = 300, drop: frozenset[str] = frozenset(),
                 keep: int = 3) -> Differential:
    ev, target, res = Evaluator(pack, drop), _encoded_only(pack), Differential()
    res.fired, res.silent = {c.id: 0 for c in ev.clauses}, {c.id: 0 for c in ev.clauses}
    declared = {a.id for a in pack.actions}
    for wf, validated in candidates(pack, seed, random_mutants):
        hits = ev(wf)
        z3_codes, real = sorted({c.code for c in ev.clauses if hits[c.id]}), check_policy(wf, target)
        undeclared = any(t.action not in declared for t in wf.transitions)
        res.candidates, res.unvalidated, res.admitted = res.candidates + 1, res.unvalidated + (not validated), res.admitted + (not real)
        res.admission_only += undeclared
        for cid, hit in hits.items():
            (res.fired if hit else res.silent)[cid] += 1
        if not _agree(z3_codes, real, undeclared):
            res.disagreements.append({"z3": z3_codes, "python": real} | ({"candidate": wf.model_dump(mode="json")}
                                                                         if len(res.disagreements) < keep else {}))
    return res


# ---- a generic candidate stream -------------------------------------------------------------------------------

Spec = dict[str, Any]


def to_spec(wf: Workflow) -> Spec:
    return {"initial": wf.initial_state, "states": list(wf.states), "transitions": {
        t.action: {"id": t.id, "role": t.role, "from": t.from_state, "to": t.to_state, "guards": set(t.guards),
                   "req": set(t.required_effects), "forb": set(t.forbidden_effects)} for t in wf.transitions}}


def from_spec(spec: Spec, model_id: str) -> tuple[Workflow, bool]:
    ts = [{"id": t.get("id", "TR-" + a.upper()), "action": a, "from_state": t["from"], "to_state": t["to"], "role": t["role"],
           "guards": tuple(sorted(t["guards"])), "required_effects": tuple(sorted(t["req"])),
           "forbidden_effects": tuple(sorted(t["forb"]))} for a, t in spec["transitions"].items()]
    states = tuple(dict.fromkeys(spec["states"]))
    try:
        return Workflow.model_validate({"id": model_id, "initial_state": spec["initial"], "states": states, "transitions": ts}), True
    except ValueError:
        return Workflow.model_construct(id=model_id, initial_state=spec["initial"], states=states,
                                        transitions=tuple(Transition.model_construct(**t) for t in ts)), False


def _clone(spec: Spec) -> Spec:
    return {"initial": spec["initial"], "states": list(spec["states"]),
            "transitions": {a: {**t, "guards": set(t["guards"]), "req": set(t["req"]), "forb": set(t["forb"])}
                            for a, t in spec["transitions"].items()}}


def _edit(spec: Spec, fn: Any) -> Spec:
    out = _clone(spec)
    fn(out)
    return out


def _template(pack: Pack, action: str, v: G.Vocabulary) -> dict[str, Any]:
    spec = pack.action(action)
    guards, req = (spec.guards, spec.required_effects) if spec is not None else ((), ())
    return {"role": v.roles[0], "from": v.states[0], "to": v.states[0], "guards": set(guards), "req": set(req),
            "forb": set(pack.effects.forbidden)}


def _transition_mutations(spec: Spec, a: str, v: G.Vocabulary) -> Iterator[Spec]:
    cur = spec["transitions"][a]
    for r in (*v.roles, FOREIGN["role"]):
        if r != cur["role"]:
            yield _edit(spec, lambda s, r=r: s["transitions"][a].update(role=r))
    for end in ("from", "to"):
        for st in (*v.states, FOREIGN["state"]):
            if st != cur[end]:
                yield _edit(spec, lambda s, e=end, st=st: s["transitions"][a].update({e: st}))
    for key, universe in (("guards", v.guards), ("req", (*v.effects, FOREIGN["effect"])), ("forb", (*v.effects, FOREIGN["effect"]))):
        for x in universe:
            yield _edit(spec, lambda s, k=key, x=x: s["transitions"][a][k].symmetric_difference_update({x}))
    yield _edit(spec, lambda s: s["transitions"].pop(a))


def single_mutations(spec: Spec, pack: Pack, v: G.Vocabulary) -> Iterator[Spec]:
    """Every one-field change within the vocabulary plus one foreign value per field, in a fixed order."""
    for a in list(spec["transitions"]):
        yield from _transition_mutations(spec, a, v)
    for a in (*v.actions, FOREIGN["action"]):
        if a not in spec["transitions"]:
            yield _edit(spec, lambda s, a=a: s["transitions"].update({a: _template(pack, a, v)}))
    for st in (*v.states, FOREIGN["state"]):
        yield _edit(spec, lambda s, st=st: s.update(states=[x for x in s["states"] if x != st] if st in s["states"] else [*s["states"], st]))
        if st != spec["initial"]:
            yield _edit(spec, lambda s, st=st: s.update(initial=st))


def candidates(pack: Pack, seed: int, random_mutants: int) -> Iterator[tuple[Workflow, bool]]:
    """Seeds (the baseline and every meaning's structural result), all their single mutants, then seeded multi-mutants."""
    rng, v = random.Random(seed), G.vocabulary(pack)  # noqa: S311 - seeded case generator, not security
    seeds = [to_spec(m) for m in G._models(pack)]
    for spec in seeds:
        yield from_spec(spec, pack.model.id)
        for m in single_mutations(spec, pack, v):
            yield from_spec(m, pack.model.id)
    for _ in range(random_mutants):
        spec = _clone(rng.choice(seeds))
        for _ in range(rng.randint(2, 5)):
            spec = rng.choice(list(single_mutations(spec, pack, v)))
        yield from_spec(spec, pack.model.id)


def pack_proof(pack: Pack, seed: int = 20260929, random_mutants: int = 300) -> dict[str, Any]:
    g = G.grammar(pack, "proof")
    clauses, invariants = G.policy_clauses(g, pack), G.law_invariants(g, pack)
    admits_some = _solver(g.canonical(), E.admits(clauses)).check() == z3.sat
    falsifiable = {i.id: _falsifiable(g, i) for i in invariants}
    diff = differential(pack, seed, random_mutants)
    first_law = next((c.id for c in clauses if c.name.startswith("law:")), clauses[0].id)
    control = differential(pack, seed, random_mutants, drop=frozenset({first_law}))
    ok = admits_some and all(falsifiable.values()) and not diff.disagreements and diff.candidates > 0 and bool(control.disagreements)
    return {"verdict": "PASS" if ok else "FAIL", "pack": pack.id, "vocabulary": G.vocabulary(pack).__dict__,
            "clauses": len(clauses), "encoded_laws": len(invariants), "not_encoded": G.not_encoded(pack),
            "policy_admits_some_candidate": admits_some, "each_law_falsifiable": falsifiable,
            "independence": independence(g, pack),
            "differential": {"seed": seed, "candidates": diff.candidates, "admitted_by_real_policy": diff.admitted,
                             "bypassing_pydantic_validators": diff.unvalidated,
                             "compared_on_admission_only_undeclared_action": diff.admission_only, "disagreements": diff.disagreements,
                             "clauses_never_fired": sorted(c for c, n in diff.fired.items() if n == 0),
                             "clauses_never_silent": sorted(c for c, n in diff.silent.items() if n == 0)},
            "negative_control": {"deleted_clause": first_law, "disagreements_found": len(control.disagreements),
                                 "detected": bool(control.disagreements)},
            "verifiers": [{"kind": x.kind, "mode": x.mode, "reason": x.reason} for x in pack.verifiers]}


# ---- report / CLI -----------------------------------------------------------------------------------------------

def build_report(pack: Pack, random_mutants: int = 300, seed: int = 20260929) -> dict[str, Any]:
    """The generic proof for any pack, plus the equivalence gate and its controls where the pack has a hand encoding."""
    proof = pack_proof(pack, seed, random_mutants)
    hand = next((x for x in pack.verifiers if x.kind == "smt_proof" and x.mode == "hand_encoded"), None)
    report: dict[str, Any] = {"schema": "eija.smt-laws/v1", "kind": "smt_generated_laws", "pack": pack.id,
                              "pack_digest": pack.digest, "generic_proof": proof}
    if hand is None:
        report["equivalence"] = {"status": "NOT_RUN", "reason": "the pack has no hand-written SMT encoding to compare with"}
        report["verdict"] = proof["verdict"]
        return report
    eq = equivalence(pack)
    controls = equivalence_controls(pack)
    report["equivalence"] = eq | {"negative_controls": controls}
    ok = proof["verdict"] == "PASS" and eq["verdict"] == "PASS" and all(c["detected"] for c in controls)
    report["verdict"] = "PASS" if ok else "FAIL"
    return report

