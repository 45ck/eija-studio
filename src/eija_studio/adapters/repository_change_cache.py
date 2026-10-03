"""Bounded retention eligibility and installed extractor prerequisite identity.

Retention is optional. Revalidation and request ordering remain with the Git
comparison adapter; these helpers neither read target source nor return it.
"""
from __future__ import annotations

import json
import stat
import sys
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, fields, is_dataclass
from importlib import metadata
from pathlib import Path
from typing import Any

from . import repository_analysis
from .repository_change_snapshot import _Comparison

CacheIdentity = tuple[Any, ...]
SyntaxReader = Callable[[str, bytes], dict[str, Any]]
# Retained payload bounds, not a claim about Python object overhead or process RSS.
MAX_CACHE_SOURCE_BYTES = 8 * 1024 * 1024
MAX_CACHE_METADATA_BYTES = 2 * 1024 * 1024
MAX_PREREQUISITE_FILES = 256
STABLE_SYNTAX_GAPS = frozenset({
    "SOURCE_UNPARSEABLE", "UNCLASSIFIED_DEFINITION", "DYNAMIC_ASSIGNMENT_TARGET",
    "UNCLASSIFIED_EXPORT", "UNCLASSIFIED_CLASS", "PARSE_ERROR", "SYMBOL_LIMIT", "DUPLICATE_REFERENCE",
})


@dataclass(frozen=True)
class _RetainedComparison:
    identity: CacheIdentity
    comparison: _Comparison



def _file_identity(path: Path) -> tuple[str, int, int, int]:
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Extractor prerequisite is not a regular file")
    return str(path), info.st_size, info.st_mtime_ns, info.st_ctime_ns



def _distribution_identity(name: str, expected: str) -> tuple[Any, ...]:
    distribution = metadata.distribution(name)
    installed = distribution.files
    if distribution.version != expected or not installed or len(installed) > MAX_PREREQUISITE_FILES:
        raise ValueError("Extractor prerequisites are unavailable or unsupported")
    return name, expected, tuple(_file_identity(Path(str(distribution.locate_file(item)))) for item in installed)



def _reader_prerequisites(reader: SyntaxReader | None) -> CacheIdentity | None:
    """Inspect the fixed worker's prerequisites without importing native parsers.

    Unknown injected readers are deliberately uncached: their prerequisites and
    mutable state are not described by the production adapter's contract.
    File availability/stat identity detects local installation changes; it is
    not cryptographic integrity verification or a guarantee the next parse runs.
    """
    if reader is None:
        return ("file_only",)
    if reader is not repository_analysis.syntax_reader:
        return None
    extractor = repository_analysis.extract_javascript
    script = Path(extractor.__file__).resolve()
    try:
        return (
            _distribution_identity("tree-sitter", extractor.PARSER_VERSION),
            _distribution_identity("tree-sitter-javascript", extractor.GRAMMAR_VERSION),
            tuple(_file_identity(path) for path in (
                script, script.with_name("_javascript_parser.py"),
                Path(repository_analysis.__file__).resolve(), Path(sys.executable),
            )),
        )
    except (metadata.PackageNotFoundError, OSError, ValueError, TypeError):
        return None



def _stable_facts(path: str, facts: dict[str, Any]) -> bool:
    if not path.endswith((".py", ".js")):
        return facts.get("method") == "file_only"
    return (facts.get("status") in {"EXTRACTED", "PARTIAL"}
            and facts.get("method") in {"python_ast", "python_ast_ast-v2", repository_analysis.extract_javascript.METHOD}
            and all(gap["reason"] in STABLE_SYNTAX_GAPS for gap in facts.get("gaps", [])))



def _cache_metadata(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: getattr(value, item.name) for item in fields(value)}
    if isinstance(value, bytes):
        return {"byte_length": len(value)}
    if isinstance(value, set):
        return sorted(value)
    raise TypeError("Unexpected comparison metadata")



def _cacheable(comparison: _Comparison, identity: CacheIdentity) -> bool:
    if comparison.gaps:
        return False
    sides = (comparison.before, comparison.after)
    if any(not _stable_facts(path, facts) for side in sides for path, facts in side.facts.items()):
        return False
    size = sum(len(data) for side in sides for data in side.capture.files.values())
    if size > MAX_CACHE_SOURCE_BYTES:
        return False
    # Stream the canonical encoding so oversized inventories do not allocate one
    # unbounded serialized string just to decide whether retention is permitted.
    encoder = json.JSONEncoder(default=_cache_metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    size = 0
    for chunk in encoder.iterencode(_RetainedComparison(identity, comparison)):
        size += len(chunk)
        if size > MAX_CACHE_METADATA_BYTES:
            return False
    return True



def _retention_candidate(comparison: _Comparison, identity: CacheIdentity,
                         generation: int | None) -> _RetainedComparison | None:
    if generation is None or identity[-1] is None:
        return None
    try:
        if _cacheable(comparison, identity):
            return _RetainedComparison(identity, deepcopy(comparison))
    except (TypeError, ValueError, RecursionError):
        # Retention is optional; a valid public result does not depend on it.
        return None
    return None
