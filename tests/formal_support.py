"""Shared builders for the evidence-kinds tests: workflows, receipts, synthetic checkouts and tool reports.

The Bend artifact is the real committed snapshot (verification/bend/evidence/bend.json) read through the real
adapter. The SMT and bounded-model-check artifacts are golden files derived from real reports of the
smt-bmc lane (see tests/fixtures/formal); the synthetic report builders below mimic that report format so the
adapters can be tested without z3 or a long search.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from eija_studio.adapters.formal import FormalReports, bend
from eija_studio.adapters.formal.common import current_sources
from eija_studio.application.formal import attach
from eija_studio.domain.formal import Context, FormalArtifact, FORMAL_PRODUCER
from eija_studio.domain.evidence_kinds import KINDS
from eija_studio.domain.formal_bmc import MUTANTS as BMC_MUTANTS, STEP_INVARIANTS, STATE_INVARIANTS, SOURCES as BMC_SOURCES
from eija_studio.domain.formal_smt import INVARIANTS as SMT_INVARIANTS, NAMED_CONTROLS, SOURCES as SMT_SOURCES
from eija_studio.domain.models import Workflow, fingerprint
from eija_studio.domain.policy import baseline
from verification.excursion_pack import candidate as excursion_candidate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "formal"
DIMENSIONS = {"implementation": "impl-1", "policy": "policy-1", "environment": "env-1", "harness": "harness-1",
              "presentation": "layout-1"}
KIND_NAMES = ("bend_proof", "smt_proof", "bounded_model_check")


def workflows(rejection_source: str = "Recommended") -> tuple[Workflow, Workflow]:
    base = baseline()
    return base, excursion_candidate(rejection_source)


def subject_of(candidate: Workflow) -> dict[str, Any]:
    return DIMENSIONS | {"semantic": candidate.semantic_hash}


def context_of(base: Workflow, candidate: Workflow) -> Context:
    return Context(candidate_semantic=candidate.semantic_hash, baseline_semantic=base.semantic_hash)


def real_bend_artifact(base: Workflow, candidate: Workflow) -> dict[str, Any]:
    """The committed Bend snapshot, normalised by the real adapter for these workflows."""
    items = [i for i in bend.collect(ROOT, base, candidate) if i.artifact["source"]["origin"].endswith("evidence/bend.json")]
    return items[0].artifact


def golden(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / f"{name}.artifact.json").read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def artifacts(base: Workflow, candidate: Workflow) -> dict[str, dict[str, Any]]:
    return {"bend_proof": real_bend_artifact(base, candidate), "smt_proof": golden("smt"), "bounded_model_check": golden("bmc")}


def receipt_of(kind: str, artifact: dict[str, Any], subject: dict[str, Any], /, *, rehash: bool = True, **overrides: Any) -> dict[str, Any]:
    """A receipt as the application intake builds it (unsealed). ``rehash=False`` keeps a stale artifact_hash."""
    spec = KINDS[kind]
    receipt: dict[str, Any] = {"id": f"r-{kind}", "claim": spec.claim, "kind": kind, "subject": dict(subject), "producer": FORMAL_PRODUCER,
                               "method": spec.method, "created_at": "2026-01-01T00:00:00+00:00", "artifact_hash": fingerprint(artifact),
                               "artifact": artifact, "measurements": {}}
    receipt.update(overrides)
    if not rehash:
        receipt["artifact_hash"] = "0" * 64
    return receipt


def leaves(value: Any, path: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    if isinstance(value, dict):
        return [p for k, v in value.items() for p in leaves(v, (*path, k))]
    if isinstance(value, list):
        return [p for i, v in enumerate(value) for p in leaves(v, (*path, i))]
    return [path]


def at(value: Any, path: tuple[Any, ...]) -> Any:
    for step in path:
        value = value[step]
    return value


def with_change(artifact: dict[str, Any], path: tuple[Any, ...], new: Any) -> dict[str, Any]:
    out = copy.deepcopy(artifact)
    at(out, path[:-1])[path[-1]] = new
    return out


def flipped(old: Any) -> Any:
    """A different value of the same JSON type."""
    if isinstance(old, bool):
        return not old
    if isinstance(old, int):
        return old + 1
    if isinstance(old, str):
        return old + "x"
    return "changed" if old is None else old


class StubSource:
    """A FormalEvidenceSource returning fixed artifacts (what a tool report would have produced)."""

    def __init__(self, items: list[FormalArtifact]):
        self.items = items

    def collect(self, baseline: Workflow, candidate: Workflow) -> list[FormalArtifact]:
        return list(self.items)


def not_run_artifact(kind: str, reason: str = "the tool is not installed") -> FormalArtifact:
    return FormalArtifact(kind, {"protocol": KINDS[kind].protocol, "not_run": {"reason": reason, "prerequisite": "the tool"}}, {})


def stub_all(base: Workflow, candidate: Workflow, **replace: dict[str, Any]) -> StubSource:
    """All three kinds from the real/golden artifacts, with per-kind replacements."""
    arts = artifacts(base, candidate) | replace
    return StubSource([FormalArtifact(k, arts[k], {}) for k in KIND_NAMES])


# ------------------------------------------------------------------ synthetic checkouts and reports

def sha_of_sources(root: Path, relative: tuple[str, ...]) -> dict[str, str]:
    return current_sources(root, relative)


def smt_report(sources: dict[str, str]) -> dict[str, Any]:
    """A report in the smt-bmc lane's ``eija.formal-report/v1`` format, describing a passing run."""
    rows = [{"clause": c, "status": "critical", "violated_invariants": [i],
             "witness": {"transitions": [{"action": "Approve", "role": "Teacher", "from_state": "Submitted", "to_state": "Approved"}]}}
            for c, i in NAMED_CONTROLS.items()]
    base, cand = workflows()
    other = workflows("Submitted")[1]
    return {"schema": "eija.formal-report/v1", "kind": "smt_proof", "verdict": "PASS", "claim": "synthetic",
            "subject": {"function": "eija_studio.domain.policy.check_policy", "sources_sha256_lf": sources},
            "tool": {"name": "z3-solver", "package_version": "5.1.0.0", "z3": "5.1.0"},
            "bounds": {"actions": ["Submit"], "roles": ["Teacher"], "states": ["Draft"], "guards": ["actor_active"],
                       "effect_atoms": ["PaymentCaptured"], "unknown_action_slot": True, "unknown_state_slot": True},
            "assumptions": ["a"], "limitations": ["l"],
            "checks": [{"id": "all_invariants_proved", "status": "PASS", "detail": "12/12"}],
            "results": {
                "invariants": [{"id": i, "statement": "s", "status": "proved"} for i in SMT_INVARIANTS],
                "non_vacuity": {"policy_admits_some_candidate": True,
                                "each_invariant_falsifiable_by_some_candidate": dict.fromkeys(SMT_INVARIANTS, True)},
                "accepted_set": {"enumeration_complete": True, "count": 3, "equals_kernel_reachable_set": True, "inconsistent_models": [],
                                 "accepted": [{"semantic_hash": h.semantic_hash} for h in (base, cand, other)]},
                "differential": {"seed": 1, "candidates": 2000, "code_disagreements": [], "invariant_disagreements": [],
                                 "admitted_but_python_invariant_false": [], "clauses": 105, "clauses_never_fired": [],
                                 "clauses_never_silent": []},
                "leave_one_out": {"named_controls": [{"remove": c, "expect_violation_of": i, "counterexample_found": True}
                                                     for c, i in NAMED_CONTROLS.items()],
                                  "unknown": [], "inconsistent_witnesses": [], "rows": rows}},
            "measurements": {"seconds_total": 1.5, "platform": "test-os", "python": "3.12"}}


def bmc_report(sources: dict[str, str], depth: int = 6) -> dict[str, Any]:
    base, cand = workflows()
    model = {"states": 10, "transitions": 100, "max_depth": depth, "exhausted": False, "truncated": False,
             "expected_outcomes_unreached": [], "invariant_checks": 500}
    return {"schema": "eija.formal-report/v1", "kind": "bounded_model_check", "verdict": "PASS", "tier": "full", "claim": "synthetic",
            "subject": {"function": "eija_studio.application.runtime.execute", "sources_sha256_lf": sources},
            "tool": {"name": "verification.bmc explicit-state BFS", "system_under_test": "runtime"},
            "bounds": {"depth": depth, "actors": ["registrar"], "actions": ["Submit"]},
            "invariants": {"step": list(STEP_INVARIANTS), "state": list(STATE_INVARIANTS)},
            "assumptions": ["a"], "limitations": ["l"],
            "checks": [{"id": "no_invariant_violation_within_bound", "status": "PASS", "detail": "d"}],
            "results": {"models": {"baseline": model | {"semantic_hash": base.semantic_hash},
                                   "candidate-reject-from-Recommended": model | {"semantic_hash": cand.semantic_hash}},
                        "counterexamples": {"baseline": [], "candidate-reject-from-Recommended": []},
                        "mutation_self_test": [{"mutant": m, "detected": True} for m in BMC_MUTANTS]},
            "measurements": {"seconds_total": 2.0, "platform": "test-os", "python": "3.12"}}


def make_checkout(tmp_path: Path, *, smt: bool = True, bmc: bool = True, bend_snapshot: bool = True) -> Path:
    """A temporary source checkout: copies of the sources the reports name, the Bend files, and chosen reports."""
    root = tmp_path / "checkout"
    for relative in (*SMT_SOURCES, *BMC_SOURCES):
        target = root / "src" / "eija_studio" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / "src" / "eija_studio" / relative).read_bytes())
    bend_dir = root / "verification" / "bend"
    (bend_dir / "evidence").mkdir(parents=True)
    for name in ("main.bend", "LAWS.bend", "PROOF.bend", "bend_generate.py"):
        (bend_dir / name).write_bytes((ROOT / "verification" / "bend" / name).read_bytes())
    if bend_snapshot:
        (bend_dir / "evidence" / "bend.json").write_bytes((ROOT / "verification" / "bend" / "evidence" / "bend.json").read_bytes())
    reports = root / "reports" / "formal"
    reports.mkdir(parents=True)
    if smt:
        (reports / "smt.json").write_text(json.dumps(smt_report(sha_of_sources(root, SMT_SOURCES))), encoding="utf-8")
    if bmc:
        (reports / "bmc.json").write_text(json.dumps(bmc_report(sha_of_sources(root, BMC_SOURCES))), encoding="utf-8")
    return root


def collect_all(root: Path, base: Workflow, candidate: Workflow) -> list[FormalArtifact]:
    return FormalReports(root).collect(base, candidate)


def attached(items: list[FormalArtifact], subject: dict[str, Any], signer: Any, existing: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Receipts as the application intake seals them."""
    counter = iter(range(10_000))
    return attach(StubSource(items), baseline(), baseline(), subject, list(existing or []), signer.seal, "2026-01-01T00:00:00+00:00",
                  lambda: f"id-{next(counter)}")
