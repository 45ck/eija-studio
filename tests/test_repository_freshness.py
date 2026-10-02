"""Previously captured links cannot silently read or explain a different source snapshot."""
from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters import repository as adapter
from eija_studio.adapters.repository import RepositoryConnection
from eija_studio.domain.models import DomainError
from eija_studio.interfaces.http import create_app
from test_repository_connection import checkout as repository_checkout, git, write

checkout = repository_checkout
REFERENCE = "repo://src/loans.py#borrow"


def test_hash_only_freshness_detects_external_edit_without_touching_source(checkout):
    root, pack = checkout
    connection = RepositoryConnection(root, pack)
    before = connection.snapshot()
    fresh = connection.freshness(expected_source_hash=before["source_hash"])
    assert fresh["status"] == "current" and fresh["read_only"] is True
    write(root, "src/loans.py", "def borrow():\n    return 47\n")
    bytes_after_edit = (root / "src/loans.py").read_bytes()
    git_after_edit = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    stale = connection.freshness(expected_source_hash=before["source_hash"])
    assert stale["status"] == "stale"
    assert stale["compared_source_hash"] == before["source_hash"] != stale["source_hash"]
    assert stale["changed"] is None  # A single digest cannot name changed files.
    assert connection.freshness(before["file_hashes"])["changed"] == ["src/loans.py"]
    assert (root / "src/loans.py").read_bytes() == bytes_after_edit
    assert git(root, "status", "--porcelain=v1", "--untracked-files=all") == git_after_edit


@pytest.mark.parametrize("operation", ["source", "impact"])
def test_bound_repository_read_rejects_changed_bytes_and_accepts_refreshed_identity(checkout, operation):
    root, pack = checkout
    connection = RepositoryConnection(root, pack)
    read = connection.read_source if operation == "source" else connection.impact
    target = REFERENCE if operation == "source" else pack.language.terms[0].id
    before = connection.snapshot()
    assert read(target, expected_source_hash=before["source_hash"])["source_hash"] == before["source_hash"]
    write(root, "src/loans.py", "def borrow():\n    return 48\n")
    with pytest.raises(DomainError) as stale:
        read(target, expected_source_hash=before["source_hash"])
    assert stale.value.code == "SOURCE_SNAPSHOT_STALE"
    assert stale.value.details["expected_source_hash"] == before["source_hash"]
    after = connection.snapshot()
    assert stale.value.details["source_hash"] == after["source_hash"]
    assert read(target, expected_source_hash=after["source_hash"])["source_hash"] == after["source_hash"]


@pytest.mark.parametrize("bad", ["", "../private", "f" * 64, "sha256:" + "f" * 63, "sha256:" + "g" * 64, 42])
def test_invalid_expected_identity_refused_before_any_capture(checkout, monkeypatch, bad):
    root, pack = checkout
    connection = RepositoryConnection(root, pack)

    def denied_capture(*args):
        raise AssertionError("invalid snapshot must not start capture")

    monkeypatch.setattr(adapter, "_capture", denied_capture)
    for operation in [lambda: connection.read_source(REFERENCE, expected_source_hash=bad),
                      lambda: connection.impact("borrow", expected_source_hash=bad),
                      lambda: connection.freshness(expected_source_hash=bad)]:
        with pytest.raises(DomainError) as invalid:
            operation()
        assert invalid.value.code == "INVALID_SOURCE_HASH"


def test_bound_read_uses_the_compared_capture_when_checkout_changes_during_index(checkout, monkeypatch):
    root, pack = checkout
    connection = RepositoryConnection(root, pack)
    before = connection.snapshot()
    original = (root / "src/loans.py").read_bytes()
    build = adapter._build

    def change_after_capture(captured, domain, path):
        graph = build(captured, domain, path)
        write(root, "src/loans.py", "def borrow():\n    return 999\n")
        return graph

    monkeypatch.setattr(adapter, "_build", change_after_capture)
    answer = connection.read_source(REFERENCE, expected_source_hash=before["source_hash"])
    assert answer["source_hash"] == before["source_hash"]
    assert answer["text"].encode() == original
    assert connection.freshness(expected_source_hash=before["source_hash"])["status"] == "stale"


@pytest.mark.parametrize("operation", ["read_source", "impact"])
def test_stale_refusal_oracle_detects_removed_snapshot_comparison(checkout, monkeypatch, operation):
    """Remove the real comparison while retaining real capture/index/read implementations."""
    root, pack = checkout
    connection = RepositoryConnection(root, pack)
    expected = connection.snapshot()["source_hash"]
    write(root, "src/loans.py", "def borrow():\n    return 777\n")
    target = REFERENCE if operation == "read_source" else pack.language.terms[0].id

    def assert_refusal():
        try:
            getattr(connection, operation)(target, expected_source_hash=expected)
        except DomainError as error:
            assert error.code == "SOURCE_SNAPSHOT_STALE"
        else:
            raise AssertionError("Different bytes were accepted as the requested snapshot")

    assert_refusal()
    monkeypatch.setattr(adapter, "_capture_at", lambda path, expected_hash: adapter._capture(path))
    with pytest.raises(AssertionError, match="Different bytes"):
        assert_refusal()


def test_http_snapshot_contract_auth_validation_and_stale_refusal(studio, checkout):
    root, pack = checkout
    studio.repository = RepositoryConnection(root, pack)
    expected = studio.workbench()["connection"]["source_hash"]
    headers = {"Authorization": "Bearer synthetic-freshness-test"}
    with TestClient(create_app(studio, "synthetic-freshness-test"), base_url="http://127.0.0.1:8765") as client:
        params = {"expected_source_hash": expected}
        assert client.get("/api/repository/freshness", params=params).status_code == 401
        response = client.get("/api/repository/freshness", params=params, headers=headers)
        assert response.status_code == 200 and response.json()["status"] == "current"
        assert response.headers["cache-control"] == "no-store"
        invalid = client.get("/api/repository/freshness", params={"expected_source_hash": "wrong"}, headers=headers)
        assert invalid.status_code == 422
        write(root, "src/loans.py", "def borrow():\n    return 49\n")
        assert client.get("/api/repository/freshness", params=params, headers=headers).json()["status"] == "stale"
        for endpoint, query in [("source", {"reference": REFERENCE}), ("impact", {"term": pack.language.terms[0].id})]:
            stale = client.get("/api/repository/" + endpoint, params=params | query, headers=headers)
            assert stale.status_code == 409 and stale.json()["code"] == "SOURCE_SNAPSHOT_STALE"
            assert "text" not in stale.json()


def test_unconfigured_freshness_does_not_claim_current(studio):
    studio.repository = None
    assert studio.repository_freshness("sha256:" + "0" * 64)["status"] == "unconfigured"


def test_agent_reads_can_pin_the_same_snapshot_without_adding_authority(studio, checkout):
    pytest.importorskip("mcp")
    module = importlib.import_module("eija_studio.interfaces.mcp_server")
    root, pack = checkout
    studio.repository = RepositoryConnection(root, pack)
    surface = module.AgentSurface(module.StudioAgentPort(studio))
    snapshot = surface.pack()["connection"]["source_hash"]
    assert surface.repository_source(REFERENCE, expected_source_hash=snapshot)["source_hash"] == snapshot
    write(root, "src/loans.py", "def borrow():\n    return 50\n")
    with pytest.raises(DomainError) as stale:
        surface.repository_source(REFERENCE, expected_source_hash=snapshot)
    assert stale.value.code == "SOURCE_SNAPSHOT_STALE"
    with pytest.raises(DomainError) as stale_impact:
        surface.repository_impact(pack.language.terms[0].id, expected_source_hash=snapshot)
    assert stale_impact.value.code == "SOURCE_SNAPSHOT_STALE"
