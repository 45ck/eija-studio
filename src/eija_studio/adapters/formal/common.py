"""Shared plumbing for the formal-report readers: find a report, hash sources, describe a missing prerequisite.

These adapters only READ what a tool wrote (or what a checkout contains) and copy raw fields into the
kernel's typed artifact shape. They compute no verdict: the kernel recomputes it (ADR-0145, ADR-0146).
Nothing here reads a clock, so an artifact is a pure function of the report and of the current sources.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from eija_studio.domain.formal import FormalArtifact


class NotRun(Exception):
    """A prerequisite is missing or a report cannot be read: the kind is NOT_RUN, never PASS."""

    def __init__(self, reason: str, prerequisite: str):
        super().__init__(reason)
        self.reason, self.prerequisite = reason, prerequisite


@dataclass(frozen=True)
class Report:
    origin: str  # path relative to the repository root, POSIX separators
    body: dict[str, Any]
    file_sha256: str


def lf_sha256(path: Path) -> str | None:
    """SHA-256 of a file with CRLF folded to LF, so a Windows and a POSIX checkout agree. None if unreadable."""
    try:
        return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return None


def read_reports(root: Path, candidates: tuple[str, ...]) -> list[Report]:
    """Every readable JSON report among the candidate paths, in the order given."""
    found = []
    for relative in candidates:
        path = root / relative
        if not path.is_file():
            continue
        try:
            raw = path.read_bytes()
            body = json.loads(raw.decode("utf-8"))
        except (OSError, ValueError) as error:
            raise NotRun(f"{relative} cannot be read as JSON ({type(error).__name__})", relative) from error
        if type(body) is not dict:
            raise NotRun(f"{relative} is not a JSON object", relative)
        found.append(Report(relative, body, hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()))
    return found


def not_run(kind: str, protocol: str, error: NotRun) -> FormalArtifact:
    return FormalArtifact(kind, {"protocol": protocol, "not_run": {"reason": error.reason, "prerequisite": error.prerequisite}}, {})


def measurements(report: Report) -> dict[str, Any]:
    """Wall-clock and platform facts about the run: recorded beside the artifact, never hashed into it."""
    body = report.body
    facts: dict[str, Any] = {"origin": report.origin, "report_file_sha256": report.file_sha256}
    raw = body.get("measurements")
    nested: dict[str, Any] = raw if type(raw) is dict else {}
    facts.update({k: nested[k] for k in ("platform", "python") if k in nested})
    facts.update({k: body[k] for k in ("platform", "python") if k in body})
    return facts


def current_sources(root: Path, relative: tuple[str, ...]) -> dict[str, str]:
    """LF-normalised SHA-256 of the kernel sources a report names, as they are in this checkout now."""
    base = root / "src" / "eija_studio"
    return {name: digest for name in relative if (digest := lf_sha256(base / name)) is not None}


def collect_from(kind: str, protocol: str, root: Path, candidates: tuple[str, ...], missing: NotRun,
                 extract: Callable[[Report], dict[str, Any]]) -> list[FormalArtifact]:
    """One artifact per readable report; a report that cannot be used becomes a NOT_RUN artifact of its own,
    so a stale or broken report never hides a good one and nothing is silently absent."""
    try:
        reports = read_reports(root, candidates)
    except NotRun as error:
        return [not_run(kind, protocol, error)]
    if not reports:
        return [not_run(kind, protocol, missing)]
    out = []
    for report in reports:
        try:
            out.append(FormalArtifact(kind, guarded(report, lambda r=report: extract(r)), measurements(report)))
        except NotRun as error:
            out.append(FormalArtifact(kind, not_run(kind, protocol, error).artifact, measurements(report)))
    return out


def guarded(report: Report, build: Any) -> dict[str, Any]:
    """Run an extractor; a report of an unexpected shape is NOT_RUN (unreadable), never a silent gap or a crash."""
    try:
        result: dict[str, Any] = build()
        return result
    except (KeyError, TypeError, IndexError, AttributeError) as error:
        raise NotRun(f"{report.origin} does not have the expected report shape ({type(error).__name__}: {error})",
                     report.origin) from error
