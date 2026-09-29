"""Symbolic encoding of the Transition grammar, of `check_policy`, and of the authority invariant.

Three separate artefacts, kept apart on purpose:

* `SymWorkflow`      the grammar: every candidate the policy could be asked about (one slot per known
                     action, plus a flag for "some other action exists").
* `policy_clauses`   a hand-written re-encoding of `domain.policy.check_policy`, one named clause per
                     condition that appends an error code. Faithfulness to the real function is NOT
                     assumed: `differential.py` compares the two on many candidates.
* `authority_invariants`  the requirement, written from the policy's stated intent (docs and ADR), not
                     from the code of `check_policy`, so that "policy => invariant" is a real claim.

Grammar assumptions (each is repeated in the evidence report):

* Actions are unique per workflow (the `Workflow.coherent` validator). `check_policy` indexes
  transitions by action, so a duplicate action would hide a transition; this is a precondition the
  proof relies on, and `duplicate_action_gap()` in `prove.py` demonstrates it.
* Roles, states and effects outside the known vocabulary are one `OTHER` value each (sound because
  the policy only tests equality against known constants).
* No other `Transition` validator is assumed: mandatory guards, required/forbidden disjointness and
  from/to membership in `states` are left free, so the proof relies on the policy alone for them.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import count

import z3

from eija_studio.domain.models import Transition, Workflow
from verification.excursion_pack import EFFECTS

from . import vocabulary as V

RoleSort, ROLE_CONST = z3.EnumSort("Role", [*V.ROLES, "OTHER"])
StateSort, STATE_CONST = z3.EnumSort("State", [*V.STATES, "OTHER"])
ROLE = dict(zip([*V.ROLES, V.OTHER], ROLE_CONST, strict=True))
STATE = dict(zip([*V.STATES, V.OTHER], STATE_CONST, strict=True))
_ids = count()
TRUE, FALSE = z3.BoolVal(True), z3.BoolVal(False)


@dataclass(frozen=True)
class SymTransition:
    action: str
    present: z3.BoolRef
    role: z3.ExprRef
    source: z3.ExprRef
    target: z3.ExprRef
    guards: dict[str, z3.BoolRef]
    required: dict[str, z3.BoolRef]
    required_other: z3.BoolRef
    forbidden: dict[str, z3.BoolRef]

    def variables(self) -> list[z3.ExprRef]:
        return [self.present, self.role, self.source, self.target, *self.guards.values(),
                *self.required.values(), self.required_other, *self.forbidden.values()]

    def absent_defaults(self) -> z3.BoolRef:
        """Canonical form of an unused slot: an absent action's fields are never read, so pin them."""
        pinned = [self.role == ROLE[V.OTHER], self.source == STATE[V.OTHER], self.target == STATE[V.OTHER],
                  *(z3.Not(g) for g in self.guards.values()), *(z3.Not(r) for r in self.required.values()),
                  z3.Not(self.required_other), *(z3.Not(f) for f in self.forbidden.values())]
        return z3.Or(self.present, z3.And(*pinned))


@dataclass(frozen=True)
class SymWorkflow:
    transitions: dict[str, SymTransition]
    has_other_action: z3.BoolRef
    states_in: dict[str, z3.BoolRef]
    states_extra: z3.BoolRef
    initial: z3.ExprRef

    @property
    def candidate(self) -> z3.BoolRef:
        return self.transitions["Recommend"].present

    def variables(self) -> list[z3.ExprRef]:
        out: list[z3.ExprRef] = [self.has_other_action, self.states_extra, self.initial, *self.states_in.values()]
        for action in V.ACTIONS:
            out.extend(self.transitions[action].variables())
        return out

    def canonical(self) -> z3.BoolRef:
        return z3.And(*(t.absent_defaults() for t in self.transitions.values()))


def new_workflow(prefix: str = "w") -> SymWorkflow:
    """Fresh symbolic candidate. Distinct prefixes give independent candidates."""
    p = f"{prefix}{next(_ids)}"

    def b(name: str) -> z3.BoolRef:
        return z3.Bool(f"{p}.{name}")

    transitions = {}
    for a in V.ACTIONS:
        transitions[a] = SymTransition(
            action=a, present=b(f"{a}.present"),
            role=z3.Const(f"{p}.{a}.role", RoleSort), source=z3.Const(f"{p}.{a}.from", StateSort),
            target=z3.Const(f"{p}.{a}.to", StateSort),
            guards={g: b(f"{a}.guard.{g}") for g in V.GUARDS},
            required={e: b(f"{a}.req.{e}") for e in V.EFFECT_ATOMS}, required_other=b(f"{a}.req.<other>"),
            forbidden={e: b(f"{a}.forb.{e}") for e in V.EFFECT_ATOMS})
    return SymWorkflow(transitions=transitions, has_other_action=b("other_action"),
                       states_in={s: b(f"state.{s}") for s in V.STATES}, states_extra=b("state.<other>"),
                       initial=z3.Const(f"{p}.initial", StateSort))


# ------------------------------------------------------------------------------------------------
# check_policy, clause by clause
# ------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Clause:
    """One condition that makes `check_policy` append `code`. `name` identifies it for leave-one-out."""
    code: str
    name: str
    formula: z3.BoolRef

    @property
    def id(self) -> str:
        return f"{self.code}/{self.name}"


def policy_clauses(w: SymWorkflow) -> list[Clause]:
    """Re-encoding of `domain.policy.check_policy` (read that function alongside this one)."""
    cand = w.candidate
    clauses: list[Clause] = []

    def add(code: str, name: str, formula: z3.BoolRef) -> None:
        clauses.append(Clause(code, name, formula))

    shape = "UNSUPPORTED_WORKFLOW_SHAPE"
    add(shape, "actions", z3.Or(w.has_other_action, *(z3.Not(w.transitions[a].present) for a in V.MANDATORY_ACTIONS)))
    add(shape, "states", z3.Or(w.states_extra, *(z3.Not(w.states_in[s]) for s in V.STATES if s != "Recommended"),
                               w.states_in["Recommended"] != cand))
    add(shape, "initial", w.initial != STATE["Draft"])
    add("UNSUPPORTED_ACTION", "unknown_action", w.has_other_action)

    expected = {  # action -> (role, source or None, target); None = only the rejection-source rule applies
        "Submit": ("Teacher", STATE["Draft"], "Submitted"),
        "Revise": ("Teacher", STATE["Rejected"], "Draft"),
        "Approve": ("Registrar", z3.If(cand, STATE["Recommended"], STATE["Submitted"]), "Approved"),
        "Reject": ("Registrar", None, "Rejected"),
        "Recommend": ("Teacher", STATE["Submitted"], "Recommended"),
    }
    for a in V.ACTIONS:
        t = w.transitions[a]
        role, source, target = expected[a]
        add(f"PROTECTED_AUTHORITY:{a}", "role", z3.And(t.present, t.role != ROLE[role]))
        add(f"PROTECTED_STATE:{a}", "to", z3.And(t.present, t.target != STATE[target]))
        if source is not None:
            add(f"PROTECTED_STATE:{a}", "from", z3.And(t.present, t.source != source))
        if a == "Reject":  # without the recommendation meaning, Reject must start from Submitted
            add(f"PROTECTED_STATE:{a}", "from-without-recommendation",
                z3.And(t.present, z3.Not(cand), t.source != STATE["Submitted"]))
        if a == "Reject":
            add("UNSUPPORTED_REJECTION_SOURCE", "source",
                z3.And(t.present, t.source != STATE["Recommended"], t.source != STATE["Submitted"]))
        wanted_guards = V.BASE_GUARD_SET | ({"actor_assigned"} if a == "Recommend" else set())
        for g in V.GUARDS:
            add(f"GUARD_POLICY:{a}", g, z3.And(t.present, z3.Not(t.guards[g]) if g in wanted_guards else t.guards[g]))
        wanted_effects = set(EFFECTS[a])
        for e in V.EFFECT_ATOMS:
            add(f"EFFECT_POLICY:{a}", f"required:{e}",
                z3.And(t.present, z3.Not(t.required[e]) if e in wanted_effects else t.required[e]))
        add(f"EFFECT_POLICY:{a}", "required:<other>", z3.And(t.present, t.required_other))
        for f in V.FORBIDDEN_EFFECTS:
            add(f"EFFECT_POLICY:{a}", f"forbidden:{f}", z3.And(t.present, z3.Not(t.forbidden[f])))
    return clauses


def error_formulas(clauses: Iterable[Clause], removed: frozenset[str] = frozenset()) -> dict[str, z3.BoolRef]:
    """error code -> "check_policy appends this code", optionally with some clauses deleted."""
    by_code: dict[str, list[z3.BoolRef]] = {}
    for c in clauses:
        by_code.setdefault(c.code, [])
        if c.id not in removed:
            by_code[c.code].append(c.formula)
    return {code: z3.Or(*fs) if fs else FALSE for code, fs in sorted(by_code.items())}


def admits(clauses: Iterable[Clause], removed: frozenset[str] = frozenset()) -> z3.BoolRef:
    """`check_policy(candidate) == []`."""
    return z3.Not(z3.Or(*error_formulas(clauses, removed).values()))


# ------------------------------------------------------------------------------------------------
# The requirement (independent of check_policy's code)
# ------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Invariant:
    id: str
    statement: str
    formula: z3.BoolRef


def authority_invariants(w: SymWorkflow) -> list[Invariant]:
    """AuthorityInvariant(c), split into independently reported conjuncts.

    Source of intent: docs/TECHNICAL_LEAD_REVIEW.md ("A teacher cannot approve. Recommendation requires
    an active currently assigned actor.") and the option consequences in domain.policy.CANONICAL_OPTIONS
    ("Registrar approval AND rejection initially require Recommended"; teachers never receive final
    authority; forbidden effects excluded; mandatory guards cannot be removed)."""
    T = w.transitions
    present = [T[a] for a in V.ACTIONS]

    def each(fn) -> z3.BoolRef:
        return z3.And(*(z3.Implies(t.present, fn(t)) for t in present))

    decide = (T["Approve"], T["Reject"])
    inv: list[Invariant] = []

    def add(id_: str, statement: str, formula: z3.BoolRef) -> None:
        inv.append(Invariant(id_, statement, formula))

    add("INV-TEACHER-NOT-DECIDER",
        "Teacher never holds Approve or Reject.",
        z3.And(*(z3.Implies(t.present, t.role != ROLE["Teacher"]) for t in decide)))
    add("INV-REGISTRAR-ONLY-DECIDES",
        "Approve and Reject are held by Registrar and by no other role.",
        z3.And(*(z3.Implies(t.present, t.role == ROLE["Registrar"]) for t in decide)))
    add("INV-TEACHER-TRANSITIONS-NEVER-DECIDE",
        "No Teacher-held transition (of any action) ends in Approved or Rejected.",
        each(lambda t: z3.Implies(t.role == ROLE["Teacher"], z3.And(t.target != STATE["Approved"], t.target != STATE["Rejected"]))))
    add("INV-TEACHER-EMITS-NO-DECISION-AUDIT",
        "No Teacher-held transition requires an Approved or Rejected audit effect.",
        each(lambda t: z3.Implies(t.role == ROLE["Teacher"],
                                  z3.And(*(z3.Not(t.required[e]) for e in V.DECISION_AUDIT)))))
    add("INV-APPROVE-REQUIRES-RECOMMENDED",
        "When the recommendation meaning is enabled (Recommend exists), Approve starts from Recommended.",
        z3.Implies(z3.And(T["Approve"].present, w.candidate), T["Approve"].source == STATE["Recommended"]))
    add("INV-APPROVED-ONLY-VIA-APPROVE",
        "Approve is the only transition that can end in Approved.",
        z3.And(*(z3.Implies(T[a].present, T[a].target != STATE["Approved"]) for a in V.ACTIONS if a != "Approve")))
    add("INV-RECOMMEND-REQUIRES-ASSIGNMENT",
        "Recommend is guarded by actor_assigned and held by Teacher.",
        z3.Implies(T["Recommend"].present, z3.And(T["Recommend"].guards["actor_assigned"],
                                                  T["Recommend"].role == ROLE["Teacher"])))
    add("INV-RECOMMEND-CANNOT-CONCLUDE",
        "Recommend ends in Recommended, never in Approved or Rejected.",
        z3.Implies(T["Recommend"].present, T["Recommend"].target == STATE["Recommended"]))
    add("INV-REJECT-SOURCE-BOUNDED",
        "Reject starts only from Recommended or Submitted.",
        z3.Implies(T["Reject"].present, z3.Or(T["Reject"].source == STATE["Recommended"],
                                              T["Reject"].source == STATE["Submitted"])))
    add("INV-APPROVE-ENDS-IN-APPROVED",
        "Approve ends in Approved.",
        z3.Implies(T["Approve"].present, T["Approve"].target == STATE["Approved"]))
    add("INV-RECOMMEND-STARTS-FROM-SUBMITTED",
        "Recommend starts from Submitted.",
        z3.Implies(T["Recommend"].present, T["Recommend"].source == STATE["Submitted"]))
    add("INV-REJECT-FROM-SUBMITTED-WITHOUT-RECOMMENDATION",
        "Without the recommendation meaning (no Recommend), Reject starts from Submitted.",
        z3.Implies(z3.And(T["Reject"].present, z3.Not(w.candidate)), T["Reject"].source == STATE["Submitted"]))
    add("INV-FORBIDDEN-EFFECTS-EXCLUDED",
        "No transition requires a forbidden effect, and every transition forbids all of them.",
        each(lambda t: z3.And(*(z3.And(z3.Not(t.required[f]), t.forbidden[f]) for f in V.REQUIRED_FORBIDDEN_EFFECTS))))
    add("INV-MANDATORY-GUARDS-PRESENT",
        "Every transition carries every base guard (a candidate cannot weaken authority checks).",
        each(lambda t: z3.And(*(t.guards[g] for g in V.REQUIRED_BASE_GUARDS))))
    add("INV-CLOSED-WORKFLOW",
        "The workflow starts in Draft, has no unknown action and no unknown state.",
        z3.And(w.initial == STATE["Draft"], z3.Not(w.has_other_action), z3.Not(w.states_extra)))
    return inv


def pydantic_valid(w: SymWorkflow) -> z3.BoolRef:
    """An over-approximation of "Workflow.model_validate would accept this candidate" (mandatory guards present,
    required and forbidden effects disjoint, every from/to state and the initial state declared in `states`).

    It is NOT part of the proof (the proof deliberately assumes no validator). It only lets the leave-one-out
    controls ask a second question: is the clause still critical if the validators are assumed? The witness is
    then re-validated by the real pydantic models in `decode`, so the Z3 model of the validators is never trusted."""
    def declared(state: z3.ExprRef) -> z3.BoolRef:
        return z3.Or(*(z3.And(state == STATE[s], w.states_in[s]) for s in V.STATES),
                     z3.And(state == STATE[V.OTHER], w.states_extra))

    return z3.And(declared(w.initial), *(z3.Implies(t.present, z3.And(
        declared(t.source), declared(t.target), *(t.guards[g] for g in sorted(V.BASE_GUARD_SET)),
        *(z3.Not(z3.And(t.required[x], t.forbidden[x])) for x in V.EFFECT_ATOMS))) for t in w.transitions.values()))


# ------------------------------------------------------------------------------------------------
# Concrete <-> symbolic
# ------------------------------------------------------------------------------------------------

def assignment(w: SymWorkflow, wf: Workflow) -> list[tuple[z3.ExprRef, z3.ExprRef]]:
    """Substitution pairs that make `w` denote the concrete Python workflow `wf`."""
    by = {t.action: t for t in wf.transitions}
    pairs: list[tuple[z3.ExprRef, z3.ExprRef]] = [
        (w.has_other_action, (TRUE if any(a not in V.ACTIONS for a in by) else FALSE)),
        (w.states_extra, (TRUE if any(s not in V.STATES for s in wf.states) else FALSE)),
        (w.initial, STATE[V.abstract(wf.initial_state, V.STATES)])]
    pairs += [(w.states_in[s], (TRUE if s in wf.states else FALSE)) for s in V.STATES]
    for a in V.ACTIONS:
        s, t = w.transitions[a], by.get(a)
        if t is None:
            pairs += [(s.present, FALSE), (s.role, ROLE[V.OTHER]), (s.source, STATE[V.OTHER]),
                      (s.target, STATE[V.OTHER]), *((g, FALSE) for g in s.guards.values()),
                      *((r, FALSE) for r in s.required.values()), (s.required_other, FALSE),
                      *((f, FALSE) for f in s.forbidden.values())]
            continue
        pairs += [(s.present, TRUE), (s.role, ROLE[V.abstract(t.role, V.ROLES)]),
                  (s.source, STATE[V.abstract(t.from_state, V.STATES)]), (s.target, STATE[V.abstract(t.to_state, V.STATES)]),
                  *((s.guards[g], (TRUE if g in t.guards else FALSE)) for g in V.GUARDS),
                  *((s.required[e], (TRUE if e in t.required_effects else FALSE)) for e in V.EFFECT_ATOMS),
                  (s.required_other, (TRUE if any(e not in V.EFFECT_ATOMS for e in t.required_effects) else FALSE)),
                  *((s.forbidden[e], (TRUE if e in t.forbidden_effects else FALSE)) for e in V.EFFECT_ATOMS)]
    return pairs


def evaluate(formula: z3.ExprRef, pairs: list[tuple[z3.ExprRef, z3.ExprRef]]) -> bool:
    return z3.is_true(z3.simplify(z3.substitute(formula, *pairs)))


def _name(enum: dict[str, z3.ExprRef], value: z3.ExprRef) -> str:
    return next(k for k, v in enum.items() if z3.eq(v, value))


def decode(w: SymWorkflow, model: z3.ModelRef) -> tuple[Workflow, bool]:
    """Concrete workflow for a Z3 model. Returns (workflow, passes_pydantic_validators).

    Unvalidated candidates (a counterexample may break `Transition`/`Workflow` validators, because the
    grammar deliberately does not assume them) are built with `model_construct`."""
    def val(x: z3.ExprRef) -> z3.ExprRef:
        return model.eval(x, model_completion=True)

    def on(x: z3.BoolRef) -> bool:
        return z3.is_true(val(x))

    transitions = []
    for a in V.ACTIONS:
        s = w.transitions[a]
        if not on(s.present):
            continue
        required = sorted([e for e in V.EFFECT_ATOMS if on(s.required[e])] + (["Audit:<other>"] if on(s.required_other) else []))
        transitions.append({"id": "TR-" + a.upper(), "action": a, "from_state": _name(STATE, val(s.source)),
                            "to_state": _name(STATE, val(s.target)), "role": _name(ROLE, val(s.role)),
                            "guards": tuple(g for g in V.GUARDS if on(s.guards[g])),
                            "required_effects": tuple(required),
                            "forbidden_effects": tuple(e for e in V.EFFECT_ATOMS if on(s.forbidden[e]))})
    if on(w.has_other_action):
        transitions.append({"id": "TR-OTHER", "action": "Other", "from_state": "Draft", "to_state": "Draft",
                            "role": "Teacher", "guards": V.BASE_GUARDS_TUPLE, "required_effects": (),
                            "forbidden_effects": V.FORBIDDEN_EFFECTS})
    states = tuple(s for s in V.STATES if on(w.states_in[s])) + (("<other-state>",) if on(w.states_extra) else ())
    initial = _name(STATE, val(w.initial))
    initial = "<other-state>" if initial == V.OTHER else initial
    data = {"id": "excursion", "initial_state": initial, "states": states, "transitions": tuple(transitions)}
    try:
        return Workflow.model_validate(data), True
    except ValueError:
        built = tuple(Transition.model_construct(**t) for t in transitions)
        return Workflow.model_construct(id="excursion", initial_state=initial, states=states, transitions=built), False
