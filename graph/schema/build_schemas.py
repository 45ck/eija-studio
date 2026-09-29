"""Generate the weave JSON Schemas and the generated part of README.md from metamodel.json.

metamodel.json is the single maintained source of the typed metamodel (node types, id grammar per type,
hash methods, link kinds with many-sorted signatures, cardinalities, anchors, propagation direction).
The three schema files and the tables in README.md are generated, so an agent cannot widen an edge
signature in one place and forget the other. Stdlib only; output is byte-stable (sorted keys, ASCII,
LF, trailing newline).

    python graph/schema/build_schemas.py            # write the generated files
    python graph/schema/build_schemas.py --check    # exit 1 if a committed file differs (NOT a repair)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DRAFT = "https://json-schema.org/draft/2020-12/schema"
END = r"(?![\s\S])"  # end of string; unlike `$` it does not match before a trailing newline in Python `re`
DIGEST = r"^sha256:[0-9a-f]{64}$"
SEMVER = r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
NODE_PROV = ["exact", "partial", "syntactic", "tool-resolved"]
INFERRED_ATTRS = {
    "tool": {"type": "string", "maxLength": 200},
    "model": {"type": "string", "maxLength": 200},
    "version": {"type": "string", "maxLength": 200},
    "confidence_permille": {"type": "integer", "minimum": 0, "maximum": 1000},
}
#: affects -> the impact aspect's flow set: to_target = {F}, to_source = {R}, both = {F, R}, none = {}
AFFECTS = ("to_source", "to_target", "both", "none")
README_BEGIN = "<!-- BEGIN GENERATED: build_schemas.py -->"
README_END = "<!-- END GENERATED -->"


def load(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or HERE / "metamodel.json").read_text(encoding="utf-8"))


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


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


def id_pattern(mm: dict[str, Any], type_name: str) -> str:
    t = mm["node_types"][type_name]
    seg = mm["id_scheme"]["fragment_segment"]
    fragment = t["fragment"]
    rx = fragment["pattern"] or seg + f"(?:/{seg})*"
    if fragment["presence"] == "none":
        tail = ""
    elif fragment["presence"] == "optional":
        tail = f"(?:#(?:{rx}))?"
    else:
        tail = f"#(?:{rx})"
    return f"^repo://(?:{t['path']}){tail}{END}"


def defs(mm: dict[str, Any]) -> dict[str, Any]:
    method_ids = [m["id"] for m in mm["hash_methods"]]
    path = mm["id_scheme"]["path"]
    seg = mm["id_scheme"]["fragment_segment"]
    d: dict[str, Any] = {
        "id": {"type": "string", "pattern": f"^repo://(?:{path})(?:#{seg}(?:/{seg})*)?{END}", "maxLength": 512},
        "path": {"type": "string", "pattern": f"^(?:{path}){END}", "maxLength": 400},
        "digest": {"type": "string", "pattern": DIGEST},
        "method": {"enum": method_ids},
    }
    # ---- nodes
    node_branches = []
    for name in sorted(mm["node_types"]):
        t = mm["node_types"][name]
        attrs = {"type": "object", "additionalProperties": False, "minProperties": 1, "properties": t["attrs"]}
        node_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["id", "type", "digest", "prov"],
            "properties": {
                "id": {"type": "string", "pattern": id_pattern(mm, name), "maxLength": 512},
                "type": {"const": name},
                "digest": {
                    "type": "object", "additionalProperties": False, "required": ["method", "value"],
                    "properties": {"method": {"enum": t["methods"]}, "value": {"$ref": "#/$defs/digest"}},
                },
                "prov": {"enum": NODE_PROV},
                "attrs": attrs,
            },
        }
        by_fragment = t.get("methods_by_fragment")
        if by_fragment:  # the hash method follows from whether the id names a fragment
            node_schema["allOf"] = [
                {"if": {"properties": {"id": {"pattern": "#"}}}, "then": {"properties": {"digest": {"properties": {"method": {"enum": by_fragment["with_fragment"]}}}}},
                 "else": {"properties": {"digest": {"properties": {"method": {"enum": by_fragment["without_fragment"]}}}}}}]
        d[f"node.{name}"] = node_schema
        node_branches.append({"if": {"properties": {"type": {"const": name}}, "required": ["type"]},
                              "then": {"$ref": f"#/$defs/node.{name}"}})
    d["node"] = {
        "type": "object",
        "required": ["type"],
        "properties": {"type": {"enum": sorted(mm["node_types"])}},
        "allOf": node_branches,
    }
    # ---- edges
    edge_branches = []
    kinds = sorted(mm["link_types"])
    for kind in kinds:
        k = mm["link_types"][kind]
        classes = sorted(set(k["classes"]) | {"inferred"})
        props: dict[str, Any] = {"class": {"enum": classes}}
        props["qualifier"] = {"enum": sorted(k["qualifiers"])} if k["qualifiers"] else False
        rules: list[dict[str, Any]] = []
        ends = k["anchor_ends"]
        if ends:
            items = [{"$ref": "#/$defs/anchor", "properties": {"end": {"const": e}}} for e in ends]
            props["anchors"] = {"type": "array", "prefixItems": items, "items": False,
                                "minItems": len(ends), "maxItems": len(ends)}
            # anchors are required for every class except a proposal (inferred)
            rules.append({"if": {"properties": {"class": {"enum": [c for c in classes if c != "inferred"]}}, "required": ["class"]},
                          "then": {"required": ["anchors"]}})
        else:
            props["anchors"] = False
        kind_attrs = dict(k["attrs"])
        plain = ({"type": "object", "additionalProperties": False, "minProperties": 1, "properties": kind_attrs}
                 if kind_attrs else False)
        proposal = {"type": "object", "additionalProperties": False, "required": ["tool", "version"],
                    "properties": {**kind_attrs, **INFERRED_ATTRS}}
        rules.append({"if": {"properties": {"class": {"const": "inferred"}}, "required": ["class"]},
                      "then": {"required": ["attrs"], "properties": {"attrs": proposal}},
                      "else": {"properties": {"attrs": plain}}})
        edge_branches.append({"if": {"properties": {"kind": {"const": kind}}, "required": ["kind"]},
                              "then": {"properties": props, "allOf": rules}})
    d["anchor"] = {
        "type": "object", "additionalProperties": False, "required": ["end", "method", "digest"],
        "properties": {"end": {"enum": ["from", "to"]}, "method": {"$ref": "#/$defs/method"}, "digest": {"$ref": "#/$defs/digest"}},
    }
    d["edge"] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["kind", "from", "to", "class", "prov", "asserted_in"],
        "properties": {
            "kind": {"enum": kinds},
            "from": {"$ref": "#/$defs/id"},
            "to": {"$ref": "#/$defs/id"},
            "qualifier": {"type": "string", "pattern": f"^[a-z][a-z0-9_]{{0,31}}{END}"},
            "class": {"enum": mm["classes"]},
            "prov": {"enum": mm["provenance"]},
            "candidates": {"type": "integer", "minimum": 2, "maximum": 64},
            "asserted_in": {"$ref": "#/$defs/path"},
            "anchors": {"type": "array", "items": {"$ref": "#/$defs/anchor"}},
            "attrs": {"type": "object", "minProperties": 1},
        },
        "allOf": [{"if": {"properties": {"prov": {"const": "candidate"}}, "required": ["prov"]}, "then": {"required": ["candidates"]}, "else": {"properties": {"candidates": False}}}, *edge_branches],
    }
    d["graph"] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["schema", "metamodel", "nodes", "edges"],
        "properties": {
            "schema": {"const": "eija.weave.graph/v1"},
            "metamodel": {"type": "string", "pattern": SEMVER},
            "view": {"type": "string", "pattern": f"^[a-z][a-z0-9_-]{{0,31}}{END}"},
            "nodes": {"type": "array", "items": {"$ref": "#/$defs/node"}},
            "edges": {"type": "array", "items": {"$ref": "#/$defs/edge"}},
            "root": {"$ref": "#/$defs/digest"},
        },
    }
    return d


def schemas(mm: dict[str, Any]) -> dict[str, dict[str, Any]]:
    d = defs(mm)
    common = ("id", "path", "digest", "method")
    keep = {
        "node": [k for k in d if k in common or k == "node" or k.startswith("node.")],
        "edge": [k for k in d if k in common or k in ("anchor", "edge")],
        "graph": list(d),
    }
    out = {}
    for name in ("node", "edge", "graph"):
        out[f"{name}.schema.json"] = {
            "$schema": DRAFT, "$id": f"urn:eija:weave:schema:{name}:1",
            "title": f"EIJA weave {name} (metamodel {mm['metamodel_version']}); generated by build_schemas.py, do not edit",
            "$ref": f"#/$defs/{name}", "$defs": {k: d[k] for k in sorted(keep[name])}}
    return out


# ---- consistency of the metamodel itself ------------------------------------------------------------

def check_metamodel(mm: dict[str, Any]) -> list[str]:
    """Return a sorted list of problems; empty means the tables are coherent."""
    problems: list[str] = []
    methods = {m["id"] for m in mm["hash_methods"]}
    types = set(mm["node_types"])
    for name, t in sorted(mm["node_types"].items()):
        for m in t["methods"]:
            if m not in methods:
                problems.append(f"node {name}: unknown hash method {m}")
        for side, ms in sorted(t.get("methods_by_fragment", {}).items()):
            for m in ms:
                if m not in t["methods"]:
                    problems.append(f"node {name}: methods_by_fragment.{side} names {m}, which is not in methods")
        if not re.fullmatch(id_pattern(mm, name), t["example"]):
            problems.append(f"node {name}: example id does not match its own pattern: {t['example']}")
    for sup, members in sorted(mm["supertypes"].items()):
        if sup in types:
            problems.append(f"supertype {sup} collides with a node type")
        for m in members:
            if m not in types:
                problems.append(f"supertype {sup}: unknown member {m}")
    for kind, k in sorted(mm["link_types"].items()):
        if not k["signatures"]:
            problems.append(f"link {kind}: no signature row")
        if k["affects"] not in AFFECTS:
            problems.append(f"link {kind}: bad affects {k['affects']}")
        if k["cover_role"] not in ("verifier", "observer", "none"):
            problems.append(f"link {kind}: bad cover_role {k['cover_role']}")
        if not (isinstance(k["rank_weight"], list) and len(k["rank_weight"]) == 2 and all(isinstance(x, int) and x >= 0 for x in k["rank_weight"])):
            problems.append(f"link {kind}: rank_weight must be two non-negative integers")
        for e in k["anchor_ends"]:
            if e not in ("from", "to"):
                problems.append(f"link {kind}: bad anchor end {e}")
        for c in k["classes"]:
            if c not in mm["classes"]:
                problems.append(f"link {kind}: bad class {c}")
        for i, r in enumerate(k["signatures"]):
            try:
                frm, to = expand(mm, r["from"]), expand(mm, r["to"])
            except KeyError as exc:
                problems.append(f"link {kind} row {i}: {exc}")
                continue
            if r.get("same_type") and set(frm) != set(to):
                problems.append(f"link {kind} row {i}: same_type needs equal sort sets")
            for q in r.get("qualifiers", []):
                if q not in k["qualifiers"]:
                    problems.append(f"link {kind} row {i}: qualifier {q} not declared on the kind")
            for ob in r.get("obligations", []):
                if not re.fullmatch(r"WV-\d{3}", ob["rule"]):
                    problems.append(f"link {kind} row {i}: bad rule id {ob['rule']}")
        # every anchored end must be content-addressable: each sort on that end has at least one hash method
        for e in k["anchor_ends"]:
            for r in k["signatures"]:
                for t in expand(mm, r[e]):
                    if not mm["node_types"][t]["methods"]:
                        problems.append(f"link {kind}: anchored end {e} has method-less type {t}")
    tags = [t["tag"] for t in mm["domain_tags"]]
    if len(set(tags)) != len(tags):
        problems.append("domain_tags: duplicate tag")
    for tag in tags:
        if not re.fullmatch(r"eija\.weave\.[a-z0-9.-]+\.v[0-9]+", tag):
            problems.append(f"domain_tags: malformed tag {tag}")
    for view, kinds in sorted(mm["views"].items()):
        for kind in kinds:
            if kind not in mm["link_types"]:
                problems.append(f"view {view}: unknown link kind {kind}")
    trace = sorted(k for k, v in mm["link_types"].items() if v["trace"])
    if sorted(mm["views"]["trace"]) != trace:
        problems.append("view trace differs from the kinds flagged trace")
    return sorted(problems)


# ---- README tables -------------------------------------------------------------------------------------

def _cell(text: str) -> str:
    return str(text).replace("|", "\\|")


def readme_tables(mm: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"Metamodel version {mm['metamodel_version']} ({len(mm['node_types'])} node types, {len(mm['link_types'])} link kinds, "
                 f"{sum(len(v['signatures']) for v in mm['link_types'].values())} signature rows). "
                 f"Generated from `metamodel.json`; edit that file, then run `python graph/schema/build_schemas.py`.")
    lines += ["", "### Node types", "", "| Type | Layer | Truth | Hash methods (first = default) | Fragment | Example id |", "|---|---|---|---|---|---|"]
    for name in sorted(mm["node_types"]):
        t = mm["node_types"][name]
        lines.append(f"| `{name}` | {t['layer']} | {t['truth']} | {', '.join(f'`{m}`' for m in t['methods'])} | "
                     f"{t['fragment']['presence']} | `{_cell(t['example'])}` |")
    lines += ["", "Supertypes (order-sorted signatures): " + "; ".join(
        f"`{s}` = {', '.join(f'`{m}`' for m in ms)}" for s, ms in sorted(mm["supertypes"].items())) + ".", ""]
    lines += ["### Link kinds", "",
              "| Kind | Classes | Soundness | Affects | Anchored ends | Acyclic | Signature rows (from -> to, structural max, obligations) |",
              "|---|---|---|---|---|---|---|"]
    for kind in sorted(mm["link_types"]):
        k = mm["link_types"][kind]
        rows = []
        for r in k["signatures"]:
            bits = []
            if "max_out" in r:
                bits.append(f"out<={r['max_out']}")
            if "max_in" in r:
                bits.append(f"in<={r['max_in']}")
            for ob in r.get("obligations", []):
                bits.append(f"{ob['rule']}: {ob['side']}>={ob['min']} ({ob['scope']})")
            if r.get("same_type"):
                bits.append("same type")
            suffix = f" [{'; '.join(bits)}]" if bits else ""
            rows.append(f"{'/'.join(r['from'])} -> {'/'.join(r['to'])}{suffix}")
        lines.append(f"| `{kind}` | {', '.join(k['classes'])} | {k['soundness']} | {k['affects']} | "
                     f"{', '.join(k['anchor_ends']) or '-'} | {'yes' if k['acyclic'] else 'no'} | {_cell('<br>'.join(rows))} |")
    lines += ["", "### Hash methods", "", "| Method | Status | Owner | Scope |", "|---|---|---|---|"]
    for m in mm["hash_methods"]:
        lines.append(f"| `{m['id']}` | {m['status']} | {_cell(m['owner'])} | {_cell(m['scope'])} |")
    lines += ["", "### Views (named link subsets, one Merkle root each)", "", "| View | Link kinds |", "|---|---|"]
    for v in sorted(mm["views"]):
        lines.append(f"| `{v}` | {', '.join(f'`{k}`' for k in sorted(mm['views'][v]))} |")
    return "\n".join(lines) + "\n"


def render_readme(mm: dict[str, Any], current: str) -> str:
    if README_BEGIN not in current or README_END not in current:
        raise SystemExit("README.md is missing the generated-section markers")
    head, rest = current.split(README_BEGIN, 1)
    _, tail = rest.split(README_END, 1)
    return f"{head}{README_BEGIN}\n\n{readme_tables(mm)}\n{README_END}{tail}"


def expected_files(mm: dict[str, Any]) -> dict[str, str]:
    files = {name: dumps(doc) for name, doc in schemas(mm).items()}
    readme = HERE / "README.md"
    if readme.exists():
        files["README.md"] = render_readme(mm, readme.read_text(encoding="utf-8"))
    return files


def main(argv: list[str]) -> int:
    mm = load()
    problems = check_metamodel(mm)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 2
    files = expected_files(mm)
    if "--check" in argv:
        stale = [n for n, text in sorted(files.items()) if (HERE / n).read_bytes() != text.encode("utf-8")]
        if stale:
            print("stale generated files: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("generated files are current")
        return 0
    for name, text in sorted(files.items()):
        (HERE / name).write_bytes(text.encode("utf-8"))
        print("wrote", name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
