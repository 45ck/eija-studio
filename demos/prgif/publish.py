"""Publish a media file to the orphan `pr-media` branch under `pr/<n>/`, using git plumbing only.

The caller's HEAD, index and working tree are never touched: the file is written as a blob
(`hash-object -w`), the trees are rebuilt with `mktree`, the commit is made with `commit-tree` on top of the
remote branch tip (or as a root commit when the branch does not exist yet), and the commit is pushed by id.
A push that loses a race is retried on the new tip; nothing is ever force-pushed.
"""
from __future__ import annotations

import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

BRANCH = "pr-media"
MAX_BYTES = 5_000_000
ALLOWED_SUFFIXES = (".gif", ".png", ".jpg", ".jpeg", ".webp", ".mp4")
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
_GITHUB = re.compile(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$")
_README = (
    "# pr-media\n\n"
    "Orphan branch holding GIFs and screenshots embedded in pull requests, under `pr/<number>/`, so `main`\n"
    "never carries binary history. Written by `python -m demos pr-gif publish`; see\n"
    "docs/engineering/PR-STANDARD.md on main.\n"
)


class PublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class Published:
    path: str  # path inside the branch, e.g. pr/31/terminal.gif
    commit: str
    url: str | None  # raw.githubusercontent.com URL when the remote is on GitHub


def git(repo: Path, *args: str, stdin: bytes | None = None) -> str:
    # Fixed `git` argv built here; paths and names are validated before they reach it.
    result = subprocess.run(  # noqa: S603
        ["git", "-C", str(repo), *args], input=stdin, capture_output=True, check=False, timeout=300,  # noqa: S607
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise PublishError(f"git {' '.join(args[:2])} failed: {detail}")
    return result.stdout.decode("utf-8", "replace").strip()


def validate(file: Path, pr: int, name: str) -> None:
    if pr <= 0:
        raise PublishError(f"--pr must be a positive pull request number, got {pr}")
    if not _SAFE_NAME.match(name) or ".." in name:
        raise PublishError(f"unsafe file name {name!r}: use letters, digits, '.', '_' and '-' only")
    if not name.lower().endswith(ALLOWED_SUFFIXES):
        raise PublishError(f"{name!r} is not a media file ({', '.join(ALLOWED_SUFFIXES)})")
    if not file.is_file():
        raise PublishError(f"no such file: {file}")
    size = file.stat().st_size
    if size > MAX_BYTES:
        raise PublishError(f"{file} is {size} bytes; the PR standard allows at most {MAX_BYTES}")


def raw_url(remote_url: str, branch: str, path: str) -> str | None:
    match = _GITHUB.search(remote_url.strip())
    if not match:
        return None
    owner, repo = match.groups()
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"


def remote_tip(repo: Path, remote: str, branch: str) -> str | None:
    """Fetch the branch into its remote-tracking ref and return its commit, or None when it does not exist."""
    listed = git(repo, "ls-remote", "--heads", remote, f"refs/heads/{branch}")
    if not listed:
        return None
    tracking = f"refs/remotes/{remote}/{branch}"
    git(repo, "fetch", "--no-write-fetch-head", "--quiet", remote, f"+refs/heads/{branch}:{tracking}")
    return git(repo, "rev-parse", f"{tracking}^{{commit}}")


def _entries(repo: Path, tree: str | None) -> dict[str, str]:
    """name -> full `ls-tree` line for one tree level (empty for a missing tree)."""
    if tree is None:
        return {}
    out = git(repo, "ls-tree", "-z", tree)
    return {line.split("\t", 1)[1]: line for line in out.split("\0") if line}


def _subtree(repo: Path, tree: str | None, name: str) -> str | None:
    line = _entries(repo, tree).get(name)
    if line is None or " tree " not in line.split("\t", 1)[0]:
        return None
    return line.split()[2]


def put(repo: Path, tree: str | None, parts: Sequence[str], blob: str) -> str:
    """Return a new tree id equal to `tree` with the blob placed at `parts` (creating trees as needed)."""
    head, rest = parts[0], parts[1:]
    entries = _entries(repo, tree)
    if rest:
        child = put(repo, _subtree(repo, tree, head), rest, blob)
        entries[head] = f"040000 tree {child}\t{head}"
    else:
        entries[head] = f"100644 blob {blob}\t{head}"
    listing = "".join(f"{entries[key]}\0" for key in sorted(entries))
    return git(repo, "mktree", "-z", stdin=listing.encode("utf-8"))


def _commit(repo: Path, parent: str | None, blob: str, parts: Sequence[str], message: str) -> str:
    base = git(repo, "rev-parse", f"{parent}^{{tree}}") if parent else None
    if base is None:  # a new orphan branch starts with a README that explains it
        readme = git(repo, "hash-object", "-w", "--stdin", stdin=_README.encode("utf-8"))
        base = put(repo, None, ["README.md"], readme)
    tree = put(repo, base, parts, blob)
    parent_args = ["-p", parent] if parent else []
    return git(repo, "commit-tree", tree, *parent_args, "-m", message)


def publish(file: Path, pr: int, *, repo: Path, name: str | None = None, remote: str = "origin",
            branch: str = BRANCH, attempts: int = 3) -> Published:
    name = name or file.name
    validate(file, pr, name)
    blob = git(repo, "hash-object", "-w", "--no-filters", str(file.resolve()))
    parts = ["pr", str(pr), name]
    path = "/".join(parts)
    for attempt in range(attempts):
        parent = remote_tip(repo, remote, branch)
        commit = _commit(repo, parent, blob, parts, f"media: {path}")
        try:
            git(repo, "push", "--quiet", remote, f"{commit}:refs/heads/{branch}")
        except PublishError:
            if attempt == attempts - 1:
                raise
            continue  # someone else published first: rebuild on their tip, never force
        git(repo, "update-ref", f"refs/remotes/{remote}/{branch}", commit)
        return Published(path=path, commit=commit, url=raw_url(git(repo, "remote", "get-url", remote), branch, path))
    raise PublishError("unreachable")  # pragma: no cover
