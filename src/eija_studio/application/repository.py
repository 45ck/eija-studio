"""Read-only repository evidence port; this does not grant project execution or approval."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class RepositorySource(Protocol):
    """Evidence about one explicitly configured checkout and its declared domain bindings."""

    def snapshot(self) -> dict[str, Any]: ...
    def context(self) -> dict[str, Any]: ...
    def impact(self, subject: str) -> dict[str, Any]: ...
    def read_source(self, reference: str) -> dict[str, Any]: ...
    def freshness(self, file_hashes: Mapping[str, str]) -> dict[str, Any]: ...


def unconfigured_repository() -> dict[str, Any]:
    """An absent connection is visible, never an empty successful extraction."""
    return {"status": "unconfigured", "root": None, "read_only": True,
            "reason": "No repository root configured. Start Studio with an explicit --repo checkout root."}
