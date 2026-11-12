"""Actions on linked objects (issue #93 item 4, ADR-0241).

A workflow may give the object a built reference names a small lifecycle, and a transition may move it (`then`). The
kernel reads the object's state through `UnitOfWork.object_state`, refuses with LINKED_OBJECT_REFUSED when the object
has no move from it, and writes the move in the same unit of work. Models without linked objects keep their bytes. The
law proof tries every state of an object, Simulate shares objects between records, the built app stores object states
and its conformance run checks the linked cases, and the SCXML chart carries the object's state, which the
differential checks.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application import runtime
from eija_studio.application.appgen import generate, linked_cases
from eija_studio.application.diagrams import state_graph
from eija_studio.application.law_proof import prove_laws, with_laws
from eija_studio.application.memo import model_hash
from eija_studio.application.scxml import to_scxml
from eija_studio.application.simulation import MemorySession, simulate
from eija_studio.domain.data import data_for
from eija_studio.domain.impact import changed_fields
from eija_studio.domain.linked import admitting, along, combinations
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.app_build import conformance
from eija_studio.interfaces.cli import main
from verification.scope import OutsideFormalScope, require_formal_scope

ROOT = Path(__file__).resolve().parents[1]
OPS = load_pack(ROOT / "packs" / "ai-ops")


def unlinked(model: Workflow) -> Workflow:
    raw = model.model_dump(mode="json")
    raw.pop("objects")
    for t in raw["transitions"]:
        t.pop("then", None)
    return Workflow.model_validate(raw)


FLAT = unlinked(OPS.model)
MOVED = [{"link": "target", "event": "lock", "from": "Idle", "to": "RollingOut"}]


def _step(state: str, action: str, actor: str, objects: dict[str, str | None], model: Workflow = OPS.model,
          session: MemorySession | None = None) -> tuple[dict, MemorySession]:
    session = session or MemorySession(OPS)
    session.create_instance({"id": "r", "case_id": "c", "model_hash": model_hash(model), "state": state, "version": 0})
    for link, at in objects.items():
        session.link("r", link, f"svc-{link}", at)
    command = ExecuteCommand(operation_id="op", actor_id=actor, instance_id="r", action=action, expected_version=0)
    return runtime.execute(session, "c", model, command, pack=OPS), session  # type: ignore[arg-type]


def test_a_lifecycle_is_closed_deterministic_and_every_step_names_one():
    target = OPS.model.lifecycle("target")
    assert target is not None and target.entity == "Microservice" and target.initial == "Idle"
    assert target.move("lock", "Idle") == "RollingOut" and target.move("lock", "RollingOut") is None
    assert target.move("release", None) is None and target.events() == {"lock", "release"}
    raw = OPS.model.model_dump(mode="json")
    bad = json.loads(json.dumps(raw))
    bad["objects"][0]["moves"].append({"event": "lock", "from_state": "Idle", "to_state": "Gone"})
    with pytest.raises(ValueError):
        Workflow.model_validate(bad)
    twice = json.loads(json.dumps(raw))
    twice["objects"][0]["moves"].append({"event": "lock", "from_state": "Idle", "to_state": "Idle"})
    with pytest.raises(ValueError):
        Workflow.model_validate(twice)
    undeclared = json.loads(json.dumps(raw))
    next(t for t in undeclared["transitions"] if t["id"] == "TR-WINDOW")["then"] = [{"link": "target", "event": "explode"}]
    with pytest.raises(ValueError, match="declared lifecycle"):
        Workflow.model_validate(undeclared)
    doubled = json.loads(json.dumps(raw))
    next(t for t in doubled["transitions"] if t["id"] == "TR-WINDOW")["then"] = [{"link": "target", "event": "lock"}] * 2
    with pytest.raises(ValueError):
        Workflow.model_validate(doubled)


def test_the_kernel_moves_the_object_in_the_same_step():
    result, session = _step("Scheduled", "OpenWindow", "deploy-window", {"target": "Idle"})
    assert result["instance"]["state"] == "Rolling" and session.object_state("r", "target") == "RollingOut"
    assert result["moved"] == MOVED


def test_the_kernel_refuses_a_step_the_object_cannot_take_and_moves_nothing():
    for at in ("RollingOut", None):
        session = MemorySession(OPS)
        with pytest.raises(DomainError) as e:
            _step("Scheduled", "OpenWindow", "deploy-window", {"target": at}, session=session)
        assert e.value.code == "LINKED_OBJECT_REFUSED"
        assert e.value.details["refs"][:2] == ["transition:TR-WINDOW", "link:target"]
        assert session.instances["r"]["state"] == "Scheduled" and session.object_state("r", "target") == at
    with pytest.raises(DomainError) as e:  # a record that names no object
        _step("Scheduled", "OpenWindow", "deploy-window", {})
    assert e.value.code == "LINKED_OBJECT_REFUSED"


def test_models_without_linked_objects_keep_their_bytes_and_never_read_objects():
    dumped = json.dumps(FLAT.model_dump(mode="json"))
    assert '"then"' not in dumped and '"objects"' not in dumped
    assert FLAT.semantic_hash != OPS.model.semantic_hash
    before, after = FLAT.transition_for("OpenWindow"), OPS.model.transition_for("OpenWindow")
    assert before is not None and after is not None and changed_fields(before, after) == ["then"]

    class NoObjects(MemorySession):
        def object_state(self, instance_id: str, link: str) -> str | None:
            raise AssertionError("an object was read for a step that moves none")

    result, _ = _step("Scheduled", "OpenWindow", "deploy-window", {}, model=FLAT, session=NoObjects(OPS))
    assert result["committed"] and "moved" not in result
    result, _ = _step("Opened", "StartBuild", "ops-agent", {"target": "Idle"}, session=NoObjects(OPS))
    assert result["committed"] and "moved" not in result


def test_combinations_along_and_admitting():
    window = OPS.model.transition_for("OpenWindow")
    assert combinations(OPS.model, window) == [{"target": "Idle"}, {"target": "RollingOut"}]
    assert combinations(OPS.model, OPS.model.transition_for("StartBuild")) == [{}]
    assert admitting(OPS.model, window) == {"target": "Idle"}
    assert admitting(OPS.model, OPS.model.transition_for("ConfirmHealthy")) == {"target": "RollingOut"}
    assert along(OPS.model)["Rolling"] == {"target": "RollingOut"} and along(OPS.model)["InProduction"] == {"target": "Idle"}
    assert along(FLAT) == {}


def test_the_law_proof_tries_every_state_of_the_object():
    report = prove_laws(OPS)
    assert report["search"]["status"] == "COMPLETE" and all(v["status"] in ("HOLDS", "EVIDENCE") for v in report["laws"])
    assert {"OpenWindow", "ConfirmHealthy", "AutoRollback"}.isdisjoint(report["search"]["never_committed"])
    assert prove_laws(OPS, FLAT)["search"]["reached"] == report["search"]["reached"]


def test_simulated_records_contend_for_shared_objects():
    run = simulate(OPS, OPS.model, seed=3, steps=2000)
    window = run["transitions"]["TR-WINDOW"]
    assert window["committed"] > 0 and window["refused"].get("LINKED_OBJECT_REFUSED", 0) > 0, window
    assert "LINKED_OBJECT_REFUSED" not in json.dumps(simulate(OPS, FLAT, seed=3, steps=2000))


def test_the_oracle_tries_each_object_state():
    cases = linked_cases(OPS, OPS.model)
    window = [(c["objects"], c["expect"]["outcome"], c.get("after")) for c in cases if c["action"] == "OpenWindow"]
    assert window == [({"target": "Idle"}, "COMMITTED", {"target": "RollingOut"}),
                      ({"target": "RollingOut"}, "REFUSED", None)]
    assert len(cases) == 6 and linked_cases(OPS, FLAT) == []
    data = data_for(OPS)
    oracle = json.loads(generate(OPS, data=data)[0]["tests/oracle.json"])
    assert len(oracle["linked_cases"]) == 6 and oracle["linked"]["Rolling"] == {"target": "RollingOut"}
    assert "linked" not in json.loads(generate(OPS, FLAT, data=data)[0]["tests/oracle.json"])
    with pytest.raises(DomainError) as e:  # a lifecycle needs a built reference naming its object
        generate(OPS)
    assert e.value.code == "LINK_NOT_BUILT" and e.value.details["refs"] == ["link:target"]


def test_the_scxml_chart_carries_the_object_and_the_differential_catches_a_chart_that_forgets_it():
    chart = to_scxml(OPS)
    assert "_event.data.object_target == &quot;Idle&quot;" in chart and '<data id="moved"' in chart
    assert "object_target" not in to_scxml(OPS, FLAT) and '<data id="moved"' not in to_scxml(OPS, FLAT)
    differential = pytest.importorskip("verification.scxml.differential")
    if differential.load is None:
        pytest.skip("python-statemachine is not installed")
    assert differential.compare(OPS)["status"] == "PASS"
    forgot = chart.replace(" and _event.data.object_target == &quot;Idle&quot;", "")
    assert forgot != chart and differential.compare(OPS, document=forgot)["status"] == "FAIL"
    no_move = chart.replace('moved + [&quot;target:RollingOut&quot;]', "moved")
    assert no_move != chart and differential.compare(OPS, document=no_move)["status"] == "FAIL"


def test_the_state_diagram_writes_the_step_and_the_formal_encodings_refuse_it():
    labels = [e.label for e in state_graph(OPS.model).edges]
    assert "OpenWindow / target.lock · DeployWindow" in labels
    assert not any("/" in label for label in (e.label for e in state_graph(FLAT).edges))
    with pytest.raises(OutsideFormalScope, match="linked objects"):
        require_formal_scope(OPS.model)
    assert require_formal_scope(FLAT) is FLAT


def test_a_built_app_keeps_object_states_and_conformance_catches_an_app_that_does_not(tmp_path):
    pack_dir, out = tmp_path / "ai-ops", tmp_path / "app"
    shutil.copytree(ROOT / "packs" / "ai-ops", pack_dir)
    assert main(["build", "--pack", str(pack_dir), "--out", str(out)]) == 0
    manifest = json.loads((out / "BUILD.json").read_text(encoding="utf-8"))
    assert manifest["conformance"]["status"] == "PASS", manifest["conformance"]
    service = out / "app" / "service.py"
    text = service.read_text(encoding="utf-8")
    marker = 'self.db.execute("UPDATE objects SET state=? WHERE id=?", (state, self.values(instance_id)[link]))'
    assert marker in text
    service.write_text(text.replace(marker, "pass"), encoding="utf-8")  # negative control: the move is lost
    assert conformance(out)["status"] == "FAIL"


def test_one_transition_never_moves_two_objects_of_one_class():
    """Review regression: two links could name one object, and both moves were written to it."""
    raw = OPS.model.model_dump(mode="json")
    raw["objects"].append(dict(raw["objects"][0], link="spare"))
    next(t for t in raw["transitions"] if t["id"] == "TR-WINDOW")["then"] = [
        {"link": "target", "event": "lock"}, {"link": "spare", "event": "lock"}]
    with pytest.raises(ValueError, match="at most one object of each class"):
        Workflow.model_validate(raw)


def test_the_law_proof_carries_object_states_forward():
    """Review regression: trying every object state at every step proved a record could finish when a lock it took
    could never be released."""
    ends = {"id": "every-change-ends", "kind": "can_reach_end", "code": "STUCK",
            "states": ["InProduction", "RolledBack", "Abandoned"]}
    pack = with_laws(OPS, [law.model_dump(mode="json") for law in OPS.laws] + [ends])
    assert {v["id"]: v for v in prove_laws(pack)["laws"]}["every-change-ends"]["status"] == "HOLDS"
    raw = OPS.model.model_dump(mode="json")
    raw["objects"][0]["moves"] = [m for m in raw["objects"][0]["moves"] if m["event"] == "lock"]  # never released
    for t in raw["transitions"]:
        if t.get("then") and t["then"][0]["event"] == "release":
            t["then"] = [{"link": "target", "event": "lock"}]
    verdict = {v["id"]: v for v in prove_laws(pack, Workflow.model_validate(raw))["laws"]}["every-change-ends"]
    assert verdict["status"] == "BROKEN" and "Rolling" in verdict["stuck"]


def test_the_differential_runs_a_timed_step_on_a_linked_object():
    """Review regression: a case without the objects' end states (a timer or value case) stopped the differential."""
    raw = OPS.model.model_dump(mode="json")
    next(t for t in raw["transitions"] if t["id"] == "TR-WINDOW")["after"] = {"amount": 1, "unit": "hours"}
    timed = Workflow.model_validate(raw)
    differential = pytest.importorskip("verification.scxml.differential")
    if differential.load is None:
        pytest.skip("python-statemachine is not installed")
    assert differential.compare(OPS, timed)["status"] == "PASS"
