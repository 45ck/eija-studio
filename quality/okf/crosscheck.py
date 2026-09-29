"""Recompute every committed source hash of the bundle and report mismatches. Standard library only.

Run it under any interpreter to check that the ``ast-*`` hashes recorded in ``okf/`` do not depend on the
Python version that produced them::

    <python> quality/okf/crosscheck.py [--root <repo>]      # exit 0: every recorded hash reproduced

It deliberately avoids PyYAML: it reads the ``sources`` entries with a regular expression so it can run in a
bare interpreter. What a pass establishes: *this interpreter reproduces the committed hashes of these sources*.
It does not establish that the hashes are stable for every future program text or Python release.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_ENTRY = re.compile(r"^- resource: (?P<uri>repo://\S+)\n(?:  title: .*\n)?  hash_method: (?P<method>\S+)\n  sha256: (?P<sha>[0-9a-f]{64})$",
                    re.MULTILINE)


def _load_codelink():
    spec = importlib.util.spec_from_file_location("okf_codelink_under_test", HERE / "codelink.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module           # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def recorded_hashes(root: Path) -> list[tuple[str, str, str, str]]:
    """``(page, uri, method, sha256)`` for every code-linked source entry in the committed bundle."""
    found = []
    for page in sorted((root / "okf").rglob("*.md")):
        text = page.read_bytes().decode("utf-8").replace("\r\n", "\n")
        if not text.startswith("---\n"):
            continue
        frontmatter = text[4:text.index("\n---\n", 4)] if "\n---\n" in text[4:] else ""
        for match in _ENTRY.finditer(frontmatter):
            found.append((page.relative_to(root / "okf").as_posix(), match["uri"], match["method"], match["sha"]))
    return found


def mismatches(root: Path) -> tuple[int, list[str]]:
    """``(entries checked, human-readable mismatches)`` for this interpreter."""
    cl = _load_codelink()
    bad = []
    entries = recorded_hashes(root)
    for page, uri, method, sha in entries:
        try:
            current = cl.digest(root, cl.parse_uri(uri), method)
        except Exception as exc:                          # any failure is a mismatch, never a pass
            bad.append(f"{page}: {uri} ({method}): {type(exc).__name__}: {exc}")
            continue
        if current != sha:
            bad.append(f"{page}: {uri} ({method}): recorded {sha[:10]}, computed {current[:10]}")
    return len(entries), bad


def main(argv: list[str]) -> int:
    root = Path(argv[argv.index("--root") + 1]).resolve() if "--root" in argv else HERE.parents[1]
    checked, bad = mismatches(root)
    print(json.dumps({"python": ".".join(map(str, sys.version_info[:3])), "checked": checked, "mismatches": bad}, indent=1))
    return 1 if bad or not checked else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
