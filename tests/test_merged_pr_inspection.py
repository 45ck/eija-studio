"""Defects found by the 2026-11-13 re-inspection of the pull requests merged from 2026-11-11 (#217 to #252).

Log: docs/quality/inspection-2026-11-13-merged-prs.md. Each test failed on main before its fix.

* M1: another source for an action that carries a time event, a value guard, a step on a linked object, or edited
  guards or effects was refused as "incoherent", so ADR-0232 (one action from several states) did not hold for them.
* M2: two links to one class could declare different lifecycles, but an object has one state; the built app started
  every object in the first lifecycle's initial state and failed its own conformance with no named cause. The policy
  now refuses it as LINKED_LIFECYCLE_CONFLICT.
* M3: the built app refused `expected_version: 1.0`, which its published contract and the kernel (ADR-0238) accept.
* M4: UML exports dropped who may start a record (ADR-0231) without listing it as not carried.
"""
from __future__ import annotations

import http.client
import importlib
import json
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from eija_studio.application.interop import export_model
from eija_studio.bootstrap import source_identity
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.application.appgen import generate
from eija_studio.domain.policy import apply_structural_all, check_policy, lifecycle_conflicts
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.app_build import app_files

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
REFUND = load_pack(ROOT / "packs" / "refund-desk")
OPS = load_pack(ROOT / "packs" / "ai-ops")


def _another_source(pack, model: Workflow, action: str, **change) -> Workflow:
    t = model.transition_for(action)
    assert t is not None
    source = next(s for s in model.states if s not in model.sources(action) and s != t.to_state)
    tx = {"kind": "add_transition", "id": "TR-ANOTHER", "action": action, "from_state": source, "to_state": t.to_state,
          "role": t.role} | change
    return apply_structural_all(model, [parse_transaction(tx)], pack)


# ---- M1 ------------------------------------------------------------------------------------------------------

def test_m1_a_timed_action_can_leave_another_state():
    timed = next(t for t in REFUND.model.transitions if t.after is not None)
    after = _another_source(REFUND, REFUND.model, timed.action)
    added = next(t for t in after.transitions if t.id == "TR-ANOTHER")
    assert len(after.sources(timed.action)) == 2 and added.after == timed.after


def test_m1_an_action_on_a_linked_object_can_leave_another_state():
    linked = next(t for t in OPS.model.transitions if t.then)
    after = _another_source(OPS, OPS.model, linked.action)
    assert next(t for t in after.transitions if t.id == "TR-ANOTHER").then == linked.then


def test_m1_a_value_guarded_action_can_leave_another_state():
    raw = LOAN.model.model_dump(mode="json")
    target = next(t for t in raw["transitions"] if t["action"] == "CheckOut")
    target["conditions"] = [{"attribute": "copies", "op": "gt", "value": 0}]
    after = _another_source(LOAN, Workflow.model_validate(raw), "CheckOut")
    assert [str(c) for c in after.transition_for("CheckOut", after.sources("CheckOut")[1]).conditions] == ["copies > 0"]


def test_m1_an_action_whose_guards_were_edited_can_leave_another_state():
    t = LOAN.model.transition_for("CheckOut")
    assert t is not None and "actor_assigned" in t.guards
    edited = apply_structural_all(LOAN.model, [parse_transaction(
        {"kind": "set_guards", "transition": t.id, "guards": [g for g in t.guards if g != "actor_assigned"]})], LOAN)
    after = _another_source(LOAN, edited, "CheckOut")
    assert "actor_assigned" not in next(x for x in after.transitions if x.id == "TR-ANOTHER").guards


def test_m1_another_source_with_a_different_target_is_refused_and_named():
    t = LOAN.model.transition_for("CheckOut")
    assert t is not None
    other = next(s for s in LOAN.model.states if s != t.to_state)
    with pytest.raises(DomainError) as refused:
        _another_source(LOAN, LOAN.model, "CheckOut", to_state=other)
    assert refused.value.code == "EDIT_INVALID" and f"already goes to {t.to_state}" in refused.value.message


# ---- M2 ------------------------------------------------------------------------------------------------------

def _two_links(lifecycle: dict) -> dict:
    raw = OPS.model.model_dump(mode="json")
    raw["objects"].append({"link": "canary", "entity": "Microservice"} | lifecycle)
    return raw


def test_m2_two_links_to_one_class_may_not_declare_different_lifecycles(tmp_path):
    model = Workflow.model_validate(_two_links({"states": ["Cold", "Warm"], "initial": "Cold",
                                                "moves": [{"event": "warm", "from_state": "Cold", "to_state": "Warm"}]}))
    assert "LINKED_LIFECYCLE_CONFLICT:Microservice" in check_policy(model, OPS)
    with pytest.raises(DomainError) as refused:
        generate(OPS, model, data_for(OPS))
    assert refused.value.code == "POLICY_BLOCKED" and "LINKED_LIFECYCLE_CONFLICT:Microservice" in refused.value.details["codes"]


def test_m2_two_links_to_one_class_may_share_its_lifecycle_in_any_order():
    first = OPS.model.objects[0].model_dump(mode="json")
    same = {"states": list(reversed(first["states"])), "initial": first["initial"], "moves": list(reversed(first["moves"]))}
    model = Workflow.model_validate(_two_links(same))
    assert len(model.objects) == 2 and not lifecycle_conflicts(model)
    assert not lifecycle_conflicts(OPS.model)


# ---- M3 ------------------------------------------------------------------------------------------------------

@pytest.fixture
def loan_app(tmp_path):
    """The library-loan app's real HTTP server and SQLite service, without a nested conformance run."""
    out = tmp_path / "built-loan"
    files, _ = app_files(LOAN, LOAN.model, identity_provider=source_identity)
    for relative, text in files.items():
        (out / relative).parent.mkdir(parents=True, exist_ok=True)
        (out / relative).write_bytes(text.encode("utf-8"))
    saved = {name: module for name, module in sys.modules.items() if name == "app" or name.startswith("app.")}
    for name in saved:
        del sys.modules[name]
    sys.path.insert(0, str(out))
    service = server = None
    try:
        service = importlib.import_module("app.service").Service(str(tmp_path / "app.sqlite3"))
        server = ThreadingHTTPServer(("127.0.0.1", 0), importlib.import_module("app.server").handler_for(service))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        yield server.server_address[1], service
    finally:
        if server:
            server.shutdown()
            server.server_close()
        if service:
            service.db.close()
        sys.path.remove(str(out))
        for name in [name for name in sys.modules if name == "app" or name.startswith("app.")]:
            del sys.modules[name]
        sys.modules.update(saved)


def _post(port: int, path: str, body: dict) -> tuple[int, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        connection.request("POST", path, json.dumps(body), {"Content-Type": "application/json"})
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally:
        connection.close()


def test_m3_the_built_app_reads_a_whole_float_version_as_a_json_integer(loan_app):
    port, _service = loan_app
    actor = next(a for a in LOAN.fixtures.actors if a.active)
    data = data_for(LOAN)
    fields = importlib.import_module("eija_studio.application.appgen").valid_values(data)
    status, created = _post(port, "/api/records", {"title": "Loan", "actor": actor.id, "fields": fields})
    assert status == 201, created
    t = next(t for t in LOAN.model.transitions if t.from_state == LOAN.model.initial_state)
    taker = next(a for a in LOAN.fixtures.actors if a.active and a.role == t.role and (a.assigned or "actor_assigned" not in t.guards))
    body = {"actor": taker.id, "action": t.action, "expected_version": 0.0, "operation_id": "op-float"}
    status, acted = _post(port, f"/api/records/{created['id']}/act", body)
    assert status == 200 and acted["committed"], acted
    for wrong in (0.5, "0", True):
        status, refused = _post(port, f"/api/records/{created['id']}/act", body | {"expected_version": wrong, "operation_id": f"op-{wrong}"})
        assert status == 400 and refused["code"] == "BAD_REQUEST", (wrong, refused)


# ---- M4 ------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["plantuml", "mermaid", "xmi", "drawio"])
def test_m4_an_export_lists_who_may_start_a_record_as_not_carried(fmt):
    raw = LOAN.model.model_dump(mode="json")
    role = sorted({t["role"] for t in raw["transitions"]})[0]
    _, report = export_model(fmt, LOAN, Workflow.model_validate(raw | {"initiators": [role]}), data_for(LOAN))
    assert any(f"who may start a record: {role}" in item for item in report["not_carried"])
    _, plain = export_model(fmt, LOAN, LOAN.model, data_for(LOAN))
    assert not any("who may start a record" in item for item in plain["not_carried"])
