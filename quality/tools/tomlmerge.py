"""Key-granular three-way merge for TOML files (a git merge driver).

Why: with a dozen parallel lanes, every lane edits `pyproject.toml` (its own optional-dependency
extra, a tool section). Git merges by lines, so two lanes that touch *neighbouring* lines conflict even
though they changed different keys. This driver merges by (table, key) instead:

* a key changed on one side only takes that side's value;
* a key changed identically on both sides is kept;
* a table changed on both sides is merged recursively;
* an array of scalars that both sides only *extended* is merged as an ordered union;
* anything else is a real conflict: exit status 1 and the file is left untouched.

Usage (git calls it as `driver %O %A %B`): `python tomlmerge.py BASE OURS THEIRS`; the merged text is
written to OURS. Requires `tomlkit`, which preserves comments and formatting. Wire it per clone with
`quality/tools/install_merge_drivers.py`; without it, git falls back to its ordinary text merge.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import tomlkit
from tomlkit.items import Array, Table
from tomlkit.container import Container

MISSING = object()


def _value(node):
    """Plain Python value for comparison (tomlkit items compare by trivia in some versions)."""
    return node.unwrap() if hasattr(node, "unwrap") else node


def _is_table(node) -> bool:
    return isinstance(node, (Table, Container))


_REQUIREMENT_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def _requirement_name(item) -> str | None:
    """Normalised distribution name if `item` looks like a PEP 508 requirement string, else None."""
    if not isinstance(item, str):
        return None
    match = _REQUIREMENT_NAME.match(item)
    return re.sub(r"[-_.]+", "-", match.group(1)).lower() if match else None


def _disagree_on_a_requirement(ours: list, added_by_theirs: list) -> bool:
    """Two lanes pinning the same package differently must be a conflict, never a union."""
    pinned = {n: x for x in ours if (n := _requirement_name(x)) is not None}
    return any(pinned.get(n) not in (None, x) for x in added_by_theirs if (n := _requirement_name(x)) is not None)


def _additive(base: list, side: list) -> bool:
    """`side` only extended `base`: every base element is still present, in order."""
    it = iter(side)
    return all(any(item == candidate for candidate in it) for item in base)


def merge_tables(base, ours, theirs, path: str = "") -> list[str]:
    """Merge `theirs` changes into `ours` in place. Returns the list of conflicting key paths."""
    conflicts: list[str] = []
    keys = list(theirs.keys()) + [k for k in base.keys() if k not in theirs]
    for key in keys:
        here = f"{path}.{key}" if path else str(key)
        b = base[key] if key in base else MISSING
        o = ours[key] if key in ours else MISSING
        t = theirs[key] if key in theirs else MISSING
        bv, ov, tv = (_value(x) if x is not MISSING else MISSING for x in (b, o, t))

        if tv == bv:                     # theirs did not touch it: keep ours
            continue
        if ov == bv:                     # only theirs changed it: take theirs (or its deletion)
            if t is MISSING:
                del ours[key]
            else:
                ours[key] = t
            continue
        if ov == tv:                     # both made the same change
            continue
        if _is_table(o) and _is_table(t):
            sub_base = b if _is_table(b) else tomlkit.table()
            conflicts += merge_tables(sub_base, o, t, here)
            continue
        if all(isinstance(x, list) for x in (ov, tv)) and (bv is MISSING or isinstance(bv, list)):
            base_list = [] if bv is MISSING else bv
            added = [x for x in tv if x not in ov]
            if _additive(base_list, ov) and _additive(base_list, tv) and not _disagree_on_a_requirement(ov, added):
                merged = list(ov) + added
                arr = tomlkit.array()
                arr.extend(merged)
                ours[key] = arr
                continue
        conflicts.append(here)
    return conflicts


def merge_files(base_path: Path, ours_path: Path, theirs_path: Path) -> list[str]:
    base = tomlkit.parse(base_path.read_text(encoding="utf-8")) if base_path.exists() else tomlkit.document()
    ours = tomlkit.parse(ours_path.read_text(encoding="utf-8"))
    theirs = tomlkit.parse(theirs_path.read_text(encoding="utf-8"))
    conflicts = merge_tables(base, ours, theirs)
    if not conflicts:
        ours_path.write_bytes(tomlkit.dumps(ours).encode("utf-8"))
    return conflicts


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: tomlmerge.py BASE OURS THEIRS", file=sys.stderr)
        return 2
    conflicts = merge_files(Path(argv[1]), Path(argv[2]), Path(argv[3]))
    for key in conflicts:
        print(f"tomlmerge: conflict at {key}", file=sys.stderr)
    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
