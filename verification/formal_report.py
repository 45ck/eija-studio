"""Shared plumbing for the `smt` and `bmc` evidence reports (no third-party imports).

Reports are JSON with sorted keys and LF endings. Wall-clock numbers live only under `measurements`,
so everything else is reproducible byte-for-byte for the same sources, seed and bounds.
"""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "src" / "eija_studio"


def lf_sha256(path: Path) -> str:
    """SHA-256 of the file with CRLF normalised, so a Windows checkout hashes like a Linux one."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def kernel_subject(*relative: str, function: str) -> dict[str, Any]:
    """Identify the kernel bytes a report is about. A hash names the bytes; it does not vouch for them."""
    return {"function": function, "sources_sha256_lf": {r: lf_sha256(KERNEL / r) for r in sorted(relative)}}


def platform_info() -> dict[str, str]:
    return {"platform": platform.platform(), "python": platform.python_version()}


def dumps(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(dumps(document).encode("utf-8"))


def not_run(kind: str, reason: str, subject: dict[str, Any]) -> dict[str, Any]:
    """A missing prerequisite is NOT_RUN, never PASS."""
    return {"schema": "eija.formal-report/v1", "kind": kind, "verdict": "NOT_RUN", "reason": reason,
            "subject": subject, "measurements": platform_info()}
