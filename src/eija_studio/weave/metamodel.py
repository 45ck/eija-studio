"""The weave metamodel: node types, link kinds and signatures, plus the rule catalogue.

``expand`` is lifted verbatim from graph/schema/build_schemas.py (WBS 1.6; tests/weave/test_lift.py checks it).
The metamodel and the catalogue are read from the repository's ``graph/`` directory, the same convention as the
domain packs (``domain.pack.PACKS_ROOT``); a checkout without them cannot be linted, and says so.

``with_pack_links`` adds ONE link kind the v1.0.0 metamodel does not have: ``refers_to`` (term -> workflow element
or formal law), the ``refs`` a pack term declares. It widens no existing signature. It is a weave-lite extension to
be proposed for metamodel v1.1 (see the PR's Deferred section).
"""
from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

GRAPH_ROOT = Path(__file__).resolve().parents[3] / "graph"
METAMODEL_FILE = GRAPH_ROOT / "schema" / "metamodel.json"
CATALOGUE_FILE = GRAPH_ROOT / "rules" / "catalogue.json"

REFERS_TO = {
    "acyclic": False, "affects": "to_source", "affects_why": "a term is affected by a change in what it refers to",
    "anchor_ends": [], "attrs": {}, "classes": ["declared"], "cover_role": "none", "proofmap": "", "qualifiers": [],
    "rank_weight": [2, 1], "signatures": [{"from": ["term"], "to": ["workflow_element", "formal_law"]}],
    "soundness": "must", "trace": False,
}


class WeaveUnavailable(Exception):
    """The metamodel or the rule catalogue cannot be read: nothing can be checked (NOT_RUN, never PASS)."""


def expand(mm: dict[str, Any], names: list[str]) -> list[str]:
    """Expand supertypes (order-sorted signatures) to concrete node types; '*' means every type."""
    out: set[str] = set()
    for name in names:
        if name == "*":
            out.update(mm["node_types"])
        elif name in mm["supertypes"]:
            out.update(mm["supertypes"][name])
        elif name in mm["node_types"]:
            out.add(name)
        else:
            raise KeyError(f"unknown sort {name!r}")
    return sorted(out)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise WeaveUnavailable(f"{path.name} cannot be read ({type(error).__name__})") from None


def with_pack_links(mm: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(mm)
    out["link_types"]["refers_to"] = copy.deepcopy(REFERS_TO)
    return out


@lru_cache(maxsize=1)
def metamodel() -> dict[str, Any]:
    """The v1.0.0 metamodel plus the pack link kind. Callers must not mutate it."""
    return with_pack_links(_read_json(METAMODEL_FILE))


@lru_cache(maxsize=1)
def catalogue() -> dict[str, Any]:
    return _read_json(CATALOGUE_FILE)


def major_version() -> str:
    return str(metamodel()["metamodel_version"]).split(".")[0]
