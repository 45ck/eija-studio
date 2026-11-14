"""Regressions from the second, principal-engineer pass over the app generator on 14 November 2026 (ADR-0254,
docs/quality/inspection-2026-11-14-app-generator-pass-2.md). Each test failed on the generator before its fix."""
from __future__ import annotations

import http.client
import json
import re
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest

from eija_studio.application.appgen import valid_values
from eija_studio.domain.app_http import status_of
from eija_studio.domain.models import DomainError
from tests.test_appgen_inspection import ai_ops, send  # noqa: F401 - the served ai-ops app fixture

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "src" / "eija_studio" / "resources" / "appgen"


def record_request(port, service, operation_id="create-1", title="Checkout 1.4"):
    made = send(port, "POST", "/api/objects/Microservice", {"actor": "ops-agent", "fields": {"name": "payments"}})[1]
    return {"title": title, "actor": "ops-agent", "fields": valid_values(service.DATA) | {"target": made["id"]},
            "operation_id": operation_id}


def test_a_create_sent_again_after_a_lost_answer_makes_one_record(ai_ops):  # noqa: F811
    """Before: the page could only say "review the latest records before trying again", and a retry made a second
    record. Now the same operation id answers the first record, and the id with another request is a conflict."""
    port, service, svc = ai_ops
    request = record_request(port, service)
    first, again = send(port, "POST", "/api/records", request), send(port, "POST", "/api/records", request)
    assert (first[0], first[1]["duplicate"], again[0], again[1]["duplicate"]) == (201, False, 200, True)
    assert again[1]["id"] == first[1]["id"] and len(svc.records()) == 1
    assert send(port, "POST", "/api/records", request | {"title": "Something else"})[1]["code"] == "OPERATION_CONFLICT"
    assert send(port, "POST", "/api/records", request | {"operation_id": ""})[0] == 400
    assert send(port, "POST", "/api/records", {k: v for k, v in request.items() if k != "operation_id"})[0] == 201  # still optional


def test_an_object_sent_again_after_a_lost_answer_is_stored_once(ai_ops):  # noqa: F811
    port, _, svc = ai_ops
    request = {"actor": "ops-agent", "fields": {"name": "payments"}, "operation_id": "object-1"}
    first, again = send(port, "POST", "/api/objects/Microservice", request), send(port, "POST", "/api/objects/Microservice", request)
    assert (first[0], again[0], again[1]["id"]) == (201, 200, first[1]["id"]) and len(svc.objects("Microservice")) == 1


def test_a_record_cannot_refer_to_an_object_whose_write_rolls_back(ai_ops):  # noqa: F811
    """Before: the reference was checked outside the write lock on the shared connection, so it saw another request's
    uncommitted object, and the record kept the id of an object that was then rolled back."""
    _, service, svc = ai_ops
    inside, release, outcome = threading.Event(), threading.Event(), []

    def work(session):
        svc.db.execute("INSERT INTO objects(id,class,fields,created_by,state) VALUES('ghost','Microservice','{}','x','Active')")
        inside.set()
        release.wait(2)
        raise service.Refused("ROLLED_BACK", "the write fails after its insert")

    def write():
        with pytest.raises(service.Refused):
            svc._write(work)

    def create():
        try:
            outcome.append(svc.create("Ghost", "ops-agent", valid_values(service.DATA) | {"target": "ghost"})["id"])
        except DomainError as refused:
            outcome.append(refused.code)

    writer = threading.Thread(target=write)
    writer.start()
    inside.wait(2)
    creator = threading.Thread(target=create)
    creator.start()
    time.sleep(0.3)
    release.set()
    writer.join()
    creator.join()
    assert outcome == ["REFERENCE_UNKNOWN"]


@pytest.mark.parametrize(("code", "status"), [("ROLE_CANNOT_START", 403), ("SEPARATION_DENIED", 403), ("TIMER_NOT_DUE", 409),
                                              ("OPERATION_CONFLICT", 409), ("REFERENCE_UNKNOWN", 400)])
def test_each_refusal_is_answered_with_the_status_the_contract_documents(ai_ops, monkeypatch, code, status):  # noqa: F811
    """Before: the server kept its own two sets, and the contract a third copy that left out eight 409 codes, HOST_DENIED
    and INTERNAL_ERROR, and said a create could not be refused 409 (ROLE_CANNOT_START was answered 409)."""
    port, _, svc = ai_ops

    def refuse(*_args):
        raise DomainError(code, "refused")
    monkeypatch.setattr(svc, "create", refuse)
    answer = send(port, "POST", "/api/records", {"title": "x", "actor": "ops-agent"})
    assert answer == (status, {"code": code, "message": "refused"}) and status_of(code) == status


def test_a_request_that_never_sends_its_body_is_answered_and_its_thread_freed(ai_ops):  # noqa: F811
    """Before: no timeout, so each connection that promised a body held a server thread for ever (40 s and counting)."""
    port, _, _ = ai_ops
    with socket.create_connection(("127.0.0.1", port)) as held:
        held.sendall(f"POST /api/records HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: application/json\r\n"
                     "Content-Length: 50\r\n\r\n".encode())
        held.settimeout(45)
        started = time.monotonic()
        answer = held.recv(4096).decode()
    assert answer.startswith("HTTP/1.0 408") and '"REQUEST_TIMEOUT"' in answer and 25 < time.monotonic() - started < 40


def test_the_browser_icon_request_is_not_an_error(ai_ops):  # noqa: F811
    """Before: every page load logged a 404 for /favicon.ico in the console."""
    port, _, _ = ai_ops
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    connection.request("GET", "/favicon.ico")
    response = connection.getresponse()
    assert (response.status, response.read()) == (204, b"")


def test_the_record_list_is_one_query_and_history_uses_an_index(ai_ops):  # noqa: F811
    """Before: one query per record for the list, and every view scanned the whole audit table; 5,000 records took
    0.395 s to list and 0.02 s to view (now 0.03 s and under 0.001 s)."""
    port, service, svc = ai_ops
    for n in range(5):
        send(port, "POST", "/api/records", record_request(port, service, f"op-{n}", f"Record {n}"))
    statements = []
    svc.db.set_trace_callback(statements.append)
    svc.records()
    svc.db.set_trace_callback(None)
    assert len([s for s in statements if s.lstrip().upper().startswith("SELECT")]) == 1
    plan = " ".join(str(tuple(r)) for r in svc.db.execute(
        "EXPLAIN QUERY PLAN SELECT kind, body FROM audit WHERE json_extract(body, '$.instance_id')=? ORDER BY seq", ("x",)))
    assert "audit_instance" in plan
    assert (TEMPLATES / "service.py.tmpl").read_text().count("MODEL.semantic_hash") == 1  # hashed once, not per record


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: node is not installed")
def test_a_number_the_browser_cannot_hold_is_sent_as_typed_not_as_null():
    """Before: Number("1e999") is Infinity, which JSON writes as null, so the page sent a missing value: an optional
    number was silently dropped, a required one was reported as missing instead of as not a number."""
    source = (TEMPLATES / "react-source" / "controller.js").read_text()
    function = re.search(r"^function number\(value\) \{.*\}$", source, re.M).group(0)
    script = function + "\nconsole.log(JSON.stringify([number('1e999'), number('12.5'), number('-0'), number('abc')]))"
    assert json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True,  # noqa: S603, S607
                                     check=True).stdout) == ["1e999", 12.5, 0, "abc"]


def test_the_page_sends_one_operation_id_per_draft():
    source = (TEMPLATES / "react-source" / "controller.js").read_text()
    assert "const operation_id = state.form.operation ||= crypto.randomUUID();" in source
    assert "const operation_id = state.objectOps[cls] ||= crypto.randomUUID();" in source
    assert "delete state.form.operation;  // a changed request is a new operation" in source
    # Choosing an object just added changes the record draft, so it takes a new id too (Codex review of #264).
    assert "updateRecordField(reference.field, made.id);" in source
