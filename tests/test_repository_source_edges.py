"""Regression controls from independent source-navigation review; no target code is executed."""
from __future__ import annotations

import ast
import json

import pytest

from eija_studio.adapters.repository import RepositoryConnection
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from test_repository_connection import checkout as repository_checkout, git, write

checkout = repository_checkout


@pytest.mark.parametrize("operation", ("snapshot", "source", "impact"))
def test_deep_valid_bound_python_returns_unavailable_without_source_disclosure(checkout, operation):
    root, pack = checkout
    source = "# SENSITIVE_SOURCE_CANARY\ndef borrow():\n    return " + "+".join(["1"] * 1200) + "\n"
    assert isinstance(ast.parse(source), ast.Module)
    write(root, "src/loans.py", source)
    connection = RepositoryConnection(root, pack)
    calls = {"snapshot": connection.snapshot,
             "source": lambda: connection.read_source("repo://src/loans.py#borrow"),
             "impact": lambda: connection.impact(pack.language.terms[0].id)}
    result = calls[operation]()
    assert result["status"] == "unavailable" and result["lint"]["verdict"] == "NOT_RUN"
    assert result["reason"] == "Source syntax exceeds the bounded repository analysis depth."
    assert "SENSITIVE_SOURCE_CANARY" not in json.dumps(result)
    assert not {"text", "source_hash", "file_hash", "graph_hash"} & result.keys()


def test_encoded_unicode_graph_symbol_resolves_after_exact_reference_allowlist(checkout):
    root, pack = checkout
    write(root, "src/unicode.py", "def café():\n    return 'visible fixture'\n")
    git(root, "add", "src/unicode.py")
    connection = RepositoryConnection(root, pack)
    reference = next(node["id"] for node in connection.snapshot()["nodes"]
                     if node["type"] == "symbol" and node["id"].startswith("repo://src/unicode.py#"))
    assert reference == "repo://src/unicode.py#caf%C3%A9"
    result = connection.read_source(reference)
    assert result["reference"] == reference and result["requested_fragment"] == "caf%C3%A9"
    assert result["symbol"] == "café" and result["symbol_lines"] == {"start": 1, "end": 2}
    assert "def café():" in result["text"] and result["fragment_resolution"] == "python_ast"
    for unlisted in ("repo://src/unicode.py#café", "repo://src/unicode.py#caf%c3%a9", "repo://src/%2e%2e/unicode.py#caf%C3%A9"):
        with pytest.raises(DomainError) as denied:
            connection.read_source(unlisted)
        assert denied.value.code == "SOURCE_REFERENCE_DENIED"


def test_unborn_repository_exposes_staged_source_without_inventing_a_head(tmp_path):
    root = tmp_path / "unborn"
    root.mkdir()
    git(root, "init", "-q")
    write(root, "src/start.py", "def start():\n    return 1\n")
    git(root, "add", "src/start.py")
    pack = load_pack(PACKS_ROOT / "library-loan")
    connection = RepositoryConnection(root, pack)
    before = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    snapshot = connection.snapshot()
    assert snapshot["status"] == "connected"
    assert snapshot["git"]["head"] is None and snapshot["git"]["dirty"] is True
    assert "src/start.py" in snapshot["file_hashes"]
    result = connection.read_source("repo://src/start.py#start")
    assert result["status"] == "connected" and "def start():" in result["text"]
    assert git(root, "status", "--porcelain=v1", "--untracked-files=all") == before


def test_injected_source_fact_profile_is_preserved(checkout):
    root, pack = checkout
    seen = []

    def facts(files):
        seen.append(sorted(files))
        return {"extraction": {"status": "EXTRACTED", "executes_target": False}}

    result = RepositoryConnection(root, pack, source_facts=facts).snapshot()
    assert result["observed_facts"] == {"extraction": {"status": "EXTRACTED", "executes_target": False}}
    assert len(seen) == 1 and "src/loans.py" in seen[0]
