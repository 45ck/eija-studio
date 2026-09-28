#!/usr/bin/env python3
"""Regenerate (--write) or verify (--check) docs/diagrams/*.md from the executable model.

--check exits 1 when a committed file differs from a fresh render, when a file is missing, or when an
unexpected file sits in docs/diagrams/. It reads only this repository and needs no network or browser.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eija_studio.application.diagram_catalog import docs_bundle

TARGET = ROOT / "docs" / "diagrams"


def drift(bundle: dict[str, str]) -> list[str]:
    problems = []
    for name, text in sorted(bundle.items()):
        path = TARGET / name
        if not path.is_file():
            problems.append(f"missing: {name}")
        elif path.read_bytes() != text.encode("utf-8"):
            problems.append(f"differs: {name}")
    if TARGET.is_dir():
        problems += [f"unexpected: {p.name}" for p in sorted(TARGET.iterdir()) if p.name not in bundle]
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    bundle = docs_bundle()
    if args.write:
        TARGET.mkdir(parents=True, exist_ok=True)
        for stale in TARGET.iterdir():
            if stale.name not in bundle:
                stale.unlink()
        for name, text in bundle.items():
            (TARGET / name).write_bytes(text.encode("utf-8"))
        print(f"wrote {len(bundle)} files to {TARGET.relative_to(ROOT)}")
        return 0
    problems = drift(bundle)
    for line in problems:
        print(line)
    print("diagrams: DRIFT" if problems else f"diagrams: PASS ({len(bundle)} files match the executable model)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
