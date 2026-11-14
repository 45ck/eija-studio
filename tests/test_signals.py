"""Messages between workflows (issue #93 item 5, ADR-0242).

A transition may require a signal effect, `Signal:LateReturn`, addressed to another workflow of the system. The kernel
writes it to the outbox in the sender's unit of work, as it writes a notification. A workflow that says it receives that
signal from that sender starts a record when the signal is delivered (`runtime.receive`); any other signal or sender is
refused with SIGNAL_NOT_ACCEPTED, and a redelivery under the same operation id starts nothing new. The system landscape
draws each signal and flags one that only one end declares; the built app has a signal endpoint its conformance run
checks against the kernel.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from eija_studio.application import runtime
from eija_studio.application.appgen import generate, signal_cases
from eija_studio.application.interop import export_model, start_from_file
from eija_studio.application.landscape import landscape
from eija_studio.application.memo import model_hash
from eija_studio.application.simulation import MemorySession
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError, ExecuteCommand, Workflow
from eija_studio.domain.pack import PackError, load_pack, parse_pack
from eija_studio.interfaces.app_build import conformance
from eija_studio.interfaces.cli import main

ROOT = Path(__file__).resolve().parents[1]
LOANS = load_pack(ROOT / "packs" / "library-loan")
FINES = load_pack(ROOT / "packs" / "library-fines")
LATE = "Signal:LateReturn"


def deaf(model: Workflow) -> Workflow:
    raw = model.model_dump(mode="json")
    raw.pop("receives")
    return Workflow.model_validate(raw)


def system(*packs):
    return [(p, data_for(p), p.model) for p in packs]


def test_a_signal_is_a_typed_effect_addressed_to_another_workflow():
    assert LOANS.effect(LATE).kind == "signal" and LOANS.effect(LATE).recipient == "library-fines"
    raw = LOANS.model_dump(mode="json")
    for change, problem in ((lambda e: e.pop("recipient"), "needs a recipient"),
                            (lambda e: e.update(recipient="library-loan"), "goes to another workflow"),
                            (lambda e: e.update(kind="audit"), "only a signal may be named Signal:")):
        bad = json.loads(json.dumps(raw))
        change(next(e for e in bad["effects"]["catalog"] if e["id"] == LATE))
        with pytest.raises(PackError, match=problem):
            parse_pack(bad)


def test_a_workflow_says_which_signals_start_a_record():
    assert [str(r) for r in FINES.model.receives] == ["Signal:LateReturn from library-loan"]
    assert FINES.model.receiving(LATE, "library-loan") is not None and FINES.model.receiving(LATE, "other") is None
    raw = FINES.model.model_dump(mode="json")
    with pytest.raises(ValueError, match="Duplicate received signal"):
        Workflow.model_validate(raw | {"receives": raw["receives"] * 2})
    with pytest.raises(ValueError):
        Workflow.model_validate(raw | {"receives": [{"signal": "LateReturn", "sender": "library-loan"}]})


def test_models_without_signals_keep_their_bytes_and_receiving_is_a_set():
    plain = deaf(FINES.model)
    assert '"receives"' not in json.dumps(plain.model_dump(mode="json")) and plain.semantic_hash != FINES.model.semantic_hash
    raw = FINES.model.model_dump(mode="json")
    two = [{"signal": LATE, "sender": "library-loan"}, {"signal": "Signal:Lost", "sender": "library-loan"}]
    assert Workflow.model_validate(raw | {"receives": two}).semantic_hash == \
        Workflow.model_validate(raw | {"receives": two[::-1]}).semantic_hash


def test_the_sender_writes_the_signal_to_its_outbox_in_the_same_step():
    session = MemorySession(LOANS)
    session.create_instance({"id": "r", "case_id": "c", "model_hash": model_hash(LOANS.model), "state": "Overdue", "version": 0})
    command = ExecuteCommand(operation_id="op", actor_id="librarian-assigned", instance_id="r", action="ReturnLate",
                             expected_version=0)
    result = runtime.execute(session, "c", LOANS.model, command, pack=LOANS)  # type: ignore[arg-type]
    assert LATE in result["effects"] and session.outbox == [LATE]


def test_the_receiver_starts_one_record_per_signal_and_refuses_others():
    session = MemorySession(FINES)
    started = runtime.receive(session, "c", FINES.model, LATE, "library-loan", "late-1", pack=FINES)  # type: ignore[arg-type]
    assert started["started"] and started["instance"]["state"] == "Issued" and len(session.instances) == 1
    again = runtime.receive(session, "c", FINES.model, LATE, "library-loan", "late-1", pack=FINES)  # type: ignore[arg-type]
    assert again["duplicate"] and again["original_result"]["instance"]["id"] == started["instance"]["id"]
    assert len(session.instances) == 1
    session.record_operation("op-taken", "another-binding", {})
    for signal, sender, operation, code in ((LATE, "library-loan", "op-taken", "OPERATION_CONFLICT"),
                                            ("Signal:Lost", "library-loan", "x", "SIGNAL_NOT_ACCEPTED"),
                                            (LATE, "excursion", "y", "SIGNAL_NOT_ACCEPTED")):
        with pytest.raises(DomainError) as e:
            runtime.receive(session, "c", FINES.model, signal, sender, operation, pack=FINES)  # type: ignore[arg-type]
        assert e.value.code == code
    assert len(session.instances) == 1


def test_a_redelivery_with_other_values_is_a_conflict():
    """Review regression: the delivery binding ignored the record values, so changed values replayed as a duplicate."""
    session = MemorySession(FINES)
    runtime.receive(session, "c", FINES.model, LATE, "library-loan", "late-1", pack=FINES, values={"amount": 10})  # type: ignore[arg-type]
    assert runtime.receive(session, "c", FINES.model, LATE, "library-loan", "late-1", pack=FINES,  # type: ignore[arg-type]
                           values={"amount": 10})["duplicate"]
    with pytest.raises(DomainError) as e:
        runtime.receive(session, "c", FINES.model, LATE, "library-loan", "late-1", pack=FINES, values={"amount": 100})  # type: ignore[arg-type]
    assert e.value.code == "OPERATION_CONFLICT" and len(session.instances) == 1


def test_the_landscape_draws_each_signal_and_flags_one_end_only():
    both = landscape("library-loan", system(LOANS, FINES))
    assert both["signals"] == [{"source": "library-loan", "target": "library-fines", "signal": LATE}]
    assert not [f for f in both["findings"] if f["code"].startswith("SIGNAL_")]
    loans = next(w for w in both["workflows"] if w["id"] == "library-loan")
    assert loans["sends"] == [{"signal": LATE, "to": "library-fines"}]
    unheard = landscape("library-loan", [(LOANS, data_for(LOANS), LOANS.model), (FINES, data_for(FINES), deaf(FINES.model))])
    assert [f["code"] for f in unheard["findings"] if f["code"].startswith("SIGNAL_")] == ["SIGNAL_UNHEARD"]
    assert "signals" not in unheard
    never = landscape("library-fines", system(FINES))
    assert [f["code"] for f in never["findings"]] == ["SIGNAL_NEVER_SENT"]
    plain = landscape("excursion", system(load_pack(ROOT / "packs" / "excursion")))
    assert "signals" not in plain and all("sends" not in w and "receives" not in w for w in plain["workflows"])


def test_a_signal_alone_puts_two_workflows_in_one_system():
    desk = load_pack(ROOT / "packs" / "refund-desk")
    raw = desk.model.model_dump(mode="json") | {"receives": [{"signal": LATE, "sender": "library-loan"}]}
    result = landscape("library-loan", [*system(LOANS), (desk, data_for(desk), Workflow.model_validate(raw))])
    assert {w["id"] for w in result["workflows"]} == {"library-loan", "refund-desk"}
    assert "SIGNAL_UNHEARD" in [f["code"] for f in result["findings"]]  # it goes to library-fines, not the desk


def test_the_oracle_delivers_each_signal_and_two_it_refuses():
    cases = signal_cases(FINES, FINES.model, data_for(FINES))
    assert [(c["signal"], c["sender"], c["expect"]) for c in cases] == [
        (LATE, "library-loan", {"outcome": "STARTED", "state": "Issued",  # with the values the record keeps (ADR-0249)
                                "fields": {"amount": 1, "reason": "Overdue", "issuedOn": "2026-01-15", "note": "Sample"}}),
        ("Signal:Unheard", "library-loan", {"outcome": "REFUSED", "code": "SIGNAL_NOT_ACCEPTED"}),
        (LATE, "unheard-workflow", {"outcome": "REFUSED", "code": "SIGNAL_NOT_ACCEPTED"})]
    assert cases[0]["again"] == {"outcome": "STARTED"}  # the same signal as a new message starts another record
    assert signal_cases(FINES, deaf(FINES.model), data_for(FINES)) == []
    assert "signal_cases" not in json.loads(generate(FINES, deaf(FINES.model), data_for(FINES))[0]["tests/oracle.json"])


def test_a_built_app_starts_records_on_signals_and_conformance_catches_one_that_hears_anything(tmp_path):
    pack_dir, out = tmp_path / "library-fines", tmp_path / "app"
    shutil.copytree(ROOT / "packs" / "library-fines", pack_dir)
    assert main(["build", "--pack", str(pack_dir), "--out", str(out)]) == 0
    manifest = json.loads((out / "BUILD.json").read_text(encoding="utf-8"))
    assert manifest["conformance"]["status"] == "PASS", manifest["conformance"]
    service = out / "app" / "service.py"
    text = service.read_text(encoding="utf-8")
    marker = "receive(session, CASE, MODEL, signal, sender, operation_id, pack=PACK, values=values)"
    assert marker in text
    service.write_text(text.replace(marker, "receive(session, CASE, MODEL, MODEL.receives[0].signal, "
                                            "MODEL.receives[0].sender, operation_id, pack=PACK, values=values)"), encoding="utf-8")
    assert conformance(out)["status"] == "FAIL"  # negative control: the app starts a record on any signal


def test_a_uml_file_keeps_the_signal_but_not_where_it_goes():
    text, _ = export_model("plantuml", LOANS, None, data_for(LOANS))
    documents, report = start_from_file("plantuml", text, "Loans", "loans")
    effect = next(e for e in documents["pack.json"]["effects"]["catalog"] if e["id"] == LATE)
    assert effect == {"id": LATE, "kind": "signal", "recipient": "unaddressed"}
    assert any("a signal goes to" in d["reason"] for d in report["defaulted"])
    assert "1 signal(s) from other workflows" in " ".join(export_model("plantuml", FINES, None, data_for(FINES))[1]["not_carried"])


def test_the_running_app_takes_signals_over_http_and_refuses_a_missing_delivery_id(tmp_path):
    """Review regression: a missing delivery id became the shared id "missing", and a long one was cut short."""
    import http.client  # noqa: PLC0415
    import importlib  # noqa: PLC0415
    import sys  # noqa: PLC0415
    import threading  # noqa: PLC0415
    from http.server import ThreadingHTTPServer  # noqa: PLC0415

    pack_dir, out = tmp_path / "library-fines", tmp_path / "app"
    shutil.copytree(ROOT / "packs" / "library-fines", pack_dir)
    assert main(["build", "--pack", str(pack_dir), "--out", str(out), "--no-test"]) == 0
    sys.path.insert(0, str(out))
    try:
        server_module, service_module = importlib.import_module("app.server"), importlib.import_module("app.service")
        server = ThreadingHTTPServer(("127.0.0.1", 0), server_module.handler_for(service_module.Service()))
        threading.Thread(target=server.serve_forever, daemon=True).start()

        def post(body):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=10)
            connection.request("POST", "/api/signals", body=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            response = connection.getresponse()
            answer = (response.status, json.loads(response.read()))
            connection.close()
            return answer

        fine = {"amount": 5, "reason": "Overdue", "issuedOn": "2026-11-12"}
        base = {"signal": LATE, "sender": "library-loan", "fields": fine}
        status, started = post(base | {"operation_id": "late-1"})
        assert status == 201 and started["record"]["state"] == "Issued" and started["record"]["fields"] == fine
        assert post(base | {"operation_id": "late-1"})[0] == 200
        assert post(base | {"operation_id": "late-1", "fields": fine | {"amount": 50}})[1]["code"] == "OPERATION_CONFLICT"
        for operation in (None, "", "x" * 101, 7):
            body = base | ({"operation_id": operation} if operation is not None else {})
            assert post(body) == (400, {"code": "BAD_REQUEST", "message": "operation_id must be a string of 1 to 100 characters"})
        assert post(base | {"operation_id": "late-2", "signal": "Signal:Lost"})[1]["code"] == "SIGNAL_NOT_ACCEPTED"
        server.shutdown()
        server.server_close()
    finally:
        sys.path.remove(str(out))
        for module in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
            del sys.modules[module]
