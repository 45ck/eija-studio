"""Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).

The kernel is the small trusted checker. An artifact (and the extractor that produced it, and any agent
that asked for it) is untrusted: a supplied green label is never read as a verdict. Each evidence kind
declares a typed artifact shape and a pure ``check`` that RECOMPUTES the verdict from the raw typed
content: law results, negative controls, declared minimum bounds, coverage and the binding to the
current subject. This module holds the vocabulary those checks share; the kinds live in
``formal_bend``, ``formal_smt`` and ``formal_bmc``, and ``evidence_kinds`` registers them.

Nothing here imports a vendor library, touches the file system or reads a clock.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

PASS, FAIL, STALE, UNKNOWN, NOT_RUN, CONFLICT = "PASS", "FAIL", "STALE", "UNKNOWN", "NOT_RUN", "CONFLICT"

# Who sealed the receipt: the application-side intake that wrapped an adapter's raw artifact.
FORMAL_PRODUCER = "eija-formal-intake"

# Evidence levels, weakest claim first in the words, strongest last. They are labels for the reader; no
# status is derived from them.
LEVEL_RECOMPUTED = "recomputed"  # the kernel re-derived the outcome from raw observations of its own semantics
LEVEL_SEALED_TOOL = "sealed_tool_verdict"  # a tool's verdict without a checkable certificate, under the sealed local producer

_DIGEST = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class FormalArtifact:
    """One raw formal artifact from a tool report. ``artifact`` is hashed; ``measurements`` (platform, timings)
    are recorded beside it and never hashed. The adapter copies what the tool said and computes no verdict."""
    kind: str
    artifact: dict[str, Any]
    measurements: dict[str, Any]


class Malformed(ValueError):
    """The artifact does not have the declared typed shape (a structural defect, judged FAIL)."""


@dataclass(frozen=True)
class Assessment:
    status: str
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class Context:
    """What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.

    ``candidate_semantic`` is ``Workflow.semantic_hash`` of the candidate under review and
    ``baseline_semantic`` that of the baseline; both are recomputed from the Workflow objects by the caller."""
    candidate_semantic: str
    baseline_semantic: str | None = None


@dataclass(frozen=True)
class KindSpec:
    """One evidence kind: what it claims, how it is checked, what it does not establish."""
    kind: str
    claim: str
    method: str
    protocol: str
    level: str
    establishes: str
    does_not_establish: tuple[str, ...]
    prerequisites: str
    check: Callable[[dict[str, Any], Context], Assessment]
    describe: Callable[[dict[str, Any]], dict[str, Any]]
    explain: Callable[[dict[str, Any], tuple[str, ...]], list[dict[str, Any]]]


class Findings:
    """Collects reasons by severity. Priority: STALE (about another subject), FAIL, UNKNOWN, else PASS."""

    def __init__(self) -> None:
        self._by: dict[str, list[str]] = {STALE: [], FAIL: [], UNKNOWN: []}

    def stale(self, why: str) -> None:
        self._by[STALE].append(why)

    def fail(self, why: str) -> None:
        self._by[FAIL].append(why)

    def unknown(self, why: str) -> None:
        self._by[UNKNOWN].append(why)

    def result(self) -> Assessment:
        for status in (STALE, FAIL, UNKNOWN):
            if self._by[status]:
                return Assessment(status, tuple(f"{s}: {why}" for s in (STALE, FAIL, UNKNOWN) for why in self._by[s]))
        return Assessment(PASS, ())


def field(container: Any, key: str, typ: type, where: str) -> Any:
    """``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed."""
    if type(container) is not dict or key not in container or type(container[key]) is not typ:
        raise Malformed(f"{where}.{key} must be a {typ.__name__}")
    return container[key]


def text(container: Any, key: str, where: str) -> str:
    value: str = field(container, key, str, where)
    if not value:
        raise Malformed(f"{where}.{key} must not be empty")
    return value


def digest(container: Any, key: str, where: str) -> str:
    value: str = field(container, key, str, where)
    if not _DIGEST.fullmatch(value):
        raise Malformed(f"{where}.{key} must be a lowercase sha256 hex digest")
    return value


def strings(container: Any, key: str, where: str, minimum: int = 1) -> list[str]:
    value = field(container, key, list, where)
    if len(value) < minimum or not all(type(x) is str and x for x in value):
        raise Malformed(f"{where}.{key} must be a list of at least {minimum} non-empty strings")
    return value  # type: ignore[no-any-return]


def has_items(container: Any, key: str, where: str) -> bool:
    """True if the list at ``key`` is not empty (its items may be of any type)."""
    return bool(field(container, key, list, where))


def records(container: Any, key: str, where: str) -> list[dict[str, Any]]:
    value = field(container, key, list, where)
    if not all(type(x) is dict for x in value):
        raise Malformed(f"{where}.{key} must be a list of objects")
    return value  # type: ignore[no-any-return]


def exact_keys(artifact: dict[str, Any], keys: frozenset[str]) -> None:
    if set(artifact) != keys:
        missing, extra = sorted(keys - set(artifact)), sorted(set(artifact) - keys)
        raise Malformed(f"artifact keys differ from the declared shape (missing {missing}, unexpected {extra})")


def carried_statements(artifact: dict[str, Any]) -> None:
    """The artifact must carry its own assumptions and limitations (a proof without them is not shown as one)."""
    strings(artifact, "assumptions", "artifact")
    strings(artifact, "limitations", "artifact")


def reported_labels(artifact: dict[str, Any], f: Findings) -> None:
    """The tool's own verdict and check labels may LOWER the status, never raise it.

    A PASS label is not evidence (the kernel recomputes from raw content), but a FAIL or an incomplete label
    the tool reported about itself (a drift check, a skipped self-test) is never ignored."""
    reported = field(artifact, "reported", dict, "artifact")
    verdict = text(reported, "verdict", "reported")
    if verdict == "FAIL":
        f.fail("the tool itself reported FAIL")
    elif verdict != "PASS":
        f.unknown(f"the tool reported {verdict}, which is not a pass")
    for check in records(reported, "checks", "reported"):
        status = text(check, "status", "check")
        if status == "FAIL":
            f.fail(f"the tool's own check {check.get('id')} failed")
        elif status != "PASS":
            f.unknown(f"the tool's own check {check.get('id')} is {status}")


def source_binding(binding: Any, required: tuple[str, ...], f: Findings) -> None:
    """Producer sources named by the tool's report versus the bytes the adapter observes now.

    ``current_sources_sha256_lf`` is observed by the sealed local adapter: attested, not recomputed here."""
    reported = field(binding, "reported_sources_sha256_lf", dict, "binding")
    current = field(binding, "current_sources_sha256_lf", dict, "binding")
    for name in required:
        if name not in reported:
            f.unknown(f"the tool's report does not name {name} among the sources it is about")
        elif current.get(name) is None:
            f.unknown(f"{name}: the current source could not be observed")
        elif reported[name] != current[name]:
            f.stale(f"{name} changed after the report was produced")


def not_run_reason(artifact: dict[str, Any]) -> Assessment:
    """A NOT_RUN artifact is exactly {protocol, not_run: {reason, prerequisite}}: honest absence, never PASS."""
    if set(artifact) != {"protocol", "not_run"}:
        raise Malformed("a NOT_RUN artifact must contain only its protocol and the not_run block")
    block = artifact["not_run"]
    reason, missing = text(block, "reason", "not_run"), text(block, "prerequisite", "not_run")
    if set(block) != {"reason", "prerequisite"}:
        raise Malformed("not_run may only carry reason and prerequisite")
    return Assessment(NOT_RUN, (f"NOT_RUN: {reason} (missing: {missing})",))


def as_records(value: Any) -> list[dict[str, Any]]:
    """Defensive view for display-only helpers: a list of dicts, or nothing."""
    return [x for x in value if type(x) is dict] if type(value) is list else []
