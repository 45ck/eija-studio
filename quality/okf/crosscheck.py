"""Recompute active committed source hashes and report mismatches. Standard library only.

Run it under any interpreter to check that the ``ast-*`` hashes recorded in ``okf/`` do not depend on the
Python version that produced them::

    <python> quality/okf/crosscheck.py [--root <repo>]      # exit 0: every active recorded hash reproduced

It deliberately avoids PyYAML: it reads the generated frontmatter with regular expressions so it can run
in a bare interpreter. Deprecated pages retain historical hashes of potentially removed sources; like the
normal code-link gate, this check excludes them and reports every excluded source entry. A run with no
active entries is NOT_RUN and exits nonzero, never PASS.

What a pass establishes: *this interpreter reproduces the active committed hashes of these sources*.
It does not establish page conformance, prose correctness or stability for every future text/Python release.
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
_STATUS = re.compile(r"^status:", re.MULTILINE)
_DEPRECATED = re.compile(r"""^status:[ \t]+(?:deprecated|'deprecated'|"deprecated")[ \t]*(?:\#[^\n]*)?$""", re.MULTILINE)
HashEntry = tuple[str, str, str, str]


def _load_codelink():
    spec = importlib.util.spec_from_file_location("okf_codelink_under_test", HERE / "codelink.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module           # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def _recorded_sources(root: Path) -> list[tuple[HashEntry, bool]]:
    found = []
    for page in sorted((root / "okf").rglob("*.md")):
        text = page.read_bytes().decode("utf-8").replace("\r\n", "\n")
        if not text.startswith("---\n"):
            continue
        frontmatter = text[4:text.index("\n---\n", 4)] if "\n---\n" in text[4:] else ""
        # Only an unambiguous top-level status excludes a page. This is not a YAML conformance check.
        deprecated = len(_STATUS.findall(frontmatter)) == 1 and _DEPRECATED.search(frontmatter) is not None
        for match in _ENTRY.finditer(frontmatter):
            entry = (page.relative_to(root / "okf").as_posix(), match["uri"], match["method"], match["sha"])
            found.append((entry, deprecated))
    return found


def recorded_hashes(root: Path) -> list[HashEntry]:
    """``(page, uri, method, sha256)`` inventory, including retained deprecated source entries."""
    return [entry for entry, _deprecated in _recorded_sources(root)]


def _check(root: Path) -> tuple[int, list[str], list[str]]:
    cl = _load_codelink()
    bad = []
    excluded = []
    checked = 0
    for (page, uri, method, sha), deprecated in _recorded_sources(root):
        if deprecated:
            excluded.append(f"{page}: {uri} ({method})")
            continue
        checked += 1
        try:
            current = cl.digest(root, cl.parse_uri(uri), method)
        except Exception as exc:                          # any active source failure is a mismatch, never a pass
            bad.append(f"{page}: {uri} ({method}): {type(exc).__name__}: {exc}")
            continue
        if current != sha:
            bad.append(f"{page}: {uri} ({method}): recorded {sha[:10]}, computed {current[:10]}")
    return checked, bad, excluded


def mismatches(root: Path) -> tuple[int, list[str]]:
    """``(active entries checked, human-readable mismatches)`` for this interpreter."""
    checked, bad, _excluded = _check(root)
    return checked, bad


def main(argv: list[str]) -> int:
    root = Path(argv[argv.index("--root") + 1]).resolve() if "--root" in argv else HERE.parents[1]
    checked, bad, excluded = _check(root)
    not_run = ["No active recorded source hashes found; hash stability is unverified."] if not checked else []
    status = "NOT_RUN" if not_run else "FAIL" if bad else "PASS"
    print(json.dumps({"python": ".".join(map(str, sys.version_info[:3])), "status": status,
                      "checked": checked, "mismatches": bad, "excluded_deprecated_count": len(excluded),
                      "excluded_deprecated": excluded, "not_run": not_run}, indent=1))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
