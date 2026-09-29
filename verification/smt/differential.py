"""Faithfulness check: the Z3 encoding must agree with the REAL `check_policy` (and with a plain-Python
statement of the authority invariant) on many concrete candidates.

Without this the theorem would be about a different policy. The candidate set is deterministic:
every single-field mutation of each accepted workflow, then seeded random multi-field mutations and
seeded fully random candidates. Candidates deliberately include ones the pydantic validators would
refuse (built with `model_construct`) and strings outside the symbolic vocabulary.

What agreement establishes: on these candidates the encoding returns exactly the error codes the
real function returns and the same invariant verdicts. It does not establish agreement everywhere;
the sampled agreement plus full clause coverage is the evidence, and the report says how many
candidates and how many clauses were exercised in each polarity.
"""
from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass, field

import z3

from eija_studio.domain.models import SemanticTransaction, Transition, Workflow
from eija_studio.domain.policy import apply_transaction, baseline, check_policy, transition

from . import encoding as E
from . import vocabulary as V

FOREIGN_ROLES = (*V.ROLES, "Auditor")
FOREIGN_STATES = (*V.STATES, "Limbo")
FOREIGN_EFFECTS = (*V.EFFECT_ATOMS, "Audit:Foreign")

Spec = dict  # {"initial": str, "states": list[str], "transitions": {action: {...}}}


# ------------------------------------------------------------------------------------------------
# Plain-Python authority invariant (independent of the Z3 encoding and of check_policy)
# ------------------------------------------------------------------------------------------------

def python_invariants(wf: Workflow) -> dict[str, bool]:
    """The same statements as `encoding.authority_invariants`, computed directly on a Workflow."""
    by = {t.action: t for t in wf.transitions}
    ts = list(wf.transitions)
    decide = [by[a] for a in ("Approve", "Reject") if a in by]
    approve, recommend, reject = by.get("Approve"), by.get("Recommend"), by.get("Reject")
    return {
        "INV-TEACHER-NOT-DECIDER": all(t.role != "Teacher" for t in decide),
        "INV-REGISTRAR-ONLY-DECIDES": all(t.role == "Registrar" for t in decide),
        "INV-TEACHER-TRANSITIONS-NEVER-DECIDE": all(t.to_state not in ("Approved", "Rejected") for t in ts if t.role == "Teacher" and t.action in V.ACTIONS),
        "INV-TEACHER-EMITS-NO-DECISION-AUDIT": all(not set(V.DECISION_AUDIT) & set(t.required_effects) for t in ts if t.role == "Teacher" and t.action in V.ACTIONS),
        "INV-APPROVE-REQUIRES-RECOMMENDED": not (approve and recommend) or approve.from_state == "Recommended",
        "INV-APPROVED-ONLY-VIA-APPROVE": all(t.to_state != "Approved" for t in ts if t.action in V.ACTIONS and t.action != "Approve"),
        "INV-RECOMMEND-REQUIRES-ASSIGNMENT": recommend is None or ("actor_assigned" in recommend.guards and recommend.role == "Teacher"),
        "INV-RECOMMEND-CANNOT-CONCLUDE": recommend is None or recommend.to_state == "Recommended",
        "INV-REJECT-SOURCE-BOUNDED": reject is None or reject.from_state in ("Recommended", "Submitted"),
        "INV-APPROVE-ENDS-IN-APPROVED": approve is None or approve.to_state == "Approved",
        "INV-RECOMMEND-STARTS-FROM-SUBMITTED": recommend is None or recommend.from_state == "Submitted",
        "INV-REJECT-FROM-SUBMITTED-WITHOUT-RECOMMENDATION": reject is None or recommend is not None or reject.from_state == "Submitted",
        "INV-FORBIDDEN-EFFECTS-EXCLUDED": all(not set(V.REQUIRED_FORBIDDEN_EFFECTS) & set(t.required_effects) and set(V.REQUIRED_FORBIDDEN_EFFECTS) <= set(t.forbidden_effects)
                                              for t in ts if t.action in V.ACTIONS),
        "INV-MANDATORY-GUARDS-PRESENT": all(set(t.guards) >= set(V.REQUIRED_BASE_GUARDS) for t in ts if t.action in V.ACTIONS),
        "INV-CLOSED-WORKFLOW": wf.initial_state == "Draft" and all(t.action in V.ACTIONS for t in ts) and all(s in V.STATES for s in wf.states),
    }


# ------------------------------------------------------------------------------------------------
# Candidate generation
# ------------------------------------------------------------------------------------------------

def to_spec(wf: Workflow) -> Spec:
    return {"initial": wf.initial_state, "states": list(wf.states), "transitions": {
        t.action: {"role": t.role, "from": t.from_state, "to": t.to_state, "guards": set(t.guards),
                   "req": set(t.required_effects), "forb": set(t.forbidden_effects)} for t in wf.transitions}}


def from_spec(spec: Spec) -> tuple[Workflow, bool]:
    """(workflow, passes_pydantic_validators)."""
    ts = [{"id": "TR-" + a.upper().replace(" ", "-"), "action": a, "from_state": t["from"], "to_state": t["to"],
           "role": t["role"], "guards": tuple(sorted(t["guards"])), "required_effects": tuple(sorted(t["req"])),
           "forbidden_effects": tuple(sorted(t["forb"]))} for a, t in spec["transitions"].items()]
    states = tuple(dict.fromkeys(spec["states"]))
    try:
        return Workflow.model_validate({"id": "excursion", "initial_state": spec["initial"], "states": states, "transitions": tuple(ts)}), True
    except ValueError:
        return Workflow.model_construct(id="excursion", initial_state=spec["initial"], states=states,
                                        transitions=tuple(Transition.model_construct(**t) for t in ts)), False


def seeds() -> list[Workflow]:
    base = baseline()
    return [base] + [apply_transaction(base, SemanticTransaction(kind="enable_recommendation", rejection_source=s))
                     for s in ("Recommended", "Submitted")]


def _template(action: str) -> dict:
    if action not in V.ACTIONS:  # a foreign action, otherwise a well-formed transition
        return {"role": "Teacher", "from": "Draft", "to": "Draft", "guards": set(V.BASE_GUARDS_TUPLE),
                "req": set(), "forb": set(V.FORBIDDEN_EFFECTS)}
    t = transition(action, "Draft", "Draft", "Teacher")
    return {"role": t.role, "from": t.from_state, "to": t.to_state, "guards": set(t.guards),
            "req": set(t.required_effects), "forb": set(t.forbidden_effects)}


def _clone(spec: Spec) -> Spec:
    return {"initial": spec["initial"], "states": list(spec["states"]), "transitions": {
        a: {"role": t["role"], "from": t["from"], "to": t["to"], "guards": set(t["guards"]),
            "req": set(t["req"]), "forb": set(t["forb"])} for a, t in spec["transitions"].items()}}


def single_mutations(spec: Spec) -> Iterator[Spec]:
    """Every one-field change to `spec` within the foreign-extended vocabulary, in a fixed order."""
    def edit(fn) -> Spec:
        s = _clone(spec)
        fn(s)
        return s

    for a in list(spec["transitions"]):
        cur = spec["transitions"][a]
        for r in FOREIGN_ROLES:
            if r != cur["role"]:
                yield edit(lambda s, a=a, r=r: s["transitions"][a].update(role=r))
        for field_ in ("from", "to"):
            for st in FOREIGN_STATES:
                if st != cur[field_]:
                    yield edit(lambda s, a=a, f=field_, st=st: s["transitions"][a].update({f: st}))
        for key, universe in (("guards", V.GUARDS), ("req", FOREIGN_EFFECTS), ("forb", FOREIGN_EFFECTS)):
            for x in universe:
                yield edit(lambda s, a=a, k=key, x=x: s["transitions"][a][k].symmetric_difference_update({x}))
        yield edit(lambda s, a=a: s["transitions"].pop(a))
    for a in (*V.ACTIONS, "Cancel"):
        if a not in spec["transitions"]:
            yield edit(lambda s, a=a: s["transitions"].update({a: _template(a)}))
    for st in FOREIGN_STATES:
        yield edit(lambda s, st=st: s.update(states=[x for x in s["states"] if x != st] if st in s["states"] else [*s["states"], st]))
    for st in FOREIGN_STATES:
        if st != spec["initial"]:
            yield edit(lambda s, st=st: s.update(initial=st))


def random_spec(rng: random.Random) -> Spec:
    actions = [a for a in V.ACTIONS if rng.random() < 0.85] + (["Cancel"] if rng.random() < 0.1 else [])
    return {"initial": rng.choice(FOREIGN_STATES), "states": [s for s in FOREIGN_STATES if rng.random() < 0.7],
            "transitions": {a: {"role": rng.choice(FOREIGN_ROLES), "from": rng.choice(FOREIGN_STATES),
                                "to": rng.choice(FOREIGN_STATES), "guards": {g for g in V.GUARDS if rng.random() < 0.7},
                                "req": {e for e in FOREIGN_EFFECTS if rng.random() < 0.25},
                                "forb": {e for e in FOREIGN_EFFECTS if rng.random() < 0.5}} for a in actions}}


def candidates(seed: int, random_mutants: int, random_fresh: int) -> Iterator[tuple[Workflow, bool]]:
    """Deterministic stream: seeds, all single mutants of each seed, then seeded random candidates."""
    rng = random.Random(seed)  # noqa: S311 - seeded case generator, not security
    base_specs = [to_spec(w) for w in seeds()]
    for spec in base_specs:
        yield from_spec(spec)
    for spec in base_specs:
        for m in single_mutations(spec):
            yield from_spec(m)
    for _ in range(random_mutants):
        spec = _clone(rng.choice(base_specs))
        for _ in range(rng.randint(2, 6)):
            spec = rng.choice(list(single_mutations(spec)))
        yield from_spec(spec)
    for _ in range(random_fresh):
        yield from_spec(random_spec(rng))


# ------------------------------------------------------------------------------------------------
# Comparison
# ------------------------------------------------------------------------------------------------

@dataclass
class DifferentialResult:
    candidates: int = 0
    accepted: int = 0
    unvalidated: int = 0
    code_disagreements: list[dict] = field(default_factory=list)
    invariant_disagreements: list[dict] = field(default_factory=list)
    soundness_violations: list[dict] = field(default_factory=list)
    clause_fired: dict[str, int] = field(default_factory=dict)
    clause_silent: dict[str, int] = field(default_factory=dict)
    invariant_true: dict[str, int] = field(default_factory=dict)
    invariant_false: dict[str, int] = field(default_factory=dict)

    @property
    def clauses_never_fired(self) -> list[str]:
        return sorted(c for c, n in self.clause_fired.items() if n == 0)

    @property
    def clauses_never_silent(self) -> list[str]:
        return sorted(c for c, n in self.clause_silent.items() if n == 0)

    @property
    def agrees(self) -> bool:
        return not (self.code_disagreements or self.invariant_disagreements or self.soundness_violations)


class Evaluator:
    """Evaluates the symbolic clauses and invariants on a concrete workflow with the Z3 solver itself.

    Every clause and invariant is defined once as a named Boolean in a persistent solver; a concrete
    workflow is asserted through assumption literals and the defined Booleans are read from the model."""

    def __init__(self, drop_clauses: frozenset[str] = frozenset()) -> None:
        """`drop_clauses` deletes encoded clauses (a deliberately unfaithful encoding, for the tests
        that show this differential check can actually detect an unfaithful encoding)."""
        self.w = E.new_workflow("diff")
        self.clauses = [c if c.id not in drop_clauses else E.Clause(c.code, c.name, E.FALSE)
                        for c in E.policy_clauses(self.w)]
        self.invariants = E.authority_invariants(self.w)
        self.solver = z3.Solver()
        self.fired = {c.id: z3.Bool("fired/" + c.id) for c in self.clauses}
        self.holds = {i.id: z3.Bool("holds/" + i.id) for i in self.invariants}
        for c in self.clauses:
            self.solver.add(self.fired[c.id] == c.formula)
        for i in self.invariants:
            self.solver.add(self.holds[i.id] == i.formula)
        self._literals: dict[tuple[int, int], z3.BoolRef] = {}

    def _literal(self, var: z3.ExprRef, value: z3.ExprRef) -> z3.BoolRef:
        key = (var.get_id(), value.get_id())
        if key not in self._literals:
            self._literals[key] = var == value
        return self._literals[key]

    def __call__(self, wf: Workflow) -> tuple[dict[str, bool], dict[str, bool]]:
        literals = [self._literal(v, x) for v, x in E.assignment(self.w, wf)]
        if self.solver.check(*literals) != z3.sat:  # pragma: no cover - a total assignment is satisfiable
            raise RuntimeError("concrete assignment unsatisfiable")
        m = self.solver.model()

        def truth(f: z3.BoolRef) -> bool:
            return z3.is_true(m.eval(f, model_completion=True))

        return ({k: truth(f) for k, f in self.fired.items()}, {k: truth(f) for k, f in self.holds.items()})


def run(seed: int = 20260928, random_mutants: int = 1500, random_fresh: int = 500, keep: int = 5,
        drop_clauses: frozenset[str] = frozenset(), stop_at_first_disagreement: bool = False) -> DifferentialResult:
    ev = Evaluator(drop_clauses)
    res = DifferentialResult(clause_fired={c.id: 0 for c in ev.clauses}, clause_silent={c.id: 0 for c in ev.clauses},
                             invariant_true={i.id: 0 for i in ev.invariants}, invariant_false={i.id: 0 for i in ev.invariants})
    for wf, validated in candidates(seed, random_mutants, random_fresh):
        res.candidates += 1
        res.unvalidated += not validated
        clause_hits, inv = ev(wf)
        for cid, hit in clause_hits.items():
            (res.clause_fired if hit else res.clause_silent)[cid] += 1
        z3_codes = sorted({c.code for c in ev.clauses if clause_hits[c.id]})
        real_codes = check_policy(wf)
        if z3_codes != real_codes:
            res.code_disagreements.append({"z3": z3_codes, "python": real_codes} | (
                {"candidate": wf.model_dump(mode="json")} if len(res.code_disagreements) < keep else {}))
        res.accepted += not real_codes
        py_inv = python_invariants(wf)
        for name, holds in inv.items():
            (res.invariant_true if holds else res.invariant_false)[name] += 1
            if holds != py_inv[name]:
                res.invariant_disagreements.append({"invariant": name, "z3": holds, "python": py_inv[name],
                                                    "candidate": wf.model_dump(mode="json")})
            if not real_codes and not py_inv[name]:
                res.soundness_violations.append({"invariant": name, "candidate": wf.model_dump(mode="json")})
        if stop_at_first_disagreement and not res.agrees:  # negative controls only need to see one disagreement
            break
    return res
