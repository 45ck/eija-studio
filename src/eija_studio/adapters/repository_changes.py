"""Read-only, bounded comparison of two local Git commits.

This adapter coordinates capture, revalidation and optional retention. Captured
syntax/impact, snapshot projection and cache eligibility have separate owners.
Git supplies immutable blobs and the diff; compared code is never executed.
"""
from __future__ import annotations

import re
import sys
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Any

from eija_studio.domain.models import DomainError, fingerprint
from eija_studio.domain.pack import Pack

from . import repository_analysis as analysis
from .repository_analysis import SyntaxReader
from .repository_capture import MAX_FILE_BYTES, MAX_TOTAL_BYTES, _git, _path_reason, _Unavailable
from .repository_change_cache import CacheIdentity, _RetainedComparison, _reader_prerequisites, _retention_candidate
from .repository_change_snapshot import (
    SCHEMA, _Object, _Side, _Comparison, _file_record, _selected_row, _validate_selection,
    public_comparison, selected_side,
)

COMMIT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
MAX_CHANGED_FILES = 128
REGULAR_MODES = frozenset({"100644", "100755"})
POLICY = "changed-tracked-utf8-v1"


def _git_read(root: Path, *args: str, **kwargs: Any) -> bytes:
    return _git(root, "--no-replace-objects", *args, **kwargs)



def _validate_revision(value: str) -> None:
    if not isinstance(value, str) or COMMIT_ID.fullmatch(value) is None:
        raise DomainError("CHANGE_REVISION_INVALID", "Use a full lowercase local commit object ID")



def _validate_root(root: Path) -> None:
    if not root.is_dir():
        raise _Unavailable("The configured repository root is unavailable.")
    top = _git_read(root, "rev-parse", "--show-toplevel").decode().strip()
    if Path(top).resolve() != root:
        raise _Unavailable("Configure the Git checkout root, not a nested directory.")
    replacements = _git_read(root, "for-each-ref", "--format=%(refname)", "refs/replace/")
    if replacements.strip():
        raise _Unavailable("Commit comparison refuses repositories with replacement objects.")
    promisor = _git_read(root, "config", "--get-regexp", r"^(extensions\.partialclone|remote\..*\.promisor)$",
                         allow_empty=True)
    if promisor.strip():
        raise _Unavailable("Commit comparison requires complete local objects; promisor repositories are unsupported.")



def _tree(root: Path, commit: str) -> _Side:
    try:
        if _git_read(root, "cat-file", "-t", commit).strip() != b"commit":
            raise _Unavailable("not a commit")
        tree = _git_read(root, "rev-parse", "--verify", commit + "^{tree}").decode().strip()
        raw = _git_read(root, "ls-tree", "-r", "-z", "--full-tree", tree)
    except _Unavailable:
        raise DomainError("CHANGE_REVISION_UNAVAILABLE", "The requested local commit and tree are unavailable") from None
    inventory: dict[str, _Object] = {}
    for entry in raw.decode("utf-8").split("\0"):
        if not entry:
            continue
        metadata, path = entry.split("\t", 1)
        mode, kind, oid = metadata.split(" ")
        if COMMIT_ID.fullmatch(oid) is None or path in inventory:
            raise _Unavailable("Git returned an invalid tree inventory.")
        inventory[path] = _Object(mode, oid, kind)
    return _Side(commit, tree, inventory)



def _ignored_paths(root: Path, paths: list[str]) -> set[str]:
    if not paths:
        return set()
    raw = _git_read(root, "check-ignore", "--no-index", "-z", "--stdin",
                    input_bytes=("\0".join(paths) + "\0").encode(), allow_empty=True)
    return {path for path in raw.decode().split("\0") if path}



def _path_exclusion(comparison: _Comparison, path: str) -> str | None:
    reason = _path_reason(path)
    if reason is not None:
        return reason
    if path in comparison.ignored:
        return "git_ignored_current_policy"
    for side in (comparison.before, comparison.after):
        obj = side.inventory.get(path)
        if obj is not None and (obj.mode not in REGULAR_MODES or obj.kind != "blob"):
            return "symlink_gitlink_or_nonregular"
    return None



def _blob(root: Path, obj: _Object, remaining: int) -> bytes:
    size = int(_git_read(root, "cat-file", "-s", obj.oid).strip())
    if size > MAX_FILE_BYTES or size > remaining:
        raise _Unavailable("FILE_SIZE_LIMIT")
    data = _git_read(root, "cat-file", "blob", obj.oid)
    if len(data) != size:
        raise _Unavailable("BLOB_SIZE_MISMATCH")
    if b"\0" in data:
        raise _Unavailable("BINARY_CONTENT")
    # _git rejects replacement-decoded output, so re-encoded valid UTF-8 is exact.
    data.decode("utf-8", errors="strict")
    return data



class RepositoryChanges:
    """One configured repository, immutable commit reads, no store or authority port."""

    def __init__(self, root: Path, pack: Pack, *, syntax_reader: SyntaxReader | None = None) -> None:
        self.root, self.pack = root.expanduser().resolve(), pack
        self.syntax_reader = syntax_reader
        self._cache_lock = Lock()
        self._cache_generation = 0
        self._retained: _RetainedComparison | None = None

    def _cache_identity(self) -> CacheIdentity:
        return (
            str(self.root), self.pack.digest, tuple(sys.version_info[:3]),
            POLICY, MAX_CHANGED_FILES, MAX_FILE_BYTES, MAX_TOTAL_BYTES, analysis.MAX_SYMBOLS,
            id(analysis._python_facts), id(analysis.codelink._digest_text), id(analysis.codelink.parse_module), id(_path_reason), id(self.syntax_reader),
            _reader_prerequisites(self.syntax_reader),
        )

    def _begin_capture(self) -> int:
        with self._cache_lock:
            self._cache_generation += 1
            self._retained = None
            return self._cache_generation

    def _retain(self, retained: _RetainedComparison | None, generation: int | None) -> None:
        if retained is None:
            return
        with self._cache_lock:
            if generation == self._cache_generation:
                self._retained = retained

    def _reuse(self, base: str, head: str, identity: CacheIdentity) -> _Comparison | None:
        with self._cache_lock:
            retained = self._retained
        if retained is None or retained.identity != identity:
            return None
        comparison = retained.comparison
        if (comparison.before.commit, comparison.after.commit) != (base, head):
            return None
        _validate_root(self.root)
        if comparison.ignored != _ignored_paths(self.root, comparison.paths):
            return None
        # Retained state is never handed to callers or mutated. Copy outside the
        # short bookkeeping lock; every concurrent request owns its own state.
        return deepcopy(comparison)

    def _ensure_current(self, comparison: _Comparison, identity: CacheIdentity) -> None:
        _validate_root(self.root)
        if comparison.ignored != _ignored_paths(self.root, comparison.paths):
            raise _Unavailable("Repository ignore policy changed while the request was prepared; retry.")
        if self._cache_identity() != identity:
            raise _Unavailable("Comparison configuration or extractor prerequisites changed; retry.")

    def _detail_comparison(self, base: str, head: str) -> tuple[_Comparison, CacheIdentity, int | None]:
        _validate_revision(base)
        _validate_revision(head)
        identity = self._cache_identity()
        comparison = self._reuse(base, head, identity)
        if comparison is not None:
            return comparison, identity, None
        generation = self._begin_capture()
        return self._comparison(base, head), identity, generation

    def _capture_path(self, comparison: _Comparison, path: str, total: int) -> int:
        for side in (comparison.before, comparison.after):
            obj = side.inventory.get(path)
            if obj is None:
                continue
            try:
                data = _blob(self.root, obj, MAX_TOTAL_BYTES - total)
            except (_Unavailable, UnicodeError, ValueError):
                comparison.gaps.append({"path": path, "reason": "BLOB_UNAVAILABLE",
                                        "message": "A permitted blob is binary, oversized, unreadable or unsupported UTF-8."})
                continue
            side.capture.files[path] = data
            side.facts[path] = analysis._facts(path, data, self.syntax_reader)
            total += len(data)
        comparison.files.append(_file_record(comparison, path))
        return total

    def _comparison(self, base: str, head: str) -> _Comparison:
        _validate_revision(base)
        _validate_revision(head)
        _validate_root(self.root)
        before, after = _tree(self.root, base), _tree(self.root, head)
        paths = sorted(path for path in before.inventory.keys() | after.inventory.keys()
                       if before.inventory.get(path) != after.inventory.get(path))
        comparison = _Comparison(before, after, paths, ignored=_ignored_paths(self.root, paths))
        total = 0
        for path in paths:
            reason = _path_exclusion(comparison, path)
            if reason is None and len(comparison.files) >= MAX_CHANGED_FILES:
                reason = "changed_file_limit"
            if reason is not None:
                comparison.excluded[reason] += 1
                continue
            total = self._capture_path(comparison, path, total)
        if comparison.ignored != _ignored_paths(self.root, paths):
            raise _Unavailable("Repository ignore policy changed while the comparison was captured; retry.")
        return comparison

    def _public(self, comparison: _Comparison) -> dict[str, Any]:
        policy = {"id": POLICY, "max_changed_files": MAX_CHANGED_FILES, "max_file_bytes": MAX_FILE_BYTES,
                  "max_total_bytes": MAX_TOTAL_BYTES, "ignore": "current configured checkout policy",
                  "ignore_decision_hash": fingerprint(sorted(comparison.ignored))}
        return public_comparison(comparison, self.pack, _git_read(self.root, "--version").decode().strip(), policy)

    @staticmethod
    def _unavailable(error: _Unavailable) -> dict[str, Any]:
        return {"schema": SCHEMA, "status": "unavailable", "read_only": True, "reason": str(error),
                "scope": {"behavior": "NOT_RUN by source comparison", "semantic_complete": False}}

    def compare_commits(self, base: str, head: str) -> dict[str, Any]:
        """Compare exact local objects; a branch movement cannot change either side."""
        # Explicit compare is always fresh, including after a failed attempt.
        generation = self._begin_capture()
        try:
            identity = self._cache_identity()
            comparison = self._comparison(base, head)
            result = self._public(comparison)
            retained = _retention_candidate(comparison, identity, generation)
            self._ensure_current(comparison, identity)
            self._retain(retained, generation)
            return result
        except _Unavailable as error:
            return self._unavailable(error)

    def _impact(self, side: _Side, reference: str) -> dict[str, Any]:
        return analysis.known_impact(side, reference, self.pack, self.root)

    def _selected_side(self, side: _Side, path: str, reference: str | None) -> dict[str, Any] | None:
        return selected_side(side, path, reference)

    def read_change_file(self, base: str, head: str, path: str, reference: str | None = None) -> dict[str, Any]:
        """Return exact bounded sides of an already permitted changed file; never current-source fallback."""
        _validate_selection(path, reference)
        try:
            comparison, identity, generation = self._detail_comparison(base, head)
            row = _selected_row(comparison, path, reference)
            public = self._public(comparison)
            diff = self._diff(base, head, path, row)
            result_status = public["status"] if diff["status"] == "AVAILABLE" else "partial"
            result = {"schema": "eija.repository.change-file.v1", "status": result_status, "read_only": True,
                    "comparison_id": public["comparison_id"], "base": public["base"], "head": public["head"], "path": path,
                    "before": self._selected_side(comparison.before, path, reference),
                    "after": self._selected_side(comparison.after, path, reference), "unified_diff": diff,
                    "selected_reference": reference, "known_impact": {
                        "before": self._impact(comparison.before, reference or "repo://" + path),
                        "after": self._impact(comparison.after, reference or "repo://" + path)}}
            retained = _retention_candidate(comparison, identity, generation)
            self._ensure_current(comparison, identity)
            self._retain(retained, generation)
            return result
        except _Unavailable as error:
            return self._unavailable(error)

    def _diff(self, base: str, head: str, path: str, row: dict[str, Any]) -> dict[str, Any]:
        if any(side is not None and side["status"] != "captured" for side in (row["before"], row["after"])):
            return {"status": "NOT_RUN", "text": "", "reason": "Both present sides must be captured text.", "truncated": False}
        try:
            text = _git_read(self.root, "--literal-pathspecs", "-c", "core.quotePath=true", "diff", "--no-ext-diff", "--no-textconv",
                             "--no-renames", "--no-color", "--text", "--diff-algorithm=myers", "--no-indent-heuristic",
                             "--src-prefix=a/", "--dst-prefix=b/", "--unified=3", base, head, "--", path).decode("utf-8")
        except _Unavailable:
            return {"status": "NOT_RUN", "text": "", "reason": "The bounded Git diff is unavailable.", "truncated": False}
        return {"status": "AVAILABLE", "text": text, "context_lines": 3, "truncated": False}
