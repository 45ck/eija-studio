"""Admissibility of ``bounded_model_check`` receipts (ADR-0146; lane smt-bmc, ADR-0030).

Bounded means bounded: this kind can never say more than "no violation within depth k over the stated
alphabet". Recomputed here from the raw artifact: the declared depth is at least the kernel's minimum, every
explored model was searched without a time-cap cut, produced observations and provoked the outcome classes
it should (otherwise the alphabet never reached the interesting behaviour), no counterexample was found,
each seeded runtime fault was detected by the same search (the self-test is the negative control), and the
candidate under review is one of the models explored.

Accepted under the sealed local producer, not recomputed: the counts themselves (the search is not re-run
by the kernel) and the observed current bytes of the runtime sources.
"""
from __future__ import annotations

from typing import Any

from .formal import (
    LEVEL_SEALED_TOOL, Assessment, Context, Findings, KindSpec, carried_statements, exact_keys, reported_labels, field, has_items,
    records, source_binding, strings, text,
)

PROTOCOL = "eija.formal.bounded-model-check/v1"
KEYS = frozenset({"protocol", "tool", "tier", "claim", "subject_function", "bounds", "invariants", "models",
                  "counterexamples", "mutation_self_test", "binding", "assumptions", "limitations", "reported", "source"})
SUBJECT_FUNCTION = "eija_studio.application.runtime.execute"
SOURCES = ("application/runtime.py", "adapters/sqlite_store.py", "domain/models.py", "domain/policy.py")
MIN_DEPTH = 6  # the full tier's bound: shallower runs are shown but do not count as evidence
MUTANTS = ("revocation_ignored", "assignment_ignored", "role_ignored", "replay_before_authority",
           "stale_version_accepted", "replay_reapplies_effects")
STEP_INVARIANTS = ("AUTHORITY-ON-COMMIT", "AUTHORITY-BEFORE-REPLAY", "CAS-ON-COMMIT", "STATE-GUARD-ON-COMMIT",
                   "EXACTLY-ONCE-OPERATION")
STATE_INVARIANTS = ("PACK-LAWS-HOLD-ON-RUN",)  # the pack's laws judged on the recorded run by domain.laws.evaluate_run

ESTABLISHES = ("No reachable state or step within the stated depth and alphabet violates the safety invariants when the real "
               "runtime executes every fixture actor, stale versions, operation replays and revocation or assignment changes.")
DOES_NOT_ESTABLISH = (
    "Anything beyond the stated depth: a bounded search is not a proof for depth k+1.",
    "Concurrent writers, process crashes or fault injection: one instance, commands applied one at a time.",
    "That the runtime or SQLite is correct: it observes their behaviour on the explored alphabet only.",
    "Independence: the reference model is a same-author oracle.",
)
PREREQUISITES = "python -m verification.bmc (no extra dependency); NOT_RUN if the report was not produced."


def _bounds(a: dict[str, Any], f: Findings) -> int:
    bounds = field(a, "bounds", dict, "artifact")
    depth: int = field(bounds, "depth", int, "bounds")
    if depth < MIN_DEPTH:
        f.unknown(f"the search depth {depth} is smaller than the declared minimum {MIN_DEPTH}")
    for key in ("actors", "actions"):
        strings(bounds, key, "bounds")
    return depth


def _invariants(a: dict[str, Any], f: Findings) -> None:
    inv = field(a, "invariants", dict, "artifact")
    have = set(strings(inv, "step", "invariants")) | set(strings(inv, "state", "invariants"))
    for name in (*STEP_INVARIANTS, *STATE_INVARIANTS):
        if name not in have:
            f.unknown(f"invariant {name} is not among those the search checked")


def _model(name: str, m: dict[str, Any], depth: int, f: Findings) -> None:
    if field(m, "truncated", bool, name):
        f.unknown(f"{name}: the search was cut off by the wall-clock cap (inconclusive)")
    counts = [field(m, key, int, name) for key in ("states", "transitions", "invariant_checks")]
    if min(counts) < 1:
        f.unknown(f"{name}: the search explored nothing that was checked")
    if field(m, "max_depth", int, name) < depth and not field(m, "exhausted", bool, name):
        f.unknown(f"{name}: the search stopped before the declared depth without exhausting the reachable set")
    if has_items(m, "expected_outcomes_unreached", name):
        f.unknown(f"{name}: the alphabet never provoked some outcome classes, so silence there proves nothing")


def _models(a: dict[str, Any], ctx: Context, depth: int, f: Findings) -> None:
    models = field(a, "models", dict, "artifact")
    for name, m in sorted(models.items()):
        _model(name, m if type(m) is dict else {}, depth, f)
    if ctx.candidate_semantic not in {m.get("semantic_hash") for m in models.values() if type(m) is dict}:
        f.stale("the candidate under review is not among the models the search explored")
    found = field(a, "counterexamples", dict, "artifact")
    for name, items in sorted(found.items()):
        if type(items) is not list:
            f.fail(f"counterexamples.{name} must be a list")
        elif items:
            first = items[0] if type(items[0]) is dict else {}
            f.fail(f"{name}: counterexample to {first.get('invariant')} in {first.get('length')} moves")


def _self_test(a: dict[str, Any], f: Findings) -> None:
    rows = {text(r, "mutant", "self_test"): r for r in records(a, "mutation_self_test", "artifact")}
    for name in MUTANTS:
        if name not in rows:
            f.unknown(f"seeded runtime fault {name} was not run through the search: its sensitivity is not shown")
        elif rows[name].get("detected") is not True:
            f.fail(f"seeded runtime fault {name} was NOT detected: the search would miss this class of bug")


def _binding(a: dict[str, Any], f: Findings) -> None:
    if text(a, "subject_function", "artifact") != SUBJECT_FUNCTION:
        f.unknown(f"the search is about {a['subject_function']}, not {SUBJECT_FUNCTION}")
    source_binding(field(a, "binding", dict, "artifact"), SOURCES, f)


def check(a: dict[str, Any], ctx: Context) -> Assessment:
    exact_keys(a, KEYS)
    carried_statements(a)
    text(field(a, "source", dict, "artifact"), "origin", "source")
    f = Findings()
    reported_labels(a, f)
    depth = _bounds(a, f)
    _invariants(a, f)
    _models(a, ctx, depth, f)
    _self_test(a, f)
    _binding(a, f)
    return f.result()


def describe(a: dict[str, Any]) -> dict[str, Any]:
    models = {n: {"states": m["states"], "transitions": m["transitions"], "max_depth": m["max_depth"], "exhausted": m["exhausted"]}
              for n, m in sorted(a["models"].items())}
    found = [{"model": n, **c} for n, items in sorted(a["counterexamples"].items()) for c in items if type(c) is dict]
    return {"tool": {"name": a["tool"].get("name"), "tier": a["tier"]}, "bounds": a["bounds"], "models": models,
            "assumptions": list(a["assumptions"]), "limitations": list(a["limitations"]), "counterexamples": found[:5]}


def explain(a: dict[str, Any], policy_errors: tuple[str, ...]) -> list[dict[str, Any]]:
    """The bounded search explains no policy error: its faults are runtime faults, not workflow faults."""
    return []


SPEC = KindSpec(kind="bounded_model_check", claim="runtime_safety_bounded", method="formal-bounded-model-check-v1",
                protocol=PROTOCOL, level=LEVEL_SEALED_TOOL, establishes=ESTABLISHES, does_not_establish=DOES_NOT_ESTABLISH,
                prerequisites=PREREQUISITES, check=check, describe=describe, explain=explain)
