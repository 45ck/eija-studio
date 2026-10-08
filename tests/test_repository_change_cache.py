"""Retention counterexamples: real Git objects, no target code or browser execution."""
from __future__ import annotations

import base64
import hashlib
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Event
from types import SimpleNamespace

import pytest
from eija_studio.adapters import repository_changes as changes
from eija_studio.adapters import repository_analysis as analysis
from eija_studio.adapters import repository_change_cache as cache
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import default_pack
from test_repository_changes import commit, git, write

PATH = "src/example.py"
REFERENCE = "repo://src/example.py#example"


@pytest.fixture(scope="module")
def seed_repository(tmp_path_factory):
    root = tmp_path_factory.mktemp("retained-comparison-seed")
    git(root, "init", "--quiet", "--initial-branch=main")
    git(root, "config", "user.name", "Disposable retention test")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    write(root, PATH, b"def example():\n    return 'before'\n")
    write(root, "README.md", b"Before\n")
    base = commit(root, "before")
    write(root, PATH, b"def example():\n    return 'after'\n")
    write(root, "README.md", b"After\n")
    head = commit(root, "after")
    write(root, PATH, b"def example():\n    return 'later'\n")
    later = commit(root, "later")
    return root, base, head, later


@pytest.fixture
def repository(seed_repository, tmp_path):
    seed, base, head, later = seed_repository
    root = tmp_path / "target"
    shutil.copytree(seed, root)
    return root, base, head, later


def adapter(root, reader=None):
    return changes.RepositoryChanges(root, default_pack(), syntax_reader=reader)


def capture_counter(monkeypatch, reader):
    original = reader._comparison
    calls = []

    def counted(base, head):
        calls.append((base, head))
        return original(base, head)

    monkeypatch.setattr(reader, "_comparison", counted)
    return calls


def test_detail_reuses_but_explicit_compare_always_recaptures(repository, monkeypatch):
    root, base, head, _ = repository
    reader = adapter(root)
    calls = capture_counter(monkeypatch, reader)
    summary = reader.compare_commits(base, head)
    assert reader._retained is not None  # Ordinary non-code file-only facts are stable.
    first = reader.read_change_file(base, head, PATH, REFERENCE)
    second = reader.read_change_file(base, head, PATH, REFERENCE)
    assert first == second
    assert first["comparison_id"] == summary["comparison_id"]
    assert calls == [(base, head)]
    assert reader.compare_commits(base, head) == summary
    assert calls == [(base, head), (base, head)]


def test_cached_and_uncached_detail_payloads_are_identical(repository):
    root, base, head, _ = repository
    reader = adapter(root)
    reader.compare_commits(base, head)
    assert reader.read_change_file(base, head, PATH, REFERENCE) == adapter(root).read_change_file(
        base, head, PATH, REFERENCE
    )


def test_current_checkout_changes_do_not_replace_retained_immutable_source(repository, monkeypatch):
    root, base, head, _ = repository
    reader = adapter(root)
    summary = reader.compare_commits(base, head)
    calls = capture_counter(monkeypatch, reader)
    write(root, PATH, b"raise RuntimeError('must not execute current source')\n")
    result = reader.read_change_file(base, head, PATH)
    assert result["comparison_id"] == summary["comparison_id"]
    assert "return 'after'" in result["after"]["text"]
    assert calls == []


def test_returned_summary_and_detail_cannot_poison_retained_content(repository):
    root, base, head, _ = repository
    reader = adapter(root)
    summary = reader.compare_commits(base, head)
    expected = deepcopy(reader.read_change_file(base, head, PATH, REFERENCE))
    summary["files"].clear()
    summary["gaps"].append({"reason": "CLIENT_MUTATION"})
    summary["capture_policy"]["id"] = "client mutation"
    detail = reader.read_change_file(base, head, PATH, REFERENCE)
    detail["after"]["symbol"]["start_line"] = 999
    detail["after"]["text"] = "client mutation"
    detail["known_impact"].clear()
    assert reader.read_change_file(base, head, PATH, REFERENCE) == expected


@pytest.mark.parametrize("invalid", ["HEAD", "f" * 40])
def test_failed_comparison_clears_previous_entry(repository, monkeypatch, invalid):
    root, base, head, _ = repository
    reader = adapter(root)
    reader.compare_commits(base, head)
    calls = capture_counter(monkeypatch, reader)
    with pytest.raises(DomainError):
        reader.compare_commits(invalid, head)
    assert reader._retained is None
    reader.read_change_file(base, head, PATH)
    assert calls[-1] == (base, head)


def test_unavailable_comparison_clears_previous_entry(repository, monkeypatch):
    root, base, head, _ = repository
    reader = adapter(root)
    reader.compare_commits(base, head)
    git(root, "config", "remote.origin.promisor", "true")
    result = reader.compare_commits(base, head)
    assert result["status"] == "unavailable"
    assert reader._retained is None


def test_later_completed_pair_cannot_be_overwritten_by_older_inflight_compare(repository, monkeypatch):
    root, base, head, later = repository
    reader = adapter(root)
    original = reader._comparison
    captured, release = Event(), Event()

    def delayed(left, right):
        result = original(left, right)
        if right == head:
            captured.set()
            assert release.wait(10), "Coordinator did not release the bounded test"
        return result

    monkeypatch.setattr(reader, "_comparison", delayed)
    with ThreadPoolExecutor(max_workers=2) as pool:
        older = pool.submit(reader.compare_commits, base, head)
        try:
            assert captured.wait(10)
            newer = reader.compare_commits(head, later)
        finally:
            release.set()
        previous = older.result(timeout=10)
    assert previous["head"]["commit"] == head
    assert newer["head"]["commit"] == later
    assert reader._retained.comparison.after.commit == later
    assert reader.read_change_file(head, later, PATH)["comparison_id"] == newer["comparison_id"]


def test_failed_new_compare_prevents_old_inflight_capture_from_repopulating(repository, monkeypatch):
    root, base, head, _ = repository
    reader = adapter(root)
    original = reader._comparison
    captured, release = Event(), Event()

    def delayed(left, right):
        result = original(left, right)
        captured.set()
        assert release.wait(10)
        return result

    monkeypatch.setattr(reader, "_comparison", delayed)
    with ThreadPoolExecutor(max_workers=1) as pool:
        older = pool.submit(reader.compare_commits, base, head)
        try:
            assert captured.wait(10)
            with pytest.raises(DomainError):
                reader.compare_commits("HEAD", head)
        finally:
            release.set()
        assert older.result(timeout=10)["status"] == "available"
    assert reader._retained is None


def test_concurrent_details_keep_their_own_pair_and_defensive_copy(repository, monkeypatch):
    root, base, head, later = repository
    reader = adapter(root)
    old_summary = reader.compare_commits(base, head)
    original = reader._diff
    selected, release = Event(), Event()

    def delayed(left, right, path, row):
        if right == head:
            selected.set()
            assert release.wait(10)
        return original(left, right, path, row)

    monkeypatch.setattr(reader, "_diff", delayed)
    with ThreadPoolExecutor(max_workers=2) as pool:
        old_request = pool.submit(reader.read_change_file, base, head, PATH)
        try:
            assert selected.wait(10)
            new_detail = reader.read_change_file(head, later, PATH)
        finally:
            release.set()
        old_detail = old_request.result(timeout=10)
    assert old_detail["comparison_id"] == old_summary["comparison_id"]
    assert "return 'after'" in old_detail["after"]["text"]
    assert "return 'later'" in new_detail["after"]["text"]
    assert old_detail["comparison_id"] != new_detail["comparison_id"]
    assert reader._retained.comparison.after.commit == later


@pytest.mark.parametrize("policy", [".gitignore", ".git/info/exclude", "configured-global-excludes"])
def test_new_current_ignore_decision_cannot_disclose_cached_selected_path(repository, policy):
    root, base, head, _ = repository
    reader = adapter(root)
    reader.compare_commits(base, head)
    target = policy
    if policy == "configured-global-excludes":
        target = "local-excludes"
        git(root, "config", "core.excludesFile", str(root / target))
    write(root, target, (PATH + "\n").encode())
    with pytest.raises(DomainError) as error:
        reader.read_change_file(base, head, PATH)
    assert error.value.code == "CHANGE_REFERENCE_DENIED"
    assert reader._retained is None


def test_ignored_unselected_path_invalidates_full_comparison_identity(repository, monkeypatch):
    root, base, head, _ = repository
    reader = adapter(root)
    summary = reader.compare_commits(base, head)
    calls = capture_counter(monkeypatch, reader)
    write(root, ".gitignore", b"README.md\n")
    detail = reader.read_change_file(base, head, PATH)
    assert detail["comparison_id"] != summary["comparison_id"]
    assert calls == [(base, head)]


@pytest.mark.parametrize("warm", [False, True])
def test_ignore_change_after_diff_is_checked_before_any_content_return(repository, monkeypatch, warm):
    root, base, head, _ = repository
    reader = adapter(root)
    if warm:
        reader.compare_commits(base, head)
    original = reader._diff

    def change_policy(*args):
        result = original(*args)
        write(root, ".gitignore", (PATH + "\n").encode())
        return result

    monkeypatch.setattr(reader, "_diff", change_policy)
    result = reader.read_change_file(base, head, PATH)
    assert result["status"] == "unavailable"
    assert "before" not in result and "after" not in result


@pytest.mark.parametrize("restriction", ["replacement", "promisor"])
def test_current_root_restrictions_are_revalidated_before_reuse(repository, monkeypatch, restriction):
    root, base, head, _ = repository
    reader = adapter(root)
    reader.compare_commits(base, head)
    if restriction == "replacement":
        git(root, "replace", base, head)
    else:
        git(root, "config", "remote.origin.promisor", "true")
    monkeypatch.setattr(changes, "_blob", lambda *_args: pytest.fail("Restricted root reached a blob"))
    result = reader.read_change_file(base, head, PATH)
    assert result["status"] == "unavailable"
    assert "before" not in result and "after" not in result


def test_restriction_added_during_detail_is_checked_before_return(repository, monkeypatch):
    root, base, head, _ = repository
    reader = adapter(root)
    reader.compare_commits(base, head)
    original = reader._diff

    def change_root(*args):
        result = original(*args)
        git(root, "config", "remote.origin.promisor", "true")
        return result

    monkeypatch.setattr(reader, "_diff", change_root)
    result = reader.read_change_file(base, head, PATH)
    assert result["status"] == "unavailable"
    assert "after" not in result


@pytest.mark.parametrize("limit", ["MAX_CACHE_SOURCE_BYTES", "MAX_CACHE_METADATA_BYTES"])
def test_oversized_valid_comparison_succeeds_without_retention(repository, monkeypatch, limit):
    root, base, head, _ = repository
    expected = adapter(root).read_change_file(base, head, PATH)
    monkeypatch.setattr(cache, limit, 1)
    reader = adapter(root)
    assert reader.compare_commits(base, head)["status"] == "available"
    assert reader._retained is None
    assert reader.read_change_file(base, head, PATH) == expected
    assert reader._retained is None


def test_pack_change_invalidates_retained_subject(repository, monkeypatch):
    root, base, head, _ = repository
    reader = adapter(root)
    summary = reader.compare_commits(base, head)
    calls = capture_counter(monkeypatch, reader)
    reader.pack = reader.pack.model_copy(update={
        "pack": reader.pack.pack.model_copy(update={"description": "Different configured pack"})
    })
    detail = reader.read_change_file(base, head, PATH)
    assert detail["comparison_id"] != summary["comparison_id"]
    assert calls == [(base, head)]


def test_uncaptured_blob_failure_is_not_retained(repository, monkeypatch):
    root, base, head, _ = repository
    monkeypatch.setattr(changes, "MAX_FILE_BYTES", 1)
    reader = adapter(root)
    assert reader.compare_commits(base, head)["status"] == "partial"
    assert reader._retained is None


@pytest.fixture
def javascript_repository(repository):
    root, _, _, _ = repository
    write(root, "src/app.js", b"function load() { return 1; }\n")
    base = commit(root, "JS before")
    write(root, "src/app.js", b"function load() { return 2; }\n")
    head = commit(root, "JS after")
    return root, base, head


@pytest.fixture
def simulated_worker(monkeypatch, tmp_path):
    """Controlled worker/prerequisites for disappearance tests, not live parser proof."""
    binary = tmp_path / "simulated-parser.bin"
    binary.write_bytes(b"simulated installed parser")
    versions = {"tree-sitter": "0.26.0", "tree-sitter-javascript": "0.25.0"}

    def distribution(name):
        return SimpleNamespace(version=versions[name], files=[binary.name], locate_file=lambda _item: binary)

    monkeypatch.setattr(cache.metadata, "distribution", distribution)
    calls = []
    outcome = {"status": "EXTRACTED", "reason": None}

    def worker(_command, *, input, **_kwargs):
        request = json.loads(input)
        data = base64.b64decode(request["source_base64"])
        calls.append(request["path"])
        reason = outcome["reason"] if binary.exists() else "PARSER_UNAVAILABLE"
        status = outcome["status"] if binary.exists() else "NOT_RUN"
        symbols = [] if status == "NOT_RUN" else [{
            "reference": "repo://" + request["path"] + "#js/function/load", "kind": "function",
            "syntax_digest": hashlib.sha256(data).hexdigest(), "start_line": 1, "end_line": 1,
        }]
        response = {"status": status, "method": "js-tree-tokens-v1", "symbols": symbols,
                    "gaps": [{"reason": reason, "message": "Controlled fixture"}] if reason else [],
                    "parser_version": "0.26.0", "grammar_version": "0.25.0"}
        return SimpleNamespace(returncode=0, stdout=json.dumps(response))

    monkeypatch.setattr(analysis, "run_bounded", worker)
    return binary, versions, calls, outcome


def test_disappearing_binary_with_surviving_metadata_forces_reparse(javascript_repository, simulated_worker):
    root, base, head = javascript_repository
    binary, _, calls, _ = simulated_worker
    reader = adapter(root, analysis.syntax_reader)
    reader.compare_commits(base, head)
    assert reader._retained is not None
    assert len(calls) == 2
    binary.unlink()
    detail = reader.read_change_file(base, head, "src/app.js")
    assert detail["status"] == "partial"
    assert len(calls) == 4
    assert reader._retained is None
    assert "return 2" in detail["after"]["text"]


def test_prerequisite_loss_during_cached_detail_refuses_return(javascript_repository, simulated_worker, monkeypatch):
    root, base, head = javascript_repository
    binary, _, _, _ = simulated_worker
    reader = adapter(root, analysis.syntax_reader)
    reader.compare_commits(base, head)
    original = reader._diff

    def remove_prerequisite(*args):
        result = original(*args)
        binary.unlink()
        return result

    monkeypatch.setattr(reader, "_diff", remove_prerequisite)
    result = reader.read_change_file(base, head, "src/app.js")
    assert result["status"] == "unavailable"
    assert "before" not in result and "after" not in result


def test_changed_parser_version_invalidates_retention(javascript_repository, simulated_worker):
    root, base, head = javascript_repository
    _, versions, calls, _ = simulated_worker
    reader = adapter(root, analysis.syntax_reader)
    reader.compare_commits(base, head)
    versions["tree-sitter"] = "unvalidated-version"
    reader.read_change_file(base, head, "src/app.js")
    assert len(calls) == 4
    assert reader._retained is None


@pytest.mark.parametrize(("status", "reason", "retained"), [
    ("NOT_RUN", "PARSER_TIMEOUT", False),
    ("NOT_RUN", "PARSER_PROCESS_FAILED", False),
    ("PARTIAL", "PARSE_FAILED", False),
    ("PARTIAL", "UNCLASSIFIED_CLASS", True),
    ("PARTIAL", "PARSE_ERROR", True),
    ("PARTIAL", "DUPLICATE_REFERENCE", True),
])
def test_stable_scope_gaps_and_transient_failures_are_distinct(
    javascript_repository, simulated_worker, status, reason, retained
):
    root, base, head = javascript_repository
    _, _, _, outcome = simulated_worker
    outcome.update(status=status, reason=reason)
    reader = adapter(root, analysis.syntax_reader)
    assert reader.compare_commits(base, head)["status"] == "partial"
    assert (reader._retained is not None) is retained


def test_missing_js_hook_and_unknown_injected_hook_are_not_retained(javascript_repository):
    root, base, head = javascript_repository
    for hook in (None, lambda _path, _data: {"status": "EXTRACTED", "method": "unknown", "symbols": [], "gaps": []}):
        reader = adapter(root, hook)
        reader.compare_commits(base, head)
        assert reader._retained is None


def test_prerequisite_inventory_is_bounded(simulated_worker, monkeypatch):
    binary, _, _, _ = simulated_worker
    monkeypatch.setattr(cache.metadata, "distribution", lambda _name: SimpleNamespace(
        version="0.26.0", files=[binary.name] * (cache.MAX_PREREQUISITE_FILES + 1)
    ))
    assert changes._reader_prerequisites(analysis.syntax_reader) is None


def test_missing_distribution_metadata_disables_retention(monkeypatch):
    def absent(name):
        raise cache.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(cache.metadata, "distribution", absent)
    assert changes._reader_prerequisites(analysis.syntax_reader) is None
