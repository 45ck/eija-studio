"""WBS 1.6 proof: impact is the reachability closure over the metamodel's declared affects direction, with a witness path.

MEASUREMENT: for EVERY pack-level node of each pack (all states, transitions, roles, laws, terms of the mini repository:
the count is asserted) the certified closure equals two independent reference closures (naive Kleene fixpoint and
Warshall), the trusted checker accepts it, and every witness path is a chain of real affects edges from the target.
Negative controls: a tampered certificate is rejected; an unknown target is refused.
"""
from __future__ import annotations

from itertools import pairwise
from pathlib import Path

import pytest
from weave_support import PACKS, ROOT, index, load_source, write_repo

from eija_studio.weave import closure
from eija_studio.weave.impact import UnknownTarget, adjacency, impact, resolve_target

PACK_TYPES = {"state", "transition", "role", "formal_law", "term"}


@pytest.mark.parametrize("name", PACKS)
def test_closure_equals_two_reference_closures_and_every_witness_is_a_real_path(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path, name)
    pack, graph = index(root, pack_file)
    adj = adjacency(graph)
    edges = closure.edge_set(adj)
    oracle = load_source("weave_impact_oracle", ROOT / "graph/formal/eijaref/closure.py")
    targets = [n["id"] for n in graph.nodes if n["type"] in PACK_TYPES]
    assert len(targets) >= len(pack.model.states) + len(pack.model.transitions) + len(pack.roles) + len(pack.laws) + len(pack.language.terms)
    for target in targets:
        report = impact(graph, target)
        got = {a["id"] for a in report["affected"]} | {target}
        assert report["certificate"] == "accepted"
        assert got == closure.lfp_kleene(adj, [target]) == oracle.warshall_closure(adj, [target])
        for a in report["affected"]:
            path = a["witness"]
            assert path[0] == target and path[-1] == a["id"] and len(path) == a["rank"] + 1
            assert all((u, v) in edges for u, v in pairwise(path))


@pytest.mark.parametrize("name", PACKS)
def test_a_state_change_reaches_its_transitions_terms_diagram_element_and_workflow(tmp_path: Path, name: str) -> None:
    root, pack_file = write_repo(tmp_path, name)
    pack, graph = index(root, pack_file)
    state = pack.model.initial_state  # it has an outgoing transition: a change to a state affects what leaves it
    report = impact(graph, f"state:{state}")
    reached = {a["id"]: a["type"] for a in report["affected"]}
    assert f"repo://docs/diagrams/{name}.state-machine.mmd#{name}.state.{state}" in reached
    assert {"transition", "workflow", "diagram_element", "diagram"} <= set(reached.values())
    direct = {f"repo://{graph.pack_path}#{term.id}" for term in pack.language.terms if f"state:{state}" in term.refs}
    assert direct <= set(reached)  # a term that names the state directly is affected by it


def test_a_bound_python_symbol_change_reaches_the_term_it_is_bound_to(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    pack, graph = index(root, pack_file)
    report = impact(graph, "repo://src/lib.py#helper")
    assert f"repo://{graph.pack_path}#{min(t.id for t in pack.language.terms)}" in {a["id"] for a in report["affected"]}


def test_negative_control_a_tampered_certificate_is_rejected(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    _, graph = index(root, pack_file)
    adj = adjacency(graph)
    target = resolve_target(graph, "state:Draft")
    cert = closure.certify(adj, [target])
    edges = closure.edge_set(adj)
    assert closure.check_certificate(edges, [target], cert) == (True, "accepted")
    dropped = next(n for n in sorted(cert["C"]) if n != target and n in adj)  # a node with successors: removing it breaks closure
    smaller = {**cert, "C": frozenset(cert["C"] - {dropped})}
    assert closure.check_certificate(edges, [target], smaller)[0] is False


def test_negative_control_unknown_targets_are_refused(tmp_path: Path) -> None:
    root, pack_file = write_repo(tmp_path, "excursion")
    _, graph = index(root, pack_file)
    for text in ("state:NoSuchState", "no-such-term", "law:", ""):
        with pytest.raises(UnknownTarget):
            resolve_target(graph, text)
    assert resolve_target(graph, "final-approval").endswith("#final-approval")
