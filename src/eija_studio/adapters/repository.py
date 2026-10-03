"""Repository analysis and bounded source navigation over captured checkout bytes."""
from __future__ import annotations

import hashlib
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import Pack
from eija_studio.weave.codelink import CodeRef, find_symbol, parse_module, parse_uri
from eija_studio.weave.impact import UnknownTarget, impact
from eija_studio.weave.index import Graph, build_index
from eija_studio.weave.rules import lint

from .repository_capture import _Capture, _Unavailable, _capture, _path_reason

SourceFactReader = Callable[[Mapping[str, bytes]], dict[str, Any]]

MAX_SOURCE_LINES = 200
MAX_SOURCE_BYTES = 32768
SOURCE_CONTEXT_LINES = 3


def _validate_snapshot_hash(value: str | None) -> None:
    if value is not None and (not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71
                              or any(character not in "0123456789abcdef" for character in value[7:])):
        raise DomainError("INVALID_SOURCE_HASH", "Use the exact sha256: source hash returned by the repository connection")


def _capture_at(root: Path, expected_source_hash: str | None) -> _Capture:
    """Compare against the very capture used for the answer, never a separate check/read pair."""
    _validate_snapshot_hash(expected_source_hash)
    captured = _capture(root)
    if expected_source_hash is not None and captured.source_hash != expected_source_hash:
        raise DomainError("SOURCE_SNAPSHOT_STALE", "Repository bytes changed. Refresh the source connection before following this snapshot's links.",
                          {"expected_source_hash": expected_source_hash, "source_hash": captured.source_hash,
                           "read_only": True, "scope": "Captured source bytes; no correctness or approval decision."})
    return captured


def _manifest_changes(current: Mapping[str, str], previous: Mapping[str, str]) -> dict[str, list[str]]:
    return {"changed": sorted(path for path in current.keys() & previous.keys() if current[path] != previous[path]),
            "added": sorted(current.keys() - previous.keys()), "removed": sorted(previous.keys() - current.keys())}


def _build(captured: _Capture, pack: Pack, root: Path) -> Graph:
    for term in pack.language.terms:
        for binding in term.binds:
            try:
                ref = parse_uri(binding)
            except ValueError as error:
                raise _Unavailable("The pack contains an unsafe repository binding path.") from error
            if ":" in ref.path or Path(ref.path).is_absolute():
                raise _Unavailable("The pack contains an unsafe repository binding path.")
    temporary_root = Path(tempfile.gettempdir()).resolve()
    if temporary_root == root or root in temporary_root.parents:
        raise _Unavailable("The temporary mirror directory must be outside the connected checkout.")
    with tempfile.TemporaryDirectory(prefix="eija-repository-", dir=temporary_root) as directory:
        mirror = Path(directory)
        for path, data in captured.files.items():
            target = mirror / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        try:
            graph = build_index(mirror, pack)
        except RecursionError:
            raise _Unavailable("Source syntax exceeds the bounded repository analysis depth.") from None
    graph.gaps = sorted(graph.gaps + captured.gaps, key=lambda row: (row["path"], row["reason"]))
    return graph


def _source_reference(reference: str) -> CodeRef:
    """Validate a reference without resolving any caller-supplied filesystem path."""
    try:
        if len(reference) > 800 or any(ord(character) < 32 for character in reference):
            raise ValueError("invalid reference")
        ref = parse_uri(reference)
        if _path_reason(ref.path) is not None:
            raise ValueError("excluded reference")
    except (TypeError, ValueError):
        raise DomainError("SOURCE_REFERENCE_DENIED", "Choose a captured source node or an explicit repository binding") from None
    return ref


def _known_source(ref: CodeRef, captured: _Capture, graph: Graph, pack: Pack) -> bool:
    if ref.path not in captured.files:
        return False
    if any(ref.uri() == binding for term in pack.language.terms for binding in term.binds):
        return True
    return ref.path.endswith(".py") and any(node["id"] == ref.uri() and node["type"] in {"module", "symbol", "test"}
                                            for node in graph.nodes)


def _source_span(ref: CodeRef, text: str) -> tuple[int, int, str | None]:
    """One-based AST range, or a file-only preview when no Python symbol was requested."""
    if not ref.path.endswith(".py") or ref.fragment is None:
        return 1, max(1, len(text.splitlines())), None
    try:
        fragment = unquote(ref.fragment, encoding="utf-8", errors="strict")
        node = find_symbol(parse_module(text, ref.path), fragment)
    except (SyntaxError, ValueError, RecursionError, UnicodeError):
        node = None
    if node is None:
        raise DomainError("SOURCE_REFERENCE_UNRESOLVED", "The requested Python symbol is absent from the current captured source")
    start = int(getattr(node, "lineno", 1))
    decorators = getattr(node, "decorator_list", ())
    start = min([start, *(int(decorator.lineno) for decorator in decorators)])
    return start, int(getattr(node, "end_lineno", start) or start), fragment


def _source_excerpt(ref: CodeRef, data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8")
    start, end, symbol = _source_span(ref, text)
    lines = text.splitlines(keepends=True)
    first = max(1, start - SOURCE_CONTEXT_LINES)
    last = min(len(lines), end + SOURCE_CONTEXT_LINES, first + MAX_SOURCE_LINES - 1)
    selected = "".join(lines[first - 1:last])
    bounded = selected.encode("utf-8")[:MAX_SOURCE_BYTES].decode("utf-8", errors="ignore")
    actual_last = first + max(1, len(bounded.splitlines())) - 1
    return {"symbol": symbol, "requested_fragment": ref.fragment,
            "symbol_lines": {"start": start, "end": end} if symbol else None,
            "lines": {"start": first, "end": actual_last}, "total_lines": max(1, len(lines)), "text": bounded,
            "fragment_resolution": "python_ast" if symbol else "file_only",
            "truncated": last < end or bounded != selected,
            "snippet_hash": hashlib.sha256(bounded.encode("utf-8")).hexdigest()}


class RepositoryConnection:
    """One configured checkout; every result is recomputed and never accepts binding baselines."""

    def __init__(self, root: Path, pack: Pack, *, source_facts: SourceFactReader | None = None) -> None:
        self.root = root.expanduser().resolve()
        self.pack = pack
        self.source_facts = source_facts

    def _observed_facts(self, files: Mapping[str, bytes]) -> dict[str, Any]:
        if self.source_facts is not None:
            return self.source_facts(files)
        return {"extraction": {"status": "NOT_RUN", "method": None, "executes_target": False,
                               "limitations": ["No implementation-fact profile matches the configured source bindings."]},
                "declared_model": {"pack_id": self.pack.id, "pack_digest": self.pack.digest,
                                   "status": "DECLARED_MODEL_ONLY", "scope": "Pack declarations only."},
                "conformance": {"status": "NOT_RUN", "reason": "No implementation-conformance verifier is configured."}}

    def _unavailable(self, reason: str) -> dict[str, Any]:
        return {"status": "unavailable", "root": str(self.root), "read_only": True,
                "reason": reason, "pack": {"id": self.pack.id, "digest": self.pack.digest},
                "lint": {"verdict": "NOT_RUN", "findings": [], "verdicts": {}, "not_run": []}}

    def snapshot(self) -> dict[str, Any]:
        """Hashes, declared links and actual Weave results; no source text or untracked file names."""
        try:
            captured = _capture(self.root)
            graph = _build(captured, self.pack, self.root)
        except (_Unavailable, UnicodeError) as error:
            reason = str(error) if isinstance(error, _Unavailable) else "Repository paths are not valid UTF-8."
            return self._unavailable(reason)
        checks = lint(graph, None)
        return {"status": "connected", "root": str(self.root), "read_only": True,
                "pack": {"id": self.pack.id, "digest": self.pack.digest}, "git": captured.git,
                "source_hash": captured.source_hash, "file_hashes": captured.hashes,
                "graph_hash": graph.root_hash, "summary": graph.counts(),
                "coverage": {"tracked_files": captured.tracked, "captured_files": len(captured.files),
                             "excluded": dict(sorted(captured.excluded.items())), "semantic_complete": False,
                             "scope": "Python AST, annotated UI elements, and explicit pack repo:// bindings.",
                             "limitations": ["No execution or test results are produced by indexing.",
                                             "Links express declared relationships, not inferred behavior.",
                                             "Untracked, ignored, private, dependency and binary files are excluded.",
                                             "No accepted-binding baseline was loaded or created."]},
                "gaps": graph.gaps, "nodes": graph.nodes, "edges": graph.edges,
                "observed_facts": self._observed_facts(captured.files),
                "bindings": [{"term": b.term, "target": b.target, "digest": b.digest,
                              "resolved": b.digest is not None} for b in graph.bindings],
                "lint": {"verdict": checks.verdict, "verdicts": checks.verdicts,
                         "findings": checks.findings, "not_run": checks.not_run}}

    def context(self) -> dict[str, Any]:
        """The same evidence envelope for an agent; no agent-specific stronger claims."""
        return self.snapshot()

    def read_source(self, reference: str, *, expected_source_hash: str | None = None) -> dict[str, Any]:
        """Read bounded text only from a known node/binding in one fresh safe capture; never execute the target."""
        ref = _source_reference(reference)
        try:
            captured = _capture_at(self.root, expected_source_hash)
            graph = _build(captured, self.pack, self.root)
        except (_Unavailable, UnicodeError) as error:
            reason = str(error) if isinstance(error, _Unavailable) else "Repository paths are not valid UTF-8."
            return self._unavailable(reason)
        if not _known_source(ref, captured, graph, self.pack):
            raise DomainError("SOURCE_REFERENCE_DENIED", "Choose a captured source node or an explicit repository binding")
        return {"status": "connected", "read_only": True, "reference": ref.uri(), "path": ref.path,
                "pack_digest": self.pack.digest, "file_hash": captured.hashes[ref.path],
                "source_hash": captured.source_hash, "graph_hash": graph.root_hash,
                "scope": "Current captured working-tree bytes; hashes identify this read, not correctness or future freshness.",
                **_source_excerpt(ref, captured.files[ref.path])}

    def impact(self, subject: str, *, expected_source_hash: str | None = None) -> dict[str, Any]:
        """Use the existing certified closure and witness paths over a fresh captured graph."""
        try:
            captured = _capture_at(self.root, expected_source_hash)
            graph = _build(captured, self.pack, self.root)
        except (_Unavailable, UnicodeError) as error:
            reason = str(error) if isinstance(error, _Unavailable) else "Repository paths are not valid UTF-8."
            return self._unavailable(reason)
        envelope: dict[str, Any] = {"status": "connected", "root": str(self.root), "pack_digest": self.pack.digest,
                    "source_hash": captured.source_hash, "graph_hash": graph.root_hash,
                    "scope": "Declared Weave links only; unknown real-world dependencies are not covered.",
                    "gaps": graph.gaps}
        try:
            envelope["impact"] = impact(graph, subject)
        except UnknownTarget:
            envelope.update({"status": "unknown_target", "reason": "Subject is not in the captured graph."})
        return envelope

    def freshness(self, file_hashes: Mapping[str, str] | None = None, *,
                  expected_source_hash: str | None = None) -> dict[str, Any]:
        """Compare captured hashes without ever resolving paths supplied by the caller."""
        _validate_snapshot_hash(expected_source_hash)
        if file_hashes is None and expected_source_hash is None:
            raise DomainError("INVALID_SOURCE_HASH", "Provide the captured snapshot hash to check freshness")
        try:
            captured = _capture(self.root)
        except (_Unavailable, UnicodeError) as error:
            reason = str(error) if isinstance(error, _Unavailable) else "Repository paths are not valid UTF-8."
            return self._unavailable(reason)
        current = captured.hashes
        if file_hashes is None:
            return {"status": "current" if captured.source_hash == expected_source_hash else "stale",
                    "compared_source_hash": expected_source_hash, "source_hash": captured.source_hash,
                    "read_only": True, "changed": None, "added": None, "removed": None,
                    "scope": "Captured byte identity at this check; changed paths require both file manifests. Not correctness or approval."}
        changes = _manifest_changes(current, file_hashes)
        different_hash = expected_source_hash is not None and captured.source_hash != expected_source_hash
        return {"status": "stale" if any(changes.values()) or different_hash else "current", **changes,
                "source_hash": captured.source_hash,
                "compared_source_hash": expected_source_hash, "read_only": True,
                "scope": "Captured file bytes only; this is not a correctness or approval check."}
