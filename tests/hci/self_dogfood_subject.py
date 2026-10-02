"""Content identity for the disposable replay, using bounded Git metadata reads."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
import sysconfig
from collections import Counter
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import PurePosixPath

from eija_studio.adapters.repository_capture import _git, _private_name, _unsafe_path

SCOPES = ("src", "packs", "tests/hci/self_dogfood_replay.py", "tests/hci/self_dogfood_subject.py")
GENERATED = {"__pycache__", "build", "dist"}
PRIVATE = {"private", "secrets", "credentials"}
DEPENDENCIES = ("eija-studio", "playwright", "axe-playwright-python", "fastapi", "uvicorn", "pydantic", "httpx")


def generated_part(part):
    return part.casefold() in GENERATED or part.endswith(".egg-info")


def excluded_path(name):
    parts = PurePosixPath(name).parts
    if _unsafe_path(name):
        return "unsafe_path"
    if any(generated_part(part) for part in parts):
        return "generated"
    if any(part.startswith(".") or part.casefold() in PRIVATE for part in parts):
        return "private"
    if _private_name(parts[-1].casefold()) or PurePosixPath(name).suffix.casefold() in {".key", ".pem", ".pfx", ".p12"}:
        return "private"
    return None


def file_identity(root, name):
    target = root
    for part in PurePosixPath(name).parts:
        target /= part
        info = target.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Link or reparse point in source manifest scope")
    target.resolve(strict=True).relative_to(root)
    before = target.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink > 1:
        raise ValueError("Source manifest entry is not a regular single-link file")
    with target.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError("Source file changed before its bytes were hashed")
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    after = target.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError("Source file changed while its bytes were hashed")
    return {"sha256": digest, "bytes": before.st_size}


def dependencies():
    result = {}
    for package in DEPENDENCIES:
        try:
            result[package] = version(package)
        except PackageNotFoundError:
            result[package] = "NOT_INSTALLED"
    return result


def capture_subject(root):
    """Hash public source bytes, including untracked files, without executing target code."""
    root = root.resolve()
    tracked = set(_git(root, "ls-files", "--cached", "-z", "--", *SCOPES).decode().split("\0"))
    all_names = _git(root, "ls-files", "--cached", "--others", "-z", "--", *SCOPES).decode().split("\0")
    changed = set(_git(root, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z",
                       "HEAD", "--", *SCOPES).decode().split("\0"))
    files, excluded = {}, Counter()
    for name in sorted(set(all_names) - {""}):
        reason = excluded_path(name)
        if reason:
            excluded[reason] += 1
            continue
        state = "untracked" if name not in tracked else "modified" if name in changed else "tracked"
        try:
            files[name] = file_identity(root, name) | {"git_state": state}
        except FileNotFoundError:
            files[name] = {"sha256": None, "bytes": None, "git_state": "missing"}
    content = {name: item["sha256"] for name, item in files.items()}
    return {"schema": "eija.browser-subject.v1", "utc": datetime.now(UTC).isoformat(),
            "git_head": _git(root, "rev-parse", "HEAD").decode().strip(),
            "checkout_dirty": bool(_git(root, "status", "--porcelain=v1", "--untracked-files=all")),
            "scope": list(SCOPES), "excluded_counts": dict(excluded), "files": files,
            "content_sha256": hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest(),
            "python": sys.version, "platform": sysconfig.get_platform(), "dependencies": dependencies(),
            "note": "HEAD names a base commit; listed bytes identify this possibly dirty run. Private paths are omitted."}


def compare_subjects(before, after):
    names = sorted(before["files"].keys() | after["files"].keys())
    changed = [name for name in names if before["files"].get(name, {}).get("sha256") !=
               after["files"].get(name, {}).get("sha256")]
    return {"status": "UNCHANGED" if not changed else "CHANGED", "changed_paths": changed,
            "scope": "Captured src, packs and replay bytes; private/generated paths excluded. Git staging is not a byte change."}
