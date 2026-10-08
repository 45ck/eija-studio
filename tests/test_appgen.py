"""`eija build` (ADR-0150): the generated app commits and refuses exactly where the kernel does, and says so honestly."""
from __future__ import annotations

import http.client
import importlib
import json
import sys
import threading
from hashlib import sha256
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from eija_studio.application.appgen import UNDECLARED_ACTION, UNKNOWN_ACTOR, absent, generate, oracle_cases
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.app_build import conformance
from eija_studio.interfaces.cli import main

ROOT = Path(__file__).resolve().parents[1]
PACKS = ("excursion", "library-loan", "eija-review-slice")
EXCURSION = load_pack(ROOT / "packs" / "excursion")


def build(tmp_path: Path, pack: str, *extra: str) -> tuple[int, Path]:
    out = tmp_path / pack
    return main(["build", "--pack", str(ROOT / "packs" / pack), "--out", str(out), *extra]), out


def case(cases, **key):
    return next(c for c in cases if all(c[k] == v for k, v in key.items()))


def test_generation_is_deterministic():
    assert generate(EXCURSION) == generate(EXCURSION)


def test_the_oracle_is_the_kernel_answering_each_case():
    cases = oracle_cases(EXCURSION, EXCURSION.model)
    approve = case(cases, state="Submitted", action="Approve", actor="registrar", expected_version=0)
    assert approve["expect"] == {"outcome": "COMMITTED", "state": "Approved", "effects": ["Audit:ExcursionApproved"]}
    assert approve["replay"] == {"outcome": "DUPLICATE", "state": "Approved"}
    expected = {("teacher-assigned", "Approve", 0): "ROLE_DENIED", ("teacher-revoked", "Submit", 0): "ACTOR_REVOKED",
                (UNKNOWN_ACTOR, "Submit", 0): "UNKNOWN_ACTOR", ("registrar", UNDECLARED_ACTION, 0): "ACTION_DENIED",
                ("registrar", "Approve", 1): "STALE_VERSION"}
    for (actor, action, version), code in expected.items():
        found = case(cases, state="Submitted", action=action, actor=actor, expected_version=version)
        assert found["expect"] == {"outcome": "REFUSED", "code": code}
    assert case(cases, state="Draft", action="Approve", actor="registrar", expected_version=0)["expect"]["code"] == "STATE_DENIED"


def test_negative_sentinels_never_collide_with_declared_names():
    assert absent("UndeclaredAction", {"UndeclaredAction", "UndeclaredAction1"}) == "UndeclaredAction2"
    assert absent(UNKNOWN_ACTOR, {"registrar"}) == UNKNOWN_ACTOR


def test_a_workflow_from_another_pack_is_refused():
    other = load_pack(ROOT / "packs" / "library-loan").model
    with pytest.raises(DomainError) as refused:
        generate(EXCURSION, other)
    assert refused.value.code == "WORKFLOW_PACK_MISMATCH"


def test_a_workflow_the_policy_refuses_is_never_built():
    unsafe = Workflow.model_validate_json((ROOT / "examples" / "unsafe-teacher-final-approval.json").read_text(encoding="utf-8"))
    with pytest.raises(DomainError) as refused:
        generate(EXCURSION, unsafe)
    assert refused.value.code == "POLICY_BLOCKED"


@pytest.mark.parametrize("pack", PACKS)
def test_every_pack_builds_an_app_that_passes_its_kernel_conformance(tmp_path, pack):
    code, out = build(tmp_path, pack)
    manifest = json.loads((out / "BUILD.json").read_text(encoding="utf-8"))
    assert code == 0 and manifest["conformance"]["status"] == "PASS", manifest["conformance"]
    assert manifest["oracle"]["cases"] > 0 and manifest["kernel_source_review"] in ("RELEASE_FIXTURE_MATCH", "SOURCE_REVIEW_REQUIRED")
    for relative, digest in manifest["files"].items():
        assert sha256((out / relative).read_bytes()).hexdigest() == digest


MUTANTS = {  # negative controls: each breaks the app's storage or its built-in model; the conformance run must catch it
    "operation not recorded": ("excursion", "app/service.py",
                               'self.db.execute("INSERT INTO operations VALUES(?,?,?)", (operation_id, binding, canonical(result)))',
                               "return None"),
    "audit effect not written": ("excursion", "app/service.py",
                                 'self.db.execute("INSERT INTO audit(kind, body) VALUES(?,?)", (kind, canonical(body)))',
                                 "return None"),
    "notification not queued": ("library-loan", "app/service.py",
                                'self.db.execute("INSERT INTO outbox VALUES(?,?,?,?)", (operation_id + ":" + effect, case_id, effect, recipient))',
                                "return None"),
    "approval handed to teachers": ("excursion", "app/model.json", '"role":"Registrar"', '"role":"Teacher"'),
    "unassigned actor treated as assigned": ("library-loan", "app/pack.json", '"assigned":false', '"assigned":true'),
}


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_conformance_catches_a_broken_app(tmp_path, name):
    pack, relative, before, after = MUTANTS[name]
    code, out = build(tmp_path, pack, "--no-test")
    target = out / relative
    text = target.read_text(encoding="utf-8")
    assert code == 0 and before in text
    target.write_text(text.replace(before, after), encoding="utf-8")
    assert conformance(out)["status"] == "FAIL"


def test_build_never_overwrites_a_directory_it_did_not_write(tmp_path):
    out = tmp_path / "excursion"
    out.mkdir()
    (out / "notes.txt").write_text("mine", encoding="utf-8")
    assert build(tmp_path, "excursion", "--no-test")[0] == 2
    assert (out / "notes.txt").read_text(encoding="utf-8") == "mine" and not (out / "BUILD.json").exists()


def test_a_fake_manifest_does_not_make_a_directory_ours(tmp_path):
    out = tmp_path / "excursion"
    (out / "app").mkdir(parents=True)
    (out / "app" / "notes.py").write_text("mine", encoding="utf-8")
    (out / "BUILD.json").write_text(json.dumps({"format": "eija.app-build.v1", "files": {"README.md": "x"}}), encoding="utf-8")
    assert build(tmp_path, "excursion", "--no-test")[0] == 2
    assert (out / "app" / "notes.py").read_text(encoding="utf-8") == "mine"


def test_rebuild_replaces_generated_files_and_keeps_data(tmp_path):
    _, out = build(tmp_path, "excursion", "--no-test")
    (out / "data").mkdir()
    (out / "data" / "app.sqlite3").write_bytes(b"records")
    (out / "app" / "service.py").write_text("broken", encoding="utf-8")
    code, out = build(tmp_path, "excursion")
    assert code == 0 and (out / "data" / "app.sqlite3").read_bytes() == b"records"
    assert json.loads((out / "BUILD.json").read_text(encoding="utf-8"))["conformance"]["status"] == "PASS"


@pytest.fixture
def running_app(tmp_path):
    _, out = build(tmp_path, "excursion", "--no-test")
    sys.path.insert(0, str(out))
    try:
        server_module, service_module = importlib.import_module("app.server"), importlib.import_module("app.service")
        server = ThreadingHTTPServer(("127.0.0.1", 0), server_module.handler_for(service_module.Service()))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        yield server.server_address[1]
        server.shutdown()
        server.server_close()
    finally:
        sys.path.remove(str(out))
        for module in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
            del sys.modules[module]


def call(port, path, body=None, kind="application/json"):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    data = body if isinstance(body, bytes) else None if body is None else json.dumps(body).encode()
    connection.request("GET" if data is None else "POST", path, body=data, headers={"Content-Type": kind} if data else {})
    response = connection.getresponse()
    value = (response.status, json.loads(response.read()), response.headers)
    connection.close()
    return value


def test_the_running_app_enforces_the_model_over_http(running_app):
    status, record, headers = call(running_app, "/api/records", {"title": "Museum trip", "actor": "teacher-assigned"})
    assert status == 201 and record["state"] == "Draft" and "default-src 'self'" in headers["Content-Security-Policy"]
    act = f"/api/records/{record['id']}/act"
    status, refused, _ = call(running_app, act, {"action": "Submit", "actor": "registrar", "expected_version": 0, "operation_id": "a"})
    assert (status, refused["code"]) == (403, "ROLE_DENIED")
    status, done, _ = call(running_app, act, {"action": "Submit", "actor": "teacher-assigned", "expected_version": 0, "operation_id": "b"})
    assert status == 200 and done["record"]["state"] == "Submitted"
    status, stale, _ = call(running_app, act, {"action": "Approve", "actor": "registrar", "expected_version": 0, "operation_id": "c"})
    assert (status, stale["code"]) == (409, "STALE_VERSION")
    status, view, _ = call(running_app, f"/api/records/{record['id']}?actor=registrar")
    assert [o["action"] for o in view["options"] if o["allowed"]] == ["Approve", "Reject"]
    assert [(h["effect"], h["actor"], h["state"]) for h in view["history"]] == [("Audit:ExcursionSubmitted", "teacher-assigned", "Submitted")]


def test_the_app_refuses_non_json_posts(running_app):
    status, refused, _ = call(running_app, "/api/records", b"title=x&actor=teacher-assigned", "application/x-www-form-urlencoded")
    assert (status, refused["code"]) == (400, "BAD_REQUEST")
