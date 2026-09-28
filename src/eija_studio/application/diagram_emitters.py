"""Text emitters for the diagram models in `application.diagrams`: Mermaid, PlantUML and Graphviz DOT.

Emitters only serialise. They add no information the model does not carry, sort everything they own
(identifier maps, legend rows, class definitions) and end every document with a single newline, so equal
input gives byte-identical output on every platform. Labels are escaped for the target syntax because a
model may come from an untrusted file (`eija render --workflow`).
"""
from __future__ import annotations

import re
from typing import Any, Callable

from eija_studio.domain.models import DomainError
from .diagrams import (
    ClassModel, Diagram, Edge, Graph, Message, Node, Note, Sequence, Step, STATUS_ORDER,
)

FORMATS = ("mermaid", "plantuml", "dot")

# status -> (fill, stroke, text). Light fills with dark text keep contrast in light and dark GitHub themes.
PALETTE = {
    "blocked": ("#ffc2c2", "#82071e", "#4c0008"),
    "added": ("#d4f4dd", "#1a7f37", "#0b3d1a"),
    "removed": ("#ffe0e0", "#cf222e", "#5c0b12"),
    "changed": ("#fff3c4", "#9a6700", "#4a3200"),
    "affected": ("#ffe8cc", "#bc4c00", "#4d2000"),
    "same": ("#f6f8fa", "#57606a", "#1f2328"),
}
_NATURAL = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_RESERVED = {"end", "state", "class", "classdef", "style", "graph", "subgraph", "direction", "click", "note", "default",
             "flowchart", "linkstyle", "participant", "actor", "opt", "alt", "loop", "rect", "as", "left", "right", "over",
             "title", "legend", "start", "endlegend", "interface", "enum", "package", "rectangle"}


def safe_ids(raw: list[str] | set[str] | tuple[str, ...]) -> dict[str, str]:
    """Stable identifier map. Assigned in sorted order, so it does not depend on definition order."""
    out: dict[str, str] = {}
    taken: set[str] = set()
    for name in sorted(set(raw)):
        ident = name if _NATURAL.match(name) and name.lower() not in _RESERVED else "n_" + re.sub(r"[^A-Za-z0-9_]", "_", name)
        base, n = ident, 1
        while ident in taken:
            n += 1
            ident = f"{base}_{n}"
        taken.add(ident)
        out[name] = ident
    return out


def _clean(text: str) -> str:
    return " ".join(text.split())


_OPEN, _CLOSE = "\u0001", "\u0002"  # sentinels: survive _mm() so generics can become tildes
# `:` would end a state name or start a `:::class` shorthand; a leading backtick opens a markdown string.
_MM_ESCAPE = {"#": "#35;", ";": "#59;", '"': "#quot;", "<": "#lt;", ">": "#gt;", "{": "#123;", "}": "#125;", ":": "#58;", "`": "#96;"}


def _mm(text: str) -> str:
    return re.sub(r'[#;"<>{}:`]', lambda m: _MM_ESCAPE[m.group()], _clean(text))


def _mm_generic(text: str) -> str:
    """Member types are stored with <>; Mermaid class members spell generics with tildes."""
    return _mm(text.replace("<", _OPEN).replace(">", _CLOSE)).replace(_OPEN, "~").replace(_CLOSE, "~")


_PU_ESCAPE = {"%": "<U+0025>", "<": "<U+003C>", "[[": "<U+005B>["}


def _puml(text: str) -> str:
    """PlantUML labels are Creole: `<b>`, `<img:url>` and `[[link]]` would be interpreted, so `<` and `[` are
    written as unicode escapes, which PlantUML documents for literal characters. `%` starts a preprocessor
    builtin (`%load_json`, `%date`, `%getenv` expand even inside a label), so it is escaped too."""
    plain = _clean(text).replace('"', "'").replace("\\", "/")
    return re.sub(r"%|<|\[\[", lambda m: _PU_ESCAPE[m.group()], plain)


def _dot(text: str) -> str:
    return _clean(text).replace("\\", "\\\\").replace('"', '\\"')


def _starts(g: Graph) -> list[tuple[str, str, str]]:
    """Start-marker edges as (state, label, status). One plain edge, or in a diff whose initial state moved a
    removed edge to the old initial state and an added edge to the new one."""
    if g.initial is None:
        return []
    if g.initial_removed is None:
        return [(g.initial, "", "same")]
    return [(g.initial_removed, "- start", "removed"), (g.initial, g.initial_label, "added")]


def _comments(lines: tuple[str, ...], prefix: str) -> list[str]:
    return [f"{prefix} eija: {_clean(line)}" for line in lines]


# ---------------------------------------------------------------- Mermaid

def _mm_classdefs() -> list[str]:
    return [f"classDef {s} fill:{f},stroke:{k},color:{c}" + (",stroke-dasharray:5 3" if s == "removed" else "")
            for s, (f, k, c) in PALETTE.items() if s != "same"]


def _mm_classdef_lines(g: Graph) -> list[str]:
    used = {n.status for n in g.nodes} | {s for s, _ in g.legend}
    return [f"    {d}" for d in _mm_classdefs() if d.split()[1] in used]


def _mm_class_lines(g: Graph, ids: dict[str, str]) -> list[str]:
    """`class a,b status` lines: one per non-default status that has members, in STATUS_ORDER."""
    out = []
    for status in STATUS_ORDER:
        members = [ids[n.id] for n in g.nodes if n.status == status]
        if members and status != "same":
            out.append(f"    class {','.join(members)} {status}")
    return out


def _mm_state_legend(g: Graph) -> list[str]:
    out: list[str] = []
    for status, meaning in g.legend:
        if status != "same":
            out += [f'    state "{_mm(meaning)}" as legend_{status}', f"    class legend_{status} {status}"]
    return out


def _mm_state(g: Graph) -> str:
    ids = safe_ids([n.id for n in g.nodes])
    out = [*_comments(g.provenance, "%%"), "stateDiagram-v2", f"    direction {g.direction}", *_mm_classdef_lines(g)]
    out += [f'    state "{_mm(n.label)}" as {ids[n.id]}' for n in g.nodes if ids[n.id] != n.label]
    out += [f"    [*] --> {ids[state]}" + (f": {_mm(label)}" if label else "") for state, label, _ in _starts(g)]
    out += [f"    {ids[e.source]} --> {ids[e.target]}" + (f": {_mm(e.label)}" if e.label else "") for e in g.edges]
    out += [f"    {ids[t]} --> [*]" for t in g.terminals]
    out += _mm_class_lines(g, ids) + _mm_state_legend(g)
    return "\n".join(out) + "\n"


def _mm_flow_nodes(g: Graph, ids: dict[str, str]) -> list[str]:
    clusters = safe_ids([c.id for c in g.clusters])
    out: list[str] = []
    for c in g.clusters:
        out.append(f'    subgraph c_{clusters[c.id]}["{_mm(c.label)}"]')
        out += [f'        {ids[n.id]}["{_mm(n.label)}"]' for n in g.nodes if n.cluster == c.id]
        out += ["    end", f"    style c_{clusters[c.id]} fill:#ffffff,stroke:#8c959f"]  # neutral fill: keeps a cluster apart from the amber 'changed' nodes
    return out + [f'    {ids[n.id]}["{_mm(n.label)}"]' for n in g.nodes if n.cluster is None]


def _mm_flow_edges(g: Graph, ids: dict[str, str]) -> list[str]:
    out = [f"    {ids[e.source]} -->" + (f'|"{_mm(e.label)}"|' if e.label else "") + f" {ids[e.target]}" for e in g.edges]
    hot = [str(i) for i, e in enumerate(g.edges) if e.status == "affected"]
    return out + _mm_class_lines(g, ids) + ([f"    linkStyle {','.join(hot)} stroke:{PALETTE['affected'][1]},stroke-width:2px"] if hot else [])


def _mm_flow_legend(g: Graph) -> list[str]:
    if not g.legend:
        return []
    out = ['    subgraph legend["Legend"]', *[f'        legend_{s}["{_mm(m)}"]' for s, m in g.legend], "    end",
           "    style legend fill:#ffffff,stroke:#8c959f"]
    return out + [f"    class legend_{s} {s}" for s, _ in g.legend if s != "same"]


def _mm_flow(g: Graph) -> str:
    ids = safe_ids([n.id for n in g.nodes])
    out = [*_comments(g.provenance, "%%"), f"flowchart {g.direction}", *_mm_classdef_lines(g), *_mm_flow_nodes(g, ids)]
    return "\n".join([*out, *_mm_flow_edges(g, ids), *_mm_flow_legend(g)]) + "\n"


def _mm_steps(steps: tuple[Step, ...], indent: str) -> list[str]:
    out: list[str] = []
    for s in steps:
        if isinstance(s, Message):
            out.append(f"{indent}{s.source}{'-->>' if s.reply else '->>'}{s.target}: {_mm(s.text)}")
        elif isinstance(s, Note):
            out.append(f"{indent}Note over {','.join(s.over)}: {_mm(s.text)}")
        else:
            out += [f"{indent}opt {_mm(s.label)}", *_mm_steps(s.steps, indent + "    "), f"{indent}end"]
    return out


def _mm_sequence(q: Sequence) -> str:
    out = [*_comments(q.provenance, "%%"), "sequenceDiagram", "    autonumber"]
    out += [f"    participant {p.id}" for p in q.participants]
    return "\n".join(out + _mm_steps(q.steps, "    ")) + "\n"


def _mm_class(c: ClassModel) -> str:
    out = [*_comments(c.provenance, "%%"), "classDiagram", "    direction LR"]
    for k in c.classes:
        out.append(f"    class {k.name} {{")
        if k.stereotype:
            out.append(f"        <<{k.stereotype}>>")
        out += [f"        +{_mm_generic(m.type)} {m.name}" if m.type else f"        {m.name}" for m in k.members]
        out.append("    }")
    for r in c.relations:
        out.append(f'    {r.source} "1" --> "{r.multiplicity}" {r.target} : {r.label}' if r.association
                   else f'    {r.source} "1" *-- "{r.multiplicity}" {r.target} : {r.label}')
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- PlantUML

def _pu_color(status: str) -> str:
    fill, stroke, text = PALETTE[status]
    return f"{fill[1:]};line:{stroke[1:]};text:{text[1:]}"


def _pu_legend(g: Graph) -> list[str]:
    if not g.legend:
        return []
    return ["legend right", "  |= Status |= Meaning |"] + [f"  |<{PALETTE[s][0]}> {s} | {_puml(m)} |" for s, m in g.legend] + ["endlegend"]


def _pu_arrow(status: str) -> str:
    color = PALETTE[status][1] if status != "same" else PALETTE["same"][1]
    return f"-[{color}{',dashed' if status == 'removed' else ''}]->"


def _pu_node(keyword: str, n: Node, ids: dict[str, str], indent: str = "") -> str:
    return f'{indent}{keyword} "{_puml(n.label)}" as {ids[n.id]}' + (f" #{_pu_color(n.status)}" if n.status != "same" else "")


def _pu_edge(e: Edge, ids: dict[str, str]) -> str:
    return f"{ids[e.source]} {_pu_arrow(e.status)} {ids[e.target]}" + (f" : {_puml(e.label)}" if e.label else "")


def _pu_state_body(g: Graph, ids: dict[str, str]) -> list[str]:
    out = ["hide empty description", *[_pu_node("state", n, ids) for n in g.nodes]]
    out += [f"[*] {_pu_arrow(status) if status != 'same' else '-->'} {ids[state]}" + (f" : {_puml(label)}" if label else "")
            for state, label, status in _starts(g)]
    return out + [_pu_edge(e, ids) for e in g.edges] + [f"{ids[t]} --> [*]" for t in g.terminals]


def _pu_flow_body(g: Graph, ids: dict[str, str]) -> list[str]:
    out: list[str] = []
    for c in g.clusters:
        out.append(f'package "{_puml(c.label)}" {{')
        out += [_pu_node("rectangle", n, ids, "  ") for n in g.nodes if n.cluster == c.id]
        out.append("}")
    out += [_pu_node("rectangle", n, ids) for n in g.nodes if n.cluster is None]
    return out + [_pu_edge(e, ids) for e in g.edges]


def _pu_graph(g: Graph) -> str:
    ids = safe_ids([n.id for n in g.nodes])
    out = ["@startuml", *_comments(g.provenance, "'"), f"title {_puml(g.title)}"]
    if g.direction == "LR":
        out.append("left to right direction")
    out += _pu_state_body(g, ids) if g.kind == "state" else _pu_flow_body(g, ids)
    return "\n".join([*out, *_pu_legend(g), "@enduml"]) + "\n"


def _pu_steps(steps: tuple[Step, ...], indent: str) -> list[str]:
    out: list[str] = []
    for s in steps:
        if isinstance(s, Message):
            out.append(f"{indent}{s.source} {'-->' if s.reply else '->'} {s.target} : {_puml(s.text)}")
        elif isinstance(s, Note):
            out.append(f"{indent}note over {','.join(s.over)} : {_puml(s.text)}")
        else:
            out += [f"{indent}opt {_puml(s.label)}", *_pu_steps(s.steps, indent + "  "), f"{indent}end"]
    return out


def _pu_sequence(q: Sequence) -> str:
    out = ["@startuml", *_comments(q.provenance, "'"), f"title {_puml(q.title)}", "autonumber"]
    out += [f"participant {p.id}" for p in q.participants]
    return "\n".join(out + _pu_steps(q.steps, "") + ["@enduml"]) + "\n"


def _pu_class(c: ClassModel) -> str:
    out = ["@startuml", *_comments(c.provenance, "'"), f"title {_puml(c.title)}", "left to right direction"]
    for k in c.classes:
        keyword = "enum" if k.stereotype == "enumeration" else "class"
        out.append(f"{keyword} {k.name}" + (f" <<{k.stereotype}>>" if k.stereotype and keyword == "class" else "") + " {")
        out += [f"  +{_puml(m.type)} {m.name}" if m.type else f"  {m.name}" for m in k.members]
        out.append("}")
    for r in c.relations:
        out.append(f'{r.source} "1" --> "{r.multiplicity}" {r.target} : {r.label}' if r.association
                   else f'{r.source} "1" *-- "{r.multiplicity}" {r.target} : {r.label}')
    return "\n".join([*out, "@enduml"]) + "\n"


# ---------------------------------------------------------------- Graphviz DOT

def _dot_attrs(**attrs: str) -> str:
    return "[" + ", ".join(f'{k}="{_dot(v)}"' for k, v in attrs.items()) + "]"


def _dot_node(ident: str, label: str, status: str) -> str:
    fill, stroke, text = PALETTE[status]
    return f'    "{ident}" ' + _dot_attrs(label=label, fillcolor=fill, color=stroke, fontcolor=text,
                                          style="rounded,filled,dashed" if status == "removed" else "rounded,filled")


def _dot_edge(source: str, target: str, label: str, status: str) -> str:
    attrs = {"color": PALETTE[status][1]}
    if label:
        attrs["label"] = label
    if status == "removed":
        attrs["style"] = "dashed"
    return f'    "{source}" -> "{target}" ' + _dot_attrs(**attrs)


def _dot_header(g: Graph, ids: dict[str, str]) -> list[str]:
    out = [*_comments(g.provenance, "//"), f'digraph "{_dot(g.title)}" {{', f"    rankdir={g.direction};",
           '    graph [fontname="Helvetica"];', '    node [shape=box, fontname="Helvetica", margin="0.15,0.08"];',
           '    edge [fontname="Helvetica", fontsize=10];']
    if g.initial is not None:
        out.append('    "__start" [shape=point, width=0.15, label=""];')
        out += [_dot_edge("__start", ids[state], label, status) if label else f'    "__start" -> "{ids[state]}";'
                for state, label, status in _starts(g)]
    if g.terminals:
        out.append('    "__end" [shape=doublecircle, width=0.2, label="", style=filled, fillcolor="#1f2328"];')
    return out


def _dot_nodes(g: Graph, ids: dict[str, str]) -> list[str]:
    clusters = safe_ids([c.id for c in g.clusters])
    out: list[str] = []
    for c in g.clusters:
        out.append(f'    subgraph "cluster_{clusters[c.id]}" {{ label="{_dot(c.label)}"; style=rounded;')
        out += [_dot_node(ids[n.id], n.label, n.status) for n in g.nodes if n.cluster == c.id]
        out.append("    }")
    return out + [_dot_node(ids[n.id], n.label, n.status) for n in g.nodes if n.cluster is None]


def _dot_legend(g: Graph) -> list[str]:
    if not g.legend:
        return []
    return ['    subgraph "cluster_legend" { label="Legend"; style=rounded;', *[_dot_node("legend_" + s, m, s) for s, m in g.legend], "    }"]


def _dot_graph(g: Graph) -> str:
    ids = safe_ids([n.id for n in g.nodes])
    out = _dot_header(g, ids) + _dot_nodes(g, ids)
    out += [_dot_edge(ids[e.source], ids[e.target], e.label, e.status) for e in g.edges]
    out += [f'    "{ids[t]}" -> "__end";' for t in g.terminals]
    return "\n".join([*out, *_dot_legend(g), "}"]) + "\n"


# ---------------------------------------------------------------- dispatch

def _unsupported(kind: str, fmt: str) -> DomainError:
    return DomainError("FORMAT_UNSUPPORTED", f"{kind} diagrams are not emitted as {fmt}; supported: "
                       + ("mermaid, plantuml" if kind in {"sequence", "class"} else "mermaid, plantuml, dot"))


def emit(diagram: Diagram, fmt: str) -> str:
    """Serialise a diagram model. Raises DomainError FORMAT_UNSUPPORTED for a kind/format with no emitter."""
    if fmt not in FORMATS:
        raise DomainError("FORMAT_UNSUPPORTED", f"Unknown format {fmt!r}; use one of {', '.join(FORMATS)}")
    table: dict[type, dict[str, Callable[[Any], str]]] = {
        Graph: {"mermaid": lambda d: _mm_state(d) if d.kind == "state" else _mm_flow(d), "plantuml": _pu_graph, "dot": _dot_graph},
        Sequence: {"mermaid": _mm_sequence, "plantuml": _pu_sequence},
        ClassModel: {"mermaid": _mm_class, "plantuml": _pu_class},
    }
    emitter = table[type(diagram)].get(fmt)
    if emitter is None:
        raise _unsupported("sequence" if isinstance(diagram, Sequence) else "class", fmt)
    return str(emitter(diagram))
