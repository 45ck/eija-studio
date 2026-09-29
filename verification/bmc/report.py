"""Runs the search on each workflow variant and assembles the `bounded_model_check` evidence report."""
from __future__ import annotations

import json
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

from eija_studio.adapters.sqlite_store import sandbox_factory
from eija_studio.application import runtime
from eija_studio.domain.models import SemanticTransaction, Workflow
from eija_studio.domain.policy import apply_transaction, baseline
from verification.formal_report import dumps, kernel_subject, platform_info

from . import mutants as M
from .explorer import Config, Result, explore

SNAPSHOT = Path(__file__).resolve().parent / "expected_statistics.json"
ENFORCE_COVERAGE_FROM_DEPTH = 4
# Full tier keeps the gate near a minute; the release tier adds the variant that differs only in the rejection source.
DEFAULT_MODELS = {"full": ("baseline", "candidate-reject-from-Recommended"),
                  "release": ("baseline", "candidate-reject-from-Recommended", "candidate-reject-from-Submitted")}
SUBJECT_FILES = ("application/runtime.py", "adapters/sqlite_store.py", "domain/models.py", "domain/policy.py")

ASSUMPTIONS = (
    "The system under test is application.runtime.execute over adapters.sqlite_store (ephemeral profile: same transactions, no per-commit fsync).",
    "One workflow instance per sandbox; commands are applied one at a time (no concurrent writers, no crash points).",
    "Actors are the fixture directory (teacher-assigned, teacher-unassigned, teacher-revoked, registrar, viewer) plus one unknown id; roles never change.",
    "Environment moves flip only the flags listed in bounds.environment_toggles; every other actor flag stays at its fixture value.",
    "Operation ids are canonical (op0, op1, ...) plus replays of recorded ids; expected_version is the current version or one stale value.",
    "The reference model in spec.py is a same-author oracle, not an independent one.",
)
LIMITATIONS = (
    "Bounded: no violation within depth k is not a proof for depth k+1 (per-depth new-state counts and `exhausted` show whether the reachable set closed).",
    "Explicit-state search over an executed implementation: it observes behaviour, it does not prove the runtime or SQLite correct.",
    "Does not explore concurrent interleavings, process crashes or fault injection; tests/test_runtime.py covers those separately.",
    "Not a human study and not an independent verification: same authorship as the runtime and the verifier oracle.",
)
INVARIANTS = {
    "step": ["AUTHORITY-ON-COMMIT", "AUTHORITY-BEFORE-REPLAY", "CAS-ON-COMMIT", "STATE-GUARD-ON-COMMIT",
             "EXACTLY-ONCE-OPERATION", "OPERATION-BINDING", "COMMIT-EFFECTS-EXACT", "REPLAY-HAS-NO-EFFECT",
             "REJECTION-LEAVES-NO-TRACE", "NO-SPURIOUS-DENIAL", "DENIAL-REASON", "NO-UNEXPECTED-EXCEPTION"],
    "state": ["ONE-INSTANCE", "STATE-IN-MODEL", "VERSION-COUNTS-COMMITS", "AUDIT-TRAIL-IS-A-VALID-RUN",
              "DECISION-ONLY-BY-REGISTRAR", "AUDIT-ACTOR-HOLDS-TRANSITION-ROLE", "APPROVAL-FOLLOWS-RECOMMENDATION",
              "NO-FORBIDDEN-EFFECT", "EFFECTS-DECLARED-BY-MODEL", "OUTBOX-MATCHES-COMMITTED-RECOMMENDS",
              "AUDIT-REFERENCES-RECORDED-OPERATION"]}


def workflows() -> dict[str, Workflow]:
    base = baseline()

    def candidate(source: str) -> Workflow:
        return apply_transaction(base, SemanticTransaction(kind="enable_recommendation", rejection_source=source))

    return {"baseline": base, "candidate-reject-from-Recommended": candidate("Recommended"),
            "candidate-reject-from-Submitted": candidate("Submitted")}


def expected_outcomes(model: Workflow) -> list[str]:
    """Outcome classes the alphabet can provoke on this workflow; each must be observed at sufficient depth."""
    actions = sorted(t.action for t in model.transitions)
    want = [f"committed:{a}" for a in actions] + [
        "duplicate", "rejected:ACTOR_REVOKED", "rejected:ROLE_DENIED", "rejected:STALE_VERSION", "rejected:STATE_DENIED",
        "rejected:OPERATION_CONFLICT", "rejected:ACTION_DENIED", "rejected:UNKNOWN_ACTOR", "env:active=0", "env:active=1"]
    if "Recommend" in actions:
        want.append("rejected:ASSIGNMENT_DENIED")
    return sorted(want)


def stats_of(res: Result, model: Workflow) -> dict[str, Any]:
    want = expected_outcomes(model)
    return {"semantic_hash": model.semantic_hash, "verdict": res.verdict, "states": res.states,
            "transitions": res.transitions, "max_depth": res.max_depth, "exhausted": res.exhausted,
            "truncated": res.truncated, "per_depth": res.per_depth, "outcomes": dict(sorted(res.outcomes.items())),
            "expected_outcomes_unreached": sorted(w for w in want if w not in res.outcomes),
            "invariant_checks": res.invariant_checks}


def deterministic_stats(models: dict[str, dict[str, Any]]) -> dict[str, Any]:
    keys = ("semantic_hash", "states", "transitions", "max_depth", "exhausted", "per_depth", "outcomes")
    return {name: {k: s[k] for k in keys} for name, s in sorted(models.items())}


def load_snapshot() -> dict[str, Any]:
    try:
        return json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_snapshot(depth: int, stats: dict[str, Any], config: dict[str, Any]) -> None:
    doc = load_snapshot() or {"schema": "eija.bmc-statistics/v1", "runs": {}}
    doc["runs"][f"depth-{depth}"] = {"config": config, "models": stats}
    SNAPSHOT.write_bytes(dumps(doc).encode("utf-8"))


def _comparable(config: dict[str, Any]) -> dict[str, Any]:
    """The wall-clock cap does not change the explored state space (a run it cuts short is INCONCLUSIVE anyway)."""
    return {k: v for k, v in config.items() if k != "max_seconds"}


def drift(depth: int, stats: dict[str, Any], config: dict[str, Any]) -> tuple[bool | None, str]:
    """(True, ..) identical to the committed statistics; (False, why) drift; (None, why) NOT_RUN: nothing to compare."""
    run = load_snapshot().get("runs", {}).get(f"depth-{depth}")
    if run is None:
        return None, f"no committed statistics for depth {depth}"
    if _comparable(run["config"]) != _comparable(config):
        return None, "committed statistics were produced with a different alphabet/config"
    if any(name not in run["models"] or run["models"][name] != s for name, s in stats.items()):
        return False, ("state-space statistics differ from the committed snapshot; review the runtime change, "
                       "then `python -m verification.bmc --write-snapshot`")
    return True, "identical to expected_statistics.json"


def self_test(workdir: Path, depth: int) -> list[dict[str, Any]]:
    """Every seeded fault must be caught within `depth` moves (the real runtime is checked separately)."""
    model = workflows()["candidate-reject-from-Recommended"]
    rows = []
    for mutant in M.MUTANTS:
        with mutant.activate() as fn:
            res = explore("mutant:" + mutant.name, model, replace(Config(depth=depth), stop_when_found=tuple(sorted(mutant.expected_invariants))),
                          sandbox_factory(workdir), execute_fn=fn)
        found = res.findings.first
        hit = sorted(mutant.expected_invariants & set(found))
        shortest = min((found[k]["length"] for k in hit), default=None)
        rows.append({"mutant": mutant.name, "description": mutant.description, "detected": bool(hit),
                     "expected_invariants": sorted(mutant.expected_invariants), "violated": sorted(found),
                     "shortest_counterexample_length": shortest,
                     "counterexample": found[hit[0]] if hit else None, "states": res.states, "transitions": res.transitions})
    return rows


def build_report(cfg: Config, workdir: Path, *, run_self_test: bool = True, self_test_depth: int = 3,
                 tier: str = "full", model_names: tuple[str, ...] | None = None,
                 check_drift: bool = True) -> dict[str, Any]:
    t0 = time.perf_counter()
    workdir.mkdir(parents=True, exist_ok=True)
    sandbox = sandbox_factory(workdir)
    chosen = {n: m for n, m in workflows().items() if model_names is None or n in model_names}
    per_model: dict[str, dict[str, Any]] = {}
    counterexamples: dict[str, list[dict[str, Any]]] = {}
    seconds: dict[str, float] = {}
    for name, model in chosen.items():
        res = explore(name, model, cfg, sandbox, execute_fn=runtime.execute)
        per_model[name] = stats_of(res, model)
        counterexamples[name] = sorted(res.findings.first.values(), key=lambda f: (f["length"], f["invariant"]))
        seconds[name] = round(res.seconds, 3)
    mutation = self_test(workdir, self_test_depth) if run_self_test else []
    stats = deterministic_stats(per_model)

    truncated = any(s["truncated"] for s in per_model.values())
    enforce = cfg.depth >= ENFORCE_COVERAGE_FROM_DEPTH
    checks = [
        ("no_invariant_violation_within_bound", all(s["verdict"] != "FAIL" for s in per_model.values()),
         "; ".join(f"{n}: {s['verdict']} ({s['states']} states, {s['transitions']} transitions)" for n, s in per_model.items())),
        ("search_completed_within_time_cap", not truncated, "INCONCLUSIVE: max_seconds reached" if truncated else "no model was cut off"),
        ("alphabet_reaches_every_outcome_class", (not enforce) or not any(s["expected_outcomes_unreached"] for s in per_model.values()),
         f"enforced from depth {ENFORCE_COVERAGE_FROM_DEPTH}" if not enforce else
         "; ".join(f"{n}: unreached {s['expected_outcomes_unreached']}" for n, s in per_model.items())),
    ]
    if run_self_test:
        checks.append(("seeded_runtime_faults_are_detected", all(r["detected"] for r in mutation),
                       f"{sum(r['detected'] for r in mutation)}/{len(mutation)} mutants caught"))
    else:
        checks.append(("seeded_runtime_faults_are_detected", None, "self-test skipped (--no-self-test)"))
    if check_drift:
        checks.append(("committed_statistics_have_no_drift", *drift(cfg.depth, stats, cfg.describe())))
    failed = [c for c in checks if c[1] is False and c[0] != "search_completed_within_time_cap"]
    not_run = [c for c in checks if c[1] is None]
    # PARTIAL: nothing failed, but a protection was not exercised (no committed statistics to compare, or no
    # self-test). It is never reported as PASS, so a differently-configured run cannot look like the gated one.
    verdict = "FAIL" if failed else "INCONCLUSIVE" if truncated else "PARTIAL" if not_run else "PASS"
    return {
        "schema": "eija.formal-report/v1", "kind": "bounded_model_check", "verdict": verdict, "tier": tier,
        "claim": ("No reachable state or transition within the bound violates a safety invariant when the real runtime is "
                  "driven by every fixture actor, stale versions, operation-id replays and revocation/assignment changes."),
        "subject": kernel_subject(*SUBJECT_FILES, function="eija_studio.application.runtime.execute"),
        "tool": {"name": "verification.bmc explicit-state BFS",
                 "system_under_test": "application.runtime.execute + adapters.sqlite_store (ephemeral)"},
        "bounds": cfg.describe(), "assumptions": list(ASSUMPTIONS), "limitations": list(LIMITATIONS),
        "invariants": INVARIANTS,
        "checks": [{"id": i, "status": "NOT_RUN" if ok is None else "PASS" if ok else "FAIL", "detail": d} for i, ok, d in checks],
        "results": {"models": per_model, "counterexamples": counterexamples, "mutation_self_test": mutation},
        "measurements": {"note": "wall-clock, platform-dependent; excluded from drift checks",
                         "seconds_total": round(time.perf_counter() - t0, 3), "seconds_by_model": seconds, **platform_info()},
    }
