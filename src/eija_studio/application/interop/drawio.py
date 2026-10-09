"""draw.io (diagrams.net): the pack as a three-page `.drawio` file drawn with draw.io's own UML shapes, and back (ADR-0190).

draw.io is where many teams sketch their UML, so a PlayIDE model can be opened, laid out and annotated there. The
export uses the shapes of draw.io's UML palette (state, initial and final state, class with attribute rows,
enumeration, actor, use case) so it reads and edits like any hand-drawn diagram, laid out in layers from the initial
state. Descriptions ride on the shapes as draw.io tooltips (Edit Data).

`drawio_reader.py` reads drawings back, which is the least certain of the four formats.
"""
from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from typing import Any

from eija_studio.domain.data import DataModel, Entity
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack

from .model import (GENERATOR, attribute_type, enumerations, export_report, multiplicity, terminals, transition_label,
                    use_case_links)

STATE = "rounded=1;whiteSpace=wrap;html=1;arcSize=40;fontColor=#000080;fillColor=#ffffc0;strokeColor=#ff0000;"
START = "ellipse;html=1;shape=startState;fillColor=#000000;strokeColor=#ff0000;"
END = "ellipse;html=1;shape=endState;fillColor=#000000;strokeColor=#ff0000;"
TRANSITION = "html=1;verticalAlign=bottom;endArrow=open;endSize=8;strokeColor=#ff0000;"
CLASS = ("swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=40;"
         "horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;")
MEMBER = ("text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;"
          "rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;")
ENDS = {"composition": "endArrow=open;endFill=0;startArrow=diamondThin;startFill=1;startSize=14;",
        "aggregation": "endArrow=open;endFill=0;startArrow=diamondThin;startFill=0;startSize=14;",
        "association": "endArrow=open;endFill=0;"}
EDGE_LABEL = "edgeLabel;resizable=0;html=1;verticalAlign=bottom;"
ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
USE_CASE = "ellipse;whiteSpace=wrap;html=1;"
ACTOR_BOX = "rounded=0;whiteSpace=wrap;html=1;"  # an actor that is not a person: the classifier notation with its keyword


class _Page:
    def __init__(self, name: str):
        self.name, self.root = name, ET.Element("root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", {"id": "1", "parent": "0"})

    def vertex(self, ident: str, value: str, style: str, x: int, y: int, w: int, h: int, *, parent: str = "1",
               tooltip: str = "") -> None:
        holder = ET.SubElement(self.root, "UserObject", label=value, tooltip=tooltip, id=ident) if tooltip else self.root
        attrs = {"style": style, "vertex": "1", "parent": parent} | ({} if tooltip else {"id": ident, "value": value})
        cell = ET.SubElement(holder, "mxCell", attrs)
        ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})

    def edge(self, ident: str, value: str, style: str, source: str, target: str) -> None:
        cell = ET.SubElement(self.root, "mxCell", {"id": ident, "value": value, "style": style, "edge": "1", "parent": "1",
                                                    "source": source, "target": target})
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    def end_label(self, edge: str, value: str, at: str) -> None:
        cell = ET.SubElement(self.root, "mxCell", {"id": f"{edge}.{'src' if at == '-1' else 'dst'}", "value": value,
                             "style": EDGE_LABEL + ("align=left;" if at == "-1" else "align=right;"),
                             "vertex": "1", "connectable": "0", "parent": edge})
        ET.SubElement(cell, "mxGeometry", {"x": at, "relative": "1", "as": "geometry"})

    def element(self, ident: str) -> ET.Element:
        diagram = ET.Element("diagram", id=ident, name=self.name)
        model = ET.SubElement(diagram, "mxGraphModel", {"grid": "1", "gridSize": "10", "page": "1", "pageWidth": "1169",
                                                        "pageHeight": "827"})
        model.append(self.root)
        return diagram


def _layers(model: Workflow) -> dict[str, int]:
    """Breadth-first depth from the initial state; unreachable states go one layer past the deepest."""
    depth = {model.initial_state: 0}
    queue = [model.initial_state]
    for state in queue:
        for t in sorted(model.transitions, key=lambda t: t.id):
            if t.from_state == state and t.to_state not in depth:
                depth[t.to_state] = depth[state] + 1
                queue.append(t.to_state)
    last = max(depth.values()) + 1
    return {s: depth.get(s, last) for s in model.states}


def _state_page(model: Workflow) -> _Page:
    page, layers = _Page("State machine"), _layers(model)
    rows: dict[int, int] = {}
    place: dict[str, tuple[int, int]] = {}
    for state in model.states:
        row = rows[layers[state]] = rows.get(layers[state], -1) + 1
        place[state] = (120 + layers[state] * 240, 60 + row * 140)
    ids = {s: f"state-{n}" for n, s in enumerate(model.states)}
    page.vertex("initial", "", START, 40, place[model.initial_state][1] + 13, 30, 30)
    page.edge("start", "", TRANSITION, "initial", ids[model.initial_state])
    for state in model.states:
        page.vertex(ids[state], html.escape(state), STATE, *place[state], 140, 56)
    for n, t in enumerate(sorted(model.transitions, key=lambda t: t.id)):
        page.edge(f"transition-{n}", html.escape(transition_label(t)), TRANSITION, ids[t.from_state], ids[t.to_state])
    for n, state in enumerate(terminals(model)):
        x, y = place[state]
        page.vertex(f"final-{n}", "", END, x + 180, y + 13, 30, 30)
        page.edge(f"end-{n}", "", TRANSITION, ids[state], f"final-{n}")
    return page


def _class_box(page: _Page, ident: str, header: str, rows: list[tuple[str, str]], x: int, tooltip: str) -> None:
    page.vertex(ident, header, CLASS, x, 60, 260, 40 + 26 * len(rows), tooltip=tooltip)
    for n, (row, note) in enumerate(rows):
        page.vertex(f"{ident}.{n}", html.escape(row), MEMBER, 0, 40 + 26 * n, 260, 26, parent=ident, tooltip=note)


def _rows(entity: Entity, enums: dict[tuple[str, str], str]) -> list[tuple[str, str]]:
    return [(f"+ {a.name} : {attribute_type(entity.name, a, enums)} [{multiplicity(a)}]"
             + (f" {{maxLength = {a.max_length}}}" if a.type == "text" else ""), a.description) for a in entity.attributes]


def _enum_boxes(page: _Page, data: DataModel, enums: dict[tuple[str, str], str]) -> None:
    for n, ((entity_name, attribute), name) in enumerate(sorted(enums.items(), key=lambda kv: kv[1])):
        choices = next(a.choices for a in data.entity(entity_name).attributes if a.name == attribute)
        page.vertex(f"enum-{n}", f"&laquo;enumeration&raquo;<br>{name}", CLASS, 40 + n * 300, 420, 260, 40 + 26 * len(choices))
        for m, choice in enumerate(choices):
            page.vertex(f"enum-{n}.{m}", html.escape(choice), MEMBER, 0, 40 + 26 * m, 260, 26, parent=f"enum-{n}")


def _class_page(data: DataModel) -> _Page:
    page, enums = _Page("Class model"), enumerations(data)
    ids = {e.name: f"class-{n}" for n, e in enumerate(data.entities)}
    for n, entity in enumerate(data.entities):
        header = ("&laquo;record&raquo;<br>" if entity.name == data.record else "") + entity.name
        _class_box(page, ids[entity.name], header, _rows(entity, enums), 40 + n * 300, entity.description)
    _enum_boxes(page, data, enums)
    for n, link in enumerate(data.associations):
        edge = f"assoc-{n}"
        page.edge(edge, html.escape(link.role), ENDS[link.kind] + "html=1;", ids[link.source], ids[link.target])
        page.end_label(edge, link.source_multiplicity, "-1")
        page.end_label(edge, link.target_multiplicity, "1")
    return page


def _use_case_page(pack: Pack, model: Workflow) -> _Page:
    page = _Page("Use cases")
    actions = sorted({t.action for t in model.transitions})
    for n, declared in enumerate(pack.roles):
        if declared.kind == "human":
            page.vertex(f"actor-{n}", html.escape(declared.id), ACTOR, 40, 60 + n * 120, 30, 60, tooltip=declared.description)
        else:  # ADR-0210: «agent», «timer» or «system» over the name, as the use case diagram draws it
            page.vertex(f"actor-{n}", f"&laquo;{declared.kind}&raquo;<br><b>{html.escape(declared.id)}</b>", ACTOR_BOX,
                        10, 60 + n * 120, 120, 60, tooltip=declared.description)
    for n, action in enumerate(actions):
        page.vertex(f"usecase-{n}", html.escape(action), USE_CASE, 360, 40 + n * 90, 160, 60)
    roles = {r.id: n for n, r in enumerate(pack.roles)}
    for n, (role, action) in enumerate(use_case_links(model)):
        page.edge(f"performs-{n}", "", "endArrow=none;html=1;", f"actor-{roles[role]}", f"usecase-{actions.index(action)}")
    return page


def export(pack: Pack, model: Workflow, data: DataModel | None) -> tuple[str, dict[str, Any]]:
    mxfile = ET.Element("mxfile", host=GENERATOR, agent=f"pack {pack.id} {pack.pack.version}, model {model.semantic_hash}")
    pages = [_state_page(model)] + ([_class_page(data)] if data else []) + [_use_case_page(pack, model)]
    for n, page in enumerate(pages):
        mxfile.append(page.element(f"page-{n}"))
    ET.indent(mxfile, space="  ")
    return ET.tostring(mxfile, encoding="unicode") + "\n", export_report("drawio", pack, model, data)
