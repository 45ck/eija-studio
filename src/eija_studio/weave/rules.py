"""Weave-lite rules over the index (WBS 1.6): WV-001 dangling, WV-002 ill-typed, WV-005 suspect binding.

The join-level rules come from the lifted ``typecheck.check_document`` (the executable definition of the metamodel's
signatures); this module maps its findings onto catalogue rules and adds the suspect-binding check. Also mapped, because
the same pass finds them: WV-003 (an id or edge defined twice), WV-022 (a cycle in an acyclic kind), WV-055 (a maximum
degree exceeded). Not implemented, by decision: WV-010 and WV-020 (see the PR's Deferred section).

Verdicts follow the lifted ``rule_verdict``: NOT_RUN absorbs PASS, never FAIL. A rule is NOT_RUN when a prerequisite is
absent (no baseline for WV-005) and, on a partially extracted repository (unparsable files), silence is NOT_RUN too:
a finding seen is real, an empty result says nothing. A suspect binding is a REVIEW signal ("the target changed since a
human last accepted it"), never a claim that the binding is false; clearing it is a human act (rewriting the baseline).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import codelink
from .index import Graph, edge_id
from .metamodel import catalogue, metamodel
from .sarif import build_sarif, exit_code, fold_verdicts, rule_verdict
from .typecheck import check_document

BASELINE_SCHEMA = "eija.weave.baseline.v1"
IMPLEMENTED = ("WV-001", "WV-002", "WV-003", "WV-005", "WV-022", "WV-055")
NO_BASELINE = "no baseline: accepting the current bindings (`eija index --write-baseline`) is a human decision"


@dataclass
class LintResult:
    root_hash: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    verdicts: dict[str, str] = field(default_factory=dict)
    not_run: list[dict[str, str]] = field(default_factory=list)
    gaps: list[dict[str, str]] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return fold_verdicts(self.verdicts.values())

    def by_rule(self, rule: str) -> list[dict[str, Any]]:
        return [f for f in self.findings if f["rule"] == rule]


# ---- baseline (the human-accepted digests of bound targets) ---------------------------------------------------

def load_baseline(path: Path) -> dict[str, str] | None:
    """Accepted digests by binding key, or None when there is no usable baseline (absent, unreadable or malformed)."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != BASELINE_SCHEMA or not isinstance(doc.get("bindings"), dict):
        return None
    return {str(k): str(v) for k, v in doc["bindings"].items()}


def baseline_text(graph: Graph) -> str:
    bindings = {b.key: b.digest for b in graph.bindings if b.digest is not None}
    return json.dumps({"schema": BASELINE_SCHEMA, "bindings": dict(sorted(bindings.items()))}, indent=2, sort_keys=True) + "\n"


def write_baseline(path: Path, graph: Graph) -> int:
    """Record the current digests of every resolvable binding. A HUMAN act: the CLI only, never an agent tool."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(baseline_text(graph), encoding="utf-8", newline="\n")
    return sum(1 for b in graph.bindings if b.digest is not None)


# ---- typecheck findings -> catalogue rules ---------------------------------------------------------------------

def _path_of(node_id: str) -> str:
    body = node_id[len(codelink.SCHEME):] if node_id.startswith(codelink.SCHEME) else ""
    return body.partition("#")[0]


def _finding(rule: str, message_id: str, args: dict[str, Any], uri: str, logical: list[str]) -> dict[str, Any]:
    return {"rule": rule, "message_id": message_id, "args": args, "uri": uri, "start_line": None,
            "logical": logical, "witness": [], "suppression": None}


def _label(edge: dict[str, Any]) -> str:
    return f"{edge['kind']}: {edge['from']} -> {edge['to']}"


def _anchor(edge: dict[str, Any], nodes: dict[str, dict[str, Any]]) -> str:
    """The file a finding is reported at: the end of the edge that exists, else the source end."""
    present = [e for e in (edge["to"], edge["from"]) if e in nodes]
    return _path_of((present or [edge["from"]])[0])


def _dangling(edge: dict[str, Any], message: str, nodes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    side = "source" if message.startswith("source") else "target"
    endpoint = edge["from"] if side == "source" else edge["to"]
    args = {"link": _label(edge), "kind": edge["kind"], "side": side, "endpoint": endpoint}
    return _finding("WV-001", "link-endpoint-missing", args, _anchor(edge, nodes), [edge_id(edge)])


def _allowed(kind: str) -> str:
    rows = metamodel()["link_types"][kind]["signatures"]
    return "; ".join(f"{'|'.join(r['from'])} -> {'|'.join(r['to'])}" for r in rows)


def _ill_typed(edge: dict[str, Any], message: str, nodes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ends = [nodes.get(edge["from"], {}).get("type", "?"), nodes.get(edge["to"], {}).get("type", "?")]
    allowed = _allowed(edge["kind"]) if edge["kind"] in metamodel()["link_types"] else message
    args = {"link": _label(edge), "kind": edge["kind"], "from_type": ends[0], "to_type": ends[1], "allowed": allowed}
    return _finding("WV-002", "link-signature-violated", args, _anchor(edge, nodes), [edge_id(edge)])


def _duplicate(subject: str, uri: str) -> dict[str, Any]:
    args = {"id": subject, "site_a": "first record", "site_b": "second record"}
    return _finding("WV-003", "id-defined-twice", args, uri, [subject])


def _cardinality(subject: str, message: str) -> dict[str, Any]:
    head, _, node = subject.partition(":")
    side = "outgoing" if message.startswith("out") else "incoming"
    count, _, maximum = message.partition(" ")[2].partition(" > ")
    args = {"node": node, "kind": head.partition("#")[0], "side": side, "count": count, "max": maximum, "links": ""}
    return _finding("WV-055", "link-maximum-exceeded", args, _path_of(node), [node])


def _cycle(subject: str, message: str, kind: str = "") -> dict[str, Any]:
    members = sorted({m for m in message.split(" -> ") if m})
    args = {"kind": kind or subject, "members": ", ".join(members), "cycle": message}
    return _finding("WV-022", "acyclic-kind-has-cycle", args, _path_of(members[0]) if members else "", members)


def _typecheck_finding(code: str, subject: str, message: str, graph: Graph, edges: dict[str, dict[str, Any]]) -> dict[str, Any]:
    nodes, edge = graph.by_id(), edges.get(subject, {"kind": "?", "from": subject, "to": subject})
    if code == "dangling-link":
        return _dangling(edge, message, nodes)
    if code in ("duplicate-id", "duplicate-edge"):
        return _duplicate(subject, _anchor(edge, nodes) if code == "duplicate-edge" else _path_of(subject))
    if code == "cardinality-exceeded":
        return _cardinality(subject, message)
    if code == "link-kind-cycle":
        return _cycle(subject, message)
    if code == "rename-cycle":
        return _cycle(subject, message, "renamed_to")
    return _ill_typed(edge, message, nodes)  # ill-typed-edge and self-loop: no signature admits this link


def structural_findings(graph: Graph) -> list[dict[str, Any]]:
    edges = {"|".join((e["kind"], e["from"], e["to"], e.get("qualifier", ""))): e for e in graph.edges}
    problems = check_document(metamodel(), graph.nodes, graph.edges)
    return [_typecheck_finding(code, subject, message, graph, edges) for code, subject, message in problems]


# ---- WV-005 ----------------------------------------------------------------------------------------------------

def suspect_findings(graph: Graph, baseline: dict[str, str]) -> list[dict[str, Any]]:
    """Bindings whose target digest differs from the accepted one. Direct only; the transitive form is deferred."""
    found: list[dict[str, Any]] = []
    by_key = {b.key: b for b in graph.bindings}
    for key in sorted(by_key):
        binding = by_key[key]
        accepted = baseline.get(key)
        if binding.digest is None or accepted is None or accepted == binding.digest:
            continue
        args = {"link": f"binding: {binding.term} <- {binding.target}", "target": binding.target,
                "baseline_digest": accepted, "current_digest": binding.digest, "path_length": "0"}
        found.append(_finding("WV-005", "suspect-link-direct", args, _path_of(binding.target), [binding.term]))
    return found


# ---- run -------------------------------------------------------------------------------------------------------

def _verdict(rule: str, findings: list[dict[str, Any]], prerequisite: str | None, partial: bool) -> tuple[str, str | None]:
    """(verdict, NOT_RUN reason). Gating findings are the rule's error-level messages."""
    catalog = {r["id"]: r for r in catalogue()["rules"]}[rule]
    levels = {m["id"]: m["level"] for m in catalog["messages"]}
    gating = sum(1 for f in findings if f["rule"] == rule and levels[f["message_id"]] == "error")
    effect = "monotone" if partial else "none"
    verdict = rule_verdict(gating, prerequisite is None, effect)
    if verdict == "NOT_RUN":
        return verdict, prerequisite or "extraction was partial (files that could not be parsed): an empty result proves nothing"
    return verdict, None


def lint(graph: Graph, baseline: dict[str, str] | None) -> LintResult:
    findings = structural_findings(graph)
    if baseline is not None:
        findings += suspect_findings(graph, baseline)
    result = LintResult(graph.root_hash, gaps=list(graph.gaps))
    for rule in IMPLEMENTED:
        prerequisite = NO_BASELINE if rule == "WV-005" and baseline is None else None
        verdict, reason = _verdict(rule, findings, prerequisite, bool(graph.gaps))
        result.verdicts[rule] = verdict
        if reason:
            result.not_run.append({"rule": rule, "reason": reason})
    result.findings = sorted(findings, key=lambda f: (f["uri"], f["rule"], json.dumps(f["args"], sort_keys=True)))
    return result


def _artifacts(root: Path, result: LintResult) -> dict[str, str]:
    out: dict[str, str] = {}
    for uri in sorted({f["uri"] for f in result.findings if f["uri"]}):
        try:
            out[uri] = codelink.digest(root, codelink.CodeRef(uri), codelink.FILE_LF)
        except (codelink.Unresolved, ValueError, OSError):
            continue
    return out


def to_sarif(root: Path, result: LintResult, tool_version: str) -> dict[str, Any]:
    """SARIF 2.1.0 in the EIJA determinism profile (relative uris, sorted, no clock)."""
    return build_sarif(catalogue(), result.findings, not_run=result.not_run, artifacts=_artifacts(root, result),
                       graph_root=result.root_hash, verdicts=result.verdicts, tool_version=tool_version)


def exit_status(result: LintResult, not_run_accepted: bool = False) -> int:
    return exit_code(result.verdict, not_run_accepted)
