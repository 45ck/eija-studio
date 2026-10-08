"""A selected historical filename must never expand to other Git pathspec matches."""
from __future__ import annotations

import json

import pytest
from test_repository_changes import adapter, commit, git, write
from test_repository_changes import repository as repository_fixture


@pytest.fixture
def literal_repository(tmp_path):
    return repository_fixture.__wrapped__(tmp_path)


def test_glob_named_file_diff_does_not_read_ignored_matching_neighbors(literal_repository):
    root, _, _, _, _ = literal_repository
    selected = "src/[ab].py"  # Brackets are valid filename characters on Windows and POSIX.
    before = b"def selected():\n    return 'selected before'\n"
    after = b"def selected():\n    return 'selected after'\n"
    canaries = {"src/a.py": "PRIVATE_A_PATHSPEC_CANARY", "src/b.py": "PRIVATE_B_PATHSPEC_CANARY"}
    write(root, ".gitignore", b"src/a.py\nsrc/b.py\n")
    write(root, selected, before)
    for path, canary in canaries.items():
        write(root, path, f"def hidden():\n    return '{canary} before'\n".encode())
    base = commit(root, "literal filename and intentionally tracked ignored neighbors")
    write(root, selected, after)
    for path, canary in canaries.items():
        write(root, path, f"def hidden():\n    return '{canary} after'\n".encode())
    head = commit(root, "change all three files")

    reader = adapter(root)
    summary = reader.compare_commits(base, head)
    assert [row["path"] for row in summary["files"]] == [selected]
    assert summary["coverage"]["excluded_by_reason"] == {"git_ignored_current_policy": 2}
    assert summary["coverage"]["inventory_reconciles"] is True

    result = reader.read_change_file(base, head, selected)
    assert result["comparison_id"] == summary["comparison_id"]
    assert result["before"]["text"].encode() == before
    assert result["after"]["text"].encode() == after
    assert result["unified_diff"]["status"] == "AVAILABLE"
    expected = git(root, "--literal-pathspecs", "-c", "core.quotePath=true", "diff", "--no-ext-diff",
                   "--no-textconv", "--no-renames", "--no-color", "--text", "--diff-algorithm=myers",
                   "--no-indent-heuristic", "--src-prefix=a/", "--dst-prefix=b/", "--unified=3",
                   base, head, "--", selected).decode()
    assert result["unified_diff"]["text"] == expected
    serialized = json.dumps(result)
    for path, canary in canaries.items():
        assert path not in serialized
        assert canary not in serialized
