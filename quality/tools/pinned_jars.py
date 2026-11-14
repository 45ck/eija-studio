"""Fetch the pinned Java tools the full tier needs, verified against their recorded sha256.

    python -m quality.tools.pinned_jars alloy plantuml     # exit 0: every jar present and verified; 3: NOT_RUN

`formal_tla` has always downloaded its pinned jar (verification/tla/tlc.py). The Alloy (graph/formal/TOOLS.lock) and
PlantUML (verification/interop/plantuml_oracle.py) jars had only a manual `curl` in a docstring, so `graph_formal_full`
and `interop_plantuml` were NOT_RUN on every machine that had not run it by hand, the hosted nightly included. A jar
whose digest differs is never used: the file is removed and the gate stays NOT_RUN. A download failure is NOT_RUN
(exit 3), never a pass and never a crash; the gate itself then reports NOT_RUN as before.
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".tmp" / "tools"


def _alloy() -> tuple[str, str, Path]:
    lock = json.loads((ROOT / "graph" / "formal" / "TOOLS.lock").read_text(encoding="utf-8"))["alloy"]
    return lock["url"], lock["sha256"], TOOLS / f"alloy-{lock['release'].removeprefix('v')}.jar"  # graph/formal/run_alloy.py DEFAULT_JARS


def _plantuml() -> tuple[str, str, Path]:
    from verification.interop import plantuml_oracle as oracle  # noqa: PLC0415 - read only when asked for

    return oracle.JAR_URL, oracle.JAR_SHA256, TOOLS / oracle.JAR_NAME


JARS = {"alloy": _alloy, "plantuml": _plantuml}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure(name: str) -> str | None:
    """Return None when the jar is present and verified, else the NOT_RUN reason."""
    url, sha256, path = JARS[name]()
    if path.is_file() and _digest(path) == sha256:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    try:
        with urllib.request.urlopen(url, timeout=120) as response, partial.open("wb") as out:  # noqa: S310 - pinned https URL
            out.write(response.read())
    except OSError as exc:
        partial.unlink(missing_ok=True)
        return f"could not download {path.name} ({type(exc).__name__})"
    if _digest(partial) != sha256:
        partial.unlink()
        return f"{path.name} downloaded from {url} does not match its pinned sha256: not used"
    partial.replace(path)
    return None


def main(argv: list[str]) -> int:
    unknown = sorted(set(argv) - set(JARS))
    if not argv or unknown:
        sys.stderr.write(f"usage: python -m quality.tools.pinned_jars {{{','.join(JARS)}}} ...\n")
        return 2
    reasons = [f"NOT_RUN: {reason}" for name in argv if (reason := ensure(name))]
    for reason in reasons:
        sys.stdout.write(reason + "\n")
    return 3 if reasons else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
