"""Bounded model checking of the real runtime (verification/bmc): checker behaviour and negative controls.

Tests marked `formal` run searches that take seconds each, so the default (fast/coverage) pytest run deselects them
(`-m "not formal"` in pyproject) and the `bmc` session selects them (`pytest -m formal`).
"""
import json
from dataclasses import replace
from unittest import mock

import pytest
from eija_studio.adapters.sqlite_store import sandbox_factory
from eija_studio.application import runtime
from eija_studio.application.runtime import execute, initialise
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow

from verification.bmc import __main__ as bmc_cli
from verification.bmc import mutants as M
from verification.bmc import report, spec
from verification.bmc.explorer import Config, explore
from verification.bmc.snapshot import Observer

formal = pytest.mark.formal

CANDIDATE = report.workflows()["candidate-reject-from-Recommended"]
BASELINE = report.workflows()["baseline"]


@pytest.fixture
def sandbox(tmp_path):
    root = tmp_path / "bmc"
    root.mkdir()
    return sandbox_factory(root)


@formal
def test_real_runtime_has_no_violation_within_depth_three(sandbox):
    res = explore("candidate", CANDIDATE, Config(depth=3), sandbox)
    assert res.verdict == "PASS" and not res.findings.first
    assert res.states > 10 and res.transitions > 500 and res.max_depth == 3
    # the alphabet actually provokes the interesting behaviour (otherwise "no violation" is vacuous)
    for wanted in ("committed:Submit", "committed:Recommend", "committed:Approve", "duplicate", "rejected:ACTOR_REVOKED",
                   "rejected:ASSIGNMENT_DENIED", "rejected:STALE_VERSION", "rejected:OPERATION_CONFLICT",
                   "rejected:STATE_DENIED", "rejected:ACTION_DENIED", "rejected:UNKNOWN_ACTOR", "env:active=0"):
        assert wanted in res.outcomes, wanted


def test_baseline_rejects_recommend_as_unmodelled(sandbox):
    res = explore("baseline", BASELINE, Config(depth=2), sandbox)
    assert res.verdict == "PASS" and "committed:Recommend" not in res.outcomes and "rejected:ACTION_DENIED" in res.outcomes


def test_search_is_deterministic(sandbox):
    a = explore("m", CANDIDATE, Config(depth=2), sandbox)
    b = explore("m", CANDIDATE, Config(depth=2), sandbox)
    assert (a.states, a.transitions, a.per_depth, a.outcomes) == (b.states, b.transitions, b.per_depth, b.outcomes)


def test_depth_bound_is_reported_not_hidden(sandbox):
    res = explore("m", CANDIDATE, Config(depth=1), sandbox)
    assert res.max_depth == 1 and not res.exhausted and len(res.per_depth) == 1


def test_time_cap_makes_the_run_inconclusive_never_pass(sandbox):
    res = explore("m", CANDIDATE, replace(Config(depth=6), max_seconds=0.0), sandbox)
    assert res.truncated and res.verdict == "INCONCLUSIVE"


@formal
@pytest.mark.parametrize("mutant", M.MUTANTS, ids=lambda m: m.name)
def test_every_seeded_runtime_fault_is_found_with_a_shortest_trace(sandbox, mutant):
    with mutant.activate() as fn:
        res = explore(mutant.name, CANDIDATE, Config(depth=3, stop_when_found=tuple(mutant.expected_invariants)), sandbox, execute_fn=fn)
    hit = mutant.expected_invariants & set(res.findings.first)
    assert hit, f"{mutant.name} not detected: {sorted(res.findings.first)}"
    found = res.findings.first[sorted(hit)[0]]
    assert found["length"] <= 2 and len(found["trace"]) == found["length"]


@formal
def test_replay_before_authority_counterexample_is_the_expected_scenario(sandbox):
    mutant = next(m for m in M.MUTANTS if m.name == "replay_before_authority")
    with mutant.activate() as fn:
        res = explore("m", CANDIDATE, Config(depth=2), sandbox, execute_fn=fn)
    trace = res.findings.first["AUTHORITY-BEFORE-REPLAY"]["trace"]
    assert len(trace) == 2 and trace[0].endswith("op=op0") and trace[1].endswith("op=op0")   # commit, then a replay by someone else


def test_real_runtime_after_mutant_context_is_unpatched(sandbox):
    mutant = next(m for m in M.MUTANTS if m.name == "revocation_ignored")
    with mutant.activate():
        pass
    assert explore("m", CANDIDATE, Config(depth=1), sandbox).verdict == "PASS"


# ---- the state invariants must detect tampered databases (checker sensitivity) -------------------

def _valid_state(sandbox):
    """A real snapshot after Submit and Recommend, produced through the runtime."""
    with sandbox() as store:
        with store.transaction() as u:
            item = initialise(u, spec.CASE, CANDIDATE)
        for op, actor, action, v in (("op0", "teacher-assigned", "Submit", 0), ("op1", "teacher-assigned", "Recommend", 1),
                                     ("op2", "registrar", "Approve", 2)):
            with store.transaction() as u:
                execute(u, spec.CASE, CANDIDATE, ExecuteCommand(operation_id=op, actor_id=actor, instance_id=item["id"], action=action, expected_version=v))
        obs = Observer(store)
        try:
            return obs.read()
        finally:
            obs.close()


def test_a_genuine_run_satisfies_every_state_invariant(sandbox):
    assert spec.check_state(CANDIDATE, _valid_state(sandbox)) == []


def _forged(kind, actor, base):
    body = json.dumps({"case_id": spec.CASE, "operation_id": "op9", "actor_id": actor, "instance_id": "x", "result": {}})
    return (*base.audit, (kind, body))


@pytest.mark.parametrize("tamper,invariant", [
    (lambda s: replace(s, audit=_forged("Audit:ExcursionApproved", "teacher-assigned", s)), "DECISION-ONLY-BY-REGISTRAR"),
    (lambda s: replace(s, audit=s.audit[:-1]), "AUDIT-TRAIL-IS-A-VALID-RUN"),                      # state ahead of its trail
    (lambda s: replace(s, instances=((*s.instance[:4], s.version + 1),)), "VERSION-COUNTS-COMMITS"),
    (lambda s: replace(s, outbox=()), "OUTBOX-MATCHES-COMMITTED-RECOMMENDS"),
    (lambda s: replace(s, audit=_forged("Audit:PaymentCaptured", "registrar", s)), "NO-FORBIDDEN-EFFECT"),
    (lambda s: replace(s, audit=s.audit[:1] + s.audit[2:]), "APPROVAL-FOLLOWS-RECOMMENDATION"),      # approval without a recommendation
])
def test_state_invariants_detect_tampering(sandbox, tamper, invariant):
    bad = tamper(_valid_state(sandbox))
    assert invariant in {v.invariant for v in spec.check_state(CANDIDATE, bad)}


def test_step_oracle_distinguishes_commit_replay_and_denial(sandbox):
    snap = _valid_state(sandbox)
    rec = {"op0": spec.Command("teacher-assigned", "Submit", 0, "op0")}
    revoked = replace(snap, actors=tuple((a[0], a[1], 0, a[3]) if a[0] == "teacher-assigned" else a for a in snap.actors))
    replay = spec.Command("teacher-assigned", "Submit", 0, "op0")
    assert spec.expectation(CANDIDATE, snap, rec, replay).kind == "duplicate"
    assert spec.expectation(CANDIDATE, revoked, rec, replay).kind == "reject"                   # authority before replay
    assert spec.expectation(CANDIDATE, snap, rec, replace(replay, actor="registrar")).allowed_codes == {"ROLE_DENIED"}
    assert spec.expectation(CANDIDATE, snap, {}, spec.Command("registrar", "Bogus", 3, "op3")).allowed_codes == {"ACTION_DENIED"}


def test_committed_statistics_snapshot_is_valid_json_with_the_full_tier_run():
    doc = report.load_snapshot()
    run = doc["runs"]["depth-6"]
    assert run["config"]["depth"] == 6 and set(run["models"]) == set(report.DEFAULT_MODELS["full"])


# ---- a run that could not check everything must not read as a PASS --------------------------------------

@formal
def test_a_run_without_committed_statistics_is_partial_not_pass(tmp_path):
    """Depth 2 has no committed statistics: the drift check cannot compare, so the verdict must say so."""
    doc = report.build_report(Config(depth=2), tmp_path / "w", run_self_test=False, model_names=("baseline",))
    statuses = {c["id"]: c["status"] for c in doc["checks"]}
    assert statuses["committed_statistics_have_no_drift"] == "NOT_RUN" and statuses["seeded_runtime_faults_are_detected"] == "NOT_RUN"
    assert doc["verdict"] == "PARTIAL"


def test_a_wall_clock_cap_does_not_disable_the_drift_check():
    snapshot_config = report.load_snapshot()["runs"]["depth-6"]["config"]
    assert report.drift(6, {}, {**snapshot_config, "max_seconds": 100.0})[0] is True
    assert report.drift(6, {}, {**snapshot_config, "stale_versions": snapshot_config["stale_versions"] + 1})[0] is None


@pytest.mark.parametrize("verdict", ["FAIL", "INCONCLUSIVE", "PARTIAL"])
def test_write_snapshot_is_refused_unless_the_run_is_a_full_pass(tmp_path, monkeypatch, verdict):
    monkeypatch.setattr(report, "SNAPSHOT", tmp_path / "expected_statistics.json")
    doc = {"verdict": verdict, "checks": [], "results": {"models": {}, "counterexamples": {}}, "measurements": {"seconds_total": 0.0}}
    monkeypatch.setattr(report, "build_report", lambda *a, **k: doc)
    assert bmc_cli.main(["--depth", "2", "--write-snapshot", "--out", str(tmp_path / "bmc.json")]) != 0
    assert not (tmp_path / "expected_statistics.json").exists()


# ---- unsafe POLICY variants: the state invariants must flag them when the policy gate is bypassed ------------
# The runtime calls `ensure_policy` on every execute, so an unsafe workflow cannot run at all unless the gate is
# removed. These controls remove it (in the test only) to show the BMC invariants would catch what the gate blocks.

def _unsafe(candidate, action, **changes):
    swapped = tuple(t.model_copy(update=changes) if t.action == action else t for t in candidate.transitions)
    return Workflow.model_construct(**{**dict(candidate), "transitions": swapped})


def _explore_without_policy_gate(sandbox, model, depth, stop_when_found=()):
    with mock.patch.object(runtime, "ensure_policy", lambda _model: None):
        return explore("unsafe", model, Config(depth=depth, stop_when_found=stop_when_found), sandbox)


def test_the_policy_gate_is_what_blocks_an_unsafe_workflow(sandbox):
    unsafe = _unsafe(CANDIDATE, "Approve", role="Teacher")
    with pytest.raises(DomainError) as blocked:
        explore("unsafe", unsafe, Config(depth=1), sandbox)
    assert blocked.value.code == "POLICY_BLOCKED"


@formal
@pytest.mark.parametrize("label,model,invariant,length", [
    ("teacher may approve", _unsafe(CANDIDATE, "Approve", role="Teacher"), "DECISION-ONLY-BY-REGISTRAR", 3),
    ("approve skips Recommended", _unsafe(CANDIDATE, "Approve", from_state="Submitted"), "APPROVAL-FOLLOWS-RECOMMENDATION", 2),
    ("forbidden effect required", _unsafe(CANDIDATE, "Approve", required_effects=("Audit:ExcursionApproved", "Audit:PaymentCaptured")),
     "NO-FORBIDDEN-EFFECT", 3),
])
def test_unsafe_workflow_variants_yield_shortest_counterexamples(sandbox, label, model, invariant, length):
    res = _explore_without_policy_gate(sandbox, model, depth=3, stop_when_found=(invariant,))
    assert invariant in res.findings.first, (label, sorted(res.findings.first))
    assert res.findings.first[invariant]["length"] == length and res.verdict == "FAIL"
