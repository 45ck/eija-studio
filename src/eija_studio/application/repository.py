"""Read-only repository evidence port; this does not grant project execution or approval."""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Protocol

from eija_studio.domain.models import DomainError


COMMIT_OID_PATTERN = r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$"


class RepositoryChangeSource(Protocol):
    """Immutable, read-only facts for an explicit pair in one configured repository."""

    def compare_commits(self, base: str, head: str) -> dict[str, Any]: ...
    def read_change_file(self, base: str, head: str, path: str,
                         reference: str | None = None) -> dict[str, Any]: ...


def validate_change_revisions(base: str, head: str) -> None:
    """Validate full object IDs before calling any configured repository port."""
    if any(not isinstance(value, str) or re.fullmatch(COMMIT_OID_PATTERN, value) is None
           for value in (base, head)):
        raise DomainError("CHANGE_REVISION_INVALID", "Use a full lowercase local commit object ID")


def unconfigured_repository_changes() -> dict[str, Any]:
    """No comparison connection is not a successful empty code change."""
    return {"schema": "eija.repository.change.v1", "status": "unconfigured", "read_only": True,
            "reason": "Start with --repo PATH to compare local commits"}


def compare_repository_changes(source: RepositoryChangeSource | None, base: str, head: str) -> dict[str, Any]:
    """Validate an immutable comparison request before dispatch to its read-only port."""
    validate_change_revisions(base, head)
    if source is None:
        return unconfigured_repository_changes()
    return source.compare_commits(base, head)


def read_repository_change_file(source: RepositoryChangeSource | None, base: str, head: str, path: str,
                                reference: str | None = None) -> dict[str, Any]:
    """Bound the historical selection before dispatch; absence never bypasses validation."""
    validate_change_revisions(base, head)
    if (not isinstance(path, str) or not 1 <= len(path) <= 1024 or "\x00" in path
            or (reference is not None and (not isinstance(reference, str) or not 1 <= len(reference) <= 800))):
        raise DomainError("CHANGE_REFERENCE_DENIED", "Choose a permitted changed file or extracted reference")
    if source is None:
        return unconfigured_repository_changes()
    return source.read_change_file(base, head, path, reference)


class RepositorySource(Protocol):
    """Evidence about one explicitly configured checkout and its declared domain bindings."""

    def snapshot(self) -> dict[str, Any]: ...
    def context(self) -> dict[str, Any]: ...
    def impact(self, subject: str, *, expected_source_hash: str | None = None) -> dict[str, Any]: ...
    def read_source(self, reference: str, *, expected_source_hash: str | None = None) -> dict[str, Any]: ...
    def freshness(self, file_hashes: Mapping[str, str] | None = None, *,
                  expected_source_hash: str | None = None) -> dict[str, Any]: ...


def unconfigured_repository() -> dict[str, Any]:
    """An absent connection is visible, never an empty successful extraction."""
    return {"status": "unconfigured", "root": None, "read_only": True,
            "reason": "No repository root configured. Start Studio with an explicit --repo checkout root."}
