"""Admissibility of ``smt_proof`` receipts (ADR-0146; lane smt-bmc, ADR-0029).

Recomputed here from the raw artifact: every required invariant is ``proved`` (a refuted one is a FAIL and
its witness is shown), the proof is not vacuous, the accepted set was enumerated completely and contains the
candidate under review, the encoding of the policy agrees with the real ``check_policy`` on a declared
minimum number of differential candidates with no disagreement, each named leave-one-out control produced a
counterexample, and the sources the report is about are the sources now in the checkout.

Accepted under the sealed local producer, not recomputed: that Z3 answered ``unsat`` (no checkable proof
object is exported), and the observed current bytes of the policy sources.
"""
from __future__ import annotations

from typing import Any

from .formal import (
    LEVEL_SEALED_TOOL, Assessment, Context, Findings, KindSpec, as_records, carried_statements, exact_keys, reported_labels, field,
    has_items, records, source_binding, strings, text,
)

PROTOCOL = "eija.formal.smt-proof/v1"
KEYS = frozenset({"protocol", "tool", "claim", "subject_function", "bounds", "assumptions", "limitations", "invariants",
                  "non_vacuity", "accepted_set", "differential", "negative_controls", "binding", "reported", "source"})
SUBJECT_FUNCTION = "eija_studio.domain.policy.check_policy"
SOURCES = ("domain/policy.py", "domain/models.py")
ACCEPTED_Z3_PACKAGES = ("5.1.0.0",)
INVARIANTS = ("INV-TEACHER-NOT-DECIDER", "INV-REGISTRAR-ONLY-DECIDES", "INV-TEACHER-TRANSITIONS-NEVER-DECIDE",
              "INV-TEACHER-EMITS-NO-DECISION-AUDIT", "INV-APPROVE-REQUIRES-RECOMMENDED", "INV-APPROVED-ONLY-VIA-APPROVE",
              "INV-RECOMMEND-REQUIRES-ASSIGNMENT", "INV-RECOMMEND-CANNOT-CONCLUDE", "INV-REJECT-SOURCE-BOUNDED",
              "INV-FORBIDDEN-EFFECTS-EXCLUDED", "INV-MANDATORY-GUARDS-PRESENT", "INV-CLOSED-WORKFLOW")
# The leave-one-out controls the kernel requires: deleting this policy clause must violate this invariant.
NAMED_CONTROLS = {
    "PROTECTED_AUTHORITY:Approve/role": "INV-TEACHER-NOT-DECIDER",
    "PROTECTED_AUTHORITY:Reject/role": "INV-TEACHER-NOT-DECIDER",
    "PROTECTED_STATE:Approve/from": "INV-APPROVE-REQUIRES-RECOMMENDED",
    "GUARD_POLICY:Recommend/actor_assigned": "INV-RECOMMEND-REQUIRES-ASSIGNMENT",
    "GUARD_POLICY:Reject/actor_active": "INV-MANDATORY-GUARDS-PRESENT",
    "EFFECT_POLICY:Approve/forbidden:PaymentCaptured": "INV-FORBIDDEN-EFFECTS-EXCLUDED",
    "EFFECT_POLICY:Approve/required:PaymentCaptured": "INV-FORBIDDEN-EFFECTS-EXCLUDED",
    "UNSUPPORTED_REJECTION_SOURCE/source": "INV-REJECT-SOURCE-BOUNDED",
}
MIN_DIFFERENTIAL_CANDIDATES = 1000  # the encoding's faithfulness is SAMPLED; fewer samples than this are not enough to say so
_STATUSES = ("proved", "refuted", "unknown")

ESTABLISHES = ("For every candidate in the symbolic Transition grammar, if check_policy admits it then twelve authority "
               "invariants hold; the policy admits exactly the workflows the kernel can produce.")
DOES_NOT_ESTABLISH = (
    "Anything about the runtime, SQLite, HTTP or the interpreter: it is about the policy function on the modelled grammar.",
    "That Z3 is right: an unsat answer has no independently checked proof object, so it rests on the sealed local producer.",
    "That the encoding equals check_policy: faithfulness is sampled by a differential test, not proved.",
    "That the invariants are the right requirement: same authorship as the policy.",
)
PREREQUISITES = "z3-solver (pip install -e .[smt]) and python -m verification.smt; NOT_RUN otherwise."


def _tool(a: dict[str, Any], f: Findings) -> None:
    tool = field(a, "tool", dict, "artifact")
    if text(tool, "name", "tool") != "z3-solver":
        f.unknown(f"the solver {tool['name']!r} is not one this kernel knows")
    if text(tool, "package_version", "tool") not in ACCEPTED_Z3_PACKAGES:
        f.unknown(f"z3-solver {tool['package_version']} is not a version this kernel accepts {list(ACCEPTED_Z3_PACKAGES)}")


def _grammar(a: dict[str, Any], f: Findings) -> None:
    bounds = field(a, "bounds", dict, "artifact")
    for key in ("actions", "roles", "states", "guards", "effect_atoms"):
        strings(bounds, key, "bounds")
    for key in ("unknown_action_slot", "unknown_state_slot"):
        if bounds.get(key) is not True:
            f.unknown(f"the grammar does not admit {key.split('_')[1]}s outside the known vocabulary, so the claim is narrower")


def _invariants(a: dict[str, Any], f: Findings) -> None:
    seen = {text(x, "id", "invariant"): text(x, "status", "invariant") for x in records(a, "invariants", "artifact")}
    for name in INVARIANTS:
        if name not in seen:
            f.unknown(f"invariant {name} is not covered by the receipt")
    for name, status in sorted(seen.items()):
        if status not in _STATUSES:
            f.fail(f"{name}: unrecognised status {status!r}")
        elif status == "refuted":
            f.fail(f"{name} is REFUTED: the solver found an admitted candidate that violates it")
        elif status == "unknown":
            f.unknown(f"{name}: the solver did not decide (timeout)")


def _vacuity(a: dict[str, Any], f: Findings) -> None:
    vac = field(a, "non_vacuity", dict, "artifact")
    if vac.get("policy_admits_some_candidate") is not True:
        f.unknown("the policy admits no candidate, so every invariant holds vacuously")
    falsifiable = field(vac, "each_invariant_falsifiable_by_some_candidate", dict, "non_vacuity")
    for name in INVARIANTS:
        if falsifiable.get(name) is not True:
            f.unknown(f"{name} is not shown to be falsifiable by any grammar candidate, so its proof may be vacuous")


def _accepted(a: dict[str, Any], ctx: Context, f: Findings) -> None:
    acc = field(a, "accepted_set", dict, "artifact")
    hashes = strings(acc, "semantic_hashes", "accepted_set")
    if field(acc, "enumeration_complete", bool, "accepted_set") is not True or field(acc, "count", int, "accepted_set") != len(hashes):
        f.unknown("the set of admitted workflows was not enumerated completely")
    if has_items(acc, "inconsistent_models", "accepted_set"):
        f.fail("the encoding admits workflows that the real check_policy or the validators reject (unfaithful encoding)")
    if field(acc, "equals_kernel_reachable_set", bool, "accepted_set") is not True:
        f.unknown("the admitted set differs from the workflows the kernel can produce")
    if ctx.candidate_semantic not in hashes:
        f.stale("the candidate under review is not among the workflows the policy was shown to admit")


def _differential(a: dict[str, Any], f: Findings) -> None:
    diff = field(a, "differential", dict, "artifact")
    if field(diff, "candidates", int, "differential") < MIN_DIFFERENTIAL_CANDIDATES:
        f.unknown(f"the encoding was compared with check_policy on fewer than {MIN_DIFFERENTIAL_CANDIDATES} candidates")
    for key in ("code_disagreements", "invariant_disagreements", "admitted_but_python_invariant_false"):
        if has_items(diff, key, "differential"):
            f.fail(f"differential test: {key} is not empty (the encoding is not faithful)")
    for key in ("clauses_never_fired", "clauses_never_silent"):
        if has_items(diff, key, "differential"):
            f.unknown(f"differential test: {key} is not empty (agreement on those clauses is vacuous)")


def _controls(a: dict[str, Any], f: Findings) -> None:
    controls = field(a, "negative_controls", dict, "artifact")
    named = {text(c, "remove", "control"): c for c in records(controls, "named", "negative_controls")}
    for clause, invariant in NAMED_CONTROLS.items():
        c = named.get(clause)
        if c is None:
            f.unknown(f"negative control (remove {clause}) is missing: the proof's sensitivity is not shown")
        elif c.get("expect_violation_of") != invariant or c.get("counterexample_found") is not True:
            f.fail(f"negative control (remove {clause}) did not yield a counterexample violating {invariant}")
    if has_items(controls, "unknown", "negative_controls"):
        f.unknown("some leave-one-out controls were undecided")
    if has_items(controls, "inconsistent_witnesses", "negative_controls"):
        f.fail("a leave-one-out counterexample was not rejected by the real check_policy")


def _binding(a: dict[str, Any], f: Findings) -> None:
    if text(a, "subject_function", "artifact") != SUBJECT_FUNCTION:
        f.unknown(f"the proof is about {a['subject_function']}, not {SUBJECT_FUNCTION}")
    source_binding(field(a, "binding", dict, "artifact"), SOURCES, f)


def check(a: dict[str, Any], ctx: Context) -> Assessment:
    exact_keys(a, KEYS)
    carried_statements(a)
    text(field(a, "source", dict, "artifact"), "origin", "source")
    f = Findings()
    reported_labels(a, f)
    _tool(a, f)
    _grammar(a, f)
    _invariants(a, f)
    _vacuity(a, f)
    _accepted(a, ctx, f)
    _differential(a, f)
    _controls(a, f)
    _binding(a, f)
    return f.result()


def describe(a: dict[str, Any]) -> dict[str, Any]:
    refuted = [x for x in a["invariants"] if x["status"] == "refuted"]
    return {"tool": {"name": a["tool"]["name"], "version": a["tool"]["package_version"], "z3": a["tool"].get("z3")},
            "bounds": a["bounds"], "assumptions": list(a["assumptions"]), "limitations": list(a["limitations"]),
            "invariants": {"proved": sum(x["status"] == "proved" for x in a["invariants"]), "total": len(a["invariants"])},
            "counterexamples": [{"invariant": x["id"], "witness": x.get("counterexample")} for x in refuted]}


def explain(a: dict[str, Any], policy_errors: tuple[str, ...]) -> list[dict[str, Any]]:
    """Leave-one-out counterexamples for the policy clauses behind the policy errors the kernel reports.

    Display only: deleting the clause that blocks this fault lets a candidate with the fault through."""
    raw = a.get("negative_controls")
    controls: dict[str, Any] = raw if type(raw) is dict else {}
    found = []
    for c in as_records(controls.get("named")):
        clause = str(c.get("remove", ""))
        code = clause.partition("/")[0]
        if code in policy_errors and c.get("counterexample_found") is True:
            found.append({"source": "smt_proof negative control", "control": clause, "policy_findings": [code],
                          "violates": c.get("expect_violation_of"), "witness": c.get("witness"),
                          "note": "Z3 counterexample: without this policy clause a candidate with this fault would be admitted."})
    return found


SPEC = KindSpec(kind="smt_proof", claim="policy_soundness", method="formal-smt-proof-v1", protocol=PROTOCOL,
                level=LEVEL_SEALED_TOOL, establishes=ESTABLISHES, does_not_establish=DOES_NOT_ESTABLISH,
                prerequisites=PREREQUISITES, check=check, describe=describe, explain=explain)
