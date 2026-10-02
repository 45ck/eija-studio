"""Captured immutable comparison snapshots shared by capture, analysis and retention."""
from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from eija_studio.domain.models import DomainError, fingerprint
from eija_studio.domain.pack import Pack

from .repository import MAX_SOURCE_BYTES, MAX_SOURCE_LINES, SOURCE_CONTEXT_LINES
from .repository_capture import _Capture, _path_reason

SCHEMA = "eija.repository.change.v1"


@dataclass(frozen=True)
class _Object:
    mode: str
    oid: str
    kind: str



@dataclass
class _Side:
    commit: str
    tree: str
    inventory: dict[str, _Object]
    capture: _Capture = field(default_factory=_Capture)
    facts: dict[str, dict[str, Any]] = field(default_factory=dict)



@dataclass
class _Comparison:
    before: _Side
    after: _Side
    paths: list[str]
    files: list[dict[str, Any]] = field(default_factory=list)
    excluded: Counter[str] = field(default_factory=Counter)
    gaps: list[dict[str, str]] = field(default_factory=list)
    ignored: set[str] = field(default_factory=set)



def _symbol_status(left: dict[str, Any] | None, right: dict[str, Any] | None,
                   before_count: int, after_count: int) -> str:
    if before_count > 1 or after_count > 1:
        return "ambiguous"
    if left is None or right is None:
        return "added" if left is None else "removed"
    return "unchanged" if left["syntax_digest"] == right["syntax_digest"] else "changed"



def _symbol_changes(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    old, new = before.get("symbols", []), after.get("symbols", [])
    counts = Counter(item["reference"] for item in old), Counter(item["reference"] for item in new)
    previous = {item["reference"]: item for item in old}
    current = {item["reference"]: item for item in new}
    result = []
    for reference in sorted(previous.keys() | current.keys()):
        left, right = previous.get(reference), current.get(reference)
        status = _symbol_status(left, right, counts[0][reference], counts[1][reference])
        item = current[reference] if reference in current else previous[reference]
        result.append({"reference": reference, "kind": item["kind"], "status": status,
                       "before": left if counts[0][reference] == 1 else None,
                       "after": right if counts[1][reference] == 1 else None})
    return result



def _validate_selection(path: str, reference: str | None) -> None:
    if not isinstance(path, str) or _path_reason(path) is not None:
        raise DomainError("CHANGE_REFERENCE_DENIED", "Choose a permitted changed file or extracted reference")
    if reference is not None and (not isinstance(reference, str) or len(reference) > 800):
        raise DomainError("CHANGE_REFERENCE_DENIED", "Choose a permitted changed file or extracted reference")



def _selected_row(comparison: _Comparison, path: str, reference: str | None) -> dict[str, Any]:
    row = next((value for value in comparison.files if value["path"] == path), None)
    if row is None or (reference is not None and reference not in {item["reference"] for item in row["symbols"]}):
        raise DomainError("CHANGE_REFERENCE_DENIED", "Choose a permitted changed file or extracted reference")
    return row



def _file_side(side: _Side, path: str) -> dict[str, Any] | None:
    obj = side.inventory.get(path)
    if obj is None:
        return None
    data = side.capture.files.get(path)
    return {"blob": obj.oid, "mode": obj.mode, "file_sha256": hashlib.sha256(data).hexdigest() if data is not None else None,
            "byte_length": len(data) if data is not None else None,
            "status": "captured" if data is not None else "unavailable"}



def _file_record(comparison: _Comparison, path: str) -> dict[str, Any]:
    before, after = _file_side(comparison.before, path), _file_side(comparison.after, path)
    old_facts, new_facts = comparison.before.facts.get(path, {}), comparison.after.facts.get(path, {})
    return {"path": path, "status": "added" if before is None else "deleted" if after is None else "modified",
            "before": before, "after": after,
            "extraction": {"before": old_facts, "after": new_facts},
            "symbols": _symbol_changes(old_facts, new_facts)}



def _physical_lines(text: str) -> list[str]:
    # Python source positions count CR, LF and CRLF, not Unicode separators or
    # other string whitespace. Keep the original terminators and unterminated tail.
    return [line for line in re.findall(r"[^\r\n]*(?:\r\n|\r|\n|$)", text) if line]



def _excerpt(data: bytes, start: int = 1, end: int | None = None) -> dict[str, Any]:
    lines = _physical_lines(data.decode("utf-8"))
    last_requested = end or max(1, len(lines))
    first = max(1, start - SOURCE_CONTEXT_LINES)
    last = min(len(lines), last_requested + SOURCE_CONTEXT_LINES, first + MAX_SOURCE_LINES - 1)
    selected = "".join(lines[first - 1:last])
    text = selected.encode("utf-8")[:MAX_SOURCE_BYTES].decode("utf-8", errors="ignore")
    return {"text": text, "range": {"start": first, "end": first + max(1, len(_physical_lines(text))) - 1},
            "truncated": last < last_requested or text != selected,
            "snippet_sha256": hashlib.sha256(text.encode()).hexdigest()}



def selected_side(side: _Side, path: str, reference: str | None) -> dict[str, Any] | None:
    if path not in side.inventory:
        return None
    data = side.capture.files.get(path)
    if data is None:
        return {"status": "unavailable", "blob": side.inventory[path].oid}
    result = _file_side(side, path)
    if result is None:
        raise AssertionError("Captured source must have file metadata")
    if reference is None:
        return result | _excerpt(data)
    matches = [item for item in side.facts.get(path, {}).get("symbols", []) if item["reference"] == reference]
    if not matches:
        return {"status": "not_present", "blob": side.inventory[path].oid, "reference": reference}
    if len(matches) != 1:
        return {"status": "ambiguous", "blob": side.inventory[path].oid, "reference": reference}
    symbol = matches[0]
    return result | _excerpt(data, symbol["start_line"], symbol["end_line"]) | {"symbol": symbol}



def public_comparison(comparison: _Comparison, pack: Pack, git_version: str, policy: dict[str, Any]) -> dict[str, Any]:
    def subject(side: _Side) -> dict[str, str]:
        return {"commit": side.commit, "tree": side.tree, "changed_source_hash": side.capture.source_hash}
    identities = {"base": subject(comparison.before), "head": subject(comparison.after), "capture_policy": policy,
                  "pack_digest": pack.digest,
                  "git_version": git_version,
                  "syntax": [[row["path"], row["extraction"]] for row in comparison.files]}
    partial = bool(comparison.excluded or comparison.gaps)
    for row in comparison.files:
        if row["path"].endswith((".py", ".js")):
            partial |= any(facts.get("status") != "EXTRACTED" for facts in row["extraction"].values() if facts)
        partial |= any(item["status"] == "ambiguous" for item in row["symbols"])
    return {"schema": SCHEMA, "status": "partial" if partial else "available", "read_only": True,
            "comparison_id": fingerprint(identities), "base": identities["base"], "head": identities["head"],
            "capture_policy": policy, "pack": {"id": pack.id, "digest": pack.digest},
            "tools": {"git_version": identities["git_version"], "python_version": ".".join(map(str, sys.version_info[:3]))},
            "scope": {"capture": "Only permitted changed blobs from two immutable local trees.",
                      "behavior": "NOT_RUN by source comparison", "semantic_complete": False,
                      "rename_policy": "Deletion plus addition; no inferred symbol identity.",
                      "working_tree": "Not compared or executed."},
            "coverage": {"changed_paths_total": len(comparison.paths), "displayed_paths": len(comparison.files),
                         "excluded_by_reason": dict(sorted(comparison.excluded.items())),
                         "inventory_reconciles": len(comparison.paths) == len(comparison.files) + sum(comparison.excluded.values())},
            "files": comparison.files, "gaps": comparison.gaps}
