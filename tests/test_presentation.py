"""The app-map is bound design; identities and cards never decide authority."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from kernel_support import harness_studio

from eija_studio.adapters.providers.process import resolve_command, run_bounded
from eija_studio.application.build_subject import SUBJECT_FILE, build_subject
from eija_studio.application.presentation import app_presentation
from eija_studio.bootstrap import source_identity
from eija_studio.domain.models import DomainError, ExecuteCommand, OWNER, Workflow, canonical
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.app_build import app_files
from eija_studio.interfaces.http import create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def files():
    pack = load_pack(ROOT / "packs/library-loan")
    return app_files(pack, pack.model, identity_provider=source_identity)[0]


def revised(files, path, change):
    """A deliberately distinct test build, not a restamped production receipt."""
    replaced = dict(files)
    document = json.loads(replaced[path])
    change(document)
    replaced[path] = canonical(document) + "\n"
    old = json.loads(replaced[SUBJECT_FILE])
    replaced[SUBJECT_FILE] = canonical(build_subject(replaced, implementation_digest=old["implementation_digest"],
                                                   template_paths=old["template_paths"]))
    return replaced


def test_projection_maps_exact_declared_fields_order_and_action_consequences(files):
    report = app_presentation(files)
    assert report["support"] == "CHECKED_DESIGN" and report["subject"] == json.loads(files[SUBJECT_FILE])
    assert report["observation"] == {"runtime": "NOT_OBSERVED", "rendered_ui": "NOT_OBSERVED", "policy_change": False}
    assert report["create"]["title"] == "Request a loan"
    assert [(f["attribute"], f["label"], f["type"], f["editable"]) for f in report["create"]["fields"]] == [
        ("itemTitle", "Title", "text", True), ("format", "Format", "choice", True),
        ("memberCard", "Member card", "text", True), ("dueDate", "Due back", "date", True)]
    checkout = next(a for a in report["actions"] if a["use_case"] == "CheckOut")
    assert checkout["use_case_ref"] == "transition:TR-CHECKOUT" and checkout["class_ref"] == "class:Loan"
    assert checkout["authority"]["from_state"] == "Requested" and checkout["authority"]["to_state"] == "OnLoan"
    assert checkout["authority"]["role"] == "Librarian"
    assert checkout["fields"] and all(not field["editable"] for field in checkout["fields"])
    assert {node["id"] for node in report["navigation"]["destinations"]} == {
        "records", "new-record", "record-detail", *(a["id"] for a in report["actions"])}
    assert not any("/" in node["id"] for node in report["navigation"]["destinations"])  # actual panels, no invented URLs


@pytest.mark.parametrize("change,code", [
    (lambda d: d["screens"][1]["fields"].append({"attribute": "missing", "label": "Ghost"}), "SCREEN_UNKNOWN_ATTRIBUTE"),
    (lambda d: d["screens"][1].update(use_case="InventedAction"), "SCREEN_UNKNOWN_USE_CASE"),
])
def test_even_a_distinct_valid_subject_cannot_make_unknown_fields_or_actions_design(files, change, code):
    candidate = revised(files, "app/screens.json", change)
    with pytest.raises(DomainError) as refused:
        app_presentation(candidate)
    assert refused.value.code == "SCREENS_BLOCKED" and code in refused.value.details["codes"]


@pytest.mark.parametrize("path,change,dimension", [
    ("app/screens.json", lambda d: d["screens"][0]["fields"][0].update(label="Book name"), "screens_digest"),
    ("app/screens.json", lambda d: d["screens"][0]["fields"].reverse(), "screens_digest"),
    ("app/data.json", lambda d: d["entities"][0]["attributes"][0].update(type="number"), "data_digest"),
])
def test_label_order_or_type_changes_bind_a_new_subject_and_visible_projection(files, path, change, dimension):
    old = app_presentation(files)
    new = app_presentation(revised(files, path, change))
    assert new["subject"]["model_hash"] == old["subject"]["model_hash"]
    assert new["subject"][dimension] != old["subject"][dimension] and new["subject"]["digest"] != old["subject"]["digest"]
    assert new["create"]["fields"] != old["create"]["fields"]


def test_missing_foreign_or_substituted_subject_is_refused(files):
    absent = {name: text for name, text in files.items() if name != SUBJECT_FILE}
    foreign = dict(files)
    other = load_pack(ROOT / "packs/excursion")
    foreign[SUBJECT_FILE] = app_files(other, other.model, identity_provider=source_identity)[0][SUBJECT_FILE]
    replaced = dict(files) | {"app/screens.json": files["app/screens.json"].replace("Request a loan", "Borrow a book")}
    for invalid in (absent, foreign, replaced):
        with pytest.raises(DomainError):
            app_presentation(invalid)


def test_snapshot_projection_does_not_reread_the_pack_and_returned_data_cannot_mutate_it(files, monkeypatch):
    expected = app_presentation(files)
    monkeypatch.setattr("eija_studio.domain.data.load_data", lambda *args: pytest.fail("snapshot reread external data"))
    monkeypatch.setattr("eija_studio.domain.screens.load_screens", lambda *args: pytest.fail("snapshot reread external screens"))
    result = app_presentation(files)
    result["create"]["fields"].clear()
    result["limits"].clear()
    assert app_presentation(files) == expected


def test_declared_action_screen_does_not_grant_the_wrong_actor_authority(tmp_path):
    """A real Studio/kernel refusal, independently chosen from an explicit domain requirement."""
    pack = load_pack(ROOT / "packs/excursion")
    studio = harness_studio(tmp_path / "authority", pack=pack)
    case = studio.create(pack.fixtures.demo_request)
    case = studio.propose(case["id"], case["version"])
    case = studio.select(case["id"], case["version"], "recommend_only", OWNER)
    model = Workflow.model_validate(case["candidate"])
    projection = app_presentation(app_files(pack, model, identity_provider=studio.identity_provider)[0])
    approval = next(screen for screen in projection["actions"] if screen["use_case"] == "Approve")
    assert approval["authority"]["role"] == "Registrar" and approval["authority"]["status"] == "SERVICE_CHECKED_AT_ACTION"
    item = studio.reset_preview(case["id"], case["version"], "Recommended")
    with studio.store.transaction() as unit:
        before_effects = unit.effect_counts()
    with pytest.raises(DomainError) as refused:
        studio.execute(case["id"], ExecuteCommand(operation_id="presentation-denied", actor_id="teacher-assigned",
                                                 instance_id=item["id"], action="Approve", expected_version=item["version"]))
    assert refused.value.code == "ROLE_DENIED"
    with studio.store.transaction() as unit:
        assert unit.find_instance(item["id"], case["id"])["version"] == item["version"]
        assert unit.find_operation("presentation-denied") is None
        assert unit.effect_counts() == before_effects


def test_route_is_readonly_authenticated_strict_and_refuses_a_competing_revision(studio, monkeypatch):
    client = TestClient(create_app(studio, "presentation-test", port=8765), base_url="http://127.0.0.1:8765")
    headers = {"Authorization": "Bearer presentation-test", "Origin": "http://127.0.0.1:8765"}
    before = studio.workbench()["model"]
    assert client.post("/api/play/presentation", json={}).status_code == 401
    assert client.post("/api/play/presentation", json={}, headers={"Authorization": "Bearer presentation-test"}).status_code == 403
    assert client.post("/api/play/presentation", json={"approve": True}, headers=headers).status_code == 422
    result = client.post("/api/play/presentation", json={}, headers=headers)
    assert result.status_code == 200 and result.json()["support"] == "CHECKED_DESIGN"
    assert studio.workbench()["model"] == before
    original, reads = studio.workbench, 0

    def moved():
        nonlocal reads
        reads += 1
        snapshot = original()
        if reads >= 2:
            snapshot["baseline_version"] += 1
        return snapshot

    monkeypatch.setattr(studio, "workbench", moved)
    stale = client.post("/api/play/presentation", json={}, headers=headers)
    assert stale.status_code == 409 and stale.json()["code"] == "MODEL_CHANGED"


def test_presentation_assets_are_real_files_with_expected_mime_and_normal_security(studio):
    client = TestClient(create_app(studio, "presentation-assets", port=8765), base_url="http://127.0.0.1:8765")
    page = client.get("/play")
    assert page.status_code == 200
    assert "script-src 'self'" in page.headers["content-security-policy"]
    assert "'unsafe-eval'" not in page.headers["content-security-policy"]
    assert "'unsafe-inline'" not in page.headers["content-security-policy"]
    for name, media_types in (("play-presentation.js", {"text/javascript", "application/javascript"}),
                              ("play-presentation.css", {"text/css"})):
        assert "/assets/" + name in page.text
        response = client.get("/assets/" + name)
        assert response.status_code == 200
        assert response.headers["content-type"].split(";", 1)[0] in media_types
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.text == (ROOT / "src/eija_studio/resources/web" / name).read_text(encoding="utf-8")
    refused = client.get("/assets/play-presentation.js.backup")
    assert refused.status_code == 404 and refused.json()["code"] == "NOT_FOUND"


@pytest.mark.skipif(shutil.which("node") is None, reason="NOT_RUN: Node is not installed")
def test_actual_presentation_receiver_association_and_staleness():
    node = shutil.which("node")
    assert node is not None
    result = run_bounded([*resolve_command(node), "--test", str(ROOT / "tests/web/play-presentation.test.cjs")],
                         cwd=str(ROOT), input=None, env=dict(os.environ), timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.browser
@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("EIJA_BROWSER_TESTS") != "1", reason="NOT_RUN: actual browser; set EIJA_BROWSER_TESTS=1")
def test_actual_app_map_links_declared_screens_and_matches_rendered_react_controls():
    browser_api = pytest.importorskip("playwright.sync_api", reason="NOT_RUN: install the hci extra")
    from demos.lib import ephemeral_eija_server  # noqa: PLC0415 - opt-in browser only

    with ephemeral_eija_server(pack=ROOT / "packs/library-loan") as server, browser_api.sync_playwright() as playwright:
        executable = os.environ.get("EIJA_CHROMIUM")
        chrome = (playwright.chromium.launch(headless=True, executable_path=executable) if executable
                  else playwright.chromium.launch(channel="chrome", headless=True))
        try:
            page = chrome.new_page(viewport={"width": 1600, "height": 1000})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"{server.base_url}/play#{server.token}")
            page.wait_for_selector("body[data-ready=true]", timeout=60_000)
            page.click("#build")
            page.wait_for_function("() => window.PlayIDE.runningBuild() !== null", timeout=180_000)
            page.wait_for_selector("#presentation-panel", state="visible")
            assert not page.locator("#presentation-panel").evaluate("node => node.open")
            with page.expect_response("**/api/play/presentation") as loaded:
                page.click("#presentation-panel>summary")
            report = loaded.value.json()
            assert report["frontend"]["framework"] == "React"
            page.wait_for_function("() => document.getElementById('presentation-status').dataset.match === 'true'")
            page.click('[data-presentation-node="action:TR-CHECKOUT"]')
            assert "Requested → OnLoan · Librarian" in page.locator("#presentation-inspector").inner_text()
            page.get_by_role("button", name="Use case", exact=True).click()
            page.wait_for_function("() => window.PlayIDE.selected() === 'transition:TR-CHECKOUT'")
            assert page.is_visible("#usecase-canvas")
            page.get_by_role("button", name="Record class", exact=True).click()
            page.wait_for_function("() => window.PlayIDE.selected() === 'class:Loan'")
            assert page.is_visible("#class-canvas")
            page.get_by_role("button", name="Design screen", exact=True).click()
            assert page.is_visible("#screens")
            assert page.locator('#screen-list button[aria-current="true"]').inner_text().startswith("CheckOut")
            page.click("#tab-states")
            current = page.evaluate("() => window.PlayIDE.runningBuild().subject")
            assert current == report["subject"]
            frame = page.frame_locator("#run-frame")
            frame.locator('html[data-frontend="react"]').wait_for(timeout=60_000)
            assert frame.locator('.app-navigation [data-nav-id="record-detail"]').is_disabled()
            frame.locator('.app-navigation [data-nav-id="new-record"]').click()
            assert frame.locator("#title").evaluate("node => node === document.activeElement")
            assert frame.locator('.app-navigation [data-nav-id="new-record"]').get_attribute("aria-current") == "page"
            assert frame.locator("#create-title").inner_text() == report["create"]["title"]
            assert frame.locator("#create-button").inner_text() == report["create"]["button"]
            assert frame.locator("#fields input, #fields select").evaluate_all("nodes => nodes.map(node => node.id)") == [
                "field-" + field["attribute"] for field in report["create"]["fields"]]
            for field in report["create"]["fields"]:
                control = frame.locator("#field-" + field["attribute"])
                if field["type"] == "choice":
                    assert control.evaluate("node => node.tagName") == "SELECT"
                else:
                    assert control.get_attribute("type") == {"boolean": "checkbox"}.get(field["type"], field["type"])
                role = {"text": "textbox", "number": "spinbutton", "boolean": "checkbox", "choice": "combobox"}.get(field["type"])
                if role:
                    named = frame.locator("#fields").get_by_role(role, name=field["label"], exact=True)
                    assert named.get_attribute("id") == "field-" + field["attribute"]
                else:  # Date inputs have no implicit ARIA role; preserve their exact accessible name.
                    browser_api.expect(control).to_have_accessible_name(field["label"])
                assert control.evaluate("node => [...node.labels].filter(label => label.htmlFor === node.id).length") == 1
                assert control.evaluate("node => node.required") == (field["required"] and field["type"] != "boolean")
            assert errors == []
        finally:
            chrome.close()
