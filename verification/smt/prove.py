"""Z3 proofs, accepted-set enumeration, leave-one-out negative controls and the evidence report."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import z3
from eija_studio.domain.models import SemanticTransaction, Transition, Workflow
from eija_studio.domain.policy import apply_transaction, baseline, check_policy

from verification.formal_report import dumps, kernel_subject, platform_info

from . import differential as D
from . import encoding as E
from . import vocabulary as V

SNAPSHOT = Path(__file__).resolve().parent / "accepted_set.json"
TIMEOUT_MS = 60_000

# Named controls: deleting exactly this clause of the encoded policy must let the named invariant fail.
NAMED_CONTROLS: tuple[tuple[str, str], ...] = (
    ("PROTECTED_AUTHORITY:Approve/role", "INV-TEACHER-NOT-DECIDER"),
    ("PROTECTED_AUTHORITY:Reject/role", "INV-TEACHER-NOT-DECIDER"),
    ("PROTECTED_STATE:Approve/from", "INV-APPROVE-REQUIRES-RECOMMENDED"),
    ("GUARD_POLICY:Recommend/actor_assigned", "INV-RECOMMEND-REQUIRES-ASSIGNMENT"),
    ("GUARD_POLICY:Reject/actor_active", "INV-MANDATORY-GUARDS-PRESENT"),
    ("EFFECT_POLICY:Approve/forbidden:PaymentCaptured", "INV-FORBIDDEN-EFFECTS-EXCLUDED"),
    ("EFFECT_POLICY:Approve/required:PaymentCaptured", "INV-FORBIDDEN-EFFECTS-EXCLUDED"),
    ("UNSUPPORTED_REJECTION_SOURCE/source", "INV-REJECT-SOURCE-BOUNDED"),
)

ASSUMPTIONS = (
    "Candidates are workflows with unique actions (Workflow.coherent). check_policy indexes transitions by action; see assumption_witness.",
    "Roles, states and effects outside the known vocabulary are one OTHER value each: sound because check_policy only compares them by equality/membership against known constants (checked by the differential test on foreign strings).",
    "No Transition validator is assumed (base guards, required/forbidden disjointness, from/to membership are left free), so the policy alone must enforce them.",
    "Transition ids are not read by check_policy and are outside the grammar.",
    "The Z3 encoding of check_policy is hand-written; its faithfulness is established only by the differential test (sampled), not by proof.",
    "AuthorityInvariant is the authors' statement of the policy's intent (same authorship as the policy): it is not an independently derived requirement.",
)
LIMITATIONS = (
    "Proves properties of the policy function on the modelled grammar, not of the runtime, SQLite adapter, HTTP layer or Python interpreter.",
    "UNSAT answers are Z3's; no independently checked proof object is produced. Z3 is in the trusted base.",
    "The accepted set is stated up to extra (non-mandatory) forbidden_effects atoms: check_policy only requires FORBIDDEN to be a subset, so infinitely many harmless supersets are admitted.",
    "Not a human study, not a security audit.",
)


def subject() -> dict[str, Any]:
    return kernel_subject("domain/models.py", "domain/policy.py", function="eija_studio.domain.policy.check_policy")


# ------------------------------------------------------------------------------------------------
# Proofs
# ------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Verdict:
    id: str
    statement: str
    status: str            # proved | refuted | unknown
    seconds: float
    counterexample: dict[str, Any] | None = None

    def as_json(self, with_time: bool = True) -> dict[str, Any]:
        out: dict[str, Any] = {"id": self.id, "statement": self.statement, "status": self.status}
        if self.counterexample is not None:
            out["counterexample"] = self.counterexample
        if with_time:
            out["seconds"] = round(self.seconds, 4)
        return out


def _solver(*constraints: z3.BoolRef) -> z3.Solver:
    s = z3.Solver()
    s.set(timeout=TIMEOUT_MS)
    s.add(*constraints)
    return s


def _witness(w: E.SymWorkflow, m: z3.ModelRef) -> dict[str, Any]:
    wf, validated = E.decode(w, m)
    return {"passes_pydantic_validators": validated, "real_check_policy": check_policy(wf), "candidate": wf.model_dump(mode="json")}


def prove_invariants(removed: frozenset[str] = frozenset()) -> list[Verdict]:
    """For each invariant I: is `canonical AND check_policy admits AND NOT I` satisfiable?

    UNSAT means: over the whole grammar, admission implies I. SAT yields a counterexample candidate."""
    w = E.new_workflow("proof")
    admit = E.admits(E.policy_clauses(w), removed)
    out = []
    for inv in E.authority_invariants(w):
        s = _solver(w.canonical(), admit, z3.Not(inv.formula))
        t0 = time.perf_counter()
        r = s.check()
        dt = time.perf_counter() - t0
        if r == z3.unsat:
            out.append(Verdict(inv.id, inv.statement, "proved", dt))
        elif r == z3.sat:
            out.append(Verdict(inv.id, inv.statement, "refuted", dt, _witness(w, s.model())))
        else:
            out.append(Verdict(inv.id, inv.statement, "unknown", dt))
    return out


def non_vacuity() -> dict[str, Any]:
    """The implication is not vacuous: the policy admits something, and every invariant is falsifiable
    by SOME grammar candidate (i.e. the grammar is rich enough to violate each one)."""
    w = E.new_workflow("vac")
    admits_something = _solver(w.canonical(), E.admits(E.policy_clauses(w))).check() == z3.sat
    falsifiable = {inv.id: _solver(w.canonical(), z3.Not(inv.formula)).check() == z3.sat for inv in E.authority_invariants(w)}
    return {"policy_admits_some_candidate": admits_something, "each_invariant_falsifiable_by_some_candidate": falsifiable}


# ------------------------------------------------------------------------------------------------
# Accepted set
# ------------------------------------------------------------------------------------------------

def _label(wf: Workflow) -> str:
    by = {t.action: t for t in wf.transitions}
    return "baseline" if "Recommend" not in by else f"candidate-reject-from-{by['Reject'].from_state}"


def _summary(wf: Workflow) -> dict[str, Any]:
    return {"label": _label(wf), "semantic_hash": wf.semantic_hash, "states": sorted(wf.states),
            "transitions": [{"action": t.action, "role": t.role, "from": t.from_state, "to": t.to_state,
                             "guards": sorted(t.guards), "required_effects": sorted(t.required_effects),
                             "forbidden_effects": sorted(t.forbidden_effects)}
                            for t in sorted(wf.transitions, key=lambda t: t.id)]}


def enumerate_accepted(limit: int = 64) -> dict[str, Any]:
    """All-SAT over `canonical AND admits`, blocking each found model, up to `limit`.

    Extra forbidden-effect atoms (beyond FORBIDDEN) are pinned off so the enumeration is finite: they are
    the only unconstrained degrees of freedom (documented in LIMITATIONS)."""
    w = E.new_workflow("enum")
    pin_extras = z3.And(*(z3.Not(t.forbidden[e]) for t in w.transitions.values() for e in V.EFFECT_ATOMS
                          if e not in V.FORBIDDEN_EFFECTS))
    s = _solver(w.canonical(), E.admits(E.policy_clauses(w)), pin_extras)
    variables = w.variables()
    found: list[Workflow] = []
    inconsistent: list[dict[str, Any]] = []
    complete = False
    while len(found) < limit:
        r = s.check()
        if r == z3.unsat:
            complete = True
            break
        if r != z3.sat:
            break
        m = s.model()
        wf, validated = E.decode(w, m)
        errors = check_policy(wf)
        if not validated or errors:  # a faithfulness failure: the encoding admits what the real policy or pydantic refuses
            inconsistent.append({"real_check_policy": errors, "passes_pydantic_validators": validated,
                                 "candidate": wf.model_dump(mode="json")})
        else:
            found.append(wf)
        s.add(z3.Or(*(v != m.eval(v, model_completion=True) for v in variables)))
    found.sort(key=lambda x: (len(x.transitions), _label(x)))
    base = baseline()
    reachable = [base] + [apply_transaction(base, SemanticTransaction(kind="enable_recommendation", rejection_source=src))
                          for src in ("Recommended", "Submitted")]
    return {"enumeration_complete": complete, "count": len(found), "inconsistent_models": inconsistent, "accepted": [_summary(x) for x in found],
            "equals_kernel_reachable_set": sorted(x.semantic_hash for x in found) == sorted(x.semantic_hash for x in reachable),
            "kernel_reachable_labels": sorted(_label(x) for x in reachable),
            "expected_labels": ["baseline", "candidate-reject-from-Recommended", "candidate-reject-from-Submitted"]}


# ------------------------------------------------------------------------------------------------
# Negative controls: delete one clause of the encoded policy
# ------------------------------------------------------------------------------------------------

def leave_one_out() -> dict[str, Any]:
    """For every clause c: does `policy minus c` admit a candidate violating some invariant?

    A `critical` clause is one the authority invariant needs. A `not_needed_by_invariants` clause is
    subsumed by the others or enforces a property outside the invariant set (for example the Submit role):
    that is reported, not hidden. Each counterexample is re-run through the REAL check_policy, which must
    reject it citing the deleted clause's code."""
    w = E.new_workflow("loo")
    clauses = E.policy_clauses(w)
    invariants = E.authority_invariants(w)
    negated = z3.Or(*(z3.Not(i.formula) for i in invariants))
    rows = []
    for c in clauses:
        s = _solver(w.canonical(), E.admits(clauses, frozenset({c.id})), negated)
        r = s.check()
        if r == z3.sat:
            m = s.model()
            wf, validated = E.decode(w, m)
            violated = sorted(i.id for i in invariants if z3.is_false(m.eval(i.formula, model_completion=True)))
            real = check_policy(wf)
            rows.append({"clause": c.id, "status": "critical", "violated_invariants": violated,
                         "real_check_policy_rejects": bool(real), "real_errors_include_clause_code": c.code in real,
                         "passes_pydantic_validators": validated, "witness": wf.model_dump(mode="json")})
        else:
            rows.append({"clause": c.id, "status": "not_needed_by_invariants" if r == z3.unsat else "unknown"})
    controls = []
    by_id = {r["clause"]: r for r in rows}
    for clause, invariant in NAMED_CONTROLS:
        row = by_id.get(clause)
        ok = bool(row and row["status"] == "critical" and invariant in row["violated_invariants"]
                  and row["real_check_policy_rejects"] and row["real_errors_include_clause_code"])
        controls.append({"remove": clause, "expect_violation_of": invariant, "counterexample_found": ok})
    return {"clauses": len(rows), "critical": sum(r["status"] == "critical" for r in rows),
            "not_needed_by_invariants": sorted(r["clause"] for r in rows if r["status"] == "not_needed_by_invariants"),
            "unknown": sorted(r["clause"] for r in rows if r["status"] == "unknown"),
            "named_controls": controls,
            "inconsistent_witnesses": sorted(r["clause"] for r in rows if r["status"] == "critical" and not (
                r["real_check_policy_rejects"] and r["real_errors_include_clause_code"])),
            "rows": rows}


# ------------------------------------------------------------------------------------------------
# The uniqueness assumption
# ------------------------------------------------------------------------------------------------

def assumption_witness() -> dict[str, Any]:
    """Shows why 'unique actions' is an assumption: without the Workflow validator, a duplicated action
    hides a Teacher-held Approve from check_policy (it indexes transitions by action; the last one wins)."""
    base = baseline()
    approve = next(t for t in base.transitions if t.action == "Approve")
    rogue = Transition.model_construct(**{**approve.model_dump(), "id": "TR-ROGUE", "role": "Teacher"})
    dup = Workflow.model_construct(initial_state=base.initial_state, states=base.states,
                                   transitions=(rogue, *base.transitions))
    try:
        Workflow.model_validate(dup.model_dump())
        rejected_by_validator = False
    except ValueError:
        rejected_by_validator = True
    return {"assumption": "actions are unique per workflow (Workflow.coherent)",
            "unvalidated_duplicate_action_workflow_admitted_by_check_policy": check_policy(dup) == [],
            "teacher_holds_approve_in_that_workflow": any(t.action == "Approve" and t.role == "Teacher" for t in dup.transitions),
            "workflow_validator_rejects_it": rejected_by_validator,
            "consequence": "Soundness of check_policy depends on every Workflow passing pydantic validation; model_construct bypasses it."}


# ------------------------------------------------------------------------------------------------
# Report
# ------------------------------------------------------------------------------------------------

def grammar_description() -> dict[str, Any]:
    return {"actions": list(V.ACTIONS), "roles": [*V.ROLES, "<other>"], "states": [*V.STATES, "<other>"],
            "guards": list(V.GUARDS), "effect_atoms": list(V.EFFECT_ATOMS), "unknown_action_slot": True,
            "unknown_state_slot": True, "bounded_by": "one slot per known action (unique actions), enumerated vocabulary"}


def snapshot_document(accepted: dict[str, Any]) -> dict[str, Any]:
    """Deterministic, timestamp-free artefact committed to the repository and drift-checked."""
    w = E.new_workflow("snap")
    return {"schema": "eija.smt-accepted-set/v1", "subject": subject(), "grammar": grammar_description(),
            "invariants": [{"id": i.id, "statement": i.statement} for i in E.authority_invariants(w)],
            "accepted_up_to_extra_forbidden_effects": accepted["accepted"]}


def snapshot_text(accepted: dict[str, Any]) -> str:
    import json
    return json.dumps(snapshot_document(accepted), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def drift(accepted: dict[str, Any]) -> str | None:
    """None if the committed snapshot equals a fresh regeneration, else a description."""
    fresh = snapshot_text(accepted)
    if not SNAPSHOT.exists():
        return f"{SNAPSHOT.name} is missing; regenerate with `python -m verification.smt --write-snapshot`"
    if SNAPSHOT.read_bytes().decode("utf-8") != fresh:
        return f"{SNAPSHOT.name} differs from regeneration; review the policy change, then `python -m verification.smt --write-snapshot`"
    return None


def build_report(differential_mutants: int = 1500, differential_fresh: int = 500, seed: int = 20260928) -> dict[str, Any]:
    t0 = time.perf_counter()
    lap: dict[str, float] = {}

    def timed(name: str, fn):
        t = time.perf_counter()
        value = fn()
        lap[name] = round(time.perf_counter() - t, 3)
        return value

    verdicts = timed("prove_invariants", prove_invariants)
    vacuity = timed("non_vacuity", non_vacuity)
    accepted = timed("enumerate_accepted", enumerate_accepted)
    loo = timed("leave_one_out", leave_one_out)
    diff = timed("differential", lambda: D.run(seed, differential_mutants, differential_fresh))
    witness = timed("assumption_witness", assumption_witness)
    problem = drift(accepted)

    checks = [
        ("all_invariants_proved", all(v.status == "proved" for v in verdicts), f"{sum(v.status == 'proved' for v in verdicts)}/{len(verdicts)} UNSAT"),
        ("non_vacuous", vacuity["policy_admits_some_candidate"] and all(vacuity["each_invariant_falsifiable_by_some_candidate"].values()),
         "policy admits a candidate; each invariant is falsifiable by some candidate"),
        ("accepted_set_is_exactly_kernel_reachable_set", accepted["enumeration_complete"] and accepted["count"] == 3
         and accepted["equals_kernel_reachable_set"] and not accepted["inconsistent_models"],
         f"{accepted['count']} accepted, complete={accepted['enumeration_complete']}, {len(accepted['inconsistent_models'])} inconsistent"),
        ("differential_agrees_with_real_check_policy", diff.agrees and diff.candidates > 0,
         f"{diff.candidates} candidates, {diff.accepted} admitted, {diff.unvalidated} bypass pydantic validators, {len(diff.code_disagreements)} disagreements"),
        ("differential_exercises_every_clause_both_ways", not diff.clauses_never_fired and not diff.clauses_never_silent,
         f"never fired: {diff.clauses_never_fired}; never silent: {diff.clauses_never_silent}"),
        ("named_negative_controls_yield_counterexamples", all(c["counterexample_found"] for c in loo["named_controls"]),
         f"{sum(c['counterexample_found'] for c in loo['named_controls'])}/{len(loo['named_controls'])}"),
        ("leave_one_out_witnesses_rejected_by_real_policy", not loo["inconsistent_witnesses"] and not loo["unknown"],
         f"{loo['critical']} critical clauses of {loo['clauses']}"),
        ("committed_snapshot_has_no_drift", problem is None, problem or "regeneration identical"),
    ]
    verdict = "PASS" if all(ok for _, ok, _ in checks) else "FAIL"
    return {
        "schema": "eija.formal-report/v1", "kind": "smt_proof", "verdict": verdict,
        "claim": "For every candidate in the symbolic Transition grammar, check_policy(c) == [] implies AuthorityInvariant(c).",
        "subject": subject(),
        "tool": {"name": "z3-solver", "package_version": _pkg_version("z3-solver"), "z3": z3.get_version_string()},
        "bounds": grammar_description(), "assumptions": list(ASSUMPTIONS), "limitations": list(LIMITATIONS),
        "checks": [{"id": i, "status": "PASS" if ok else "FAIL", "detail": d} for i, ok, d in checks],
        "results": {
            "invariants": [v.as_json(with_time=False) for v in verdicts], "non_vacuity": vacuity,
            "accepted_set": {k: accepted[k] for k in ("enumeration_complete", "count", "equals_kernel_reachable_set", "inconsistent_models",
                                                       "expected_labels", "kernel_reachable_labels", "accepted")},
            "differential": {"seed": seed, "candidates": diff.candidates, "admitted_by_real_policy": diff.accepted,
                             "bypassing_pydantic_validators": diff.unvalidated, "code_disagreements": diff.code_disagreements,
                             "invariant_disagreements": diff.invariant_disagreements,
                             "admitted_but_python_invariant_false": diff.soundness_violations,
                             "clauses": len(diff.clause_fired), "clauses_never_fired": diff.clauses_never_fired,
                             "clauses_never_silent": diff.clauses_never_silent,
                             "invariant_true_counts": dict(sorted(diff.invariant_true.items())),
                             "invariant_false_counts": dict(sorted(diff.invariant_false.items()))},
            "leave_one_out": {k: loo[k] for k in ("clauses", "critical", "not_needed_by_invariants", "unknown",
                                                  "named_controls", "inconsistent_witnesses")} | {"rows": loo["rows"]},
            "assumption_witness": witness,
        },
        "measurements": {"note": "wall-clock, platform-dependent; excluded from drift checks",
                         "seconds_total": round(time.perf_counter() - t0, 3), "seconds_by_phase": lap,
                         "invariant_seconds": {v.id: round(v.seconds, 4) for v in verdicts},
                         **platform_info()},
    }


def _pkg_version(name: str) -> str:
    from importlib.metadata import version
    return version(name)
