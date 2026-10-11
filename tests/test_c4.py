"""C4 structural relationships are extracted; model and design claims stay separate."""
from __future__ import annotations

from pathlib import Path
import json
import shutil

from fastapi.testclient import TestClient
from kernel_support import harness_studio

from eija_studio.application.build_subject import SUBJECT_FILE, build_subject
from eija_studio.application.c4 import app_c4
from eija_studio.application.components import app_components
from eija_studio.bootstrap import source_identity
from eija_studio.domain.data import data_for
from eija_studio.domain.models import Workflow, canonical
from eija_studio.domain.pack import load_pack
from eija_studio.domain.screens import screens_for
from eija_studio.interfaces.app_build import app_files
from eija_studio.interfaces.c4 import register
from eija_studio.interfaces.http import create_app

ROOT = Path(__file__).resolve().parents[1]


def projected(name: str = "library-loan") -> tuple[dict, dict[str, str]]:
    pack = load_pack(ROOT / "packs" / name)
    data = data_for(pack)
    screens = screens_for(pack, pack.model, data)
    files, _ = app_files(pack, pack.model, screens, identity_provider=source_identity)
    return app_c4(files), files


def test_context_contracts_and_three_real_containers():
    result, _ = projected()
    containers = result["levels"]["containers"]
    assert {n["id"] for n in containers["nodes"]} == {"node:browser", "node:process", "node:database"}
    assert {(r["source"], r["target"], r["mechanism"]) for r in containers["relationships"]} == {
        ("node:browser", "node:process", "HTTP"), ("node:process", "node:database", "sqlite3")}
    context = result["levels"]["context"]
    actors = [n for n in context["nodes"] if n["id"].startswith("actor:")]
    assert actors and all(n["support"] == "fixture_contract" for n in actors)
    assert all(n["details"]["authentication"] == "UNSUPPORTED" for n in actors)
    assert result["observation"] == {"runtime": "NOT_OBSERVED", "deployment": "UNSUPPORTED", "policy_change": False}


def test_every_component_relationship_is_an_existing_extracted_dependency():
    result, files = projected()
    actual = {(d["source"], d["target"], ", ".join(d["names"]) or "imports")
              for d in app_components(files)["dependencies"]}
    view = result["levels"]["components"]
    ids = {node["id"] for node in view["nodes"]}
    assert "app/web" not in ids  # browser is a different container, not inside the server
    for relation in view["relationships"]:
        assert (relation["source"], relation["target"], relation["label"]) in actual
        assert relation["source"] in ids and relation["target"] in ids and relation["sources"]
    assert any(r["target"] == "eija_studio.application.runtime" for r in view["relationships"])


def test_removed_import_does_not_survive_as_a_c4_dependency_or_database_container():
    pack = load_pack(ROOT / "packs/library-loan")
    data = data_for(pack)
    screens = screens_for(pack, pack.model, data)
    files, _ = app_files(pack, pack.model, screens, identity_provider=source_identity)
    for path, text in list(files.items()):
        files[path] = text.replace("import sqlite3\n", "")
    previous = json.loads(files[SUBJECT_FILE])
    # This is an explicitly generated negative-control subject, not amended production evidence.
    files[SUBJECT_FILE] = canonical(build_subject(files, implementation_digest=previous["implementation_digest"],
                                                 template_paths=previous["template_paths"]))
    result = app_c4(files)
    assert "node:database" not in {n["id"] for n in result["levels"]["containers"]["nodes"]}
    assert not any(r["target"] == "sqlite3" for r in result["levels"]["components"]["relationships"])


def test_model_edit_changes_identity_actor_contract_and_generated_file_subject():
    pack = load_pack(ROOT / "packs/library-loan")
    old, _ = projected()
    document = pack.model.model_dump(mode="json")
    changed = document["transitions"][0]
    changed["to_state"] = changed["from_state"]
    candidate = Workflow.model_validate(document)
    data = data_for(pack)
    screens = screens_for(pack, candidate, data)
    files, _ = app_files(pack, candidate, screens, identity_provider=source_identity)
    result = app_c4(files)
    assert result["subject"]["model_hash"] == candidate.semantic_hash != old["subject"]["model_hash"]
    assert result["subject"]["generated_files_hash"] != old["subject"]["generated_files_hash"]
    system = next(n for n in result["levels"]["context"]["nodes"] if n["kind"] == "software_system")
    assert next(t for t in system["details"]["actions"] if t["id"] == changed["id"])["to_state"] == changed["from_state"]


def test_data_and_effects_do_not_acquire_external_execution():
    result, _ = projected()
    assert result["data_support"]["drawn_only"]
    assert result["data_support"]["associations"]
    assert all(e["delivery"] in {"LOCAL_OUTBOX_ONLY", "LOCAL_AUDIT_ONLY"} for e in result["effects"])
    assert any("external delivery" in text for text in result["limits"])
    result["limits"].clear()
    assert projected()[0]["limits"]  # caller mutation cannot alter later scope


def test_pack_without_data_has_no_invented_data_component():
    result, _ = projected("eija-review-slice")
    assert result["subject"]["data_digest"] is None and result["data_support"] is None
    assert "app/data.json" not in {n["id"] for n in result["levels"]["components"]["nodes"]}


def test_readonly_route_preserves_auth_origin_strict_input_and_active_model(studio):
    app = create_app(studio, "c4-test", port=8765)
    if not any(route.path == "/api/play/c4" for route in app.routes):
        register(app, studio, lambda _body: Workflow.model_validate(studio.workbench()["model"]),
                 lambda _plan: studio.pack,
                 lambda _body, model: screens_for(studio.pack, model, data_for(studio.pack)))
    client = TestClient(app, base_url="http://127.0.0.1:8765")
    headers = {"Authorization": "Bearer c4-test", "Origin": "http://127.0.0.1:8765"}
    before = studio.workbench()["model"]
    assert client.post("/api/play/c4", json={}).status_code == 401
    assert client.post("/api/play/c4", json={}, headers={"Authorization": "Bearer c4-test"}).status_code == 403
    result = client.post("/api/play/c4", json={}, headers=headers)
    assert result.status_code == 200
    assert result.json()["generation"]["conformance"] == "NOT_RUN"
    assert result.json()["subject"]["model_hash"] == Workflow.model_validate(before).semantic_hash
    assert client.post("/api/play/c4", json={"approved": True}, headers=headers).status_code == 422
    assert studio.workbench()["model"] == before


def test_competing_activation_cannot_attach_new_revision_to_old_structure(studio, monkeypatch):
    app = create_app(studio, "c4-race", port=8765)
    if not any(route.path == "/api/play/c4" for route in app.routes):
        register(app, studio, lambda _body: Workflow.model_validate(studio.workbench()["model"]),
                 lambda _plan: studio.pack,
                 lambda _body, model: screens_for(studio.pack, model, data_for(studio.pack)))
    original = studio.workbench
    reads = 0

    def moved_revision():
        nonlocal reads
        reads += 1
        snapshot = original()
        if reads >= 2:
            snapshot["baseline_version"] += 1
        return snapshot

    monkeypatch.setattr(studio, "workbench", moved_revision)
    client = TestClient(app, base_url="http://127.0.0.1:8765")
    response = client.post("/api/play/c4", json={}, headers={"Authorization": "Bearer c4-race", "Origin": "http://127.0.0.1:8765"})
    assert response.status_code == 409 and response.json()["code"] == "MODEL_CHANGED"


def test_data_file_changed_after_generation_cannot_relabel_the_snapshot(tmp_path, monkeypatch):
    """The optional data file is outside pack identity; C4 must use the generated bytes."""
    directory = tmp_path / "library"
    shutil.copytree(ROOT / "packs/library-loan", directory)
    pack = load_pack(directory)
    studio = harness_studio(tmp_path / "workspace", pack=pack)
    original_data = data_for(pack)
    changed = original_data.model_dump(mode="json")
    changed["entities"][0]["description"] = "Changed while architecture was being generated"
    generated_subject = {}

    def concurrent_data_edit(*args, **kwargs):
        files, manifest = app_files(*args, **kwargs)
        generated_subject.update(manifest["subject"])
        (directory / "data.json").write_text(canonical(changed), encoding="utf-8")
        return files, manifest

    monkeypatch.setattr("eija_studio.interfaces.c4.app_files", concurrent_data_edit)
    client = TestClient(create_app(studio, "c4-data-race", port=8765), base_url="http://127.0.0.1:8765")
    response = client.post("/api/play/c4", json={}, headers={"Authorization": "Bearer c4-data-race",
                                                            "Origin": "http://127.0.0.1:8765"})
    assert response.status_code == 200
    report = response.json()
    assert data_for(pack).digest != original_data.digest
    assert report["subject"] == generated_subject
    assert report["subject"]["data_digest"] == original_data.digest
