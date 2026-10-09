"""The deployment diagram (#143, ADR-0206): where a built app runs, read from its generated files. Each fact comes from
the files, so changing a file changes the diagram; a file that is missing leaves its part out."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio import __version__
from eija_studio.application.deployment import app_deployment
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces.app_build import app_files
from eija_studio.interfaces.http import create_app
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
SESSION = "synthetic-deployment-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


def built() -> dict[str, str]:
    pack = load_pack(PACKS_ROOT / "library-loan")
    return app_files(pack, pack.model)[0]


def nodes(report) -> dict[str, dict]:
    return {n["id"]: n for n in report["nodes"]}


def test_the_built_app_runs_as_a_browser_a_python_process_and_a_database_file():
    report = app_deployment(built(), "9.9.9")
    found = nodes(report)
    assert list(found) == ["node:browser", "node:process", "node:database"]
    process = found["node:process"]
    assert process["address"] == "127.0.0.1:8000" and process["set_by"] == ["--port", "PORT"]
    assert [a["name"] for a in process["artifacts"]] == ["run.py", "app (generated package)", "model files", "eija_studio 9.9.9 (installed)"]
    assert "app/model.json" in process["artifacts"][2]["files"] and "app/server.py" in process["artifacts"][1]["files"]
    assert found["node:database"]["address"] == "data/app.sqlite3" and found["node:database"]["set_by"] == ["--data"]
    assert found["node:browser"]["artifacts"][0]["files"] == ["app/web/app.css", "app/web/app.js", "app/web/index.html"]


def test_the_paths_are_the_routes_the_page_calls_and_the_sqlite3_connection():
    paths = app_deployment(built(), "0")["paths"]
    assert paths[0] == {"source": "node:browser", "target": "node:process", "protocol": "HTTP", "names": ["/api/app", "/api/outbox", "/api/records"]}
    assert paths[1]["protocol"] == "sqlite3" and paths[1]["target"] == "node:database"


def test_the_diagram_follows_the_files_not_a_description():
    files = built()
    files["run.py"] = files["run.py"].replace('"8000"', '"9123"').replace('"app.sqlite3"', '"loans.db"')
    files["app/server.py"] = files["app/server.py"].replace('ThreadingHTTPServer(("127.0.0.1"', 'ThreadingHTTPServer(("0.0.0.0"')
    found = nodes(app_deployment(files, "0"))
    assert found["node:process"]["address"] == "0.0.0.0:9123"
    assert found["node:database"]["name"] == "loans.db" and found["node:database"]["address"] == "data/loans.db"


def test_without_sqlite3_or_a_page_those_parts_are_not_drawn():
    files = {p: t for p, t in built().items() if not p.startswith("app/web/")}
    files = {p: t.replace("import sqlite3", "import json") for p, t in files.items()}
    report = app_deployment(files, "0")
    assert list(nodes(report)) == ["node:process"] and report["paths"] == []


@pytest.fixture
def client(tmp_path):
    app = create_app(harness_studio(tmp_path / "workspace", pack=PACKS_ROOT / "library-loan"), SESSION)
    yield TestClient(app, base_url=HEADERS["Origin"])
    app.state.play.stop()


def test_the_components_route_carries_the_deployment_with_the_installed_kernel(client):
    response = client.post("/api/play/components", json={}, headers=HEADERS)
    assert response.status_code == 200, response.text
    deployment = response.json()["deployment"]
    assert deployment["format"] == "eija.deployment.v1"
    assert f"eija_studio {__version__} (installed)" in [a["name"] for a in deployment["nodes"][1]["artifacts"]]


def test_the_page_loads_the_deployment_lens_after_play_js(client):
    page = client.get("/play").text
    assert page.index("/assets/play.js") < page.index("/assets/play-deployment.js") and 'data-lens="deployment"' in page
    assert client.get("/assets/play-deployment.js").status_code == 200
    source = (ROOT / "src/eija_studio/resources/web/play-deployment.js").read_text(encoding="utf-8")
    assert "fetch(" not in source  # it asks the server through the page's api(); the server decides
