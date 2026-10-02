"""Bounded repository reads adapted to the existing deterministic Weave engine.

Only tracked, non-ignored, permitted text files enter a temporary mirror. Weave never
receives the original checkout, so a declared binding cannot bypass those exclusions.
Git metadata commands do not run project code, hooks, filters, or external diff tools.
The trusted-local-user assumption still applies: this is not an OS security sandbox.
"""
from __future__ import annotations

import hashlib
import os
import stat
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from eija_studio.weave.index import WEB_SUFFIXES, dhash

from .providers.process import CliOutputLimit, CliShimUnsupported, CliTimeout, resolve_command, run_bounded

MAX_FILES = 5000
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 32 * 1024 * 1024
MAX_GIT_BYTES = 2 * 1024 * 1024
MAX_WORKTREES = 64
TEXT_SUFFIXES = frozenset({".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt", ".csv",
                           ".java", ".kt", ".go", ".rs", ".cs", ".c", ".h", ".cpp", ".hpp",
                           ".rb", ".php", ".swift", ".sh", ".ps1", ".sql", ".css", *WEB_SUFFIXES})
DATA_SUFFIXES = frozenset({".md", ".json", ".yaml", ".yml", ".toml", ".txt", ".csv", ".css"})
EXCLUDED_PARTS = frozenset({"node_modules", "vendor", "third_party", "vendored", "site-packages",
                            "build", "dist", "htmlcov", "__pycache__", "venv", "private", "secrets",
                            "credentials", "reports", "evidence", "downloads"})
PRIVATE_NAMES = frozenset({"auth.json", "credentials.json", "secrets.json", "secrets.py", "receipt.key",
                           "id_rsa", "id_ed25519", "token.json", "tokens.json", "config.local.json"})
UNSUPPORTED = "No symbol or behavior extraction for this language; file bindings and UI annotations only."


class _Unavailable(Exception):
    """A bounded read failed; the public result contains only a fixed reason."""


class _Excluded(Exception):
    """A file cannot be read under the capture policy."""


@dataclass
class _Capture:
    files: dict[str, bytes] = field(default_factory=dict)
    excluded: Counter[str] = field(default_factory=Counter)
    gaps: list[dict[str, str]] = field(default_factory=list)
    tracked: int = 0
    git: dict[str, Any] = field(default_factory=dict)

    @property
    def hashes(self) -> dict[str, str]:
        return {path: hashlib.sha256(data).hexdigest() for path, data in sorted(self.files.items())}

    @property
    def source_hash(self) -> str:
        return dhash("eija.repository.source.v1", [[path, digest] for path, digest in self.hashes.items()])


def _git(root: Path, *args: str, input_bytes: bytes | None = None, allow_empty: bool = False) -> bytes:
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update({"GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"})
    try:
        command = [*resolve_command("git"), "--no-optional-locks", "-c", "core.fsmonitor=false",
                   "-C", str(root), *args]
        result = run_bounded(command, input=input_bytes.decode("utf-8") if input_bytes else None,
                             env=env, timeout=10, max_bytes=MAX_GIT_BYTES)
    except (OSError, CliTimeout, CliOutputLimit, CliShimUnsupported) as error:
        raise _Unavailable("Git metadata is unavailable, timed out, or exceeded the bounded read limit.") from error
    if "\ufffd" in result.stdout:
        raise _Unavailable("Git metadata contains unsupported text encoding.")
    if result.returncode not in ({0, 1} if allow_empty else {0}):
        raise _Unavailable("Git metadata is unavailable for this checkout.")
    return result.stdout.encode("utf-8")


def _worktrees(data: bytes) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for entry in data.decode("utf-8", errors="replace").split("\0"):
        key, _, value = entry.partition(" ")
        if key == "worktree":
            if current:
                records.append(current)
            current = {"path": value}
        elif key in {"HEAD", "branch"}:
            current[key.lower()] = value.removeprefix("refs/heads/")
        elif key in {"detached", "bare", "locked", "prunable"}:
            current[key] = True
    if current:
        records.append(current)
    return sorted(records, key=lambda row: row["path"])[:MAX_WORKTREES]


def _metadata(root: Path) -> dict[str, Any]:
    head = _git(root, "rev-parse", "--verify", "--quiet", "HEAD", allow_empty=True).decode().strip()
    branch = _git(root, "symbolic-ref", "--short", "-q", "HEAD", allow_empty=True).decode().strip()
    changes = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=no", "--ignore-submodules=all")
    trees = _git(root, "worktree", "list", "--porcelain", "-z")
    return {"head": head or None, "branch": branch or None, "dirty": bool(changes),
            "untracked": "not inspected", "worktrees": _worktrees(trees), "worktree_limit": MAX_WORKTREES}


def _unsafe_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return not parts or path.startswith("/") or "\\" in path or any(p in {".", ".."} or ":" in p for p in parts)


def _path_reason(path: str) -> str | None:
    if _unsafe_path(path):
        return "unsafe_path"
    lower = tuple(p.casefold() for p in PurePosixPath(path).parts)
    if any(p.startswith(".") or p in EXCLUDED_PARTS or p.endswith(".egg-info") for p in lower):
        return "private_or_dependency_path"
    name = lower[-1]
    if _private_name(name):
        return "private_filename"
    if PurePosixPath(path).suffix.casefold() not in TEXT_SUFFIXES:
        return "unsupported_file_type"
    return None


def _private_name(name: str) -> bool:
    return name in PRIVATE_NAMES or any(word in name for word in ("credential", ".private.", ".secret."))


def _regular_file(root: Path, path: str) -> tuple[Path, os.stat_result]:
    target = root / path
    current = root
    for part in PurePosixPath(path).parts:
        current /= part
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise _Excluded("symlink_or_reparse_point")
    target.resolve(strict=True).relative_to(root)
    before = target.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink > 1:
        raise _Excluded("not_a_regular_single_link_file")
    if before.st_size > MAX_FILE_BYTES:
        raise _Excluded("file_size_limit")
    return target, before


def _read_file(root: Path, path: str) -> tuple[bytes | None, str | None]:
    try:
        target, before = _regular_file(root, path)
        with target.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
                return None, "changed_during_read"
            target.resolve(strict=True).relative_to(root)
            data = stream.read(MAX_FILE_BYTES + 1)
        after = target.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            return None, "changed_during_read"
        if len(data) > MAX_FILE_BYTES:
            return None, "file_size_limit"
        data.decode("utf-8")
        if b"\0" in data:
            return None, "binary_content"
        return data, None
    except _Excluded as error:
        return None, str(error)
    except UnicodeDecodeError:
        return None, "not_utf8"
    except (OSError, ValueError):
        return None, "missing_unreadable_or_outside_root"


def _capture_file(result: _Capture, root: Path, path: str, total: int) -> int:
    if len(result.files) >= MAX_FILES or total >= MAX_TOTAL_BYTES:
        result.excluded["capture_limit"] += 1
        return total
    data, reason = _read_file(root, path)
    if reason or data is None:
        result.excluded[reason or "unreadable"] += 1
        result.gaps.append({"path": path, "reason": reason or "unreadable"})
        return total
    if total + len(data) > MAX_TOTAL_BYTES:
        result.excluded["capture_limit"] += 1
        return total
    result.files[path] = data
    suffix = PurePosixPath(path).suffix
    if suffix not in {".py", ".html", ".htm", ".svg", *DATA_SUFFIXES}:
        result.gaps.append({"path": path, "reason": UNSUPPORTED})
    return total + len(data)


def _capture(root: Path) -> _Capture:
    if not root.is_dir():
        raise _Unavailable("The configured repository root does not exist or is not a directory.")
    top = _git(root, "rev-parse", "--show-toplevel").decode("utf-8", errors="strict").strip()
    if Path(top).resolve() != root:
        raise _Unavailable("Configure the Git checkout root, not a nested directory.")
    tracked = _git(root, "ls-files", "--cached", "-z")
    paths = sorted({p for p in tracked.decode("utf-8", errors="strict").split("\0") if p})
    ignored = _git(root, "check-ignore", "--no-index", "-z", "--stdin", input_bytes=tracked,
                   allow_empty=True) if tracked else b""
    ignored_paths = set(ignored.decode("utf-8", errors="strict").split("\0"))
    result = _Capture(tracked=len(paths), git=_metadata(root))
    total = 0
    for path in paths:
        reason = "git_ignored" if path in ignored_paths else _path_reason(path)
        if reason:
            result.excluded[reason] += 1
            continue
        total = _capture_file(result, root, path, total)
    if result.excluded.get("capture_limit"):
        result.gaps.append({"path": "", "reason": "Source capture limit reached; extraction is partial."})
    return result
