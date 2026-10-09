"""PlayIDE (ADR-0151): the canvas page and Build & run, which starts only an app whose kernel conformance PASSes."""
from __future__ import annotations

import hashlib
import http.client
import json
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces import play
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

SESSION = "synthetic-play-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


@pytest.fixture
def studio(tmp_path):
    return harness_studio(tmp_path / "workspace")


@pytest.fixture
def client(studio):
    app = create_app(studio, SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"])
    app.state.play.stop()


def test_the_page_may_frame_only_loopback_apps(client):
    page = client.get("/play")
    csp = page.headers["Content-Security-Policy"]
    assert page.status_code == 200 and "PlayIDE" in page.text
    assert "frame-src 'self' http://127.0.0.1:*" in csp and "frame-ancestors 'none'" in csp
    assert "http://127.0.0.1:*" not in client.get("/").headers["Content-Security-Policy"]
    assert client.get("/assets/vendor/maxgraph.min.js").status_code == 200


def test_build_needs_the_session_token(client):
    assert client.post("/api/play/build", json={}, headers={"Origin": HEADERS["Origin"]}).status_code == 401


def test_build_and_run_starts_the_active_model_as_a_live_app(client, studio):
    result = client.post("/api/play/build", json={}, headers=HEADERS).json()
    assert result["conformance"]["status"] == "PASS" and result["cases"] > 0
    with studio.store.transaction() as u:
        assert result["model"] == Workflow.model_validate(u.active()["model"]).semantic_hash
    url = urlsplit(result["url"])
    assert url.hostname == "127.0.0.1"
    connection = http.client.HTTPConnection("127.0.0.1", url.port, timeout=10)
    connection.request("GET", "/api/app")
    described = json.loads(connection.getresponse().read())
    connection.close()
    assert described["model_hash"] == result["model"]
    again = client.post("/api/play/build", json={}, headers=HEADERS).json()
    assert again["url"] == result["url"]  # the same model keeps the same running app


def test_a_failing_app_is_never_started(client, monkeypatch):
    monkeypatch.setattr(play, "build_into", lambda *a, **k: {"oracle": {"cases": 1}, "files": {}, "kernel_source_review": "X",
                                                              "conformance": {"status": "FAIL", "detail": "planted"}})
    result = client.post("/api/play/build", json={}, headers=HEADERS).json()
    assert result["conformance"]["status"] == "FAIL" and result["url"] is None


def test_the_vendored_diagram_engine_is_the_recorded_release():
    web = Path(play.__file__).resolve().parents[1] / "resources" / "web" / "vendor"
    record = json.loads((web / "maxgraph.VENDOR.json").read_text(encoding="utf-8"))
    for name, facts in record["files"].items():
        data = (web / name).read_bytes()
        assert (len(data), hashlib.sha256(data).hexdigest()) == (facts["bytes"], facts["sha256"])
    assert record["license"] == "Apache-2.0" and record["version"] == "0.25.0"


def test_build_refuses_a_model_the_page_no_longer_shows(client, studio):
    with studio.store.transaction() as u:
        shown = u.active()["model"]
    assert client.post("/api/play/build", json={"model": shown}, headers=HEADERS).json()["conformance"]["status"] == "PASS"
    changed = Workflow.model_validate(shown).model_dump(mode="json")
    changed["transitions"] = changed["transitions"][:-1]
    refused = client.post("/api/play/build", json={"model": changed}, headers=HEADERS)
    assert (refused.status_code, refused.json()["code"]) == (409, "MODEL_CHANGED")


def test_simulate_runs_the_shown_model_and_refuses_a_stale_one(client, studio):
    with studio.store.transaction() as u:
        shown = u.active()["model"]
    run = client.post("/api/play/simulate", json={"model": shown, "seed": 2, "steps": 120}, headers=HEADERS).json()
    assert run["format"] == "eija.simulation.v1" and run["steps"] == 120
    assert run["model"] == Workflow.model_validate(shown).semantic_hash
    changed = Workflow.model_validate(shown).model_dump(mode="json")
    changed["transitions"] = changed["transitions"][:-1]
    assert client.post("/api/play/simulate", json={"model": changed}, headers=HEADERS).json()["code"] == "MODEL_CHANGED"
    assert client.post("/api/play/simulate", json={"steps": 0}, headers=HEADERS).status_code == 422


def test_the_class_diagram_reads_the_packs_data_model(client):
    body = client.get("/api/play/data", headers=HEADERS).json()
    assert body["data"]["record"] == "Excursion" and len(body["digest"]) == 64


def test_the_screen_designer_checks_and_builds_edited_screens(client, studio):
    shown = client.post("/api/play/screens", json={}, headers=HEADERS).json()
    assert shown["problems"] == [] and shown["use_cases"][0] is None
    screens = json.loads(json.dumps(shown["screens"]))
    create = next(s for s in screens["screens"] if s["use_case"] is None)
    create["fields"] = create["fields"][1:]  # drop a required attribute: nobody could create a record
    checked = client.post("/api/play/screens", json={"screens": screens}, headers=HEADERS).json()
    assert [p["code"] for p in checked["problems"]] == ["SCREEN_MISSING_REQUIRED"]
    refused = client.post("/api/play/build", json={"screens": screens}, headers=HEADERS)
    assert refused.status_code >= 400 and refused.json()["code"] == "SCREENS_BLOCKED"
    create["fields"] = next(s for s in shown["screens"]["screens"] if s["use_case"] is None)["fields"]
    create["title"] = "Start one"
    built = client.post("/api/play/build", json={"screens": screens}, headers=HEADERS).json()
    assert built["conformance"]["status"] == "PASS" and built["screens"] != shown["digest"]
    foreign = client.post("/api/play/screens", json={"screens": screens | {"id": "elsewhere"}}, headers=HEADERS)
    assert foreign.json()["code"] == "SCREENS_PACK_MISMATCH"


def test_the_component_diagram_is_read_from_the_app_the_model_builds(client):
    diagram = client.post("/api/play/components", json={}, headers=HEADERS).json()
    assert diagram["format"] == "eija.components.v1" and diagram["cases"] > 0
    assert any(d["source"] == "app.service" and d["target"] == "eija_studio.application.runtime" for d in diagram["dependencies"])


def test_plan_mode_proposes_previews_and_tries_but_never_saves(client, studio):
    with studio.store.transaction() as u:
        before = u.active()["model"]
    first = studio.pack.model.states[0]
    proposed = client.post("/api/play/plan", json={"request": f"add state Lost after {first}"}, headers=HEADERS).json()
    assert proposed.get("code") is None, proposed
    roles = client.get("/api/status", headers=HEADERS).json()["pack"]["roles"]
    assert roles == [r.id for r in studio.pack.roles]  # the palette offers the pack's declared roles
    assert proposed["trust"] == "UNTRUSTED_PROPOSAL" and proposed["steps"][0]["transaction"]["kind"] == "add_state"
    steps = [s["transaction"] for s in proposed["steps"]]
    preview = client.post("/api/play/plan/preview", json={"steps": steps, "accepted": [False]}, headers=HEADERS).json()
    assert preview["accepted"] == 0 and preview["candidate"] is None
    refused = client.post("/api/play/plan", json={"request": "make it better"}, headers=HEADERS)
    assert refused.json()["code"] == "PLAN_REQUEST_UNSUPPORTED"
    with studio.store.transaction() as u:
        assert u.active()["model"] == before  # nothing was saved or applied


def test_the_ripple_of_a_plan_reaches_every_diagram_and_saves_nothing(tmp_path):
    studio = harness_studio(tmp_path / "loan", pack=Path(__file__).resolve().parents[1] / "packs" / "library-loan")
    client = TestClient(create_app(studio, SESSION), base_url=HEADERS["Origin"])
    with studio.store.transaction() as u:
        before = u.active()["model"]
    plan = [{"kind": "add_state", "state": "Lost", "after": studio.pack.model.states[-1]}]
    result = client.post("/api/play/ripple", json={"plan": plan}, headers=HEADERS).json()
    assert result.get("code") is None, result
    assert result["format"] == "eija.ripple.v1" and set(result["diagrams"]) == {"states", "classes", "usecases", "screens", "components", "sequences", "system"}
    assert "Adds state Lost" in [i["text"] for i in result["diagrams"]["states"]]
    assert [p["code"] for p in result["problems"]] == ["STATE_UNREACHABLE"]  # nothing leads into the new state yet
    assert result["live"] is False and [s["fixes"] for s in result["follow_ons"]] == ["STATE_UNREACHABLE"]
    assert result["conformance"]["cases_after"] > 0 and result["diagrams"]["classes"]  # the record's state enumeration
    nothing = client.post("/api/play/ripple", json={}, headers=HEADERS).json()
    assert all(items == [] for items in nothing["diagrams"].values()) and nothing["follow_ons"] == []
    with studio.store.transaction() as u:
        assert u.active()["model"] == before


def test_the_run_bar_gets_the_shown_models_run_log_and_stop_ends_the_app(client, studio):
    """ADR-0160: Run, Pause and Step move through a kernel-decided log; Stop ends the running app."""
    assert client.get("/assets/play-run.js").status_code == 200
    with studio.store.transaction() as u:
        shown = u.active()["model"]
    state = studio.pack.model.states[1]
    log = client.post("/api/play/run", json={"model": shown, "steps": 80, "breakpoints": ["state:" + state],
                                              "break_on_refusal": True}, headers=HEADERS).json()
    assert log["format"] == "eija.run.v1" and len(log["trace"]) == 80 and log["stops"]
    assert log["model"] == Workflow.model_validate(shown).semantic_hash
    refused = client.post("/api/play/run", json={"breakpoints": ["state:Nowhere"]}, headers=HEADERS)
    assert refused.json()["code"] == "UNKNOWN_BREAKPOINT"
    assert client.post("/api/play/run", json={}, headers={"Origin": HEADERS["Origin"]}).status_code == 401
    assert client.post("/api/play/stop", json={}, headers=HEADERS).json() == {"stopped": False}
    assert client.post("/api/play/build", json={}, headers=HEADERS).json()["url"]
    assert client.post("/api/play/stop", json={}, headers=HEADERS).json() == {"stopped": True}
    assert client.post("/api/play/stop", json={}, headers=HEADERS).json() == {"stopped": False}


def test_laws_are_proved_on_the_shown_model(client, studio):
    """The Laws tab (ADR-0166): every law of the pack with its verdict, on the model on screen."""
    assert client.post("/api/play/laws", json={}, headers={"Origin": HEADERS["Origin"]}).status_code == 401
    report = client.post("/api/play/laws", json={}, headers=HEADERS).json()
    assert report["format"] == "eija.law-proof.v1" and report["status"] == "HOLDS"
    assert [law["id"] for law in report["laws"]] == [law.id for law in studio.pack.laws]
    assert report["search"]["status"] == "COMPLETE"
    assert "/assets/play-laws.js" in client.get("/play").text and client.get("/assets/play-laws.js").status_code == 200
@pytest.fixture
def loan_client(tmp_path):
    studio = harness_studio(tmp_path / "loan", pack=load_pack(Path(__file__).resolve().parents[1] / "packs" / "library-loan"))
    app = create_app(studio, SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"]), studio
    app.state.play.stop()


def test_review_compares_the_shown_change_with_the_model_in_force_and_saves_nothing(loan_client):
    client, studio = loan_client
    with studio.store.transaction() as u:
        before = u.active()["model"]
    request = "add Renew from Overdue to OnLoan for Librarian then remove transition ReturnLate"
    steps = [s["transaction"] for s in client.post("/api/play/plan", json={"request": request}, headers=HEADERS).json()["steps"]]
    review = client.post("/api/play/review", json={"plan": steps}, headers=HEADERS).json()
    assert review.get("code") is None, review
    assert review["changed"] and review["before"] == Workflow.model_validate(before).semantic_hash
    assert [(i["risk"], i["change"]) for i in review["items"]] == [("high", "removed"), ("medium", "added")]
    nothing = client.post("/api/play/review", json={}, headers=HEADERS).json()
    assert not nothing["changed"] and nothing["items"] == []
    assert client.post("/api/play/review", json={"plan": steps}, headers={"Origin": HEADERS["Origin"]}).status_code == 401
    stale = client.post("/api/play/review", json={"plan": steps, "model": review["after_model"]}, headers=HEADERS).json()
    assert stale["code"] == "MODEL_CHANGED"  # a page showing another base model is told to reload
    with studio.store.transaction() as u:
        assert u.active()["model"] == before  # a review saves, approves and applies nothing
