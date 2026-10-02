"""Pack and connection wiring, plus non-mutating agent checks. No owner decisions or live providers."""
from __future__ import annotations

import json
import tomllib

import pytest
from fastapi.testclient import TestClient

from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces import cli
from eija_studio.interfaces.http import create_app


HEADERS = {"Authorization": "Bearer synthetic-test-session"}


@pytest.mark.parametrize("name", ("excursion", "library-loan"))
def test_workbench_is_authenticated_and_derived_from_the_active_pack(tmp_path, name):
    pack = load_pack(PACKS_ROOT / name)
    studio = build_studio(tmp_path / name, pack=pack)
    before = studio.store.list_cases()
    with TestClient(create_app(studio, "synthetic-test-session"), base_url="http://127.0.0.1:8765") as client:
        assert client.get("/api/workbench").status_code == 401
        response = client.get("/api/workbench", headers=HEADERS)
        assert response.status_code == 200
        result = response.json()
        assert result["pack"] == {"id": pack.id, "name": pack.pack.name, "version": pack.pack.version, "digest": pack.digest}
        assert result["model"] == pack.model.model_dump(mode="json")
        assert result["language"] == pack.language.model_dump(mode="json")
        assert result["laws"] == [law.model_dump(mode="json") for law in pack.laws]
        assert result["roles"] == [role.model_dump(mode="json") for role in pack.roles]
        assert result["connection"] is None
        assert result["source_review_required"] is (not studio.identity_provider()["trusted_fixture"])
        assert response.headers["cache-control"] == "no-store"
    assert studio.store.list_cases() == before


def test_repository_metadata_stays_separate_and_impact_has_no_path_input(studio):
    class ReadOnlyRepository:
        def snapshot(self):
            return {"status": "connected", "coverage": {"complete": False}, "gaps": ["dynamic calls"]}

        def impact(self, subject):
            return {"status": "ok", "subject": subject, "complete": False}

    studio.repository = ReadOnlyRepository()
    with TestClient(create_app(studio, "synthetic-test-session"), base_url="http://127.0.0.1:8765") as client:
        assert client.get("/api/repository/impact", params={"term": "approval"}).status_code == 401
        context = client.get("/api/workbench", headers=HEADERS).json()
        assert context["connection"]["gaps"] == ["dynamic calls"]
        assert context["model"]["id"] == studio.pack.id
        result = client.get("/api/repository/impact", params={"term": "approval"}, headers=HEADERS).json()
        assert result == {"status": "ok", "subject": "approval", "complete": False}
        assert client.get("/api/repository/impact", params={"term": ""}, headers=HEADERS).status_code == 422


def test_unconfigured_repository_does_not_claim_inspection(studio):
    assert studio.repository_impact("approval")["status"] == "unconfigured"


def test_compile_uses_explicit_pack_for_policy_impact_and_metadata(tmp_path, capsys):
    pack = load_pack(PACKS_ROOT / "library-loan")
    workflow = tmp_path / "workflow.json"
    workflow.write_text(pack.model.model_dump_json(), encoding="utf-8")
    result = cli.main(["compile", str(workflow), "--pack", str(PACKS_ROOT / "library-loan"),
                       "--workspace", str(tmp_path / "workspace"), "--out", str(tmp_path / "compiled"), "--no-formal"])
    capsys.readouterr()
    compiled = json.loads((tmp_path / "compiled" / "compiled.json").read_text(encoding="utf-8"))
    assert compiled["pack"]["id"] == pack.id and compiled["pack"]["digest"] == pack.digest
    assert compiled["policy_errors"] == [] and compiled["impact"]["changed_actions"] == []
    assert result == (2 if compiled["source_review_required"] else 0)
    assert "receipt" not in compiled


def test_render_compares_to_explicit_pack_and_creates_no_workspace(tmp_path, capsys):
    pack = load_pack(PACKS_ROOT / "library-loan")
    workflow, rendered, workspace = tmp_path / "workflow.json", tmp_path / "diagram.mmd", tmp_path / "workspace"
    workflow.write_text(pack.model.model_dump_json(), encoding="utf-8")
    assert cli.main(["render", "--workflow", str(workflow), "--pack", str(PACKS_ROOT / "library-loan"),
                     "--workspace", str(workspace), "--view", "diff", "--out", str(rendered)]) == 0
    capsys.readouterr()
    diagram = rendered.read_text(encoding="utf-8")
    assert pack.model.semantic_hash in diagram
    assert "workflow excursion" not in diagram and not workspace.exists()


def test_printed_mcp_config_retains_pack_and_repository_without_access(tmp_path, capsys):
    workspace, pack, repository = (tmp_path / name for name in ("workspace", "declared pack", "repository"))
    assert cli.main(["mcp", "--workspace", str(workspace), "--pack", str(pack), "--repo", str(repository),
                     "--print-config", "codex"]) == 0
    args = tomllib.loads(capsys.readouterr().out)["mcp_servers"]["eija"]["args"]
    assert args[-4:] == ["--pack", str(pack.resolve()), "--repo", str(repository.resolve())]
    assert not any(path.exists() for path in (workspace, pack, repository))


def test_mcp_renderer_uses_existing_generators_and_rejects_unavailable_svg():
    model = load_pack(PACKS_ROOT / "library-loan").model
    for view, marker in (("rules", "stateDiagram"), ("states", "stateDiagram"), ("journeys", "flowchart")):
        assert marker in cli._agent_diagram(model, view, "mermaid")
    with pytest.raises(DomainError) as refused:
        cli._agent_diagram(model, "states", "svg")
    assert refused.value.code == "FORMAT_UNSUPPORTED"


def test_mcp_checks_preserve_case_and_refusal_details(studio):
    pytest.importorskip("mcp")
    from eija_studio.interfaces.mcp_server import AgentSurface, StudioAgentPort  # noqa: PLC0415 - optional SDK

    case = studio.create(studio.pack.fixtures.demo_request)
    surface = AgentSurface(StudioAgentPort(studio))
    choices = surface.affordances(case["id"])["affordances"]
    # The catalogue is a list of independently dry-run transactions from the real kernel.
    refused = next(choice for choice in choices if not choice["legal"])
    checked = surface.edit_check(case["id"], refused["transaction"])
    assert checked["legal"] is False and checked["codes"] == refused["codes"] and checked["refs"] == refused["refs"]
    assert checked["applied"] is False and checked["persisted"] is False
    assert surface.pack()["pack"]["id"] == studio.pack.id
    assert studio.view(case["id"])["case"] == case
    with pytest.raises(DomainError) as malformed:
        surface.edit_check(case["id"], {"kind": "set_role", "approve": True})
    assert malformed.value.code == "EDIT_INVALID"
    assert malformed.value.details == {"codes": ["EDIT_INVALID"], "refs": []}
