"""Impact over the index: what a change to one element can affect, with a witness path for every affected element.

The direction of "affects" is declared per link kind by the metamodel (``to_source``: the source depends on the target,
so a change to the target affects the source; ``to_target``; ``both``; ``none``). The closure is BFS with parent
pointers (``closure.certify``, untrusted) and then CHECKED by ``closure.check_certificate`` (the trusted checker, which
has no queue and no iteration): forward-closed, every parent edge real, ranks strictly decreasing. A closure that fails
the check is reported as such, never as a result.
"""
from __future__ import annotations

from typing import Any

from . import closure
from .index import Graph, frag
from .metamodel import metamodel

PACK_KINDS = ("state", "transition", "role", "law")


class UnknownTarget(LookupError):
    """The target names nothing in the index."""


def adjacency(graph: Graph) -> dict[str, list[str]]:
    """node -> nodes a change to it affects, from each link kind's declared ``affects`` direction."""
    link_types = metamodel()["link_types"]
    adj: dict[str, set[str]] = {}
    for e in graph.edges:
        direction = link_types.get(e["kind"], {}).get("affects", "none")
        if direction in ("to_source", "both"):
            adj.setdefault(e["to"], set()).add(e["from"])
        if direction in ("to_target", "both"):
            adj.setdefault(e["from"], set()).add(e["to"])
    return {k: sorted(v) for k, v in sorted(adj.items())}


def resolve_target(graph: Graph, text: str) -> str:
    """A node id, ``state:X`` / ``transition:X`` / ``role:X`` / ``law:X``, or a term id of the pack."""
    known = graph.by_id()
    base = "repo://" + graph.pack_path
    kind, _, name = text.partition(":")
    candidates = [text, f"{base}#{kind}/{frag(name)}" if kind in PACK_KINDS else "", f"{base}#{text}"]
    for candidate in candidates:
        if candidate and candidate in known:
            return candidate
    raise UnknownTarget(f"{text!r} is not a node, a pack element (state:, transition:, role:, law:) or a term id")


def _witness(cert: dict[str, Any], node: str) -> list[str]:
    path = [node]
    while path[-1] in cert["parent"]:
        path.append(cert["parent"][path[-1]])
    return path[::-1]


def impact(graph: Graph, target: str) -> dict[str, Any]:
    """The closure of ``target`` with a witness path per affected node and the verdict of the trusted checker."""
    root = resolve_target(graph, target)
    adj = adjacency(graph)
    cert = closure.certify(adj, [root])
    accepted, reason = closure.check_certificate(closure.edge_set(adj), [root], cert)
    types = {n["id"]: n["type"] for n in graph.nodes}
    affected = [{"id": n, "type": types.get(n, "?"), "rank": cert["rank"][n], "witness": _witness(cert, n)}
                for n in sorted(cert["C"], key=lambda x: (cert["rank"][x], x)) if n != root]
    return {"target": root, "affected": affected, "count": len(affected),
            "certificate": "accepted" if accepted else f"REJECTED: {reason}"}
