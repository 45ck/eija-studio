"""`pr-gif publish` plumbing against a temporary local bare repository: no network, no GitHub.

What this proves: the file lands at pr/<n>/<name> on an orphan branch, earlier media survive, a missing branch is
created, and the caller's HEAD, index and working tree are untouched. What it does not prove: GitHub serving the
raw URL (that needs the network and a public repository).
"""
import subprocess

import pytest

from demos.prgif import publish
from demos.prgif import cli as pr_gif_cli
from demos.__main__ import main

GIF = b"GIF89a" + b"\x00" * 64


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def clone(tmp_path):
    """A caller's clone with a dirty working tree, whose origin is a local bare repository."""
    bare, work = tmp_path / "origin.git", tmp_path / "work"
    subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True)
    git(work, "config", "user.name", "Test"), git(work, "config", "user.email", "test@example.invalid")
    git(work, "config", "core.autocrlf", "false")
    (work / "app.py").write_text("print('hi')\n")
    git(work, "add", "app.py"), git(work, "commit", "-q", "-m", "init")
    git(work, "remote", "add", "origin", str(bare))
    git(work, "push", "-q", "origin", "main")
    (work / "app.py").write_text("print('dirty')\n")  # unstaged change
    (work / "staged.txt").write_text("staged\n")
    git(work, "add", "staged.txt")  # staged change
    return work, bare


def caller_state(work):
    return git(work, "rev-parse", "HEAD"), git(work, "status", "--porcelain"), git(work, "branch", "--show-current")


def media(tmp_path, name="demo.gif", data=GIF):
    path = tmp_path / name
    path.write_bytes(data)
    return path


def test_creates_the_orphan_branch_and_leaves_the_caller_untouched(clone, tmp_path):
    work, bare = clone
    before = caller_state(work)
    result = publish.publish(media(tmp_path), 31, repo=work)
    assert caller_state(work) == before
    assert result.path == "pr/31/demo.gif"
    assert git(bare, "cat-file", "-p", f"pr-media:{result.path}").startswith("GIF89a")
    assert "README.md" in git(bare, "ls-tree", "--name-only", "pr-media")
    # orphan: a root commit that shares no history with main
    assert git(bare, "rev-list", "--count", "pr-media") == "1"
    assert git(bare, "rev-list", "--max-parents=0", "pr-media") != git(bare, "rev-list", "--max-parents=0", "main")


def test_second_publish_keeps_earlier_media_and_appends_a_commit(clone, tmp_path):
    work, bare = clone
    publish.publish(media(tmp_path, "a.gif"), 31, repo=work)
    publish.publish(media(tmp_path, "b.gif"), 31, repo=work)
    publish.publish(media(tmp_path, "c.gif"), 40, repo=work)
    files = git(bare, "ls-tree", "-r", "--name-only", "pr-media").splitlines()
    assert {"pr/31/a.gif", "pr/31/b.gif", "pr/40/c.gif", "README.md"} <= set(files)
    assert git(bare, "rev-list", "--count", "pr-media") == "3"


def test_republishing_the_same_name_replaces_the_file(clone, tmp_path):
    work, bare = clone
    publish.publish(media(tmp_path, "x.gif", GIF + b"1"), 5, repo=work)
    publish.publish(media(tmp_path, "x.gif", GIF + b"2"), 5, repo=work)
    blob = subprocess.run(["git", "-C", str(bare), "cat-file", "blob", "pr-media:pr/5/x.gif"],
                          capture_output=True, check=True).stdout
    assert blob.endswith(b"2")


def test_bytes_are_stored_exactly(clone, tmp_path):
    work, bare = clone
    data = b"GIF89a\r\n\x00\xff" * 50  # CRLF-looking bytes must not be normalised
    publish.publish(media(tmp_path, "raw.gif", data), 9, repo=work)
    stored = subprocess.run(["git", "-C", str(bare), "cat-file", "blob", "pr-media:pr/9/raw.gif"],
                            capture_output=True, check=True).stdout
    assert stored == data


def test_builds_on_a_tip_published_from_another_clone(clone, tmp_path):
    work, bare = clone
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", str(bare), str(other)], check=True)
    git(other, "config", "user.name", "Other"), git(other, "config", "user.email", "o@example.invalid")
    publish.publish(media(tmp_path, "first.gif"), 1, repo=other)
    publish.publish(media(tmp_path, "second.gif"), 2, repo=work)  # work never fetched pr-media itself
    files = set(git(bare, "ls-tree", "-r", "--name-only", "pr-media").splitlines())
    assert {"pr/1/first.gif", "pr/2/second.gif"} <= files


@pytest.mark.parametrize("name", ["../evil.gif", "a/b.gif", ".hidden.gif", "notes.txt", "x..gif"])
def test_unsafe_or_non_media_names_are_refused(clone, tmp_path, name):
    work, _ = clone
    with pytest.raises(publish.PublishError):
        publish.publish(media(tmp_path), 3, repo=work, name=name)


def test_over_the_size_limit_is_refused(clone, tmp_path):
    work, bare = clone
    big = media(tmp_path, "big.gif", b"GIF89a" + b"\x00" * publish.MAX_BYTES)
    with pytest.raises(publish.PublishError, match="at most"):
        publish.publish(big, 3, repo=work)
    assert git(bare, "branch", "--list", "pr-media") == ""


def test_non_positive_pr_number_is_refused(clone, tmp_path):
    work, _ = clone
    with pytest.raises(publish.PublishError):
        publish.publish(media(tmp_path), 0, repo=work)


@pytest.mark.parametrize("remote", [
    "https://github.com/45ck/eija-studio.git", "git@github.com:45ck/eija-studio.git",
    "https://github.com/45ck/eija-studio",
])
def test_raw_url_for_github_remotes(remote):
    assert publish.raw_url(remote, "pr-media", "pr/7/a.gif") == \
        "https://raw.githubusercontent.com/45ck/eija-studio/pr-media/pr/7/a.gif"


def test_no_raw_url_for_a_non_github_remote():
    assert publish.raw_url("/tmp/origin.git", "pr-media", "pr/7/a.gif") is None  # noqa: S108 - a path-shaped string, never opened


def test_cli_publish_prints_the_result(clone, tmp_path, capsys):
    work, _ = clone
    code = main(["pr-gif", "publish", str(media(tmp_path)), "--pr", "12", "--repo", str(work)])
    out = capsys.readouterr().out
    assert code == 0 and "published pr/12/demo.gif" in out and "not on GitHub" in out


def test_cli_publish_failure_is_a_failure_exit(clone, tmp_path, capsys):
    work, _ = clone
    code = main(["pr-gif", "publish", str(tmp_path / "missing.gif"), "--pr", "12", "--repo", str(work)])
    assert code == pr_gif_cli.EXIT_FAIL and capsys.readouterr().out.startswith("FAIL")
