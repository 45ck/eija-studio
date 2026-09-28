"""TLA+ lane: generation drift, kernel-derived tables, runtime-vs-spec conformance machinery.

Tests that need Java and the pinned jar are skipped with an explicit NOT_RUN reason when either is
missing; they are never counted as passing evidence in that case.
"""
from dataclasses import replace

import pytest

from eija_studio.adapters.sqlite_store import sandbox_factory
from eija_studio.domain.policy import baseline
from verification.tla import conformance, generate, model, render, tlc


def _tools() -> str | None:
    try:
        tlc.ensure_jar(fetch=False)
    except tlc.NotRun as exc:
        return str(exc)
    return None


NOT_RUN = _tools()
needs_tlc = pytest.mark.skipif(NOT_RUN is not None, reason=f"NOT_RUN: {NOT_RUN}")


def config(name):
    return next(c for c in model.configs() if c.name == name)


# ------------------------------------------------------------------ generation and kernel-derived data

def test_committed_generated_model_matches_the_kernel():
    assert generate.drift() == []


def test_generated_files_are_lf_and_deterministic():
    first, second = generate.generated_files(), generate.generated_files()
    assert first == second
    assert all("\r" not in text for text in first.values())


def test_drift_check_detects_a_changed_kernel_workflow():
    # Negative control: hand the generator a workflow whose Approve role differs from the committed model.
    hostile = config("nc_teacher_approval")
    assert generate.module_text(hostile, dump=False) != generate.module_text(replace(hostile, workflow=config("candidate").workflow), dump=False)
    committed = (generate.OUT / "MC_candidate.tla").read_text(encoding="utf-8")
    assert '"Approve" :> [src |-> "Recommended", dst |-> "Approved", role |-> "Registrar"' in committed


def test_transition_table_is_read_from_the_workflow():
    table = model.transition_table(config("candidate").workflow)
    assert table["Recommend"]["needsAssigned"] is True and table["Submit"]["needsAssigned"] is False
    assert table["Recommend"]["notify"] == ("Notification:RegistrarQueued",) and table["Approve"]["notify"] == ()
    assert "Recommend" not in model.transition_table(baseline())


def test_negative_control_workflows_are_the_ones_protected_policy_rejects():
    assert config("candidate").policy_errors == ()
    assert config("nc_teacher_approval").policy_errors == ("PROTECTED_AUTHORITY:Approve",)
    assert "EFFECT_POLICY:Approve" in config("nc_forbidden_effect").policy_errors


# ------------------------------------------------------------------------------ TLC output parsing

def test_parse_tlc_values():
    value = tlc.parse_value('( "op1" :> [used |-> TRUE, actor |-> "a", res |-> <<"S", 1>>] @@ "op2" :> [used |-> FALSE] )')
    assert value["op1"]["res"] == ("S", 1) and value["op2"]["used"] is False
    assert tlc.parse_value("<<>>") == () and tlc.parse_value('{ "x", "y" }') == frozenset({"x", "y"})
    assert tlc.parse_value("<< <<>>, <<1, -2>> >>") == ((), (1, -2))
    with pytest.raises(ValueError):
        tlc.parse_value("<<1, 2>> 3")


def test_pretty_printed_dump_lines_are_reassembled():
    lines = ["Progress(3) at time", '<< "STATE",', '   << "Draft", 0 >>,', "   <<>> >>", "Finished"]
    assert list(tlc.top_level_values(iter(lines))) == [("STATE", ("Draft", 0), ())]


def test_counterexample_renderer_names_each_step():
    cfg = config("nc_teacher_approval")
    unused = {"used": False, "actor": "-", "action": "-", "ver": 0, "res": ("-", 0)}
    directory = {"teacher-assigned": {"active": True, "assigned": True}}
    first = {"st": "Draft", "ver": 0, "audit": 0, "outbox": {"op1": 0}, "dir": directory, "ops": {"op1": unused}, "emitted": frozenset()}
    done = {"used": True, "actor": "teacher-assigned", "action": "Submit", "ver": 0, "res": ("Submitted", 1)}
    second = first | {"st": "Submitted", "ver": 1, "audit": 1, "ops": {"op1": done}}
    revoked = second | {"dir": {"teacher-assigned": {"active": False, "assigned": True}}}
    rows = render.describe_steps(cfg, [first, second, revoked])
    assert [r["n"] for r in rows] == [1, 2, 3]
    assert "teacher-assigned executes Submit as op1" in rows[1]["step"] and "Draft -> Submitted" in rows[1]["step"]
    assert rows[2]["step"] == "environment: directory sets teacher-assigned.active = False"


# ------------------------------------------------- runtime side of conformance (no Java needed)

@pytest.fixture
def sandbox(tmp_path):
    (tmp_path / "ws").mkdir()
    return sandbox_factory(tmp_path / "ws")


def test_runtime_exploration_is_closed_and_atomic(sandbox):
    graph = conformance.explore(config("candidate").workflow, 1, sandbox)
    assert graph.defects == []  # abstraction round-trips; non-committing commands changed nothing; replays return the original
    assert len(graph.nodes) > 10 and graph.initial in graph.nodes
    committed = sum(1 for n in graph.nodes.values() for s in n.succ if s is not None)
    assert committed > 0
    # every successor of every node is itself an explored node (the bounded space is closed)
    assert all(k in graph.nodes for n in graph.nodes.values() for k in (*n.succ, *n.env) if k is not None)


def test_runtime_answers_replay_after_revocation_with_authority_error_first(sandbox):
    workflow = config("candidate").workflow
    with conformance.TraceRecorder(workflow, 3, sandbox) as rec:
        assert rec.execute("op1", "teacher-assigned", "Submit", 0) == "COMMITTED"
        assert rec.execute("op1", "teacher-assigned", "Submit", 0) == "DUPLICATE"
        rec.environment("teacher-assigned", "active", 0)
        assert rec.execute("op1", "teacher-assigned", "Submit", 0) == "ACTOR_REVOKED"
        assert rec.execute("op1", "teacher-unassigned", "Submit", 0) == "OPERATION_CONFLICT"
        assert rec.execute("op1", "registrar", "Submit", 0) == "ROLE_DENIED"


def test_conformance_compare_reports_a_seeded_disagreement(sandbox):
    workflow = config("baseline").workflow
    graph = conformance.explore(workflow, 1, sandbox)
    twin = conformance.Graph(graph.initial, {k: conformance.Node(n.outcomes, n.succ, n.env) for k, n in graph.nodes.items()},
                             graph.cmds, graph.envs)
    assert conformance.compare(graph, twin)["agree"] is True
    key = next(k for k, n in twin.nodes.items() if "DUPLICATE" in n.outcomes)
    node = twin.nodes[key]
    i = node.outcomes.index("DUPLICATE")
    twin.nodes[key] = conformance.Node((*node.outcomes[:i], "COMMITTED", *node.outcomes[i + 1:]), node.succ, node.env)
    result = conformance.compare(graph, twin)
    assert result["agree"] is False and result["outcome_disagreements"] == 1


def test_random_traces_are_seed_deterministic(sandbox):
    workflow = config("candidate").workflow
    a, _ = conformance.build_traces(workflow, 6, sandbox, None, seed="s", random_count=3)
    b, _ = conformance.build_traces(workflow, 6, sandbox, None, seed="s", random_count=3)
    assert [t["steps"] for t in a if t["kind"] == "random"] == [t["steps"] for t in b if t["kind"] == "random"]


# ------------------------------------------------------------------------- TLC (needs Java + jar)

def _small(tmp_path, name, *, ops, dump=False):
    """Generate a small-bound module for `name` (the committed ones use the gate's larger bounds)."""
    small = replace(config(name), check_ops=ops, dump_ops=ops)
    files = {f"MC{'D' if dump else ''}_{name}.tla": generate.module_text(small, dump=dump),
             f"MC{'D' if dump else ''}_{name}.cfg": generate.cfg_text(small, dump=dump)}
    for file, text in files.items():
        (tmp_path / file).write_bytes(text.encode("utf-8"))
    prefix = f"MC{'D' if dump else ''}_{name}"
    return tmp_path / f"{prefix}.tla", tmp_path / f"{prefix}.cfg"


@needs_tlc
def test_tlc_accepts_candidate_and_finds_teacher_approval_counterexample(tmp_path):
    ok = tlc.run_tlc(*_small(tmp_path, "candidate", ops=2), tmp_path, workers=1)
    assert ok.result == "PASS" and ok.distinct > 100
    bad = tlc.run_tlc(*_small(tmp_path, "nc_teacher_approval", ops=3), tmp_path, workers=1)
    assert bad.result == "VIOLATION" and bad.violated == "NoTeacherApproval"
    assert [s["st"] for s in bad.trace][-1] == "Approved" and len(bad.trace) == 4


@needs_tlc
def test_runtime_and_spec_agree_on_the_baseline_state_graph(tmp_path, sandbox):
    cfg = replace(config("baseline"), dump_ops=1)
    python = conformance.explore(cfg.workflow, 1, sandbox)
    run = tlc.run_tlc(*_small(tmp_path, "baseline", ops=1, dump=True), tmp_path, workers=1)
    result = conformance.compare(python, conformance.parse_dump(run.output))
    assert result["agree"], result["examples"]
    assert result["states_runtime"] == result["states_spec"] == run.distinct


@needs_tlc
def test_seeded_spec_defect_is_detected_by_the_graph_comparison(tmp_path, sandbox):
    cand = config("candidate")
    python = conformance.explore(cand.workflow, 1, sandbox)
    (tmp_path / "MCD_seeded.tla").write_bytes(generate.dump_files(replace(cand, dump_ops=1), mutation="replay_before_auth", label="seeded")["MCD_seeded.tla"].encode())
    (tmp_path / "MCD_seeded.cfg").write_bytes(generate.dump_files(replace(cand, dump_ops=1), mutation="replay_before_auth", label="seeded")["MCD_seeded.cfg"].encode())
    run = tlc.run_tlc(tmp_path / "MCD_seeded.tla", tmp_path / "MCD_seeded.cfg", tmp_path, workers=1)
    result = conformance.compare(python, conformance.parse_dump(run.output))
    assert result["agree"] is False and result["outcome_disagreements"] > 0
