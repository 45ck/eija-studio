"""Independent checks over graph/schema/metamodel.json and instances of it (the metamodel aspect owns the file).

The metamodel aspect ships its own coherence check (``graph/schema/build_schemas.check_metamodel``) and its
own join-level reference (``graph/schema/typecheck.check_document`` (named ``reference.py`` until 2026-09-29)). This module is a SECOND, separately
written reading of the same specification (graph/schema/README.md), so that a slip in either implementation
shows up as a disagreement (differential test) and so that the formal lane owns three things the first
reading does not have:

* table lemmas about the metamodel itself (``check_tables``): a node type that no signature mentions, an
  obligation nobody can meet, a minimum above a maximum, an obligation that names a rule missing from the catalogue;
* a constructive witness that the metamodel is satisfiable with every node type inhabited and every minimum
  obligation met (``constructive_instance``), which is what "the constraints are not vacuous or contradictory" means
  for a finite table of this size (no solver is needed until obligations interact; see the design document);
* an instance checker (``check_instance``) that also enforces the minimum obligations, which the reference leaves
  to the rule catalogue (WV-010, WV-011, WV-031, WV-037, WV-053, WV-054).

Findings are tuples (code, subject); the join-level codes and subjects deliberately equal the reference's.
"""
from __future__ import annotations

from collections import Counter, defaultdict

Finding = tuple[str, str]


def expand(mm: dict, names: list[str]) -> list[str]:
    """Concrete node types of a signature side. '*' is every type; a supertype is its members."""
    out: set[str] = set()
    for n in names:
        if n == "*":
            out |= set(mm["node_types"])
        elif n in mm["supertypes"]:
            out |= set(mm["supertypes"][n])
        elif n in mm["node_types"]:
            out.add(n)
        else:
            raise KeyError(n)
    return sorted(out)


def _rows(mm: dict, kind: str) -> list[dict]:
    return [{**r, "_from": set(expand(mm, r["from"])), "_to": set(expand(mm, r["to"]))}
            for r in mm["link_types"][kind]["signatures"]]


def _obligation_type(scope: str) -> str:
    return scope.split(maxsplit=1)[0]  # "term with ddd_role aggregate" -> "term"; the qualifier text is not machine-checked here


def check_tables(mm: dict, rule_ids: set[str] | None = None) -> list[Finding]:
    out: list[Finding] = []
    types = set(mm["node_types"])
    mentioned: set[str] = set()
    for kind, spec in sorted(mm["link_types"].items()):
        rows = spec["signatures"]
        if not rows:
            out.append(("MM-003", kind))
        for i, r in enumerate(rows):
            try:
                frm, to = expand(mm, r["from"]), expand(mm, r["to"])
            except KeyError:
                out.append(("MM-002", f"{kind}#{i}"))
                continue
            if not frm or not to:
                out.append(("MM-003", f"{kind}#{i}"))
            mentioned |= set(frm) | set(to)
            for ob in r.get("obligations", []):
                side_types = set(to if ob["side"] == "in" else frm)
                scope = _obligation_type(ob["scope"])
                if scope not in side_types:
                    out.append(("MM-020", f"{kind}#{i}:{ob['rule']}"))  # the obligation can never be met on this row
                cap = r.get("max_in" if ob["side"] == "in" else "max_out")
                if cap is not None and ob["min"] > cap:
                    out.append(("MM-021", f"{kind}#{i}:{ob['rule']}"))  # minimum above maximum
                if rule_ids is not None and ob["rule"] not in rule_ids:
                    out.append(("MM-022", f"{kind}#{i}:{ob['rule']}"))  # obligation names a rule the catalogue lacks
    for t in sorted(types - mentioned):
        out.append(("MM-004", t))  # a node type no signature mentions can never be linked
    for sup, members in sorted(mm["supertypes"].items()):
        if sup in types:
            out.append(("MM-023", sup))
        for m in members:
            if m not in types:
                out.append(("MM-024", f"{sup}:{m}"))
    ids = Counter(t["tag"] for t in mm["domain_tags"])
    out += [("MM-025", tag) for tag, n in sorted(ids.items()) if n > 1]
    return sorted(set(out))


def check_instance(mm: dict, nodes: list[dict], edges: list[dict], with_min_obligations: bool = False) -> set[Finding]:
    found: set[Finding] = set()
    by_id: dict[str, dict] = {}
    for n in nodes:
        if n["id"] in by_id:
            found.add(("duplicate-id", n["id"]))
        by_id[n["id"]] = n
    seen: set[tuple] = set()
    by_kind: dict[str, list[dict]] = defaultdict(list)
    for e in edges:
        key = (e["kind"], e["from"], e["to"], e.get("qualifier", ""))
        subject = "|".join(key)
        if key in seen:
            found.add(("duplicate-edge", subject))
        seen.add(key)
        if e["from"] == e["to"]:
            found.add(("self-loop", subject))
        spec = mm["link_types"][e["kind"]]
        s, t = by_id.get(e["from"]), by_id.get(e["to"])
        if s is None and not spec.get("from_may_dangle"):
            found.add(("dangling-link", subject))
        if t is None:
            found.add(("dangling-link", subject))
        if s is not None and t is not None:
            rows = [r for r in _rows(mm, e["kind"]) if s["type"] in r["_from"] and t["type"] in r["_to"]]
            q = e.get("qualifier")
            if not rows or not any((("qualifiers" not in r) or (q in r["qualifiers"] if r["qualifiers"] else q is None))
                                   for r in rows):
                found.add(("ill-typed-edge", subject))
            if any(r.get("same_type") and s["type"] != t["type"] for r in rows) and rows:
                found.add(("ill-typed-edge", subject))
        by_kind[e["kind"]].append(e)
    for kind, es in sorted(by_kind.items()):
        for i, r in enumerate(_rows(mm, kind)):
            out_deg, in_deg = Counter(), Counter()
            for e in es:
                s, t = by_id.get(e["from"]), by_id.get(e["to"])
                if s and t and s["type"] in r["_from"] and t["type"] in r["_to"]:
                    out_deg[e["from"]] += 1
                    in_deg[e["to"]] += 1
            for _name, deg, cap in (("out", out_deg, r.get("max_out")), ("in", in_deg, r.get("max_in"))):
                if cap is not None:
                    found |= {("cardinality-exceeded", f"{kind}#{i}:{n}") for n, d in deg.items() if d > cap}
    for kind, es in sorted(by_kind.items()):
        if mm["link_types"][kind]["acyclic"]:
            pairs = {(e["from"], e["to"]) for e in es if e["from"] != e["to"]}
            nodes_ = {x for p in pairs for x in p}
            reach = {n: {b for a, b in pairs if a == n} for n in nodes_}
            changed = True
            while changed:  # transitive closure by iteration (independent of the reference's DFS)
                changed = False
                for n in nodes_:
                    new = set().union(*(reach[m] for m in reach[n])) - reach[n] if reach[n] else set()
                    if new:
                        reach[n] |= new
                        changed = True
            if any(n in reach[n] for n in nodes_):
                found.add(("link-kind-cycle", kind))
    if with_min_obligations:
        for kind, spec in sorted(mm["link_types"].items()):
            for i, r in enumerate(_rows(mm, kind)):
                for ob in r.get("obligations", []):
                    scope = _obligation_type(ob["scope"])
                    side_field = "to" if ob["side"] == "in" else "from"
                    count = Counter()
                    for e in by_kind.get(kind, []):
                        s, t = by_id.get(e["from"]), by_id.get(e["to"])
                        if s and t and s["type"] in r["_from"] and t["type"] in r["_to"]:
                            count[e[side_field]] += 1
                    for n in nodes:
                        if n["type"] == scope and count[n["id"]] < ob["min"]:
                            found.add(("obligation-unmet", f"{ob['rule']}:{n['id']}"))
    return found


def constructive_instance(mm: dict) -> tuple[list[dict], list[dict]]:
    """One node per node type (ids from the metamodel's own examples) and, for every minimum obligation, one edge that
    meets it. Deterministic: the first row that can carry the obligation, the smallest endpoint type."""
    nodes = [{"id": mm["node_types"][t]["example"], "type": t} for t in sorted(mm["node_types"])]
    of_type = {n["type"]: n["id"] for n in nodes}
    edges: list[dict] = []
    for kind, _spec in sorted(mm["link_types"].items()):
        for r in _rows(mm, kind):
            for ob in r.get("obligations", []):
                scope = _obligation_type(ob["scope"])
                own = r["_to"] if ob["side"] == "in" else r["_from"]
                other = r["_from"] if ob["side"] == "in" else r["_to"]
                if scope not in own or not other:
                    continue
                far = sorted(other - {scope})[0] if other - {scope} else scope
                q = (r["qualifiers"][0] if r.get("qualifiers") else None)
                e = {"kind": kind, "from": of_type[far] if ob["side"] == "in" else of_type[scope],
                     "to": of_type[scope] if ob["side"] == "in" else of_type[far]}
                if q is not None:
                    e["qualifier"] = q
                if e not in edges:
                    edges.append(e)
    return nodes, edges


def check_brief(brief: dict) -> list[Finding]:
    """The same table lemmas on graph/brief.json, the prose brief the schema was built from (kept so the first
    measurement is reproducible): free-text hash policy (MM-007), node types in no link type (MM-004), compound
    link class (MM-013), unknown endpoint types (MM-002)."""
    out: list[Finding] = []
    known = {n["id"] for n in brief["node_types"]}
    methods = {h["id"] for g in brief.get("hash_methods", {}).values() if isinstance(g, list) for h in g}
    used: set[str] = set()
    for l in brief["link_types"]:
        for side in ("from", "to"):
            for t in l[side]:
                used.add(t)
                if t not in known:
                    out.append(("MM-002", f"{l['id']}:{t}"))
        if "|" in l["class"]:
            out.append(("MM-013", l["id"]))
        policy = [p.strip() for p in l["hash"].replace(" or ", "|").split("|")]
        if policy != ["none"] and not all(p in methods for p in policy):
            out.append(("MM-007", l["id"]))
    out += [("MM-004", t) for t in sorted(known - used)]
    return sorted(set(out))
