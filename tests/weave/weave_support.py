"""Fixtures shared by the weave tests: a tiny repository around a copy of a real pack, and a pack-declaration shuffler."""
from __future__ import annotations

import importlib.util
import json
import random
import shutil
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from eija_studio.domain.pack import Pack, load_pack
from eija_studio.weave.index import Graph, build_index

ROOT = Path(__file__).resolve().parents[2]
PACKS = ("excursion", "library-loan")
LIB = '''"""A tiny library."""


def helper(x):
    # a comment
    return x + 1


class Box:
    def get(self):
        return 1


CONST = 3
'''
SWAPPED = '''"""A tiny library."""


class Box:
    def get(self):
        return 1


def helper(x):
    # a comment
    return x + 1


CONST = 3
'''
TEST = '''import pytest


@pytest.mark.eija(law="a-law")
def test_helper():
    assert True
'''
BIND = "repo://src/lib.py#helper"
SHUFFLED = (("model", "states"), ("model", "transitions"), ("roles",), ("actions",), ("effects", "catalog"), ("laws",),
            ("meanings",), ("language", "terms"), ("fixtures", "actors"), ("verifiers",))


def rng(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - a deterministic shuffle seed, not a secret


def bound_term(doc: dict[str, Any]) -> dict[str, Any]:
    """The term the fixture binds to Python (the smallest id, so shuffling the declarations does not change the choice)."""
    return min(doc["language"]["terms"], key=lambda term: term["id"])


def first_state(doc: dict[str, Any]) -> str:
    return min(doc["model"]["states"])


def first_transition(doc: dict[str, Any]) -> str:
    return min(t["id"] for t in doc["model"]["transitions"])


def read_pack(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "packs" / name / "pack.json").read_text(encoding="utf-8"))


def _walk(doc: dict[str, Any], path: tuple[str, ...]) -> Any:
    for key in path[:-1]:
        doc = doc[key]
    return doc, path[-1]


def shuffled(doc: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """The same pack with every declaration list in another order (a different textual document, the same pack)."""
    out = json.loads(json.dumps(doc))
    for path in SHUFFLED:
        holder, key = _walk(out, path)
        rng.shuffle(holder[key])
    return out


def write_repo(tmp: Path, name: str, doc: dict[str, Any] | None = None, *, bind: bool = True, lib: str = LIB) -> tuple[Path, Path]:
    """A repository holding the pack (optionally with its first term also bound to a Python symbol), a module, a test and a web file."""
    doc = json.loads(json.dumps(doc if doc is not None else read_pack(name)))
    if bind:
        bound_term(doc)["binds"].append(BIND)
    pack_file = tmp / "packs" / name / "pack.json"
    pack_file.parent.mkdir(parents=True, exist_ok=True)
    pack_file.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    for extra in (ROOT / "examples").glob("excursion-baseline.json"):
        (tmp / "examples").mkdir(exist_ok=True)
        shutil.copy(extra, tmp / "examples" / extra.name)
    (tmp / "src").mkdir(exist_ok=True)
    (tmp / "src" / "lib.py").write_text(lib, encoding="utf-8", newline="\n")
    (tmp / "tests").mkdir(exist_ok=True)
    (tmp / "tests" / "test_x.py").write_text(TEST, encoding="utf-8", newline="\n")
    state, transition = first_state(doc), first_transition(doc)
    (tmp / "web").mkdir(exist_ok=True)
    (tmp / "web" / "app.html").write_text(
        f'<div data-eija-id="{name}.state.{state}"></div><button data-eija-id="{name}.transition.{transition}"></button>'
        f'<i data-eija-id="other.state.x"></i>', encoding="utf-8")
    return tmp, pack_file


def index(root: Path, pack_file: Path) -> tuple[Pack, Graph]:
    pack = load_pack(pack_file)
    return pack, build_index(root, pack, pack_file)


def load_source(name: str, path: Path) -> ModuleType:
    """Import a source oracle (graph/...) by path, under a private module name."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
