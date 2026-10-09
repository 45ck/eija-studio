"""Generated SMT encoding of a domain pack's policy and laws (WBS 1.4).

Everything here is derived from a ``Pack``: the symbolic grammar's vocabulary (actions, states, roles, guards, effect
atoms), the policy clauses (the pack's declared action catalog plus one clause per law, each tagged with the law's
error code) and the laws restated as requirements. No domain word appears in this module.

The grammar is the one ``encoding.py`` uses (one slot per declared action, one OTHER value per enumerated sort, a flag
for "some undeclared action exists"); ``grammar(pack)`` builds a fresh one, and ``over_hand_grammar`` reuses the
hand-written grammar so the two encodings can be compared symbol for symbol (``laws_gate.py``).

Not encoded (reported per law, never silently dropped): ``path_requires`` (a reachability law; its inductive proof is
deferred, docs/engineering/FUTURE-WORK.md) and ``requires_evidence`` (judged by the evidence matrix, not the table).
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from itertools import count
from typing import Any, get_args

import z3

from eija_studio.domain import laws as L
from eija_studio.domain.models import DomainError, Guard, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_structural_all

from .encoding import Clause, Invariant, SymTransition, SymWorkflow

OTHER = "<other>"
TRUE, FALSE = z3.BoolVal(True), z3.BoolVal(False)
NOT_ENCODED = {"path_requires": "a reachability law: its inductive proof is deferred (docs/engineering/FUTURE-WORK.md)",
               "can_reach_end": "a liveness law: judged by the law proof over the kernel's committed steps, not encoded (ADR-0221)",
               "path_requires_kind": "a reachability law: its inductive proof is deferred (docs/engineering/FUTURE-WORK.md)",
               "requires_evidence": "judged by the evidence matrix, not by the transition table"}
_ids = count()


@dataclass(frozen=True)
class Vocabulary:
    actions: tuple[str, ...]
    states: tuple[str, ...]
    roles: tuple[str, ...]
    guards: tuple[str, ...]
    effects: tuple[str, ...]


@dataclass(frozen=True)
class Grammar:
    """A symbolic candidate workflow plus the enum constants its role/state fields range over."""
    vocab: Vocabulary
    w: SymWorkflow
    role: dict[str, z3.ExprRef]
    state: dict[str, z3.ExprRef]

    def present(self, action: str | None) -> z3.BoolRef:
        slot = self.w.transitions.get(action or "")
        return FALSE if slot is None else slot.present

    def slots(self) -> list[SymTransition]:
        return [self.w.transitions[a] for a in self.vocab.actions]

    def canonical(self) -> z3.BoolRef:
        """An absent action's fields are never read, so pin them (as ``SymTransition.absent_defaults``, over this grammar's sorts)."""
        def pinned(t: SymTransition) -> z3.BoolRef:
            atoms = (*t.guards.values(), *t.required.values(), t.required_other, *t.forbidden.values())
            return z3.And(t.role == self.role[OTHER], t.source == self.state[OTHER], t.target == self.state[OTHER],
                          *(z3.Not(x) for x in atoms))
        return z3.And(*(z3.Or(t.present, pinned(t)) for t in self.slots()))


# ---- vocabulary ---------------------------------------------------------------------------------------------

def _law_states(law: Any) -> list[str]:
    found = [getattr(law, name) for name in ("state", "initial_state", "via") if isinstance(getattr(law, name, None), str)]
    return found + list(getattr(law, "states", ()))


def _models(pack: Pack) -> list[Workflow]:
    """The baseline and what every meaning would make of it (structure only), so meaning-added names are in the grammar."""
    out = [pack.model]
    for meaning in pack.meanings:
        try:
            out.append(apply_structural_all(pack.model, meaning.transactions, pack))
        except DomainError:
            continue
    return out


def vocabulary(pack: Pack) -> Vocabulary:
    models = _models(pack)
    states = [s for m in models for s in (m.initial_state, *m.states)] + [s for law in pack.laws for s in _law_states(law)]
    roles = [r.id for r in pack.roles] + [t.role for m in models for t in m.transitions]
    roles += [law.role for law in pack.laws if isinstance(getattr(law, "role", None), str)]
    effects = [e for a in pack.actions for e in a.required_effects] + [e.id for e in pack.effects.catalog]
    effects += list(pack.effects.forbidden) + [e for law in pack.laws for e in getattr(law, "effects", ())]
    return Vocabulary(actions=tuple(a.id for a in pack.actions), states=tuple(sorted(set(states))),
                      roles=tuple(sorted(set(roles))), guards=tuple(get_args(Guard)), effects=tuple(sorted(set(effects))))


def grammar(pack: Pack, prefix: str = "g") -> Grammar:
    """A fresh symbolic candidate over the pack's own vocabulary (distinct sorts per call)."""
    v = vocabulary(pack)
    tag = f"{prefix}{next(_ids)}"
    role_sort, roles = z3.EnumSort(f"Role_{tag}", [*v.roles, OTHER])
    state_sort, states = z3.EnumSort(f"State_{tag}", [*v.states, OTHER])

    def b(name: str) -> z3.BoolRef:
        return z3.Bool(f"{tag}.{name}")

    slots = {a: SymTransition(
        action=a, present=b(f"{a}.present"), role=z3.Const(f"{tag}.{a}.role", role_sort),
        source=z3.Const(f"{tag}.{a}.from", state_sort), target=z3.Const(f"{tag}.{a}.to", state_sort),
        guards={g: b(f"{a}.guard.{g}") for g in v.guards}, required={e: b(f"{a}.req.{e}") for e in v.effects},
        required_other=b(f"{a}.req.<other>"), forbidden={e: b(f"{a}.forb.{e}") for e in v.effects}) for a in v.actions}
    w = SymWorkflow(transitions=slots, has_other_action=b("other_action"), states_in={s: b(f"state.{s}") for s in v.states},
                    states_extra=b("state.<other>"), initial=z3.Const(f"{tag}.initial", state_sort))
    return Grammar(v, w, dict(zip([*v.roles, OTHER], roles, strict=True)), dict(zip([*v.states, OTHER], states, strict=True)))


def over_hand_grammar(pack: Pack, w: SymWorkflow, role: dict[str, z3.ExprRef], state: dict[str, z3.ExprRef],
                      guards: tuple[str, ...], effects: tuple[str, ...]) -> Grammar:
    """The generated encoding over an EXISTING grammar (the hand-written one), for a symbol-for-symbol comparison.
    Refuses when the pack's vocabulary does not fit that grammar: a comparison over a smaller grammar proves nothing."""
    v = vocabulary(pack)
    missing = {"actions": set(v.actions) - set(w.transitions), "states": set(v.states) - set(state),
               "roles": set(v.roles) - set(role), "effects": set(v.effects) - set(effects)}
    if any(missing.values()):
        raise ValueError(f"the pack's vocabulary does not fit the grammar: { {k: sorted(x) for k, x in missing.items() if x} }")
    return Grammar(Vocabulary(v.actions, v.states, v.roles, guards, effects), w, role, state)


# ---- the declared action catalog (domain.policy.declared_codes) ---------------------------------------------

def _differs(atoms: dict[str, z3.BoolRef], wanted: Iterable[str]) -> z3.BoolRef:
    want = set(wanted)
    return z3.Or(*(z3.Not(x) if name in want else x for name, x in atoms.items()))


def catalog_clauses(g: Grammar, pack: Pack) -> list[Clause]:
    out = [Clause("UNSUPPORTED_ACTION", "catalog:undeclared-action", g.w.has_other_action)]
    for spec in pack.actions:
        t = g.w.transitions[spec.id]
        missing_forbidden = z3.Or(*(z3.Not(t.forbidden[f]) for f in pack.effects.forbidden))
        out.append(Clause("GUARD_POLICY:" + spec.id, "catalog:guards", z3.And(t.present, _differs(t.guards, spec.guards))))
        out.append(Clause("EFFECT_POLICY:" + spec.id, "catalog:effects", z3.And(t.present, z3.Or(
            _differs(t.required, spec.required_effects), t.required_other, missing_forbidden))))
    return out


# ---- laws ---------------------------------------------------------------------------------------------------

def _when(g: Grammar, law: Any) -> z3.BoolRef:
    if law.when is None:
        return TRUE
    present = TRUE if law.when.action_present is None else g.present(law.when.action_present)
    absent = TRUE if law.when.action_absent is None else z3.Not(g.present(law.when.action_absent))
    return z3.And(present, absent)


def _action(g: Grammar, action: str, broken: Callable[[SymTransition], z3.BoolRef]) -> z3.BoolRef:
    t = g.w.transitions.get(action)
    return FALSE if t is None else z3.And(t.present, broken(t))


def _any(g: Grammar, broken: Callable[[SymTransition], z3.BoolRef]) -> z3.BoolRef:
    return z3.Or(*(z3.And(t.present, broken(t)) for t in g.slots()))


def _shape(g: Grammar, law: L.ClosedShape) -> z3.BoolRef:
    actions = z3.Or(g.w.has_other_action, *(t.present != z3.BoolVal(t.action in law.actions) for t in g.slots()),
                    z3.BoolVal(bool(set(law.actions) - set(g.vocab.actions))))
    states = z3.Or(g.w.states_extra, *(x != z3.BoolVal(s in law.states) for s, x in g.w.states_in.items()))
    return z3.Or(actions, states, g.w.initial != g.state[law.initial_state])


def _not_of_kind(g: Grammar, law: Any, t: SymTransition) -> z3.BoolRef:
    """The transition's role is none of the law's roles of its kinds (so `<other>`, an undeclared role, never counts)."""
    return z3.And(*(t.role != g.role[r] for r in sorted(law.roles)))


_VIOLATION: dict[type, Callable[[Grammar, Any], z3.BoolRef]] = {
    L.ClosedShape: _shape,
    L.OnlyRoleHolds: lambda g, law: _action(g, law.action, lambda t: t.role != g.role[law.role]),
    L.RoleNeverHolds: lambda g, law: _action(g, law.action, lambda t: t.role == g.role[law.role]),
    L.RoleNeverEnters: lambda g, law: _any(g, lambda t: z3.And(t.role == g.role[law.role], t.target == g.state[law.state])),
    L.StateOnlyVia: lambda g, law: _any(g, lambda t: z3.And(z3.BoolVal(t.action not in law.actions), t.target == g.state[law.state])),
    L.ActionTarget: lambda g, law: _action(g, law.action, lambda t: t.target != g.state[law.state]),
    L.ActionSourceIn: lambda g, law: _action(g, law.action, lambda t: z3.And(*(t.source != g.state[s] for s in law.states))),
    L.ActionRequiresGuard: lambda g, law: _action(g, law.action, lambda t: z3.Or(*(z3.Not(t.guards[x]) for x in law.guards))),
    L.ForbiddenEffects: lambda g, law: _any(g, lambda t: z3.Or(*(z3.Or(t.required[e], z3.Not(t.forbidden[e])) for e in law.effects))),
    L.StateFinal: lambda g, law: _any(g, lambda t: t.source == g.state[law.state]),
    L.OnlyKindHolds: lambda g, law: _action(g, law.action, lambda t: _not_of_kind(g, law, t)),
    L.OnlyKindEnters: lambda g, law: _any(g, lambda t: z3.And(t.target == g.state[law.state], _not_of_kind(g, law, t))),
}


def violation(g: Grammar, law: Any) -> z3.BoolRef | None:
    """"The candidate breaks ``law``" as a formula, or None for a law kind that is not encoded (see NOT_ENCODED)."""
    fn = _VIOLATION.get(type(law))
    return None if fn is None else z3.And(_when(g, law), fn(g, law))


def encoded_laws(pack: Pack) -> list[Any]:
    return [law for law in pack.laws if type(law) in _VIOLATION]


def not_encoded(pack: Pack) -> list[dict[str, str]]:
    return [{"law": law.id, "kind": law.kind, "status": "NOT_RUN", "reason": NOT_ENCODED.get(law.kind, "no encoding")}
            for law in pack.laws if type(law) not in _VIOLATION]


def policy_clauses(g: Grammar, pack: Pack) -> list[Clause]:
    """The generated encoding of ``check_policy`` under ``pack`` (catalog clauses, then one clause per encoded law)."""
    out = catalog_clauses(g, pack)
    for law in encoded_laws(pack):
        formula = violation(g, law)
        if formula is not None:
            out.append(Clause(law.code, "law:" + law.id, formula))
    return out


def law_invariants(g: Grammar, pack: Pack) -> list[Invariant]:
    """Each encoded law restated as a requirement ("the candidate does not break it")."""
    out = []
    for law in encoded_laws(pack):
        formula = violation(g, law)
        if formula is not None:
            out.append(Invariant("LAW:" + law.id, law.description or law.kind, z3.Not(formula)))
    return out


# ---- concrete <-> symbolic ----------------------------------------------------------------------------------

def _abstract(value: str, universe: dict[str, z3.ExprRef]) -> z3.ExprRef:
    return universe.get(value, universe[OTHER])


def _slot_pairs(g: Grammar, s: SymTransition, t: Any) -> list[tuple[z3.ExprRef, z3.ExprRef]]:
    if t is None:
        return [(s.present, FALSE), (s.role, g.role[OTHER]), (s.source, g.state[OTHER]), (s.target, g.state[OTHER]),
                *((x, FALSE) for x in (*s.guards.values(), *s.required.values(), s.required_other, *s.forbidden.values()))]
    return [(s.present, TRUE), (s.role, _abstract(t.role, g.role)), (s.source, _abstract(t.from_state, g.state)),
            (s.target, _abstract(t.to_state, g.state)), *((x, z3.BoolVal(n in t.guards)) for n, x in s.guards.items()),
            *((x, z3.BoolVal(n in t.required_effects)) for n, x in s.required.items()),
            (s.required_other, z3.BoolVal(any(e not in s.required for e in t.required_effects))),
            *((x, z3.BoolVal(n in t.forbidden_effects)) for n, x in s.forbidden.items())]


def assignment(g: Grammar, wf: Workflow) -> list[tuple[z3.ExprRef, z3.ExprRef]]:
    """Substitution pairs that make the grammar denote the concrete workflow ``wf`` (unique actions assumed)."""
    by = {t.action: t for t in wf.transitions}
    pairs: list[tuple[z3.ExprRef, z3.ExprRef]] = [
        (g.w.has_other_action, z3.BoolVal(any(a not in g.w.transitions for a in by))),
        (g.w.states_extra, z3.BoolVal(any(s not in g.w.states_in for s in wf.states))),
        (g.w.initial, _abstract(wf.initial_state, g.state))]
    pairs += [(x, z3.BoolVal(s in wf.states)) for s, x in g.w.states_in.items()]
    for action, slot in g.w.transitions.items():
        pairs += _slot_pairs(g, slot, by.get(action))
    return pairs
