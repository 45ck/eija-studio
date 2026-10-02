"""Source navigation stays inside captured graph/declared bindings, without executing target code."""
from __future__ import annotations

import asyncio
import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters import repository as adapter
from eija_studio.adapters.repository import MAX_SOURCE_BYTES, MAX_SOURCE_LINES, RepositoryConnection
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import Pack
from eija_studio.interfaces.http import create_app
from test_repository_connection import checkout as repository_checkout, git, write

checkout = repository_checkout  # Reuse the existing disposable Git fixture under its familiar name.


def digest(data):
    return hashlib.sha256(data).hexdigest()


def test_source_is_exact_captured_bytes_with_ast_location_and_no_target_write(checkout):
    root, pack = checkout
    content = b"# preface\r\n\r\nclass Loans:\r\n    def borrow(self):\r\n        return 1\r\n"
    (root / "src/loans.py").write_bytes(content)
    connection = RepositoryConnection(root, pack)
    before = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    result = connection.read_source("repo://src/loans.py#Loans.borrow")
    assert result["status"] == "connected" and result["read_only"] is True
    assert result["path"] == "src/loans.py" and result["symbol"] == "Loans.borrow"
    assert result["symbol_lines"] == {"start": 4, "end": 5}
    assert result["lines"] == {"start": 1, "end": 5}
    assert result["text"].encode("utf-8") == content
    assert result["file_hash"] == result["snippet_hash"] == digest(content)
    assert result["source_hash"] == connection.snapshot()["source_hash"]
    assert result["fragment_resolution"] == "python_ast" and result["truncated"] is False
    assert (root / "src/loans.py").read_bytes() == content
    assert git(root, "status", "--porcelain=v1", "--untracked-files=all") == before


def test_source_changes_are_visible_in_file_snapshot_and_snippet_hashes(checkout):
    root, pack = checkout
    connection = RepositoryConnection(root, pack)
    before = connection.read_source("repo://src/loans.py#borrow")
    write(root, "src/loans.py", "def borrow():\n    return 2\n")
    after = connection.read_source("repo://src/loans.py#borrow")
    assert "return 2" in after["text"]
    assert all(after[key] != before[key] for key in ("file_hash", "source_hash", "snippet_hash", "graph_hash"))


@pytest.mark.parametrize("reference", ["../../private.py", "repo:///etc/passwd", "repo://../outside.py", "repo://C:/private.py",
                                       "repo://src\\loans.py", "repo://.env", "repo://private/record.py", "repo://secrets.py",
                                       "repo://receipt.key", "repo://auth.json", "repo://src/loans.py\x00"])
def test_unsafe_and_excluded_references_refused_before_capture(checkout, monkeypatch, reference):
    root, pack = checkout

    def must_not_capture(*args):
        raise AssertionError("Denied reference must not even start a repository read")

    monkeypatch.setattr(adapter, "_capture", must_not_capture)
    with pytest.raises(DomainError) as denied:
        RepositoryConnection(root, pack).read_source(reference)
    assert denied.value.code == "SOURCE_REFERENCE_DENIED"


@pytest.mark.parametrize("reference", ["repo://untracked.py", "repo://ignored.py", "repo://notes.txt", "repo://src/loans.py#unknown"])
def test_unknown_untracked_ignored_and_undeclared_noncode_are_not_a_file_browser(checkout, reference):
    root, pack = checkout
    for path in ("untracked.py", "ignored.py", "notes.txt"):
        write(root, path, "PRIVATE_CANARY = 'must never be returned'\n")
    write(root, ".gitignore", "ignored.py\n")
    git(root, "add", "--force", "ignored.py", ".gitignore", "notes.txt")
    with pytest.raises(DomainError) as denied:
        RepositoryConnection(root, pack).read_source(reference)
    assert denied.value.code == "SOURCE_REFERENCE_DENIED"
    assert "PRIVATE_CANARY" not in str(denied.value)


def test_declared_file_binding_is_a_file_only_preview_not_a_claimed_symbol(checkout):
    root, pack = checkout
    write(root, "docs/loan.md", "# Loans\n\n**Borrow:** A declared term.\n")
    git(root, "add", "docs/loan.md")
    data = pack.model_dump(mode="json")
    data["language"]["terms"][0]["binds"] = ["repo://docs/loan.md#borrow"]
    result = RepositoryConnection(root, Pack.model_validate(data)).read_source("repo://docs/loan.md#borrow")
    assert result["fragment_resolution"] == "file_only" and result["symbol"] is None
    assert result["symbol_lines"] is None and result["requested_fragment"] == "borrow"
    assert result["text"] == "# Loans\n\n**Borrow:** A declared term.\n"


def test_declared_missing_symbol_stays_unresolved(checkout):
    root, pack = checkout
    write(root, "src/loans.py", "def renamed():\n    return 1\n")
    with pytest.raises(DomainError) as unresolved:
        RepositoryConnection(root, pack).read_source("repo://src/loans.py#borrow")
    assert unresolved.value.code == "SOURCE_REFERENCE_UNRESOLVED"


def test_source_is_not_reread_after_graph_capture(checkout, monkeypatch):
    root, pack = checkout
    original = (root / "src/loans.py").read_bytes()
    build = adapter._build

    def changed_after_capture(captured, domain, path):
        graph = build(captured, domain, path)
        write(root, "src/loans.py", "def borrow():\n    return 999\n")
        return graph

    monkeypatch.setattr(adapter, "_build", changed_after_capture)
    result = RepositoryConnection(root, pack).read_source("repo://src/loans.py#borrow")
    assert result["text"].encode("utf-8") == original
    assert result["file_hash"] == digest(original)
    assert result["file_hash"] != digest((root / "src/loans.py").read_bytes())


def test_line_and_byte_bounds_are_visible_and_utf8_safe(checkout):
    root, pack = checkout
    text = "def borrow():\n" + "    value = 1\n" * 250
    write(root, "src/loans.py", text)
    result = RepositoryConnection(root, pack).read_source("repo://src/loans.py#borrow")
    assert result["truncated"] is True and len(result["text"].splitlines()) == MAX_SOURCE_LINES
    assert result["symbol_lines"]["end"] == 251
    text = "def borrow():\n    return '" + "界" * 20000 + "'\n"
    write(root, "src/loans.py", text)
    result = RepositoryConnection(root, pack).read_source("repo://src/loans.py#borrow")
    assert result["truncated"] is True and len(result["text"].encode("utf-8")) <= MAX_SOURCE_BYTES
    assert text.startswith(result["text"])
    assert result["file_hash"] == digest(text.encode("utf-8"))


def test_source_target_is_not_executed_and_symlinks_are_denied(checkout, tmp_path):
    root, pack = checkout
    write(root, "src/loans.py", "raise RuntimeError('never execute')\n\ndef borrow():\n    return 1\n")
    connection = RepositoryConnection(root, pack)
    assert "never execute" in connection.read_source("repo://src/loans.py#borrow")["text"]
    outside = tmp_path / "outside.py"
    outside.write_text("PRIVATE_CANARY = 'outside'\n", encoding="utf-8")
    (root / "src/loans.py").unlink()
    try:
        (root / "src/loans.py").symlink_to(outside)
    except OSError:
        pytest.skip("Creating symlinks requires platform permission")
    with pytest.raises(DomainError) as denied:
        connection.read_source("repo://src/loans.py#borrow")
    assert denied.value.code == "SOURCE_REFERENCE_DENIED"


def test_http_source_requires_session_and_preserves_refusal_code(studio, checkout):
    root, pack = checkout
    studio.repository = RepositoryConnection(root, pack)
    headers = {"Authorization": "Bearer synthetic-source-test"}
    with TestClient(create_app(studio, "synthetic-source-test"), base_url="http://127.0.0.1:8765") as client:
        params = {"reference": "repo://src/loans.py#borrow"}
        assert client.get("/api/repository/source", params=params).status_code == 401
        response = client.get("/api/repository/source", params=params, headers=headers)
        assert response.status_code == 200 and "def borrow" in response.json()["text"]
        assert response.headers["cache-control"] == "no-store"
        denied = client.get("/api/repository/source", params={"reference": "repo://auth.json"}, headers=headers)
        assert denied.status_code == 409 and denied.json()["code"] == "SOURCE_REFERENCE_DENIED"


def test_mcp_source_is_read_only_narrow_and_returns_same_bound_payload(studio, checkout):
    pytest.importorskip("mcp")
    from mcp import Client  # noqa: PLC0415 - optional SDK
    from eija_studio.interfaces.mcp_server import create_server  # noqa: PLC0415 - optional SDK

    root, pack = checkout
    studio.repository = RepositoryConnection(root, pack)

    async def check():
        async with Client(create_server(studio)) as client:
            listing = await client.list_tools()
            tool = next(tool for tool in listing.tools if tool.name == "repository_source")
            assert tool.annotations.read_only_hint is True and tool.annotations.destructive_hint is False
            assert set(tool.input_schema["properties"]) == {"reference", "expected_source_hash"}
            assert tool.input_schema["required"] == ["reference"]
            result = await client.call_tool("repository_source", {"reference": "repo://src/loans.py#borrow"})
            assert not result.is_error
            assert json.loads(result.content[0].text) == studio.repository_source("repo://src/loans.py#borrow")
            denied = await client.call_tool("repository_source", {"reference": "repo://auth.json"})
            assert denied.is_error and "SOURCE_REFERENCE_DENIED" in denied.content[0].text

    asyncio.run(check())
