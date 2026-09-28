"""Merge driver for generated files: keep the side that carries the generated-block marker.

`docs/adr/README.md` is generated (`quality/tools/adr_index.py`). A plain "keep ours" is wrong half the
time: merging main INTO a lane, ours is the lane's stale copy. This driver keeps whichever side still
has the generator's start marker (ours preferred when both do); regenerate afterwards. If neither side
has it, the file is a genuine conflict.

Usage (git calls it as `driver %O %A %B`): `python keep_generated.py BASE OURS THEIRS [MARKER]`.
"""
# ruff: noqa: T201
from __future__ import annotations

import sys
from pathlib import Path

DEFAULT_MARKER = "<!-- adr-index:start"


def main(argv: list[str]) -> int:
    if len(argv) not in (4, 5):
        print("usage: keep_generated.py BASE OURS THEIRS [MARKER]", file=sys.stderr)
        return 2
    marker = argv[4] if len(argv) == 5 else DEFAULT_MARKER
    ours, theirs = Path(argv[2]), Path(argv[3])
    if marker in ours.read_text(encoding="utf-8"):
        return 0
    if marker in theirs.read_text(encoding="utf-8"):
        ours.write_bytes(theirs.read_bytes())
        return 0
    print(f"keep_generated: neither side contains {marker!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
