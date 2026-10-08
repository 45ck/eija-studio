"""Reading draw.io (diagrams.net) drawings as UML (ADR-0190); `drawio.py` writes them.

Reading a drawing is the least certain of the four formats, because a drawing only says what a shape looks like. The
reader accepts draw.io's UML palette shapes (and the one-cell HTML class box), compressed or plain pages, and treats a
page as a state machine, a class model or a use case diagram by what is on it. Every shape it cannot place is
reported, never guessed. A drawing with a DTD is refused (no entity expansion), and so is one over `MAX_XML_BYTES`.
"""
from __future__ import annotations

import base64
import binascii
import html
import re
import xml.etree.ElementTree as ET
import zlib
from dataclasses import replace


from .model import Edge, Klass, Link, Parsed, xml_root
from .textual import read_member



def _plain(value: str) -> str:
    """A draw.io label as text: HTML labels lose their tags, line breaks become newlines."""
    text = re.sub(r"<\s*(br|/div|/p|hr)\s*/?>", "\n", value, flags=re.IGNORECASE)
    return html.unescape(re.sub(r"<[^>]+>", "", text)).replace("\xa0", " ")


def _percent_decode(text: str) -> str:
    """draw.io compresses a page as deflate(encodeURIComponent(xml)); undo the URI encoding without urllib."""
    raw = re.sub(r"%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), text)
    return raw.encode("latin-1").decode("utf-8", errors="replace")


def _page_model(diagram: ET.Element) -> ET.Element | None:
    found = diagram.find("mxGraphModel")
    if found is not None:
        return found
    try:
        packed = base64.b64decode((diagram.text or "").strip(), validate=True)
        xml = _percent_decode(zlib.decompress(packed, -15).decode("latin-1"))
        return ET.fromstring(xml)  # noqa: S314 - the outer document was checked for DTDs; this is draw.io's own page XML
    except (binascii.Error, zlib.error, ET.ParseError, ValueError):
        return None


def _get(element: ET.Element, key: str) -> str:
    return element.get(key) or ""


def _position(cell: ET.Element) -> tuple[float, float]:
    geometry = cell.find("mxGeometry")
    if geometry is None:
        return 0.0, 0.0
    return float(geometry.get("x", "0")), float(geometry.get("y", "0"))


class _Cell:
    def __init__(self, cell: ET.Element, holder: ET.Element | None):
        """A cell, with the `UserObject` that wraps it when it carries a tooltip (the label then lives on the wrapper)."""
        wrapper = holder if holder is not None else ET.Element("UserObject")
        self.id = _get(wrapper, "id") or _get(cell, "id")
        self.raw = _get(wrapper, "label") if holder is not None else _get(cell, "value")
        self.value = _plain(self.raw)
        self.tooltip = " ".join(_get(wrapper, "tooltip").split())
        self.style, self.parent = _get(cell, "style"), _get(cell, "parent")
        self.edge, self.vertex = cell.get("edge") == "1", cell.get("vertex") == "1"
        self.source, self.target = _get(cell, "source"), _get(cell, "target")
        self.x, self.y = _position(cell)

    def has(self, *keys: str) -> bool:
        return any(re.search(rf"(^|;){re.escape(k)}(;|=|$)", self.style) for k in keys)

    def styled(self, key: str) -> str:
        found = re.search(rf"(?:^|;){re.escape(key)}=([^;]*)", self.style)
        return found.group(1) if found else ""


def _cells(model: ET.Element) -> list[_Cell]:
    root = model.find("root")
    out: list[_Cell] = []
    for child in list(root) if root is not None else []:
        if child.tag == "mxCell":
            out.append(_Cell(child, None))
        elif child.tag in ("UserObject", "object") and (inner := child.find("mxCell")) is not None:
            out.append(_Cell(inner, child))
    return [c for c in out if c.vertex or c.edge]


def _header(value: str) -> tuple[str, set[str]]:
    lines = [x.strip() for x in value.splitlines() if x.strip()]
    stereotypes = {s.strip().lower() for line in lines for s in re.findall(r"(?:«|<<)\s*([\w ]+?)\s*(?:»|>>)", line)}
    names = [x for x in lines if not re.fullmatch(r"(?:«|<<).*(?:»|>>)", x)]
    return (names[-1] if names else ""), stereotypes


def _class_rows(cell: _Cell, children: list[_Cell]) -> tuple[str, set[str], list[tuple[str, str, str]]]:
    """Header, stereotypes and (line, tooltip, where) rows of a class box: a swimlane with rows, or one HTML cell."""
    if children:
        rows = [(c.value.strip(), c.tooltip, f"cell {c.id}") for c in sorted(children, key=lambda c: c.y) if not c.has("line")]
        return (*_header(cell.value), rows)
    head, _, body = _split_hr(cell.raw)
    return (*_header(_plain(head)), [(x.strip(), "", f"cell {cell.id}") for x in _plain(body).splitlines() if x.strip()])


def _split_hr(raw: str) -> tuple[str, str, str]:
    """The one-cell HTML class box: the name, a rule, then member rows (a second rule starts the operations)."""
    parts = re.split(r"<hr[^>]*>", raw, maxsplit=1, flags=re.IGNORECASE)
    return parts[0], "", parts[1] if len(parts) > 1 else ""


def _is_class(cell: _Cell, children: list[_Cell]) -> bool:
    return cell.vertex and ((cell.has("swimlane") and bool(children)) or bool(re.search(r"<hr", cell.raw, re.IGNORECASE)))


def _read_class(cell: _Cell, children: list[_Cell], parsed: Parsed, ids: dict[str, str]) -> None:
    name, stereotypes, rows = _class_rows(cell, children)
    where = f"cell {cell.id}"
    if "enumeration" in stereotypes:
        parsed.enums[name] = tuple(row for row, _, _ in rows)
        return
    if stereotypes & {"interface", "abstract"}:
        parsed.skip(where, f"interface {name}", "interfaces and abstract classes are not in PlayIDE's data vocabulary")
        return
    attributes = []
    for row, tooltip, at in rows:
        if "(" in row:
            parsed.skip(at, f"{name}: {row}", "operations are not in PlayIDE's data vocabulary")
        elif (attr := read_member(row, at)) is not None:
            attributes.append(replace(attr, description=tooltip))
    ids[cell.id] = name
    parsed.klass(Klass(name=name, attributes=tuple(attributes), description=cell.tooltip, record="record" in stereotypes, where=where))


def _ends(edge: _Cell, labels: list[_Cell]) -> tuple[str, str, list[str]]:
    source, target, other = "", "", []
    for label in labels:
        text = label.value.strip()
        if label.x < 0 and re.fullmatch(r"[\d*.n ]+", text):
            source = text
        elif label.x > 0 and re.fullmatch(r"[\d*.n ]+", text):
            target = text
        elif text:
            other.append(text)
    return source, target, other


def _not_association(edge: _Cell) -> bool:
    """Dashed lines and hollow triangles are dependency, realisation and generalisation."""
    return edge.styled("dashed") == "1" or "block" in (edge.styled("endArrow"), edge.styled("startArrow"))


def _whole(edge: _Cell) -> tuple[str, bool]:
    """The link's kind, and whether the diamond is at the target end (so the target is the whole)."""
    for end, flipped in (("end", True), ("start", False)):
        if edge.styled(end + "Arrow").startswith("diamond"):
            return ("composition" if edge.styled(end + "Fill") != "0" else "aggregation"), flipped
    return "association", False


def _read_link(edge: _Cell, labels: list[_Cell], ids: dict[str, str], parsed: Parsed) -> None:
    where = f"cell {edge.id}"
    if edge.source not in ids or edge.target not in ids:
        parsed.skip(where, f"connector {edge.value or edge.id}", "it does not join two classes")
        return
    if _not_association(edge):
        parsed.skip(where, f"{ids[edge.source]} -> {ids[edge.target]}", "generalisation, realisation and dependency are not in PlayIDE's data vocabulary")
        return
    a, b = ids[edge.source], ids[edge.target]
    ma, mb, other = _ends(edge, labels)
    kind, flipped = _whole(edge)
    if flipped:
        a, b, ma, mb = b, a, mb, ma
    parsed.links.append(Link(a, b, kind, edge.value.strip() or " ".join(other), ma or "1", mb or "0..*", where))


def _read_shape(cell: _Cell, children: list[_Cell], parsed: Parsed, ids: dict[str, str]) -> None:
    if _is_class(cell, children):
        _read_class(cell, [c for c in children if c.vertex], parsed, ids)
    elif cell.value.strip():
        parsed.skip(f"cell {cell.id}", cell.value.strip()[:60], "not a UML class shape")


def _children(cells: list[_Cell]) -> dict[str, list[_Cell]]:
    out: dict[str, list[_Cell]] = {}
    for cell in cells:
        out.setdefault(cell.parent, []).append(cell)
    return out


def _read_classes(cells: list[_Cell], parsed: Parsed) -> None:
    children = _children(cells)
    ids: dict[str, str] = {}
    if parsed.classes is None:
        parsed.classes = []
    for cell in (c for c in children.get("1", []) if c.vertex):
        _read_shape(cell, children.get(cell.id, []), parsed, ids)
    for cell in (c for c in cells if c.edge):
        _read_link(cell, [c for c in children.get(cell.id, []) if c.vertex], ids, parsed)


def _vertex_kind(cell: _Cell) -> str:
    if "shape=startState" in cell.style:
        return "initial"
    if "shape=endState" in cell.style:
        return "final"
    if cell.has("ellipse") and not cell.value.strip() and cell.styled("fillColor") in ("#000000", "#000", "strokeColor"):
        return "initial"
    if any(k in cell.style for k in ("shape=note", "shape=umlActor", "shape=rhombus", "rhombus", "text;")):
        return "other"
    return "state" if cell.value.strip() else "other"


def _state_vertices(cells: list[_Cell], parsed: Parsed) -> tuple[dict[str, tuple[str, str]], dict[str, list[str]]]:
    """Each top-level vertex's kind and name, and the labels drawn as children of an edge."""
    kinds: dict[str, tuple[str, str]] = {}
    labels: dict[str, list[str]] = {}
    for cell in (c for c in cells if c.vertex):
        if cell.parent not in ("1", ""):
            labels.setdefault(cell.parent, []).append(cell.value.strip())
            continue
        kind = _vertex_kind(cell)
        kinds[cell.id] = (kind, " ".join(cell.value.split()))
        if kind == "state":
            parsed.state(kinds[cell.id][1])
        elif kind == "other" and cell.value.strip():
            parsed.skip(f"cell {cell.id}", cell.value.strip()[:60], "not a UML state shape")
    return kinds, labels


def _state_edge(cell: _Cell, a: tuple[str, str], b: tuple[str, str], label: str, parsed: Parsed) -> None:
    ends = (a[0], b[0])
    if ends == ("initial", "state"):
        parsed.initial = parsed.initial or b[1]
    elif ends == ("state", "state"):
        parsed.edges.append(Edge(a[1], b[1], label, f"cell {cell.id}"))
    elif ends != ("state", "final"):  # a final state is derived from the model
        parsed.skip(f"cell {cell.id}", label or "connector", "it does not join two states")


def _read_states(cells: list[_Cell], parsed: Parsed) -> None:
    if parsed.states is None:
        parsed.states = []
    kinds, labels = _state_vertices(cells, parsed)
    other = ("other", "")
    for cell in (c for c in cells if c.edge):
        label = " ".join(" ".join([cell.value, *labels.get(cell.id, [])]).split())
        _state_edge(cell, kinds.get(cell.source, other), kinds.get(cell.target, other), label, parsed)


def _page_kind(cells: list[_Cell]) -> str:
    if any("shape=umlActor" in c.style for c in cells):
        return "usecase"
    if any(c.vertex and _is_class(c, [x for x in cells if x.parent == c.id]) for c in cells):
        return "class"
    return "state"


def parse(text: str) -> Parsed:
    root = xml_root(text, "A draw.io file")
    diagrams = [root] if root.tag == "mxGraphModel" else root.findall("diagram")
    parsed = Parsed()
    for n, diagram in enumerate(diagrams, 1):
        model = diagram if diagram.tag == "mxGraphModel" else _page_model(diagram)
        name = diagram.get("name") or f"page {n}"
        if model is None:
            parsed.skip(name, "page", "the page could not be decompressed")
            continue
        cells = _cells(model)
        kind = _page_kind(cells)
        if kind == "usecase":
            parsed.derive(name, "use case diagram")
        elif kind == "class":
            _read_classes(cells, parsed)
        else:
            _read_states(cells, parsed)
    return parsed
