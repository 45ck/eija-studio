"""Read-only source comparison composition and HTTP/MCP contracts, without owner operations."""
from __future__ import annotations

import asyncio
import builtins
import importlib
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from eija_studio import bootstrap
from eija_studio.adapters.repository_changes import RepositoryChanges
from eija_studio.adapters import repository_analysis
from eija_studio.application.repository import COMMIT_OID_PATTERN, unconfigured_repository_changes
from eija_studio.application.service import Studio
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import default_pack
from eija_studio.interfaces.http import create_app

BASE, HEAD = "a" * 40, "b" * 40
PATH, REF = "src/recover.py", "repo://src/recover.py#recover"
SESSION = "synthetic-change-test"
HEADERS = {"Authorization": "Bearer " + SESSION}
SUMMARY = {"schema": "eija.repository.change.v1", "status": "partial", "read_only": True,
           "comparison_id": "sha256:" + "c" * 64,
           "base": {"commit": BASE, "changed_source_hash": "sha256:" + "d" * 64},
           "head": {"commit": HEAD, "changed_source_hash": "sha256:" + "e" * 64},
           "scope": {"semantic_complete": False}, "coverage": {"excluded_files": 1}}
FILE = SUMMARY | {"schema": "eija.repository.change-file.v1", "path": PATH,
                  "before": {"text": "return 1\n"}, "after": {"text": "return 2\n"},
                  "known_impact": {"after": {"complete": False, "status": "UNKNOWN_TARGET"}}}


class ReadOnlyChanges:
    def __init__(self):
        self.calls = []
        self.error = None

    def compare_commits(self, base, head):
        self.calls.append(("compare", base, head))
        if self.error:
            raise self.error
        return SUMMARY

    def read_change_file(self, base, head, path, reference=None):
        self.calls.append(("file", base, head, path, reference))
        if self.error:
            raise self.error
        return FILE


def make_studio(changes=None):
    # These endpoints must never invoke the model store, signer, identity or proposal provider.
    return Studio(None, SimpleNamespace(networked=False), None, None, None,
                  pack=default_pack(), repository_changes=changes)


@pytest.fixture
def changes():
    return ReadOnlyChanges()


def test_service_unconfigured_has_no_successful_empty_diff():
    studio = make_studio()
    assert studio.repository_change(BASE, HEAD) == unconfigured_repository_changes()
    assert studio.repository_change_file(BASE, HEAD, PATH, REF) == unconfigured_repository_changes()


@pytest.mark.parametrize("bad", ["HEAD", "a" * 39, "A" * 40, "a" * 41, "--help", "a" * 40 + "\n", None])
def test_service_rejects_revision_grammar_before_configured_or_absent_port(changes, bad):
    for port in (None, changes):
        studio = make_studio(port)
        with pytest.raises(DomainError, match="full lowercase local commit") as result:
            studio.repository_change(bad, HEAD)
        assert result.value.code == "CHANGE_REVISION_INVALID"
        with pytest.raises(DomainError) as result:
            studio.repository_change_file(BASE, bad, PATH)
        assert result.value.code == "CHANGE_REVISION_INVALID"
    assert not changes.calls


@pytest.mark.parametrize(("path", "reference"), [("", None), ("p" * 1025, None), ("src/\x00.py", None),
                                               (PATH, ""), (PATH, "r" * 801), (PATH, 4)])
def test_service_bounds_file_inputs_before_port(changes, path, reference):
    for port in (None, changes):
        with pytest.raises(DomainError) as result:
            make_studio(port).repository_change_file(BASE, HEAD, path, reference)
        assert result.value.code == "CHANGE_REFERENCE_DENIED"
    assert not changes.calls


def test_service_forwards_exact_historical_contract_and_keeps_live_port_separate(changes):
    studio = make_studio(changes)
    studio.repository = object()  # No live repository method is needed for immutable reads.
    assert studio.repository_change(BASE, HEAD) is SUMMARY
    assert studio.repository_change_file(BASE, HEAD, PATH, REF) is FILE
    assert studio.repository_change_file("a" * 64, "b" * 64, PATH) is FILE
    assert changes.calls == [("compare", BASE, HEAD), ("file", BASE, HEAD, PATH, REF),
                             ("file", "a" * 64, "b" * 64, PATH, None)]
    assert "source_hash" not in SUMMARY and "source_hash" not in SUMMARY["head"]


def test_bootstrap_composes_two_read_ports_only_for_configured_root(tmp_path, monkeypatch):
    calls = []
    live, change = object(), object()
    monkeypatch.setattr(bootstrap, "SQLiteStore", lambda *a, **kw: SimpleNamespace(directory=tmp_path))
    monkeypatch.setattr(bootstrap, "ReceiptSigner", lambda *a: object())

    def connect(root, pack, **kwargs):
        calls.append(("live", root, pack, kwargs))
        return live

    def compare(root, pack, **kwargs):
        calls.append(("change", root, pack, kwargs))
        return change

    monkeypatch.setattr(bootstrap, "RepositoryConnection", connect)
    monkeypatch.setattr(bootstrap, "RepositoryChanges", compare)
    pack = default_pack()
    absent = bootstrap.build_studio(tmp_path / "workspace", pack=pack)
    assert absent.repository is None and absent.repository_changes is None and not calls
    configured = bootstrap.build_studio(tmp_path / "workspace", pack=pack, repository_root=tmp_path / "repo")
    assert configured.repository is live and configured.repository_changes is change
    assert [entry[:3] for entry in calls] == [("live", tmp_path / "repo", pack), ("change", tmp_path / "repo", pack)]
    assert calls[1][3] == {"syntax_reader": repository_analysis.syntax_reader}


def test_production_hook_module_can_load_without_optional_native_parser(monkeypatch):
    ordinary_import = builtins.__import__

    def reject_native(name, *args, **kwargs):
        if name in {"tree_sitter", "tree_sitter_javascript"}:
            raise ModuleNotFoundError("synthetic missing optional parser")
        return ordinary_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_native)
    # Both modules load without importing the optional native parser in this process.
    for module in (repository_analysis.extract_javascript, repository_analysis):
        spec = importlib.util.spec_from_file_location(module.__name__ + "_import_probe", module.__file__)
        probe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(probe)
    expected = {"status": "NOT_RUN", "method": "js-tree-tokens-v1", "symbols": [],
                "gaps": [{"reason": "PARSER_UNAVAILABLE", "message": "JavaScript syntax extraction did not complete."}]}
    monkeypatch.setattr(repository_analysis, "run_bounded", lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(expected)))
    assert repository_analysis.syntax_reader("src/a.js", b"function a() {}") == expected


@pytest.mark.parametrize(("route", "params", "expected"), [
    ("/api/repository/change", {"base": BASE, "head": HEAD}, SUMMARY),
    ("/api/repository/change/file", {"base": BASE, "head": HEAD, "path": PATH, "reference": REF}, FILE),
])
def test_http_existing_session_host_no_store_and_exact_payload(changes, route, params, expected):
    with TestClient(create_app(make_studio(changes), SESSION), base_url="http://127.0.0.1:8765") as client:
        assert client.get(route, params=params).status_code == 401
        assert not changes.calls
        denied = client.get(route, params=params, headers=HEADERS | {"host": "attacker.invalid"})
        assert denied.status_code == 403 and not changes.calls
        result = client.get(route, params=params, headers=HEADERS)
        assert result.status_code == 200 and result.json() == expected
        assert result.headers["cache-control"] == "no-store"
        assert result.headers["x-content-type-options"] == "nosniff"


@pytest.mark.parametrize(("route", "params"), [
    ("/api/repository/change", {"base": "PRIVATE_CANARY_HEAD", "head": HEAD}),
    ("/api/repository/change", {"base": BASE}),
    ("/api/repository/change/file", {"base": BASE, "head": HEAD, "path": "p" * 1025}),
    ("/api/repository/change/file", {"base": BASE, "head": HEAD, "path": PATH, "reference": "r" * 801}),
])
def test_http_contract_rejection_before_reads_never_echoes_input(changes, route, params):
    with TestClient(create_app(make_studio(changes), SESSION), base_url="http://127.0.0.1:8765") as client:
        result = client.get(route, params=params, headers=HEADERS)
        assert result.status_code == 422 and result.json()["code"] == "CONTRACT_REJECTED"
        assert "PRIVATE_CANARY" not in result.text and result.headers["cache-control"] == "no-store"
    assert not changes.calls


def test_http_unconfigured_and_domain_errors_keep_explicit_status(changes):
    params = {"base": BASE, "head": HEAD}
    with TestClient(create_app(make_studio(), SESSION), base_url="http://127.0.0.1:8765") as client:
        assert client.get("/api/repository/change", params=params, headers=HEADERS).json() == unconfigured_repository_changes()
    changes.error = DomainError("CHANGE_REVISION_UNAVAILABLE", "The local commit is unavailable")
    with TestClient(create_app(make_studio(changes), SESSION), base_url="http://127.0.0.1:8765") as client:
        result = client.get("/api/repository/change", params=params, headers=HEADERS)
        assert result.status_code == 409 and result.json()["code"] == changes.error.code
        assert result.headers["cache-control"] == "no-store"


def test_mcp_read_only_schema_and_same_bound_results(changes):
    Client = pytest.importorskip("mcp").Client
    server = importlib.import_module("eija_studio.interfaces.mcp_server")

    async def check():
        async with Client(server.create_server(make_studio(changes))) as client:
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}
            assert set(tools) == set(server.AGENT_TOOLS)
            assert not set(tools) & set(server.OWNER_ONLY_OPERATIONS)
            for name, keys in (("repository_change", {"base", "head"}),
                               ("repository_change_file", {"base", "head", "path", "reference"})):
                tool = tools[name]
                assert set(tool.input_schema["properties"]) == keys
                assert set(tool.input_schema["required"]) == keys - {"reference"}
                assert tool.input_schema["properties"]["base"]["pattern"] == COMMIT_OID_PATTERN
                assert tool.annotations.read_only_hint and not tool.annotations.destructive_hint
            result = await client.call_tool("repository_change", {"base": BASE, "head": HEAD})
            assert not result.is_error and json.loads(result.content[0].text) == SUMMARY
            result = await client.call_tool("repository_change_file", {"base": BASE, "head": HEAD, "path": PATH, "reference": REF})
            assert not result.is_error and json.loads(result.content[0].text) == FILE
    asyncio.run(check())


def test_mcp_unconfigured_refusal_and_unexpected_error_boundaries(changes):
    Client = pytest.importorskip("mcp").Client
    server = importlib.import_module("eija_studio.interfaces.mcp_server")

    async def check():
        studio = make_studio()
        async with Client(server.create_server(studio)) as client:
            result = await client.call_tool("repository_change", {"base": BASE, "head": HEAD})
            assert not result.is_error and json.loads(result.content[0].text) == unconfigured_repository_changes()
            for invalid_base in ("PRIVATE_CANARY", ["PRIVATE_CANARY"], 9, None):
                invalid = await client.call_tool("repository_change", {"base": invalid_base, "head": HEAD})
                assert invalid.is_error and "CHANGE_REVISION_INVALID" in invalid.content[0].text
                assert "PRIVATE_CANARY" not in invalid.content[0].text
            for invalid_path, invalid_ref in ((None, None), ("p" * 1025, None), (PATH, ["PRIVATE_CANARY"]), (PATH, "r" * 801)):
                invalid = await client.call_tool("repository_change_file", {
                    "base": BASE, "head": HEAD, "path": invalid_path, "reference": invalid_ref})
                assert invalid.is_error and "CHANGE_REFERENCE_DENIED" in invalid.content[0].text
                assert "PRIVATE_CANARY" not in invalid.content[0].text
            studio.repository_changes = changes
            changes.error = DomainError("CHANGE_REFERENCE_DENIED", "Choose a permitted changed file or extracted reference")
            denied = await client.call_tool("repository_change_file", {"base": BASE, "head": HEAD, "path": "private/canary.py"})
            assert denied.is_error and "CHANGE_REFERENCE_DENIED" in denied.content[0].text
            assert "private/canary" not in denied.content[0].text
            changes.error = RuntimeError("PRIVATE_INTERNAL_CANARY")
            failed = await client.call_tool("repository_change", {"base": BASE, "head": HEAD})
            assert failed.is_error and "INTERNAL_ERROR" in failed.content[0].text
            assert "PRIVATE_INTERNAL_CANARY" not in failed.content[0].text
    asyncio.run(check())


def test_mcp_static_owner_boundary_keeps_existing_exclusions():
    path = Path(__file__).with_name("test_agent_static.py")
    spec = importlib.util.spec_from_file_location("change_static_boundary_probe", path)
    static = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(static)
    assert {"repository_change", "repository_change_file"} <= static.ALLOWED_STUDIO
    assert {"repository_change", "repository_change_file"} <= static.ALLOWED_PORT
    assert not static.ALLOWED_STUDIO & set(static.OWNER_ONLY)
    assert not static.ALLOWED_PORT & set(static.OWNER_ONLY)
    assert static.owner_operation_violations(static.ADAPTER.read_text(encoding="utf-8")) == []


def _git(root: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    # Fixed Git command; callers pass only this test's disposable root and fixture arguments.
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True, env=env)  # noqa: S603, S607
    return result.stdout.strip()


def test_real_local_pair_is_pinned_across_http_and_mcp_and_leaves_worktree_alone(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Synthetic interface fixture")
    _git(root, "config", "user.email", "fixture@example.invalid")
    source = root / "recover.py"
    source.write_bytes(b"def recover():\r\n    return 1\r\n")
    _git(root, "add", "recover.py")
    _git(root, "commit", "-q", "-m", "before")
    base = _git(root, "rev-parse", "HEAD")
    source.write_bytes(b"def recover():\r\n    return 2\r\n")
    _git(root, "add", "recover.py")
    _git(root, "commit", "-q", "-m", "after")
    head = _git(root, "rev-parse", "HEAD")
    source.write_bytes(b"def recover():\n    return 999\n")
    before_status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    studio = make_studio(RepositoryChanges(root, default_pack()))
    params = {"base": base, "head": head, "path": "recover.py", "reference": "repo://recover.py#recover"}
    with TestClient(create_app(studio, SESSION), base_url="http://127.0.0.1:8765") as client:
        result = client.get("/api/repository/change/file", params=params, headers=HEADERS)
        assert result.status_code == 200
        payload = result.json()
    assert payload["before"]["text"] == "def recover():\r\n    return 1\r\n"
    assert payload["after"]["text"] == "def recover():\r\n    return 2\r\n"
    assert "return 999" not in json.dumps(payload)
    assert payload["known_impact"]["after"]["complete"] is False
    assert _git(root, "status", "--porcelain=v1", "--untracked-files=all") == before_status
    assert source.read_bytes() == b"def recover():\n    return 999\n"
    Client = pytest.importorskip("mcp").Client
    server = importlib.import_module("eija_studio.interfaces.mcp_server")

    async def check():
        async with Client(server.create_server(studio)) as client:
            actual = await client.call_tool("repository_change_file", params)
            assert not actual.is_error and json.loads(actual.content[0].text) == payload
    asyncio.run(check())
