"""Key-granular three-way merge for TOML files (a git merge driver).

Why: with a dozen parallel lanes, every lane edits `pyproject.toml` (its own optional-dependency
extra, a tool section). Git merges by lines, so two lanes that touch *neighbouring* lines conflict even
though they changed different keys. This driver merges by (table, key) instead:

* a key changed on one side only takes that side's value;
* a key changed identically on both sides is kept;
* a table changed on both sides is merged recursively;
* an array of scalars that both sides only *extended* is merged as an ordered union, except that two
  different pins of the same package are a conflict, never a union;
* anything else is a real conflict: exit status 1 and the file is left untouched.

Usage (git calls it as `driver %O %A %B`): `python tomlmerge.py BASE OURS THEIRS`; the merged text is
written to OURS. Requires `tomlkit`, which preserves comments and formatting. Wire it per clone with
`quality/tools/install_merge_drivers.py`; without it, git falls back to its ordinary text merge.
"""
# ruff: noqa: T201
from __future__ import annotations

import re
import sys
from pathlib import Path

import tomlkit
from tomlkit.container import Container
from tomlkit.items import Table

MISSING = object()
_REQUIREMENT_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def _plain(node):
    """Plain Python value for comparison (tomlkit items compare by trivia in some versions)."""
    if node is MISSING:
        return MISSING
    return node.unwrap() if hasattr(node, "unwrap") else node


def _is_table(node) -> bool:
    return isinstance(node, (Table, Container))


def _requirement_name(item) -> str | None:
    """Normalised distribution name if `item` looks like a PEP 508 requirement string, else None."""
    if not isinstance(item, str):
        return None
    match = _REQUIREMENT_NAME.match(item)
    return re.sub(r"[-_.]+", "-", match.group(1)).lower() if match else None


def _disagree_on_a_requirement(ours: list, added_by_theirs: list) -> bool:
    """Two lanes pinning the same package differently must be a conflict, never a union."""
    pinned = {n: x for x in ours if (n := _requirement_name(x)) is not None}
    return any(
        pinned.get(n) not in (None, x) for x in added_by_theirs if (n := _requirement_name(x)) is not None
    )


def _additive(base: list, side: list) -> bool:
    """`side` only extended `base`: every base element is still present, in order."""
    remaining = iter(side)
    return all(any(item == candidate for candidate in remaining) for item in base)


def _is_scalar(item) -> bool:
    return not isinstance(item, (dict, list))


def _both_only_extended(base_value, ours_value, theirs_value) -> bool:
    """All values are arrays (the base may be absent) and each side only extended the base."""
    if not (isinstance(ours_value, list) and isinstance(theirs_value, list)):
        return False
    if not (base_value is MISSING or isinstance(base_value, list)):
        return False
    base_list = [] if base_value is MISSING else base_value
    if not all(_is_scalar(x) for x in (*base_list, *ours_value, *theirs_value)):
        return False  # arrays of tables / nested arrays are never unioned: flattening would corrupt them
    return _additive(base_list, ours_value) and _additive(base_list, theirs_value)


def _union_arrays(ours, key, base_value, ours_value, theirs_value) -> bool:
    """Merge two additive edits of the same array into `ours[key]`. False when they are not mergeable."""
    if not _both_only_extended(base_value, ours_value, theirs_value):
        return False
    added = [x for x in theirs_value if x not in ours_value]
    if _disagree_on_a_requirement(ours_value, added):
        return False
    merged = tomlkit.array()
    merged.extend(list(ours_value) + added)
    ours[key] = merged
    return True


def _take_theirs(ours, key, theirs_item) -> None:
    if theirs_item is MISSING:
        del ours[key]
    else:
        ours[key] = theirs_item


def _merge_key(key: str, base, ours, theirs, here: str) -> list[str]:
    """Merge one key; return the conflicting key paths (empty when it merged)."""
    b, o, t = base.get(key, MISSING), ours.get(key, MISSING), theirs.get(key, MISSING)
    bv, ov, tv = _plain(b), _plain(o), _plain(t)
    if tv == bv or ov == tv:  # theirs did not touch it, or both made the same change
        return []
    if ov == bv:  # only theirs changed it (or deleted it)
        _take_theirs(ours, key, t)
        return []
    if _is_table(o) and _is_table(t):
        return merge_tables(b if _is_table(b) else tomlkit.table(), o, t, here)
    if _union_arrays(ours, key, bv, ov, tv):
        return []
    return [here]


def merge_tables(base, ours, theirs, path: str = "") -> list[str]:
    """Merge `theirs` changes into `ours` in place. Returns the list of conflicting key paths."""
    conflicts: list[str] = []
    for key in [*theirs, *(k for k in base if k not in theirs)]:
        here = f"{path}.{key}" if path else str(key)
        conflicts += _merge_key(key, base, ours, theirs, here)
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
