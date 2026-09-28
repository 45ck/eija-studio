"""The generated-file merge driver keeps the side that carries the generator marker, in either direction."""
from pathlib import Path

from quality.tools.keep_generated import DEFAULT_MARKER, main

MARKED = f"head\n{DEFAULT_MARKER} (generated) -->\nrows\n<!-- adr-index:end -->\n"
STALE = "head\nold hand-written table\n"


def run(tmp_path: Path, ours: str, theirs: str) -> tuple[int, str]:
    paths = {name: tmp_path / name for name in ("base", "ours", "theirs")}
    for name, text in (("base", STALE), ("ours", ours), ("theirs", theirs)):
        paths[name].write_bytes(text.encode())
    code = main(["driver", str(paths["base"]), str(paths["ours"]), str(paths["theirs"])])
    return code, paths["ours"].read_text(encoding="utf-8")


def test_ours_marked_is_kept(tmp_path):
    assert run(tmp_path, MARKED, STALE) == (0, MARKED)


def test_theirs_marked_wins_when_ours_is_the_stale_lane_copy(tmp_path):
    assert run(tmp_path, STALE, MARKED) == (0, MARKED)


def test_neither_side_marked_is_a_real_conflict(tmp_path):
    code, text = run(tmp_path, STALE, "other\n")
    assert code == 1 and text == STALE
