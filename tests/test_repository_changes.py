"""Immutable Git intake tests with real disposable repositories, no compared-code execution."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import default_pack

from eija_studio.adapters import repository_changes as changes
from eija_studio.adapters.providers.process import resolve_command, run_bounded


def git(root: Path, *args: str, data: bytes | None = None) -> bytes:
    environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0"})
    executable = shutil.which("git")
    assert executable is not None, "NOT_RUN: Git is not installed"
    result = run_bounded([*resolve_command(executable), "-C", str(root), *args],
                         input=data.decode("utf-8") if data is not None else None,
                         env=environment, timeout=10, cwd=str(root))
    result.check_returncode()
    return result.stdout.encode("utf-8")


def write(root: Path, path: str, data: bytes) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def commit(root: Path, label: str) -> str:
    git(root, "add", "-Af")
    git(root, "commit", "--quiet", "--allow-empty", "-m", label)
    return git(root, "rev-parse", "HEAD").decode().strip()


@pytest.fixture
def repository(tmp_path):
    root = tmp_path / "target"
    root.mkdir()
    git(root, "init", "--quiet", "--initial-branch=main")
    git(root, "config", "user.name", "Disposable test")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    before = b"def example():\r\n    return 'before'\r\n"
    after = b"def example():\r\n    return 'after'\r\n"
    write(root, "src/example.py", before)
    base = commit(root, "before")
    write(root, "src/example.py", after)
    head = commit(root, "after")
    return root, base, head, before, after


def adapter(root: Path, reader=None):
    return changes.RepositoryChanges(root, default_pack(), syntax_reader=reader)


def test_real_git_diff_and_python_symbol_are_bound_to_exact_unchanged_objects(repository):
    root, base, head, before, after = repository
    index = (root / ".git/index").read_bytes()
    status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    reader = adapter(root)
    summary = reader.compare_commits(base, head)
    assert summary["status"] == "available"
    assert summary["coverage"] == {"changed_paths_total": 1, "displayed_paths": 1,
                                    "excluded_by_reason": {}, "inventory_reconciles": True}
    symbol = summary["files"][0]["symbols"][0]
    assert symbol["reference"] == "repo://src/example.py#example"
    assert symbol["status"] == "changed"
    result = reader.read_change_file(base, head, "src/example.py", symbol["reference"])
    assert result["comparison_id"] == summary["comparison_id"]
    assert result["before"]["text"].encode() == before
    assert result["after"]["text"].encode() == after
    assert result["before"]["file_sha256"] == hashlib.sha256(before).hexdigest()
    assert result["after"]["file_sha256"] == hashlib.sha256(after).hexdigest()
    assert "-    return 'before'" in result["unified_diff"]["text"]
    assert "+    return 'after'" in result["unified_diff"]["text"]
    assert result["known_impact"]["before"]["complete"] is False
    assert reader.compare_commits(base, head) == summary
    assert (root / ".git/index").read_bytes() == index
    assert git(root, "status", "--porcelain=v1", "--untracked-files=all") == status


def test_branch_and_dirty_checkout_changes_do_not_change_pinned_source(repository):
    root, base, head, _, after = repository
    initial = adapter(root).compare_commits(base, head)
    write(root, "src/example.py", b"raise RuntimeError('do not execute')\n")
    commit(root, "later unrelated head")
    write(root, "src/example.py", b"uncommitted current text\n")
    assert adapter(root).compare_commits(base, head) == initial
    result = adapter(root).read_change_file(base, head, "src/example.py")
    assert result["after"]["text"].encode() == after


@pytest.mark.parametrize("revision", ["HEAD", "HEAD~1", "--help", "a" * 39, "A" * 40,
                                       "main^{tree}", "https://example.invalid/x", "a" * 40 + ":src/x.py", None])
def test_invalid_revision_is_refused_before_git(repository, monkeypatch, revision):
    root, _, head, _, _ = repository
    monkeypatch.setattr(changes, "_git_read", lambda *_args, **_kwargs: pytest.fail("invalid revision reached Git"))
    with pytest.raises(DomainError) as error:
        adapter(root).compare_commits(revision, head)
    assert error.value.code == "CHANGE_REVISION_INVALID"


def test_missing_and_noncommit_objects_have_fixed_error(repository):
    root, base, head, _, _ = repository
    blob = git(root, "rev-parse", head + ":src/example.py").decode().strip()
    for invalid in ("f" * 40, blob):
        with pytest.raises(DomainError) as error:
            adapter(root).compare_commits(invalid, base)
        assert error.value.code == "CHANGE_REVISION_UNAVAILABLE"
        assert invalid not in error.value.message


@pytest.mark.parametrize("path", ["../secret.py", "/outside.py", "C:/auth.json", r"src\example.py", "auth.json",
                                  ".env", "private/x.py", "vendor/x.py", "src/missing.py"])
def test_arbitrary_or_excluded_paths_are_never_a_file_browser(repository, path):
    root, base, head, _, _ = repository
    with pytest.raises(DomainError) as error:
        adapter(root).read_change_file(base, head, path)
    assert error.value.code == "CHANGE_REFERENCE_DENIED"
    assert path not in error.value.message


def test_unknown_symbol_does_not_fall_back_to_file_or_current_checkout(repository):
    root, base, head, _, _ = repository
    with pytest.raises(DomainError) as error:
        adapter(root).read_change_file(base, head, "src/example.py", "repo://src/example.py#missing")
    assert error.value.code == "CHANGE_REFERENCE_DENIED"


def test_private_paths_are_filtered_before_blob_reads_and_not_named(repository, monkeypatch):
    root, base, _, _, _ = repository
    forbidden = ["auth.json", "private/config.py", "vendor/lib.py", ".env"]
    for path in forbidden:
        write(root, path, b"private content must not be read\n")
    head = commit(root, "private additions")
    private_objects = {git(root, "rev-parse", head + ":" + path).decode().strip() for path in forbidden}
    original = changes._blob
    seen = []

    def record_read(root_path, obj, remaining):
        seen.append(obj.oid)
        assert obj.oid not in private_objects
        return original(root_path, obj, remaining)

    monkeypatch.setattr(changes, "_blob", record_read)
    result = adapter(root).compare_commits(base, head)
    assert result["status"] == "partial"
    assert result["coverage"]["changed_paths_total"] == 5
    assert result["coverage"]["inventory_reconciles"] is True
    assert sum(result["coverage"]["excluded_by_reason"].values()) == 4
    assert seen
    assert all(path not in json.dumps(result) for path in forbidden)


def test_current_ignore_policy_is_explicit_and_changes_comparison_identity(repository):
    root, base, head, _, _ = repository
    before = adapter(root).compare_commits(base, head)
    write(root, ".gitignore", b"src/example.py\n")
    after = adapter(root).compare_commits(base, head)
    assert after["coverage"]["displayed_paths"] == 0
    assert after["coverage"]["excluded_by_reason"] == {"git_ignored_current_policy": 1}
    assert after["comparison_id"] != before["comparison_id"]
    assert "current configured checkout" in after["capture_policy"]["ignore"]


def test_ignore_policy_race_is_not_a_success(repository, monkeypatch):
    root, base, head, _, _ = repository
    values = iter([set(), {"src/example.py"}])
    monkeypatch.setattr(changes, "_ignored_paths", lambda *_args: next(values))
    result = adapter(root).compare_commits(base, head)
    assert result["status"] == "unavailable"
    assert "changed" in result["reason"]


@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_tree_symlink_and_gitlink_are_excluded_without_target_reads(repository, mode):
    root, base, _, _, _ = repository
    oid = base if mode == "160000" else git(root, "hash-object", "-w", "--stdin", data=b"../../outside.py").decode().strip()
    git(root, "update-index", "--add", "--cacheinfo", mode + "," + oid + ",src/link.py")
    git(root, "commit", "--quiet", "-m", "nonregular entry")
    head = git(root, "rev-parse", "HEAD").decode().strip()
    result = adapter(root).compare_commits(base, head)
    assert result["status"] == "partial"
    assert result["coverage"]["excluded_by_reason"]["symlink_gitlink_or_nonregular"] == 1
    assert all(item["path"] != "src/link.py" for item in result["files"])


def test_replacement_objects_refuse_before_capture(repository, monkeypatch):
    root, base, head, _, _ = repository
    git(root, "replace", base, head)
    monkeypatch.setattr(changes, "_blob", lambda *_args: pytest.fail("replacement reached blob read"))
    result = adapter(root).compare_commits(base, head)
    assert result["status"] == "unavailable"
    assert "replacement" in result["reason"]


def test_promisor_configuration_refuses_without_fetch_or_blob_reads(repository, monkeypatch):
    root, base, head, _, _ = repository
    git(root, "config", "remote.test.promisor", "true")
    git(root, "config", "remote.test.url", "https://example.invalid/must-not-fetch")
    monkeypatch.setattr(changes, "_blob", lambda *_args: pytest.fail("promisor reached blob read"))
    result = adapter(root).compare_commits(base, head)
    assert result["status"] == "unavailable"
    assert "promisor" in result["reason"]


def test_external_diff_textconv_filters_and_target_python_are_not_executed(repository, tmp_path):
    root, base, _, _, _ = repository
    marker = tmp_path / "EXECUTED"
    driver = tmp_path / "untrusted-driver.py"
    driver.write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('bad')\n", encoding="utf-8")
    write(root, "src/example.py", ("from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('bad')\n"
                                   "def example():\n    return 'real source'\n").encode())
    write(root, ".gitattributes", b"src/example.py diff=trap filter=trap\n")
    head = commit(root, "never execute this")
    command = subprocess.list2cmdline([sys.executable, str(driver)])
    for name in ("diff.external", "diff.trap.command", "diff.trap.textconv", "filter.trap.smudge", "filter.trap.clean"):
        git(root, "config", name, command)
    result = adapter(root).read_change_file(base, head, "src/example.py")
    assert result["unified_diff"]["status"] == "AVAILABLE"
    assert "real source" in result["unified_diff"]["text"]
    assert not marker.exists()


@pytest.mark.parametrize("content", [b"\x00binary\n", b"\xffinvalid\n", "# replacement \ufffd\n".encode()])
def test_non_roundtrippable_or_binary_blob_never_gets_a_fabricated_digest(repository, content):
    root, base, _, _, _ = repository
    write(root, "src/example.py", content)
    head = commit(root, "unsupported blob")
    result = adapter(root).read_change_file(base, head, "src/example.py")
    assert result["status"] == "partial"
    assert result["after"]["status"] == "unavailable"
    assert result["unified_diff"]["status"] == "NOT_RUN"


def test_file_and_changed_path_caps_are_explicit(repository, monkeypatch):
    root, base, _, _, _ = repository
    write(root, "src/another.py", b"def another():\n    return 3\n")
    head = commit(root, "second file")
    monkeypatch.setattr(changes, "MAX_CHANGED_FILES", 1)
    result = adapter(root).compare_commits(base, head)
    assert result["coverage"]["excluded_by_reason"] == {"changed_file_limit": 1}
    assert result["coverage"]["inventory_reconciles"] is True
    monkeypatch.setattr(changes, "MAX_FILE_BYTES", 4)
    result = adapter(root).compare_commits(base, head)
    assert result["status"] == "partial"
    assert result["files"][0]["after"]["file_sha256"] is None


def test_added_removed_symbols_and_format_only_changes_are_not_confused(repository):
    root, base, _, _, _ = repository
    write(root, "src/example.py", b"def replacement():\n    return 'after'\n")
    head = commit(root, "rename is not inferred")
    rows = adapter(root).compare_commits(base, head)["files"][0]["symbols"]
    assert {item["reference"].split("#")[-1]: item["status"] for item in rows} == {"example": "removed", "replacement": "added"}
    removed = adapter(root).read_change_file(base, head, "src/example.py", "repo://src/example.py#example")
    assert removed["before"]["status"] == "captured"
    assert removed["after"]["status"] == "not_present"
    write(root, "src/example.py", b"# comment\ndef example():\n    return 'before'\n")
    formatted = commit(root, "only formatting")
    row = adapter(root).compare_commits(base, formatted)["files"][0]
    assert row["before"]["file_sha256"] != row["after"]["file_sha256"]
    assert row["symbols"][0]["status"] == "unchanged"


def test_python_private_helper_change_is_reported_as_syntactic_closure_not_behavior(repository):
    root, _, _, _, _ = repository
    write(root, "src/example.py", b"def _helper():\n    return 1\ndef example():\n    return _helper()\n")
    base = commit(root, "helper before")
    write(root, "src/example.py", b"def _helper():\n    return 2\ndef example():\n    return _helper()\n")
    head = commit(root, "helper after")
    result = adapter(root).compare_commits(base, head)
    assert result["files"][0]["symbols"][0]["status"] == "changed"
    assert result["files"][0]["extraction"]["after"]["method"] == "python_ast_ast-v2"
    assert result["scope"]["behavior"] == "NOT_RUN by source comparison"


def test_missing_js_adapter_still_returns_real_source_diff(repository):
    root, base, _, _, _ = repository
    write(root, "src/app.js", b"function load() { return 1; }\n")
    head = commit(root, "javascript addition")
    result = adapter(root).read_change_file(base, head, "src/app.js")
    assert result["status"] == "partial"
    assert result["before"] is None
    assert "function load" in result["unified_diff"]["text"]
    row = next(item for item in adapter(root).compare_commits(base, head)["files"] if item["path"] == "src/app.js")
    assert row["extraction"]["after"]["status"] == "NOT_RUN"
    assert row["symbols"] == []


def js_reader(path, data):
    return {"status": "EXTRACTED", "method": "fixture-syntax-only", "parser_version": "fixture-1",
            "grammar_version": "fixture-1", "symbols": [{"reference": "repo://" + path + "#js/function/load",
                "kind": "function", "syntax_digest": hashlib.sha256(data).hexdigest(), "start_line": 1, "end_line": 1}], "gaps": []}


def test_injected_js_facts_are_bound_to_source_and_selected_before_after(repository):
    root, _, _, _, _ = repository
    write(root, "src/app.js", b"function load() { return 1; }\n")
    base = commit(root, "JS before")
    write(root, "src/app.js", b"function load() { return 2; }\n")
    head = commit(root, "JS after")
    reader = adapter(root, js_reader)
    result = reader.read_change_file(base, head, "src/app.js", "repo://src/app.js#js/function/load")
    assert "return 1" in result["before"]["text"]
    assert "return 2" in result["after"]["text"]
    assert result["known_impact"]["after"]["status"] == "UNKNOWN_TARGET"
    row = reader.compare_commits(base, head)["files"][0]
    assert row["symbols"][0]["status"] == "changed"
    assert row["extraction"]["after"]["parser_version"] == "fixture-1"


def test_duplicate_js_reference_never_silently_selects_one_definition(repository):
    root, base, _, _, _ = repository
    write(root, "src/app.js", b"function load() {}\n")
    head = commit(root, "ambiguous JS fixture")

    def duplicate(path, data):
        result = js_reader(path, data)
        result["symbols"] *= 2
        return result

    result = adapter(root, duplicate).read_change_file(base, head, "src/app.js", "repo://src/app.js#js/function/load")
    assert result["status"] == "partial"
    assert result["after"]["status"] == "ambiguous"


def test_wrong_symbol_range_cannot_become_complete_extraction(repository):
    root, base, _, _, _ = repository
    write(root, "src/app.js", b"function load() {}\n")
    head = commit(root, "JS fixture")

    def wrong(path, data):
        result = js_reader(path, data)
        result["symbols"][0]["end_line"] = 999
        return result

    row = next(item for item in adapter(root, wrong).compare_commits(base, head)["files"] if item["path"] == "src/app.js")
    assert row["extraction"]["after"]["status"] == "PARTIAL"
    assert row["symbols"] == []


def test_diff_output_limit_is_not_reported_as_complete(repository, monkeypatch):
    root, base, head, _, _ = repository
    original = changes._git_read

    def capped(root_path, *args, **kwargs):
        if "diff" in args:
            raise changes._Unavailable("bounded output")
        return original(root_path, *args, **kwargs)

    monkeypatch.setattr(changes, "_git_read", capped)
    result = adapter(root).read_change_file(base, head, "src/example.py")
    assert result["status"] == "partial"
    assert result["unified_diff"]["status"] == "NOT_RUN"


def test_same_commit_is_an_explicit_empty_source_comparison(repository):
    root, _, head, _, _ = repository
    result = adapter(root).compare_commits(head, head)
    assert result["status"] == "available"
    assert result["files"] == []
    assert result["coverage"]["changed_paths_total"] == 0
    assert result["scope"]["behavior"] == "NOT_RUN by source comparison"


def test_unicode_source_and_escaped_path_are_exact(repository):
    root, base, _, _, _ = repository
    path = "src/naïve #q.py"
    content = "def example():\r\n    return 'héllo😀'\r\n".encode()
    write(root, path, content)
    head = commit(root, "unicode source")
    reference = "repo://src/na%C3%AFve%20%23q.py#example"
    result = adapter(root).read_change_file(base, head, path, reference)
    assert result["after"]["text"].encode() == content
    assert result["after"]["file_sha256"] == hashlib.sha256(content).hexdigest()


def test_sha256_git_object_format_is_supported(tmp_path):
    root = tmp_path / "sha256-target"
    root.mkdir()
    git(root, "init", "--quiet", "--initial-branch=main", "--object-format=sha256")
    git(root, "config", "user.name", "Disposable test")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    write(root, "src/example.py", b"def example():\n    return 1\n")
    base = commit(root, "before")
    write(root, "src/example.py", b"def example():\n    return 2\n")
    head = commit(root, "after")
    result = adapter(root).compare_commits(base, head)
    assert len(base) == len(head) == 64
    assert result["status"] == "available"
    assert result["files"][0]["symbols"][0]["status"] == "changed"


def test_malformed_reference_is_rejected_before_capture(repository, monkeypatch):
    root, base, head, _, _ = repository
    monkeypatch.setattr(changes, "_git_read", lambda *_args, **_kwargs: pytest.fail("malformed reference reached Git"))
    with pytest.raises(DomainError) as error:
        adapter(root).read_change_file(base, head, "src/example.py", {"bad": "reference"})
    assert error.value.code == "CHANGE_REFERENCE_DENIED"
