"""Regressions from the 13 November 2026 Fagan inspection of the app generator (ADR-0249,
docs/quality/inspection-2026-11-13-app-generator.md). Each test failed on the generator before its fix."""
from __future__ import annotations

import http.client
import importlib
import json
import os
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from eija_studio.application.appgen import CASE_KINDS, generate, valid_values
from eija_studio.domain.data import data_for
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.cli import main

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def ai_ops(tmp_path):
    """The ai-ops app (a built association to Microservice, which has a lifecycle), served on a loopback port."""
    out = tmp_path / "ai-ops"
    assert main(["build", "--pack", str(ROOT / "packs" / "ai-ops"), "--out", str(out), "--no-test"]) == 0
    sys.path.insert(0, str(out))
    try:
        server, service = importlib.import_module("app.server"), importlib.import_module("app.service")
        svc = service.Service()
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.handler_for(svc))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        yield httpd.server_address[1], service, svc
        httpd.shutdown()
        httpd.server_close()
    finally:
        sys.path.remove(str(out))
        for module in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
            del sys.modules[module]


def send(port, method, path, body=None, host=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"} if data is not None else {}
    connection.putrequest(method, path, skip_host=True)
    connection.putheader("Host", host or f"127.0.0.1:{port}")
    for key, value in headers.items():
        connection.putheader(key, value)
    if data is not None:
        connection.putheader("Content-Length", str(len(data)))
    connection.endheaders(data)
    response = connection.getresponse()
    value = response.status, json.loads(response.read())
    connection.close()
    return value


def a_record(port, service, title="Checkout 1.4"):
    made = send(port, "POST", "/api/objects/Microservice", {"actor": "ops-agent", "fields": {"name": "payments"}})[1]
    fields = valid_values(service.DATA) | {"target": made["id"]}
    return send(port, "POST", "/api/records", {"title": title, "actor": "ops-agent", "fields": fields})


def test_issue_249_a_rebound_host_name_is_refused_before_anything_is_read_or_written(ai_ops):
    port, _, svc = ai_ops
    for method, path, body in (("GET", "/api/app", None), ("GET", "/api/records", None),
                               ("POST", "/api/objects/Microservice", {"actor": "ops-agent", "fields": {"name": "x"}})):
        assert send(port, method, path, body, host=f"rebound.example:{port}") == (
            403, {"code": "HOST_DENIED", "message": "Loopback host required"})
    assert svc.objects("Microservice") == []
    assert send(port, "GET", "/api/app", host=f"localhost:{port}")[0] == 200


@pytest.mark.parametrize("name", ["title", "actor"])
@pytest.mark.parametrize("value", [None, 42, ["Checkout"], {"x": 1}])
def test_a_value_that_is_not_text_is_refused_not_turned_into_text(ai_ops, name, value):
    """Before: {"title": null} created a record titled "None", and 42 one titled "42"."""
    port, service, svc = ai_ops
    made = send(port, "POST", "/api/objects/Microservice", {"actor": "ops-agent", "fields": {"name": "payments"}})[1]
    body = {"title": "Checkout", "actor": "ops-agent", "fields": valid_values(service.DATA) | {"target": made["id"]}}
    assert send(port, "POST", "/api/records", body | {name: value}) == (
        400, {"code": "BAD_REQUEST", "message": f"{name} must be a string"})
    assert svc.records() == []


def test_a_stale_record_offers_no_action_it_will_refuse(ai_ops):
    """Before: a record of an earlier model offered StartBuild as allowed, and taking it was refused STALE_INSTANCE."""
    port, service, svc = ai_ops
    record = a_record(port, service)[1]
    svc.db.execute("UPDATE records SET model_hash=? WHERE id=?", ("0" * 64, record["id"]))
    options = send(port, "GET", f"/api/records/{record['id']}?actor=ops-agent")[1]["options"]
    assert options and {(o["allowed"], o["code"]) for o in options} == {(False, "STALE_INSTANCE")}
    svc.db.execute("UPDATE records SET data_digest='earlier' WHERE id=?", (record["id"],))
    options = send(port, "GET", f"/api/records/{record['id']}?actor=ops-agent")[1]["options"]
    assert {(o["allowed"], o["code"]) for o in options} == {(False, "STALE_DATA")}  # the order `act` refuses in


def test_a_read_never_sees_a_write_that_rolls_back(ai_ops):
    """Before: reads shared the connection outside the write lock, so a list taken mid-write showed a record that the
    write then rolled back."""
    _, service, svc = ai_ops
    inside, release, seen = threading.Event(), threading.Event(), []

    def work(session):
        svc.db.execute("INSERT INTO records(id,case_id,model_hash,state,version) VALUES('ghost','app','x','Opened',0)")
        inside.set()
        release.wait(2)
        raise service.Refused("ROLLED_BACK", "the write fails after its insert")

    def write():
        with pytest.raises(service.Refused):
            svc._write(work)

    writer = threading.Thread(target=write)
    writer.start()
    inside.wait(2)
    reader = threading.Thread(target=lambda: seen.append([r["id"] for r in svc.records()]))
    reader.start()
    reader.join(0.3)
    release.set()
    writer.join()
    reader.join()
    assert seen == [[]]


def test_an_unforeseen_failure_is_answered_not_dropped(ai_ops, monkeypatch):
    port, _, svc = ai_ops
    monkeypatch.setattr(svc, "records", lambda: 1 / 0)
    assert send(port, "GET", "/api/records") == (500, {"code": "INTERNAL_ERROR", "message": "The app could not answer this request"})


def test_the_readme_counts_the_cases_the_build_reports():
    """Before: README.md counted only the state x action cases (e.g. 120 of 420 for library-loan)."""
    for name in ("library-loan", "ai-ops", "library-fines"):
        pack = load_pack(ROOT / "packs" / name)
        files, manifest = generate(pack, pack.model, data_for(pack))
        oracle = json.loads(files["tests/oracle.json"])
        total = len(oracle["cases"]) + sum(len(oracle.get(k, [])) for k in CASE_KINDS)
        assert manifest["oracle"]["cases"] == total
        assert f"# {total} conformance cases" in files["README.md"]


def test_objects_a_record_refers_to_are_checked_in_the_oracle():
    pack = load_pack(ROOT / "packs" / "ai-ops")
    oracle = json.loads(generate(pack, pack.model, data_for(pack))[0]["tests/oracle.json"])
    cases = {c["name"]: c["expect"] for c in oracle["object_cases"]}
    assert cases["valid"] == {"outcome": "CREATED", "fields": {"name": "Sample", "owner": "Sample"}, "state": "Idle"}
    assert cases["name missing"] == {"outcome": "REFUSED", "code": "FIELD_REQUIRED"}
    assert cases["unknown field"] == {"outcome": "REFUSED", "code": "UNKNOWN_FIELD"}
    plain = load_pack(ROOT / "packs" / "library-loan")
    assert "object_cases" not in json.loads(generate(plain, plain.model, data_for(plain))[0]["tests/oracle.json"])


def test_the_page_lets_a_person_choose_or_add_the_object_a_record_refers_to():
    """Before: a reference field was a bare text box asking for a 32-character id, and the page had no way to make the
    object, so a pack with a required built association could never create a record from its page."""
    source = (ROOT / "src/eija_studio/resources/appgen/react-source")
    page = (source / "main.jsx").read_text(encoding="utf-8")
    controller = (source / "controller.js").read_text(encoding="utf-8")
    assert "function ReferenceField" in page and "Add a {cls}" in page
    assert "/api/objects/${cls}" in controller and "updateRecordField(reference.field, made.id)" in controller


@pytest.mark.browser
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: set EIJA_BROWSER_TESTS=1 for actual browser")
def test_a_person_adds_the_object_and_creates_the_record_in_a_real_browser(ai_ops):
    """The ai-ops page: add a Microservice inside the record form, have it chosen, create the record, and see the
    object's name (not its id) on the record. Before the fix this record could not be created from the page at all."""
    port, _, svc = ai_ops
    browser_api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the demos extra")
    with browser_api.sync_playwright() as playwright:
        executable = os.environ.get("EIJA_CHROMIUM")
        try:
            chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                      else playwright.chromium.launch(channel="chrome", headless=True))
        except browser_api.Error as error:
            pytest.skip(f"NOT_RUN: Chrome unavailable: {str(error).splitlines()[0]}")
        try:
            page = chrome.new_page(viewport={"width": 1280, "height": 1000})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{port}/")
            page.wait_for_selector("#create-button:not([disabled])")
            assert page.eval_on_selector("#field-target", "e => e.tagName") == "SELECT"
            page.fill("#title", "Checkout 1.4")
            page.select_option("#field-service", "checkout")
            page.fill("#field-commitSha", "abc1234")
            page.fill("#field-summary", "Ship it")
            page.click(".add-object summary")
            page.fill("#object-Microservice-name", "payments")
            page.get_by_role("button", name="Add Microservice").click()
            page.wait_for_selector("#object-feedback-Microservice:not([hidden])")
            made = svc.objects("Microservice")
            assert [o["fields"] for o in made] == [{"name": "payments"}] and made[0]["state"] == "Idle"
            assert page.input_value("#field-target") == made[0]["id"]
            page.click("#create-button")
            page.wait_for_selector("#result:not([hidden])")
            assert page.text_content("#result") == "Created in Opened."
            assert svc.records()[0]["fields"]["target"] == made[0]["id"]
            assert f"payments · {made[0]['id'][:8]}" in page.text_content("#detail-fields")
            assert errors == []
        finally:
            chrome.close()
