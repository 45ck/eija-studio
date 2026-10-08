"""Historical pages remain visible without weakening active-source hash checks."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from quality.okf import crosscheck

SOURCE = "The active source.\n"
SOURCE_SHA = hashlib.sha256(SOURCE.encode()).hexdigest()


def _page(root, name="active", *, status="status: stable\n", uri="repo://source.txt", sha=SOURCE_SHA):
    bundle = root / "okf"
    bundle.mkdir(exist_ok=True)
    path = bundle / f"{name}.md"
    path.write_text(
        f"---\ntype: Module\n{status}sources:\n- resource: {uri}\n"
        f"  title: Source\n  hash_method: lf-sha256-v1\n  sha256: {sha}\n---\nBody\n",
        encoding="utf-8", newline="\n",
    )
    return path


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "source.txt").write_text(SOURCE, encoding="utf-8", newline="\n")
    _page(tmp_path)
    return tmp_path


def _report(root, capsys):
    result = crosscheck.main(["--root", str(root)])
    return result, json.loads(capsys.readouterr().out)


def test_inventory_preserves_historical_entries_and_order(repo):
    _page(repo, "archive", status="status: deprecated\n", uri="repo://removed.txt", sha="0" * 64)
    entries = crosscheck.recorded_hashes(repo)
    assert entries == [
        ("active.md", "repo://source.txt", "lf-sha256-v1", SOURCE_SHA),
        ("archive.md", "repo://removed.txt", "lf-sha256-v1", "0" * 64),
    ]
    assert crosscheck.mismatches(repo) == (1, [])


@pytest.mark.parametrize("status", [
    "status: deprecated\n", "status: 'deprecated'\n", 'status: "deprecated"\n',
    "status: deprecated # retained history\n",
])
def test_report_excludes_and_identifies_each_historical_source(repo, capsys, status):
    _page(repo, "archive", status=status, uri="repo://removed.txt")
    _page(repo, "old-hash", status=status, sha="0" * 64)
    result, report = _report(repo, capsys)
    assert result == 0 and report["status"] == "PASS"
    assert report["checked"] == 1 and report["mismatches"] == [] and report["not_run"] == []
    assert report["excluded_deprecated_count"] == 2
    assert report["excluded_deprecated"] == [
        "archive.md: repo://removed.txt (lf-sha256-v1)",
        "old-hash.md: repo://source.txt (lf-sha256-v1)",
    ]


@pytest.mark.parametrize("status", [
    "", "status: stable\n", "status: draft\n", "status: unknown\n",
    "metadata:\n  status: deprecated\n", "# status: deprecated\n",
    "status: stable\nstatus: deprecated\n", "status: deprecated-suffix\n",
    "status:deprecated\n",
])
def test_only_an_unambiguous_top_level_deprecated_status_excludes(repo, capsys, status):
    _page(repo, status=status, sha="0" * 64)
    result, report = _report(repo, capsys)
    assert result == 1 and report["status"] == "FAIL"
    assert report["checked"] == 1 and len(report["mismatches"]) == 1
    assert report["excluded_deprecated_count"] == 0 and report["not_run"] == []


def test_body_text_cannot_exclude_an_active_page(repo, capsys):
    path = _page(repo, sha="0" * 64)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("status: deprecated\n")
    result, report = _report(repo, capsys)
    assert result == 1 and report["checked"] == 1 and len(report["mismatches"]) == 1
    assert report["excluded_deprecated_count"] == 0


@pytest.mark.parametrize("missing", [False, True])
def test_active_failure_still_fails_alongside_deprecated_history(repo, capsys, missing):
    _page(repo, "archive", status="status: deprecated\n", uri="repo://removed.txt")
    if missing:
        (repo / "source.txt").unlink()
    else:
        (repo / "source.txt").write_text("Changed.\n", encoding="utf-8", newline="\n")
    result, report = _report(repo, capsys)
    assert result == 1 and report["status"] == "FAIL" and report["checked"] == 1
    assert len(report["mismatches"]) == 1 and report["mismatches"][0].startswith("active.md:")
    assert report["excluded_deprecated_count"] == 1 and report["not_run"] == []


@pytest.mark.parametrize("historical", [False, True])
def test_no_active_entries_is_not_run_and_nonzero(tmp_path, capsys, historical):
    if historical:
        _page(tmp_path, "archive", status="status: deprecated\n", uri="repo://removed.txt")
    result, report = _report(tmp_path, capsys)
    assert result == 1 and report["status"] == "NOT_RUN"
    assert report["checked"] == 0 and report["mismatches"] == []
    assert report["excluded_deprecated_count"] == int(historical)
    assert report["not_run"] == ["No active recorded source hashes found; hash stability is unverified."]


def test_multiple_sources_on_one_deprecated_page_are_counted_as_entries(repo, capsys):
    path = _page(repo, "archive", status="status: deprecated\n", uri="repo://removed.txt")
    text = path.read_text(encoding="utf-8")
    other = f"- resource: repo://other.txt\n  hash_method: lf-sha256-v1\n  sha256: {'0' * 64}\n"
    path.write_text(text.replace("\n---\nBody", f"\n{other}---\nBody"), encoding="utf-8", newline="\n")
    result, report = _report(repo, capsys)
    assert result == 0 and report["checked"] == 1
    assert report["excluded_deprecated_count"] == 2 and len(report["excluded_deprecated"]) == 2


def test_cli_runs_under_a_bare_isolated_interpreter(repo):
    _page(repo, "archive", status="status: deprecated\n", uri="repo://removed.txt")
    done = subprocess.run(
        [sys.executable, "-I", "-S", str(Path(crosscheck.__file__).resolve()), "--root", str(repo)],
        capture_output=True, text=True, timeout=15, check=False,
    )
    report = json.loads(done.stdout)
    assert done.returncode == 0 and report["status"] == "PASS" and report["checked"] == 1
    assert report["mismatches"] == [] and report["excluded_deprecated_count"] == 1
