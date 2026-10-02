"""Repository boundaries and deterministic negative controls; target programs never run."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from eija_studio.adapters.repository import RepositoryConnection
from eija_studio.adapters.providers.process import resolve_command, run_bounded
from eija_studio.application.repository import unconfigured_repository
from eija_studio.domain.pack import Pack, load_pack

ROOT = Path(__file__).resolve().parents[1]


def git(root: Path, *args: str) -> str:
    try:
        command = resolve_command("git")
    except FileNotFoundError:
        pytest.skip("Git is required for repository connection fixtures")
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    result = run_bounded([*command, "-C", str(root), *args], input=None, env=env, timeout=10)
    result.check_returncode()
    return result.stdout


def write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def checkout(tmp_path: Path) -> tuple[Path, Pack]:
    root = tmp_path / "repository"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "Repository fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    pack = load_pack(ROOT / "packs" / "library-loan" / "pack.json")
    document: dict[str, Any] = pack.model_dump(mode="json")
    document["language"]["terms"][0]["binds"] = ["repo://src/loans.py#borrow"]
    pack = Pack.model_validate(document)
    write(root, "packs/library-loan/pack.json", json.dumps(document))
    write(root, "src/loans.py", "def borrow():\n    return 1\n")
    write(root, "tests/test_loans.py", "def test_borrow():\n    assert True\n")
    state = pack.model.states[0]
    write(root, "web/index.html", f'<div data-eija-id="library-loan.state.{state}"></div>')
    git(root, "add", "--all")
    git(root, "commit", "-q", "-m", "Synthetic source fixture")
    return root, pack


def test_equal_inputs_repeat_without_writing_target(checkout: tuple[Path, Pack]) -> None:
    root, pack = checkout
    before = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    connection = RepositoryConnection(root, pack)
    first = connection.snapshot()
    assert first == connection.snapshot() == connection.context()
    assert first["status"] == "connected"
    assert first["pack"]["digest"] == pack.digest
    assert first["file_hashes"]["src/loans.py"]
    assert any(n["type"] == "test" for n in first["nodes"])
    assert any(n["type"] == "ui_status" for n in first["nodes"])
    assert first["lint"]["verdicts"]["WV-005"] == "NOT_RUN"
    assert first["coverage"]["semantic_complete"] is False
    assert git(root, "status", "--porcelain=v1", "--untracked-files=all") == before


def test_missing_binding_fails_actual_weave_lint(checkout: tuple[Path, Pack]) -> None:
    root, pack = checkout
    (root / "src/loans.py").unlink()
    result = RepositoryConnection(root, pack).snapshot()
    assert result["lint"]["verdicts"]["WV-001"] == "FAIL"
    assert any(b["target"] == "repo://src/loans.py#borrow" and not b["resolved"] for b in result["bindings"])


def test_untracked_ignored_private_and_vendor_files_are_not_read(checkout: tuple[Path, Pack]) -> None:
    root, pack = checkout
    write(root, ".gitignore", "ignored.py\n")
    write(root, "ignored.py", "IGNORED_VALUE = 'must not appear'\n")
    write(root, "private/record.py", "PRIVATE_VALUE = 'must not appear'\n")
    write(root, "vendor/library.py", "VENDOR_VALUE = 'must not appear'\n")
    write(root, "untracked.py", "UNTRACKED_VALUE = 'must not appear'\n")
    git(root, "add", "--force", ".gitignore", "ignored.py", "private/record.py", "vendor/library.py")
    result = RepositoryConnection(root, pack).snapshot()
    encoded = json.dumps(result)
    assert all(value not in encoded for value in ("IGNORED_VALUE", "PRIVATE_VALUE", "VENDOR_VALUE", "UNTRACKED_VALUE"))
    assert all(path not in result["file_hashes"] for path in ("ignored.py", "private/record.py", "vendor/library.py", "untracked.py"))
    assert "untracked.py" not in encoded
    assert result["coverage"]["excluded"]["git_ignored"] == 1


def test_outside_symlink_is_never_read(checkout: tuple[Path, Pack], tmp_path: Path) -> None:
    root, pack = checkout
    outside = tmp_path / "outside.py"
    outside.write_text("OUTSIDE_VALUE = 'must not appear'\n", encoding="utf-8")
    (root / "src/loans.py").unlink()
    try:
        (root / "src/loans.py").symlink_to(outside)
    except OSError:
        pytest.skip("Creating symlinks requires platform permission")
    result = RepositoryConnection(root, pack).snapshot()
    assert "OUTSIDE_VALUE" not in json.dumps(result)
    assert "src/loans.py" not in result["file_hashes"]
    assert result["lint"]["verdicts"]["WV-001"] == "FAIL"
    assert result["coverage"]["excluded"]["symlink_or_reparse_point"] == 1


def test_changes_stale_source_even_when_public_signature_is_unchanged(checkout: tuple[Path, Pack]) -> None:
    root, pack = checkout
    connection = RepositoryConnection(root, pack)
    before = connection.snapshot()
    assert connection.freshness(before["file_hashes"])["status"] == "current"
    write(root, "src/loans.py", "def borrow():\n    return 2\n")
    freshness = connection.freshness(before["file_hashes"])
    assert freshness["status"] == "stale"
    assert freshness["changed"] == ["src/loans.py"]
    assert connection.snapshot()["source_hash"] != before["source_hash"]


def test_git_worktree_metadata_and_witness_paths(checkout: tuple[Path, Pack], tmp_path: Path) -> None:
    root, pack = checkout
    additional = tmp_path / "secondary"
    git(root, "worktree", "add", "-q", "--detach", str(additional))
    connection = RepositoryConnection(root, pack)
    metadata = connection.snapshot()["git"]
    assert metadata["head"] == git(root, "rev-parse", "HEAD").strip()
    assert len(metadata["worktrees"]) == 2
    assert all("remote" not in row for row in metadata["worktrees"])
    result = connection.impact(pack.language.terms[0].id)
    assert result["impact"]["certificate"] == "accepted"
    assert any(row["id"] == "repo://src/loans.py#borrow" for row in result["impact"]["affected"])
    assert all(row["witness"][0] == result["impact"]["target"] for row in result["impact"]["affected"])
    assert connection.impact("unknown-subject")["status"] == "unknown_target"


def test_unsupported_language_is_explicit_and_target_code_is_not_run(checkout: tuple[Path, Pack]) -> None:
    root, pack = checkout
    write(root, "app.ts", "throw new Error('do not run');\n")
    write(root, "src/loans.py", "raise RuntimeError('do not run')\n\ndef borrow():\n    return 1\n")
    git(root, "add", "app.ts", "src/loans.py")
    result = RepositoryConnection(root, pack).snapshot()
    assert result["status"] == "connected"
    assert any(gap["path"] == "app.ts" for gap in result["gaps"])
    assert result["coverage"]["semantic_complete"] is False


def test_absent_and_non_repository_are_not_success(tmp_path: Path) -> None:
    pack = load_pack(ROOT / "packs" / "library-loan" / "pack.json")
    assert unconfigured_repository()["status"] == "unconfigured"
    result = RepositoryConnection(tmp_path, pack).snapshot()
    assert result["status"] == "unavailable"
    assert result["lint"]["verdict"] == "NOT_RUN"


def test_absolute_windows_binding_cannot_escape_mirror(checkout: tuple[Path, Pack]) -> None:
    root, pack = checkout
    document = pack.model_dump(mode="json")
    document["language"]["terms"][0]["binds"] = ["repo://C:/outside.py#borrow"]
    result = RepositoryConnection(root, Pack.model_validate(document)).snapshot()
    assert result["status"] == "unavailable"
    assert "unsafe repository binding" in result["reason"]



def test_generic_connection_reports_implementation_facts_not_run(checkout):
    root, pack = checkout
    observed = RepositoryConnection(root, pack).snapshot()["observed_facts"]
    assert observed["extraction"]["status"] == "NOT_RUN"
    assert observed["conformance"]["status"] == "NOT_RUN"
    assert observed["declared_model"]["pack_digest"] == pack.digest
