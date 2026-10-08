"""The weave index: an in-memory typed graph of one repository seen through one domain pack (WBS 1.6).

Nodes and edges are plain dicts shaped for ``typecheck.check_document``. Sources, all deterministic:

* the pack: workflow, states, transitions, roles, laws and terms, with the links between them;
* generated diagram elements, keyed ``<pack>.<kind>.<id>`` (``domain.pack.ui_key``) and derived from the model elements;
* ``data-eija-id="<pack>.<kind>.<id>"`` attributes found in web files (a UI element that realises a model element);
* Python modules, symbols and tests (``extract_python``), and the ``repo://`` bindings of the pack's terms.

The ROOT HASH is one domain-separated hash over the sorted node rows, sorted edge rows and extraction gaps. It does not
depend on declaration order, file-system order or the run. It is the lean root of weave-lite, NOT the sharded root of
the design (which needs per-file shards); a tampered or reordered index is detected by recomputing it.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote

from eija_studio.domain.models import Transition, fingerprint
from eija_studio.domain.pack import Pack, Term, ui_key
from eija_studio.domain.transactions import AddState, AddTransition

from . import codelink
from .extract_python import FileFacts, extract_all, walk_files
from .metamodel import major_version
from .sarif import canonical_json

ROOT_TAG = "eija.weave.root.v1"
EDGE_TAG = "eija.weave.edge-id.v1"
WEB_SUFFIXES = (".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svg")
UI_ID = re.compile(r"""data-eija-id\s*=\s*["']([^"']+)["']""")


def dhash(tag: str, value: Any) -> str:
    """``sha256:`` + SHA-256(ASCII tag, NUL, canonical JSON): the identity aspect's domain-separated hash."""
    return "sha256:" + hashlib.sha256(tag.encode("ascii") + b"\x00" + canonical_json(value).encode("utf-8")).hexdigest()


def edge_id(edge: dict[str, Any]) -> str:
    return dhash(EDGE_TAG, [edge["kind"], edge["from"], edge["to"], edge.get("qualifier", "")])


def frag(text: str) -> str:
    """A fragment segment: RFC 3986 unreserved characters and a literal colon; every other UTF-8 byte as %XX."""
    return quote(text, safe="._~:-")


@dataclass(frozen=True)
class Binding:
    """A term's ``repo://`` binding: what was bound, and the digest of the target now (None when it does not resolve)."""
    term: str
    target: str
    digest: str | None

    @property
    def key(self) -> str:
        return f"{self.term}|{self.target}"


@dataclass
class Graph:
    pack_id: str
    pack_path: str
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    gaps: list[dict[str, str]] = field(default_factory=list)
    bindings: list[Binding] = field(default_factory=list)

    def by_id(self) -> dict[str, dict[str, Any]]:
        return {n["id"]: n for n in self.nodes}

    def rows(self) -> dict[str, Any]:
        return {"metamodel_major": major_version(),
                "nodes": [[n["id"], n["type"], n["digest"]] for n in self.nodes],
                "edges": [[e["kind"], e["from"], e["to"], e.get("qualifier", "")] for e in self.edges],
                "gaps": [[g["path"], g["reason"]] for g in self.gaps]}

    @property
    def root_hash(self) -> str:
        return dhash(ROOT_TAG, self.rows())

    def counts(self) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        for n in self.nodes:
            by_type[n["type"]] = by_type.get(n["type"], 0) + 1
        by_kind: dict[str, int] = {}
        for e in self.edges:
            by_kind[e["kind"]] = by_kind.get(e["kind"], 0) + 1
        return {"nodes": len(self.nodes), "edges": len(self.edges), "gaps": len(self.gaps),
                "node_types": dict(sorted(by_type.items())), "edge_kinds": dict(sorted(by_kind.items()))}


class _Builder:
    def __init__(self, pack: Pack, pack_path: str) -> None:
        self.graph = Graph(pack.id, pack_path)
        self._seen: dict[str, tuple[str, str]] = {}
        self.pack = pack
        self.base = "repo://" + pack_path

    def node(self, node_id: str, node_type: str, digest: str) -> str:
        """Add a node. The same id with the same type and digest is one node; a conflicting one is kept (WV-003 reports it)."""
        if self._seen.get(node_id) != (node_type, digest):
            self.graph.nodes.append({"id": node_id, "type": node_type, "digest": digest})
        self._seen.setdefault(node_id, (node_type, digest))
        return node_id

    def edge(self, kind: str, source: str, target: str) -> None:
        self.graph.edges.append({"kind": kind, "from": source, "to": target})

    def element_id(self, kind: str, name: str) -> str:
        return f"{self.base}#{kind}/{frag(name)}"


def _transition_form(t: Transition) -> dict[str, Any]:
    data = t.model_dump(mode="json")
    for key in ("guards", "required_effects", "forbidden_effects"):
        data[key] = sorted(data[key])
    return data


def _term_form(term: Term) -> dict[str, Any]:
    data = term.model_dump(mode="json")
    data["binds"], data["refs"] = sorted(data["binds"]), sorted(data["refs"])
    return data


def _pack_elements(b: _Builder) -> dict[str, str]:
    """Workflow, states, transitions, roles and laws; returns ui_key -> node id for the elements a diagram draws."""
    pack, drawn = b.pack, {}
    workflow = b.node(f"{b.base}#pack.workflow", "workflow", pack.model.semantic_hash)
    for state in pack.model.states:
        drawn[ui_key(pack.id, "state", state)] = b.node(b.element_id("state", state), "state", fingerprint({"state": state}))
    for t in pack.model.transitions:
        drawn[ui_key(pack.id, "transition", t.id)] = b.node(b.element_id("transition", t.id), "transition", fingerprint(_transition_form(t)))
    for role in pack.roles:
        drawn[ui_key(pack.id, "role", role.id)] = b.node(b.element_id("role", role.id), "role", fingerprint(role.model_dump(mode="json")))
    for law in pack.laws:
        b.node(b.element_id("law", law.id), "formal_law", fingerprint(law.model_dump(mode="json")))
    for element in drawn.values():
        b.edge("contains", workflow, element)
    return drawn


def _prospective(b: _Builder) -> None:
    """States and transitions a meaning ADDS. The pack declares them (its own coherence check accepts references to them),
    so a term may refer to them; they are nodes without a place in the baseline workflow, tagged by the meanings that add them."""
    added: dict[tuple[str, str], list[str]] = {}
    for meaning in b.pack.meanings:
        for tx in meaning.transactions:
            if isinstance(tx, AddState) and tx.state not in b.pack.model.states:
                added.setdefault(("state", tx.state), []).append(meaning.id)
            elif isinstance(tx, AddTransition) and tx.id not in {t.id for t in b.pack.model.transitions}:
                added.setdefault(("transition", tx.id), []).append(meaning.id)
    for (kind, name), meanings in sorted(added.items()):
        b.node(b.element_id(kind, name), kind, fingerprint({kind: name, "added_by": sorted(set(meanings))}))


def _pack_links(b: _Builder) -> None:
    for t in b.pack.model.transitions:
        transition = b.element_id("transition", t.id)
        b.edge("flows_to", b.element_id("state", t.from_state), transition)
        b.edge("flows_to", transition, b.element_id("state", t.to_state))
        b.edge("depends_on", transition, b.element_id("role", t.role))


def _diagram(b: _Builder, drawn: dict[str, str]) -> None:
    """The generated state-machine diagram: one diagram node, one element per drawn model element."""
    diagram = f"repo://docs/diagrams/{b.pack.id}.state-machine.mmd"
    by_id = {n["id"]: n["digest"] for n in b.graph.nodes}
    b.node(diagram, "diagram", fingerprint(sorted((k, by_id[v]) for k, v in drawn.items())))
    for key, element in sorted(drawn.items()):
        shown = b.node(f"{diagram}#{frag(key)}", "diagram_element", by_id[element])
        b.edge("contains", diagram, shown)
        b.edge("derived_from", shown, element)


def _ref_target(b: _Builder, ref: str) -> str:
    category, _, name = ref.partition(":")
    return b.element_id(category, name)


def _terms(b: _Builder) -> None:
    for term in b.pack.language.terms:
        node = b.node(f"{b.base}#{term.id}", "term", fingerprint(_term_form(term)))
        for ref in term.refs:
            b.edge("refers_to", node, _ref_target(b, ref))


def _file_type(path: str) -> str:
    return {".md": "document", ".json": "contract", ".py": "module"}.get(Path(path).suffix, "document")


def _target_digest(root: Path, ref: codelink.CodeRef, node_type: str) -> str | None:
    method = {"symbol": codelink.AST_CLOSURE, "module": codelink.AST_API}.get(node_type, codelink.FILE_LF)
    try:
        return codelink.digest(root, ref, method)
    except (codelink.Unresolved, ValueError, OSError):
        return None


def _bind_target(root: Path, uri: str, pack_uri: str, pack_digest: str) -> tuple[str, str, str | None]:
    """(node id, node type, digest or None) of a binding target. A ``.py#symbol`` binds a symbol, anything else a file.
    The pack file itself is hashed by MEANING (``pack_digest``: its elements' digests), so the order of its declarations
    or its layout never stales a binding to it; every other file is hashed by content (``lf-sha256-v1``)."""
    try:
        ref = codelink.parse_uri(uri)
    except ValueError:
        return uri, "document", None
    node_type = "symbol" if ref.path.endswith(".py") and ref.fragment is not None else _file_type(ref.path)
    if ref.uri() == pack_uri and (root / ref.path).is_file():
        return ref.uri(), node_type, pack_digest
    return ref.uri(), node_type, _target_digest(root, ref, node_type)


def _bindings(b: _Builder, root: Path) -> None:
    pack_digest = fingerprint(sorted((n["id"], n["digest"]) for n in b.graph.nodes))  # the pack's own nodes: nothing else is indexed yet
    for term in sorted(b.pack.language.terms, key=lambda t: t.id):
        term_id = f"{b.base}#{term.id}"
        for uri in sorted(term.binds):
            target, node_type, digest = _bind_target(root, uri, b.base, pack_digest)
            if digest is not None:
                b.node(target, node_type, digest)
            b.edge("realises" if node_type == "symbol" else "derived_from", target, term_id)
            b.graph.bindings.append(Binding(term_id, target, digest))


def _python_file(b: _Builder, f: FileFacts) -> None:
    module = b.node("repo://" + f.path, "module", f.module_digest)
    for s in f.symbols:
        symbol = b.node(f"{module}#{frag(s.fragment)}", "test" if s.kind == "test" else "symbol", s.digest)
        if s.kind != "test":
            b.edge("contains", module, symbol)


def _python(b: _Builder, root: Path) -> None:
    facts, gaps = extract_all(root)
    b.graph.gaps += [{"path": g.path, "reason": g.reason} for g in gaps]
    for f in facts:
        _python_file(b, f)


def _ui_element(b: _Builder, path: str, key: str) -> None:
    """One ``data-eija-id`` of this pack found in ``path``: the UI node and the link to the element it realises."""
    kind, _, name = key[len(b.pack.id) + 1:].partition(".")
    digest = fingerprint({"eija_id": key})
    base = "repo://" + path
    if kind == "state":
        b.edge("realises", b.node(f"{base}#status/{frag(key)}", "ui_status", digest), b.element_id("state", name))
    elif kind == "transition":
        b.edge("realises", b.node(f"{base}#control/{frag(key)}", "ui_control", digest), b.element_id("transition", name))
    elif kind == "term":
        b.edge("names", b.node(f"{base}#field/{frag(key)}", "ui_field", digest), f"{b.base}#{name}")
    else:
        b.node(f"{base}#region/{frag(key)}", "ui_region", digest)


def _ui(b: _Builder, root: Path) -> None:
    prefix = b.pack.id + "."
    for path in walk_files(root, WEB_SUFFIXES):
        try:
            text = (root / path).read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError):
            b.graph.gaps.append({"path": path, "reason": "cannot be read as UTF-8"})
            continue
        for key in sorted({k for k in UI_ID.findall(text) if k.startswith(prefix)}):
            _ui_element(b, path, key)


def pack_uri_path(root: Path, pack_file: Path | None, pack: Pack) -> str:
    """The repository-relative path of the pack file, or ``packs/<id>/pack.json`` when the pack lives outside ``root``."""
    if pack_file is not None:
        try:
            return pack_file.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            pass
    return f"packs/{pack.id}/pack.json"


def _finish(graph: Graph) -> Graph:
    graph.nodes.sort(key=lambda n: (n["id"], n["type"], n["digest"]))
    graph.edges.sort(key=lambda e: (e["kind"], e["from"], e["to"], e.get("qualifier", "")))
    graph.gaps.sort(key=lambda g: (g["path"], g["reason"]))
    graph.bindings.sort(key=lambda x: (x.key, x.digest or ""))
    return graph


def build_index(root: Path, pack: Pack, pack_file: Path | None = None) -> Graph:
    """Index ``root`` through ``pack``. Pure function of the pack and the files under ``root``."""
    b = _Builder(pack, pack_uri_path(root, pack_file, pack))
    drawn = _pack_elements(b)
    _prospective(b)
    _pack_links(b)
    _diagram(b, drawn)
    _terms(b)
    _bindings(b, root)
    _python(b, root)
    _ui(b, root)
    return _finish(b.graph)
