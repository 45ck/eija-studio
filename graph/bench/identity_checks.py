"""Reproducible checks behind docs/weave/design/metamodel-and-identity.md and ADR-0089.

Reference implementations (small, stdlib only) of the identity and hashing rules, plus measurements that
justify them. This file is NOT the production module: `eijagraph.canon` must reproduce the vectors in
graph/schema/identity-vectors.json byte for byte. Every check reports MEASURED (it ran; the domain is
stated) or NOT_RUN with a reason when an optional prerequisite (networkx, rfc8785, git) is missing.
Nothing here proves a property for all inputs; each check is an exhaustive enumeration of a small domain
or a seeded sample and says which.

Read-only use of the kernel: imports ``eija_studio.domain`` from ``src/`` as a test oracle only.
Output is canonical ASCII JSON (sorted keys, no timestamps), byte-identical between runs.

    python graph/bench/identity_checks.py             # print the report
    python graph/bench/identity_checks.py --write     # also write graph/bench/results/identity-checks.json
    python graph/bench/identity_checks.py --timing    # add wall-clock scale numbers (NOT deterministic)
    python graph/bench/identity_checks.py --write --timing   # also write graph/bench/results/identity-timing.json (one run, this machine)
"""
from __future__ import annotations

import hashlib
import importlib
import json
import platform
import random
import re
import subprocess
import sys
import time
import uuid
import warnings
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from eija_studio.domain.impact import closure as kernel_closure  # noqa: E402
from eija_studio.domain.models import canonical as kernel_canonical  # noqa: E402


def _optional(name: str):
    """Import an optional oracle, or None (the check then reports NOT_RUN).

    A copy installed under .tmp/site for one session is used, but it is not left in sys.path or sys.modules: other test
    modules decide NOT_RUN by importing the same name, and must see the same environment they would see without this file.
    """
    try:
        return importlib.import_module(name)
    except ImportError:
        pass
    site = ROOT / ".tmp" / "site"
    if not site.is_dir():
        return None
    sys.path.insert(0, str(site))
    try:
        mod = importlib.import_module(name)
    except ImportError:
        mod = None
    finally:
        sys.path.remove(str(site))
    if mod is not None and str(site) in str(getattr(mod, "__file__", "")):
        for key in [k for k in sys.modules if k == name or k.startswith(name + ".")]:
            del sys.modules[key]
    return mod


nx = _optional("networkx")
rfc8785 = _optional("rfc8785")

SAFE_INT = 2**53 - 1
METAMODEL_MAJOR = 1


def not_run(reason: str) -> dict:
    return {"status": "NOT_RUN", "reason": reason}


# ---- canonical serialisation: the RFC 8785 subset --------------------------------------------------------

class CanonError(ValueError):
    pass


_ESC = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}


_NEEDS_ESCAPE = re.compile(r'[\x00-\x1f"\\]')


def _str(s: str, out: list[str]) -> None:
    try:
        s.encode("utf-8")  # rejects lone surrogates, as RFC 8785 requires
    except UnicodeEncodeError as exc:
        raise CanonError("string is not well-formed Unicode") from exc
    if not _NEEDS_ESCAPE.search(s):  # fast path: nothing to escape
        out.append('"' + s + '"')
        return
    out.append('"')
    for ch in s:
        if ch in _ESC:
            out.append(_ESC[ch])
        elif ord(ch) < 0x20:
            out.append('\\u%04x' % ord(ch))
        else:
            out.append(ch)
    out.append('"')


def _value(v: Any, out: list[str]) -> None:
    if v is None:
        out.append("null")
    elif v is True:
        out.append("true")
    elif v is False:
        out.append("false")
    elif isinstance(v, int):
        if abs(v) > SAFE_INT:
            raise CanonError(f"integer outside +-(2^53-1): {v}")
        out.append(str(v))
    elif isinstance(v, str):
        _str(v, out)
    elif isinstance(v, (list, tuple)):
        out.append("[")
        for i, x in enumerate(v):
            if i:
                out.append(",")
            _value(x, out)
        out.append("]")
    elif isinstance(v, dict):
        if not all(isinstance(k, str) for k in v):
            raise CanonError("object keys must be strings")
        out.append("{")
        keys = sorted(v) if all(k.isascii() for k in v) else sorted(v, key=lambda key: key.encode("utf-16-be"))
        for i, k in enumerate(keys):  # UTF-16 code unit order (equals code point order for ASCII)
            if i:
                out.append(",")
            _str(k, out)
            out.append(":")
            _value(v[k], out)
        out.append("}")
    else:  # float, bytes, set, ... are outside the subset
        raise CanonError(f"type outside the subset: {type(v).__name__}")


def jcs_dumps(value: Any) -> bytes:
    out: list[str] = []
    _value(value, out)
    return "".join(out).encode("utf-8")


def jcs_dumps_fast(value: Any) -> bytes:
    """C-accelerated encoder. Equals jcs_dumps ONLY for pre-validated subset documents whose keys are ASCII
    (no floats, safe integers, well-formed strings): check C1 measures 0 differences on such documents."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


_DUMPS = jcs_dumps


_TAG = re.compile(r"eija\.weave\.[a-z0-9.-]+\.v[0-9]+")


def dhash(tag: str, value: Any) -> str:
    """Domain-separated hash: SHA-256 over ASCII tag, one NUL, then the JCS bytes (self-delimiting JSON)."""
    if not _TAG.fullmatch(tag):
        raise CanonError(f"bad domain tag {tag!r}")
    return "sha256:" + hashlib.sha256(tag.encode("ascii") + b"\x00" + _DUMPS(value)).hexdigest()


# ---- identity ---------------------------------------------------------------------------------------------

_UNRESERVED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:")  # RFC 3986 unreserved plus a literal colon
_PATH = re.compile(r"(?:(?!\.{1,2}(?:/|$))[A-Za-z0-9._-]+)(?:/(?!\.{1,2}(?:/|$))[A-Za-z0-9._-]+)*")


def pct_segment(text: str) -> str:
    """Canonical fragment segment: unreserved kept, every other UTF-8 byte as uppercase %XX."""
    return "".join(c if c in _UNRESERVED else "".join(f"%{b:02X}" for b in c.encode("utf-8")) for c in text)


def make_id(path: str, *segments: str) -> str:
    if not _PATH.fullmatch(path):
        raise CanonError(f"path outside the id grammar: {path!r}")
    frag = "/".join(pct_segment(s) for s in segments)
    return "repo://" + path + ("#" + frag if frag else "")


def split_id(node_id: str) -> tuple[str, str | None]:
    if not node_id.startswith("repo://"):
        raise CanonError("not a repo:// id")
    path, _, frag = node_id[len("repo://"):].partition("#")
    if not _PATH.fullmatch(path):
        raise CanonError(f"path outside the id grammar: {path!r}")
    return path, (frag or None)


def is_canonical_id(node_id: str) -> bool:
    try:
        path, frag = split_id(node_id)
    except CanonError:
        return False
    if frag is None:
        return "#" not in node_id
    segs = frag.split("/")
    if not all(re.fullmatch(r"(?:[A-Za-z0-9._~:-]|%[0-9A-F]{2})+", s) for s in segs):
        return False
    try:
        return all(pct_segment(_unpct(s)) == s for s in segs)
    except UnicodeDecodeError:
        return False


def _unpct(seg: str) -> str:
    raw, out, i = seg.encode("ascii"), bytearray(), 0
    while i < len(raw):
        if raw[i:i + 1] == b"%":
            out.append(int(raw[i + 1:i + 3], 16))
            i += 3
        else:
            out.append(raw[i])
            i += 1
    return out.decode("utf-8")


def edge_key(e: dict) -> list[str]:
    return [e["kind"], e["from"], e["to"], e.get("qualifier", "")]


def edge_id(e: dict) -> str:
    return dhash("eija.weave.edge-id.v1", edge_key(e))


EIJA_NS = uuid.uuid5(uuid.NAMESPACE_URL, "urn:eija:weave:id-namespace:1")


def export_uuid(node_id: str) -> uuid.UUID:
    return uuid.uuid5(EIJA_NS, node_id)


def export_ncname(node_id: str) -> str:
    """xs:ID-safe identifier for ArchiMate exchange files (an ID must be an NCName; a UUID may start with a digit)."""
    return "eija-" + str(export_uuid(node_id))


def uuid5_by_hand(namespace: uuid.UUID, name: str) -> uuid.UUID:
    """RFC 9562 section 5.5 written out, to cross-check the standard library."""
    h = bytearray(hashlib.sha1(namespace.bytes + name.encode("utf-8")).digest()[:16])
    h[6] = (h[6] & 0x0F) | 0x50
    h[8] = (h[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(h))


def swhid_cnt(data: bytes) -> str:
    return "swh:1:cnt:" + hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def lf_sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data.decode("utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


# ---- graph hashing: sorted records, two-level Merkle over source-file shards ---------------------------

def node_shard(rec: dict) -> str:
    return split_id(rec["id"])[0]


def node_rh(rec: dict) -> str:
    return dhash("eija.weave.node.v1", rec)


def edge_rh(rec: dict) -> str:
    return dhash("eija.weave.edge.v1", rec)


def shard_hashes(nodes: list[dict], edges: list[dict]) -> dict[str, str]:
    """{shard path: shard hash}. A shard is the set of records asserted by one source file."""
    entries: dict[str, list[list[str]]] = {}
    for n in nodes:
        entries.setdefault(node_shard(n), []).append(["n", n["id"], node_rh(n)])
    for e in edges:
        entries.setdefault(e["asserted_in"], []).append(["e", *edge_key(e), edge_rh(e)])
    return {p: dhash("eija.weave.shard.v1", sorted(rows)) for p, rows in sorted(entries.items())}


def _views() -> dict[str, list[str]]:
    """Named views (link kinds per view) from graph/schema/metamodel.json: the single definition."""
    return json.loads((ROOT / "graph" / "schema" / "metamodel.json").read_text(encoding="utf-8"))["views"]


def view_records(nodes: list[dict], edges: list[dict], view: str) -> tuple[list[dict], list[dict]]:
    """The records of one named view: its edges (kind in the view) plus the node records of their endpoints.

    An endpoint that is not a node (a tombstone start of `renamed_to`) contributes no node record.
    """
    views = _views()
    if view not in views:
        raise CanonError(f"unknown view {view!r}")
    kinds = set(views[view])
    es = [e for e in edges if e["kind"] in kinds]
    ends = {e["from"] for e in es} | {e["to"] for e in es}
    return [n for n in nodes if n["id"] in ends], es


def graph_root(nodes: list[dict], edges: list[dict], view: str | None = None) -> str:
    """Root over shards. With `view`, only the records of that view enter (see view_records) and the view name is in the input."""
    if view is not None:
        nodes, edges = view_records(nodes, edges, view)
    shards = shard_hashes(nodes, edges)
    body: dict[str, Any] = {"metamodel_major": METAMODEL_MAJOR, "shards": sorted([p, h] for p, h in shards.items())}
    if view is not None:
        body["view"] = view
    return dhash("eija.weave.root.v1", body)


# ---- rename resolution ---------------------------------------------------------------------------------

def _maps(records: list[tuple[str, str]]) -> tuple[dict[str, str], dict[str, str]]:
    """(id-level map, path-level map). Sorted first so a non-functional set still gives one deterministic (but rejected) map."""
    ordered = sorted(records)
    return ({o: n for o, n in ordered if "#" in o or "#" in n}, {o: n for o, n in ordered if "#" not in o and "#" not in n})


def _step(cur: str, id_map: dict[str, str], path_map: dict[str, str]) -> str | None:
    """One rewrite. Strategy: an id-level rule for the whole id, else the path-level rule for its file part; None at a normal form."""
    if cur in id_map:
        return id_map[cur]
    path, frag = split_id(cur)
    if "repo://" + path in path_map:
        return path_map["repo://" + path] + ("#" + frag if frag else "")
    return None


def _walk(node_id: str, id_map: dict[str, str], path_map: dict[str, str]) -> tuple[str, list[str]]:
    """(normal form, []) or ("", the cycle rotated to start at its smallest element)."""
    seen: dict[str, int] = {}
    order: list[str] = []
    cur: str | None = node_id
    while cur is not None:
        if cur in seen:
            cyc = order[seen[cur]:]
            i = cyc.index(min(cyc))
            return "", cyc[i:] + cyc[:i]
        seen[cur] = len(order)
        order.append(cur)
        nxt = _step(cur, id_map, path_map)
        if nxt is None:
            return cur, []
        cur = nxt
    raise AssertionError("unreachable")


def check_renames(records: list[tuple[str, str]]) -> list[str]:
    """Problems in a rename set (pairs old, new).

    non-functional: a left side used twice with different targets.
    cycle: a cycle of the relation itself.
    composite-cycle: a cycle of the LIFTED system (id-level rules first, then path-level rules applied to the file part). It is
    checked by walking from every left side: a cycle of the lifted system contains a step whose current id is a left side, so
    every non-terminating trajectory is found from a left side (design section 5.3).
    """
    problems = []
    seen: dict[str, str] = {}
    for old, new in sorted(records):
        if old in seen and seen[old] != new:
            problems.append(f"non-functional: {old} -> {seen[old]} and {new}")
        seen[old] = new
    for start in sorted(seen):
        cur, path = start, []
        while cur in seen:
            if cur in path:
                problems.append("cycle: " + " -> ".join(path[path.index(cur):] + [cur]))
                break
            path.append(cur)
            cur = seen[cur]
    id_map, path_map = _maps(records)
    cycles = set()
    for start in sorted(seen):
        _, cyc = _walk(start, id_map, path_map)
        if cyc:
            cycles.add(tuple(cyc))
    problems += ["composite-cycle: " + " -> ".join(c + (c[0],)) for c in sorted(cycles)]
    return sorted(set(problems))


def resolve(node_id: str, records: list[tuple[str, str]]) -> str:
    """Normal form of an id under a functional rename set. Raises CanonError on a cycle of the lifted system."""
    id_map, path_map = _maps(records)
    nf, cyc = _walk(node_id, id_map, path_map)
    if cyc:
        raise CanonError("rename cycle at " + " -> ".join(cyc + [cyc[0]]))
    return nf


# ---- synthetic graphs --------------------------------------------------------------------------------------

KINDS = ["contains", "depends_on", "calls", "covers", "verifies", "satisfies", "documents", "names"]


def synth(n_nodes: int, n_edges: int, seed: int, files: int | None = None) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    files = files or max(3, n_nodes // 6)
    nodes, seen = [], set()
    for i in range(n_nodes):
        f = f"src/pkg/mod{rng.randrange(files):05d}.py"
        nid = make_id(f, f"sym{i:06d}")
        if nid in seen:
            continue
        seen.add(nid)
        nodes.append({"id": nid, "type": "symbol", "digest": {"method": "ast-v1", "value": "sha256:" + f"{rng.getrandbits(256):064x}"},
                      "prov": "exact"})
    ids = [n["id"] for n in nodes]
    edges, ekeys = [], set()
    while len(edges) < n_edges:
        a, b = rng.choice(ids), rng.choice(ids)
        kind = rng.choice(KINDS)
        if a == b or (kind, a, b) in ekeys:
            continue
        ekeys.add((kind, a, b))
        edges.append({"kind": kind, "from": a, "to": b, "class": "derived", "prov": "exact", "asserted_in": split_id(a)[0]})
    return nodes, edges


def shuffled(rec: Any, rng: random.Random) -> Any:
    if isinstance(rec, dict):
        keys = list(rec)
        rng.shuffle(keys)
        return {k: shuffled(rec[k], rng) for k in keys}
    if isinstance(rec, list):
        return [shuffled(x, rng) for x in rec]
    return rec


# ---- checks --------------------------------------------------------------------------------------------------

def _first_diff(a: str, b: str) -> tuple[str, str]:
    for x, y in zip(a, b):
        if x != y:
            return x, y
    return (a[len(b):][:1], "") if len(a) > len(b) else ("", b[len(a):][:1])


def _rand_text(rng: random.Random, ascii_only: bool) -> str:
    pool_ascii = ["a", "b", "Z", "0", "-", "_", ".", "/", " ", '"', "\\", "\n", "\t", "\x00", "\x1f", "\x7f", "\b", "\f", "\r"]
    pool_uni = ["é", " ", " ", "퟿", "", "￿", "\U00010000", "\U0001f600", "\U0010ffff", "€"]
    pool = pool_ascii if ascii_only else pool_ascii + pool_uni
    return "".join(rng.choice(pool) for _ in range(rng.randrange(0, 6)))


def _rand_doc(rng: random.Random, ascii_keys: bool, depth: int = 0) -> Any:
    r = rng.random()
    if depth > 2 or r < 0.35:
        return rng.choice([None, True, False, 0, 1, -1, SAFE_INT, -SAFE_INT, rng.randrange(-10**6, 10**6),
                           _rand_text(rng, False)])
    if r < 0.6:
        return [_rand_doc(rng, ascii_keys, depth + 1) for _ in range(rng.randrange(0, 4))]
    return {_rand_text(rng, ascii_keys) or "k": _rand_doc(rng, ascii_keys, depth + 1) for _ in range(rng.randrange(0, 5))}


def jcs_subset(n: int = 4000, seed: int = 1) -> dict:
    """C1: own subset writer vs rfc8785 0.1.4 and vs the kernel's canonical()."""
    rng = random.Random(seed)
    docs = [(_rand_doc(rng, True), True) for _ in range(n // 2)] + [(_rand_doc(rng, False), False) for _ in range(n // 2)]
    rejects = {"float": 1.0, "nan": float("nan"), "int_2**53": 2**53, "int_-2**60": -(2**60), "lone_surrogate": "\ud800",
               "bytes": b"x", "set": {1}, "int_key": {1: 2}}
    rejected = {}
    for name, value in rejects.items():
        try:
            jcs_dumps(value)
            rejected[name] = False
        except CanonError:
            rejected[name] = True
    res: dict[str, Any] = {"status": "MEASURED", "domain": f"{len(docs)} seeded random documents (half with ASCII-only keys)",
                           "all_out_of_subset_inputs_rejected": all(rejected.values()), "rejected": rejected}
    mism_kernel_ascii = mism_kernel_uni = mism_rfc = 0
    unexplained = 0
    for doc, ascii_keys in docs:
        mine = jcs_dumps(doc)
        kernel = kernel_canonical(doc).encode("utf-8")
        if mine != kernel:
            if ascii_keys:
                mism_kernel_ascii += 1
            else:
                mism_kernel_uni += 1
                if not _explained_by_key_order(doc):
                    unexplained += 1
        if rfc8785 is not None and rfc8785.dumps(doc) != mine:
            mism_rfc += 1
    res["kernel_canonical_differs_ascii_key_docs"] = mism_kernel_ascii
    res["kernel_canonical_differs_nonascii_key_docs"] = mism_kernel_uni
    res["kernel_differences_not_explained_by_utf16_key_order"] = unexplained
    res["rfc8785_0.1.4_differs"] = mism_rfc if rfc8785 is not None else not_run("rfc8785 not installed")
    return res


def _explained_by_key_order(doc: Any) -> bool:
    """True when some object in doc has two keys ordered differently by code point and by UTF-16 code unit."""
    if isinstance(doc, dict):
        keys = list(doc)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if (a < b) != (a.encode("utf-16-be") < b.encode("utf-16-be")):
                    return True
        return any(_explained_by_key_order(v) for v in doc.values())
    if isinstance(doc, list):
        return any(_explained_by_key_order(v) for v in doc)
    return False


def utf16_order_boundary() -> dict:
    """C1b: code-point order and UTF-16 code-unit order disagree exactly for (supplementary, U+E000..U+FFFF) pairs."""
    reps = [0x0, 0x41, 0x7F, 0x80, 0x7FF, 0x800, 0xD7FF, 0xE000, 0xFFFD, 0xFFFF, 0x10000, 0x10FFFF, 0x1F600]
    disagree = []
    for a in reps:
        for b in reps:
            ca, cb = chr(a), chr(b)
            if (ca < cb) != (ca.encode("utf-16-be") < cb.encode("utf-16-be")) and a != b:
                disagree.append([a, b])
    expected = sorted([a, b] for a in reps for b in reps if (a >= 0x10000 and 0xE000 <= b <= 0xFFFF) or (b >= 0x10000 and 0xE000 <= a <= 0xFFFF))
    return {"status": "MEASURED", "domain": f"all ordered pairs of {len(reps)} representative scalar values",
            "disagreeing_pairs": len(disagree), "exactly_supplementary_vs_e000_ffff": sorted(disagree) == expected}


def domain_separation() -> dict:
    """C2: length-safe, domain-separated hashing versus Doorstop-style concatenation."""
    cat = lambda *xs: "sha256:" + hashlib.sha256("".join(xs).encode()).hexdigest()  # noqa: E731
    return {"status": "MEASURED", "domain": "hand-built pairs",
            "concat_collides_a_bc_vs_ab_c": cat("a", "bc") == cat("ab", "c"),
            "jcs_array_collides_a_bc_vs_ab_c": dhash("eija.weave.node.v1", ["a", "bc"]) == dhash("eija.weave.node.v1", ["ab", "c"]),
            "same_record_different_domain_collides": dhash("eija.weave.node.v1", {"k": 1}) == dhash("eija.weave.edge.v1", {"k": 1})}


def permutation_invariance(n_nodes: int = 300, n_edges: int = 900, shuffles: int = 200, seed: int = 3) -> dict:
    """C3: the root is a function of the record SET; insertion order, key order and list order do not matter."""
    nodes, edges = synth(n_nodes, n_edges, seed)
    base = graph_root(nodes, edges)
    rng = random.Random(seed + 1)
    roots, naive, naive_sorted_keys = set(), set(), set()
    nx_forms = set()
    for _ in range(shuffles):
        ns, es = shuffled(nodes, rng), shuffled(edges, rng)
        rng.shuffle(ns)
        rng.shuffle(es)
        roots.add(graph_root(ns, es))
        naive.add(hashlib.sha256(json.dumps({"nodes": ns, "edges": es}).encode()).hexdigest())
        naive_sorted_keys.add(hashlib.sha256(json.dumps({"nodes": ns, "edges": es}, sort_keys=True).encode()).hexdigest())
        if nx is not None:
            g = nx.MultiDiGraph()
            for r in ns:
                g.add_node(r["id"], type=r["type"])
            for r in es:
                g.add_edge(r["from"], r["to"], kind=r["kind"])
            nx_forms.add(hashlib.sha256(json.dumps(nx.node_link_data(g, edges="links")).encode()).hexdigest())
    return {"status": "MEASURED", "domain": f"{n_nodes} nodes, {n_edges} edges, {shuffles} shuffles (records, keys, lists)",
            "distinct_roots_sorted_records": len(roots), "root_equals_unshuffled": roots == {base},
            "distinct_hashes_insertion_order_json_dumps": len(naive),
            "distinct_hashes_json_dumps_sort_keys_unsorted_lists": len(naive_sorted_keys),
            "distinct_hashes_networkx_node_link_data": len(nx_forms) if nx is not None else not_run("networkx not installed")}


def labelling_versus_identity() -> dict:
    """C4: an isomorphism-invariant (label-free) hash conflates graphs an assurance graph must keep apart."""
    if nx is None:
        return not_run("networkx not installed")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # networkx 3.5 warns that WL hashes changed in 3.5; irrelevant to equality checks
        return _labelling_versus_identity()


def _labelling_versus_identity() -> dict:
    c6, two_c3 = nx.cycle_graph(6), nx.disjoint_union(nx.cycle_graph(3), nx.cycle_graph(3))
    wl_equal_but_not_isomorphic = (nx.weisfeiler_lehman_graph_hash(c6) == nx.weisfeiler_lehman_graph_hash(two_c3)
                                   and not nx.is_isomorphic(c6, two_c3))

    def build(sat_a: str, req_a: str, sat_b: str, req_b: str):
        a = [{"kind": "satisfies", "from": sat_a, "to": req_a, "class": "declared", "prov": "exact", "asserted_in": "graph/links/a.jsonl"},
             {"kind": "satisfies", "from": sat_b, "to": req_b, "class": "declared", "prov": "exact", "asserted_in": "graph/links/a.jsonl"}]
        return a

    s1, s2 = make_id("src/a.py", "S1"), make_id("src/a.py", "S2")
    r1, r2 = make_id("docs/r.csv", "R1"), make_id("docs/r.csv", "R2")
    g1 = build(s1, r1, s2, r2)   # S1 satisfies R1, S2 satisfies R2
    g2 = build(s1, r2, s2, r1)   # S1 satisfies R2, S2 satisfies R1: same shape, different claims
    shape = lambda es: nx.DiGraph([(e["from"], e["to"]) for e in es])  # noqa: E731
    wl = lambda es: nx.weisfeiler_lehman_graph_hash(shape(es))  # noqa: E731
    return {"status": "MEASURED", "domain": "two hand-built cases; networkx 3.5 weisfeiler_lehman_graph_hash",
            "wl_hash_equal_for_c6_and_two_c3_which_are_not_isomorphic": wl_equal_but_not_isomorphic,
            "isomorphic_graphs_with_different_claims_are_isomorphic": nx.is_isomorphic(shape(g1), shape(g2)),
            "label_free_wl_hash_equal_for_different_claims": wl(g1) == wl(g2),
            "sorted_record_root_equal_for_different_claims": graph_root([], g1) == graph_root([], g2)}


def shard_locality(seed: int = 5) -> dict:
    """C5: a change in one file changes exactly that shard and the root; a reorder changes nothing."""
    nodes, edges = synth(120, 300, seed, files=20)
    before = shard_hashes(nodes, edges)
    root0 = graph_root(nodes, edges)
    target = sorted(before)[3]
    n2 = [dict(n) for n in nodes]
    for n in n2:
        if node_shard(n) == target:
            n["digest"] = {"method": "ast-v1", "value": "sha256:" + "0" * 64}
            break
    after_node = shard_hashes(n2, edges)
    e2 = edges + [{"kind": "calls", "from": nodes[0]["id"], "to": nodes[1]["id"], "class": "derived", "prov": "exact",
                   "asserted_in": "src/pkg/other.py"}]
    after_edge = shard_hashes(nodes, e2)
    changed = lambda a, b: sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))  # noqa: E731
    return {"status": "MEASURED", "domain": f"{len(before)} shards, one seeded graph",
            "digest_change_shards_changed": changed(before, after_node) == [target], "digest_change_root_changed": graph_root(n2, edges) != root0,
            "edge_in_new_file_shards_changed": changed(before, after_edge) == ["src/pkg/other.py"],
            "reorder_root_unchanged": graph_root(list(reversed(nodes)), list(reversed(edges))) == root0,
            "shards_total": len(before)}


CLOSURE_MUTATIONS = ("node_record", "edge_class", "edge_qualifier", "edge_anchor", "edge_kind")


def _mutate_edge(e: dict, how: str) -> dict:
    if how == "edge_class":
        return {**e, "class": "declared" if e["class"] != "declared" else "inferred"}
    if how == "edge_qualifier":
        return {**e, "qualifier": "surface"}
    if how == "edge_anchor":
        return {**e, "anchors": [{"end": "to", "method": "ast-v1", "digest": "sha256:" + "e" * 64}]}
    return {**e, "kind": "calls" if e["kind"] != "calls" else "depends_on"}


def closure_fingerprint(trials: int = 60, seed: int = 7) -> dict:
    """C6: F(n) = hash of the node records AND the edge records induced on n's dependency closure.

    Trials rotate through five mutations: a node record, and an edge's class, qualifier, anchors or kind. F(m) changes iff the
    mutated record lies in m's closure, so the changed set must equal the kernel closure() of the mutated node (or of the edge's
    source). The v1 fingerprint (node records only) is computed alongside to show which trials it misses.
    """
    rng = random.Random(seed)
    per: dict[str, dict[str, int]] = {m: {"trials": 0, "mismatches": 0, "missed_by_node_only_v1": 0} for m in CLOSURE_MUTATIONS}
    for t in range(trials):
        how = CLOSURE_MUTATIONS[t % len(CLOSURE_MUTATIONS)]
        nodes, edges = synth(40, 90, seed * 1000 + t, files=8)
        fwd: dict[str, list[str]] = {}
        rev: dict[str, list[str]] = {}
        for e in edges:  # every kind here means "to affects from" (affects: to_source): adjacency from -> is affected
            fwd.setdefault(e["to"], []).append(e["from"])
            rev.setdefault(e["from"], []).append(e["to"])

        def fps(nds: list[dict], eds: list[dict]) -> tuple[dict[str, str], dict[str, str]]:
            by_id = {n["id"]: n for n in nds}
            v2, v1 = {}, {}
            for nid in by_id:
                deps = kernel_closure(rev, [nid])["affected"]  # everything nid depends on, cycles included
                rows = sorted([d, node_rh(by_id[d])] for d in deps)
                erows = sorted([*edge_key(e), edge_rh(e)] for e in eds if e["from"] in deps and e["to"] in deps)
                v2[nid] = dhash("eija.weave.closure.v2", {"nodes": rows, "edges": erows})
                v1[nid] = hashlib.sha256(jcs_dumps(rows)).hexdigest()  # the rejected node-only form; not a registered tag
            return v2, v1

        b2, b1 = fps(nodes, edges)
        if how == "node_record":
            m = rng.choice(sorted(n["id"] for n in nodes))
            nodes2 = [{**n, "digest": {"method": "ast-v1", "value": "sha256:" + "f" * 64}} if n["id"] == m else n for n in nodes]
            edges2 = edges
        else:
            i = rng.randrange(len(edges))
            m = edges[i]["from"]
            nodes2 = nodes
            edges2 = [_mutate_edge(e, how) if j == i else e for j, e in enumerate(edges)]
        a2, a1 = fps(nodes2, edges2)
        expected = kernel_closure(fwd, [m])["affected"]  # the kernel's closure: m affects these
        changed2 = sorted(n for n in b2 if b2[n] != a2[n])
        changed1 = sorted(n for n in b1 if b1[n] != a1[n])
        per[how]["trials"] += 1
        per[how]["mismatches"] += changed2 != expected
        per[how]["missed_by_node_only_v1"] += changed1 != expected
    return {"status": "MEASURED",
            "domain": f"{trials} seeded random cyclic graphs of 40 nodes and 90 edges, one mutated record each, five mutation kinds in rotation",
            "trials_where_changed_set_differs_from_kernel_closure": sum(v["mismatches"] for v in per.values()),
            "trials": sum(v["trials"] for v in per.values()), "by_mutation": per,
            "edge_trials_missed_by_node_only_fingerprint": sum(v["missed_by_node_only_v1"] for k, v in per.items() if k != "node_record")}


def rename_resolution(trials: int = 100, seed: int = 11) -> dict:
    """C7: rename resolution is independent of record order; conflicts and cycles are detected."""
    rng = random.Random(seed)
    files = [f"src/p/m{i}.py" for i in range(8)]
    bad = 0
    for _ in range(trials):
        chain = rng.sample(files, 5)
        recs = [(f"repo://{chain[i]}", f"repo://{chain[i + 1]}") for i in range(4)]  # path-level chain
        recs.append((make_id(chain[4], "f"), make_id(chain[4], "g")))               # id-level rename inside the last file
        probes = [make_id(chain[0], "f"), make_id(chain[0], "h"), "repo://" + chain[0]]
        expect = [resolve(p, recs) for p in probes]
        for _ in range(10):
            rng.shuffle(recs)
            bad += [resolve(p, recs) for p in probes] != expect
    conflict = check_renames([("repo://a.py", "repo://b.py"), ("repo://a.py", "repo://c.py")])
    cycle = check_renames([("repo://a.py", "repo://b.py"), ("repo://b.py", "repo://a.py")])
    # the audit counterexample: each record is functional and injective and the relation is acyclic, but the lifted system loops
    mixed = [("repo://a.py", "repo://b.py"), ("repo://b.py#f", "repo://a.py#f")]
    mixed_problems = check_renames(mixed)
    try:
        resolve("repo://a.py#f", mixed)
        mixed_resolve_raises = False
    except CanonError:
        mixed_resolve_raises = True
    return {"status": "MEASURED", "domain": f"{trials} seeded chains x 10 shuffles x 3 probes; the mixed-level counterexample",
            "order_dependent_resolutions": bad,
            "nonfunctional_detected": len(conflict) == 1, "cycle_detected": any(p.startswith("cycle") for p in cycle),
            "mixed_level_counterexample": {"records": [list(r) for r in mixed], "relation_cycle_or_conflict_found": any(
                p.startswith(("cycle", "non-functional")) for p in mixed_problems), "composite_cycle_found": any(
                p.startswith("composite-cycle") for p in mixed_problems), "resolve_raises": mixed_resolve_raises},
            "example_probe": resolve(make_id("src/p/m0.py", "f"), [("repo://src/p/m0.py", "repo://src/p/m1.py"),
                                                                    (make_id("src/p/m1.py", "f"), make_id("src/p/m1.py", "g"))])}


def id_canonicality() -> dict:
    cases = {
        "ok_symbol": ("repo://src/a.py#f.g", True), "colon_literal": ("repo://x/y.json#effect/Audit:Sent", True),
        "needless_pct_colon": ("repo://x/y.json#effect/Audit%3ASent", False), "ok_pct": ("repo://x/y.json#state/Awaiting%20approval", True),
        "lowercase_pct": ("repo://x/y.json#state/a%2fb", False), "needless_pct": ("repo://x/y.json#state/%41", False),
        "space": ("repo://x/y.json#state/a b", False), "dotdot": ("repo://x/../y.json", False), "backslash": ("repo://x\\y.json", False),
        "trailing_hash": ("repo://x/y.json#", False), "unicode_path": ("repo://x/é.json", False), "scheme": ("file://x/y.json", False),
        "leading_slash": ("repo:///x/y.json", False), "empty_segment": ("repo://x//y.json", False),
    }
    got = {k: is_canonical_id(v[0]) for k, v in cases.items()}
    return {"status": "MEASURED", "domain": "14 hand-built ids", "all_as_expected": got == {k: v[1] for k, v in cases.items()},
            "mismatches": sorted(k for k in got if got[k] != cases[k][1]),
            "roundtrip_pct": pct_segment("Awaiting approval") == "Awaiting%20approval" and _unpct("Awaiting%20approval") == "Awaiting approval"}


def export_ids() -> dict:
    ns_ok = uuid5_by_hand(uuid.NAMESPACE_DNS, "python.org") == uuid.uuid5(uuid.NAMESPACE_DNS, "python.org")
    ids = [make_id("src/a.py", f"s{i}") for i in range(2000)]
    hand_equal = all(uuid5_by_hand(EIJA_NS, i) == export_uuid(i) for i in ids)
    ex = make_id("src/eija_studio/domain/impact.py", "closure")
    return {"status": "MEASURED", "domain": "2000 ids", "hand_rfc9562_v5_equals_stdlib": ns_ok and hand_equal,
            "namespace": str(EIJA_NS), "example_id": ex, "example_uuid": str(export_uuid(ex)), "example_ncname": export_ncname(ex),
            "uuid_collisions_in_2000": 2000 - len({export_uuid(i) for i in ids}),
            "ncname_valid": bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9._-]*", export_ncname(ex)))}


def swhid_and_line_endings() -> dict:
    lic = ROOT / "LICENSE"
    lf, crlf = b"a\nb\n", b"a\r\nb\r\n"
    res: dict[str, Any] = {"status": "MEASURED", "domain": "one synthetic two-line file and the worktree LICENSE",
                           "git_blob_id_lf_vs_crlf_differ": swhid_cnt(lf) != swhid_cnt(crlf),
                           "lf_sha256_lf_vs_crlf_equal": lf_sha256(lf) == lf_sha256(crlf)}
    try:
        out = subprocess.run(["git", "hash-object", str(lic)], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
        res["swhid_cnt_equals_git_hash_object_for_LICENSE"] = swhid_cnt(lic.read_bytes()) == "swh:1:cnt:" + out
    except (OSError, subprocess.SubprocessError):
        res["swhid_cnt_equals_git_hash_object_for_LICENSE"] = not_run("git not runnable")
    return res


def scale(nodes: int = 100_000, edges: int = 400_000, seed: int = 9) -> dict:
    global _DUMPS
    t0 = time.perf_counter()
    ns, es = synth(nodes, edges, seed, files=nodes // 8)
    t1 = time.perf_counter()
    root = graph_root(ns, es)
    t2 = time.perf_counter()
    _DUMPS = jcs_dumps_fast
    try:
        fast_root = graph_root(ns, es)
    finally:
        _DUMPS = jcs_dumps
    t3 = time.perf_counter()
    return {"status": "MEASURED", "domain": f"{nodes} nodes, {edges} edges, one run, this machine, not deterministic",
            "python": sys.version.split()[0], "platform": platform.platform(), "processor": platform.processor(),
            "python_implementation": platform.python_implementation(), "generate_seconds": round(t1 - t0, 2),
            "root_seconds_pure_python_writer": round(t2 - t1, 2), "root_seconds_c_json_encoder": round(t3 - t2, 2),
            "roots_equal": root == fast_root, "root": root}


def report(timing: bool = False) -> dict:
    checks = {
        "c1_jcs_subset": jcs_subset(), "c1b_utf16_order_boundary": utf16_order_boundary(), "c2_domain_separation": domain_separation(),
        "c3_permutation_invariance": permutation_invariance(), "c4_labelling_versus_identity": labelling_versus_identity(),
        "c5_shard_locality": shard_locality(), "c6_closure_fingerprint": closure_fingerprint(), "c7_rename_resolution": rename_resolution(),
        "c8_id_canonicality": id_canonicality(), "c9_export_ids": export_ids(), "c10_swhid_and_line_endings": swhid_and_line_endings(),
    }
    if timing:
        checks["c11_scale_timing"] = scale()
    return {"schema": "eija.weave.bench.identity/v1", "python": f"{sys.version_info.major}.{sys.version_info.minor}", "checks": checks}


def vectors() -> dict:
    """Golden vectors every eijagraph.canon implementation must reproduce."""
    cases = [
        ("empty_object", {}), ("empty_array", []), ("null_true_false", [None, True, False]),
        ("int_edges", [0, -1, SAFE_INT, -SAFE_INT]), ("string_escapes", "\"\\/\b\f\n\r\t\x00\x1f\x7f"),
        ("string_unicode", "é €\U0001f600"),
        ("key_order_ascii", {"b": 1, "a": 2, "B": 3, "": 4}),
        ("key_order_utf16", {"\U00010000": 1, "￿": 2, "": 3, "퟿": 4}),
        ("nested", {"z": [{"b": None, "a": [1, 2]}], "a": {"y": "x"}}),
        ("node_record", {"id": "repo://src/a.py#f", "type": "symbol", "prov": "exact",
                         "digest": {"method": "ast-v1", "value": "sha256:" + "ab" * 32}}),
    ]
    out = []
    for name, value in cases:
        raw = jcs_dumps(value)
        out.append({"name": name, "input": value, "jcs": raw.decode("utf-8"), "sha256_of_jcs": hashlib.sha256(raw).hexdigest(),
                    "eija.weave.node.v1": dhash("eija.weave.node.v1", value)})
    rej = [{"name": "float", "why": "floats are outside the subset (RFC 8785 number formatting is not needed and not implemented)"},
           {"name": "int_2**53", "why": "outside +-(2^53-1)"}, {"name": "lone_surrogate", "why": "RFC 8785 requires an error"},
           {"name": "non_string_key", "why": "JSON object keys are strings"}, {"name": "bytes_or_set", "why": "not JSON types"}]
    ids = [{"id": make_id("src/a.py", "f"), "canonical": True}, {"id": "repo://x/y.json#state/a%2fb", "canonical": False},
           {"id": make_id("examples/e.json", "state", "Awaiting approval"), "canonical": True}]
    edge = {"kind": "satisfies", "from": make_id("src/a.py", "f"), "to": make_id("docs/verification/ACCEPTANCE_MATRIX.csv", "AC01")}
    # one shard holding both node and edge rows, in an order that exercises the row comparator ("e" < "n"; a 6-element edge row
    # against 3-element node rows is decided at element 0), plus a view root
    f = "src/a.py"
    sh_nodes = [{"id": make_id(f, "b"), "type": "symbol", "prov": "exact", "digest": {"method": "ast-v1", "value": "sha256:" + "01" * 32}},
                {"id": make_id(f, "a"), "type": "symbol", "prov": "exact", "digest": {"method": "ast-v1", "value": "sha256:" + "02" * 32}}]
    sh_edges = [{"kind": "depends_on", "from": sh_nodes[0]["id"], "to": sh_nodes[1]["id"], "class": "derived", "prov": "exact", "asserted_in": f},
                {"kind": "calls", "from": sh_nodes[0]["id"], "to": sh_nodes[1]["id"], "class": "derived", "prov": "exact", "asserted_in": f},
                {"kind": "names", "from": sh_nodes[1]["id"], "to": sh_nodes[0]["id"], "class": "declared", "prov": "exact",
                 "asserted_in": "docs/l.md", "qualifier": "surface"}]
    shard = shard_hashes(sh_nodes, sh_edges)
    return {"schema": "eija.weave.identity-vectors/v1", "jcs": out, "must_reject": rej, "ids": ids,
            "shard_rows": {"comparator": "element-wise lexicographic over the row lists; strings compare by UTF-8 bytes (every element is "
                                         "ASCII by schema, so code-point, byte and UTF-16 order coincide); rows are ['n', id, hash] and "
                                         "['e', kind, from, to, qualifier, hash]",
                           "nodes": sh_nodes, "edges": sh_edges, "shard_hashes": shard, "root": graph_root(sh_nodes, sh_edges),
                           "language_view_root": graph_root(sh_nodes, sh_edges, view="language"),
                           "structure_view_root": graph_root(sh_nodes, sh_edges, view="structure")},
            "edge_id": {"edge": edge, "key": edge_key(edge), "id": edge_id(edge)},
            "uuid": {"namespace": str(EIJA_NS), "id": ids[0]["id"], "uuid5": str(export_uuid(ids[0]["id"]))},
            "root": {"nodes_edges": "synth(30, 60, seed=1) from graph/bench/identity_checks.py",
                     "value": graph_root(*synth(30, 60, 1))}}


def dump(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main(argv: list[str]) -> int:
    rep = report(timing="--timing" in argv)
    text = dump(rep)
    sys.stdout.write(text)
    if "--write" in argv:
        (ROOT / "graph" / "bench" / "results").mkdir(exist_ok=True)
        (ROOT / "graph" / "bench" / "results" / "identity-checks.json").write_bytes(dump(report()).encode("utf-8"))
        (ROOT / "graph" / "schema" / "identity-vectors.json").write_bytes(dump(vectors()).encode("utf-8"))
        if "--timing" in argv:  # non-deterministic, so a separate artefact that no test compares byte for byte
            (ROOT / "graph" / "bench" / "results" / "identity-timing.json").write_bytes(
                dump({"schema": "eija.weave.bench.identity-timing/v1", "label": "MEASUREMENT, not deterministic, one run",
                      "c11_scale_timing": rep["checks"]["c11_scale_timing"]}).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
