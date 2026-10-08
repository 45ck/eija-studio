"""An XMI document as the readers see it: elements by local name and `xmi:type`, references, multiplicities (ADR-0190).

Tools write XMI 2.1 to 2.5.1 under different namespace URIs, so nothing here compares a namespace: tags and XMI
attributes are matched by their local names.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def xattr(element: ET.Element, name: str) -> str | None:
    """An XMI attribute (xmi:id, xmi:type, xmi:idref) whatever XMI namespace version the tool used."""
    for key, value in element.attrib.items():
        if key.startswith("{") and local(key) == name:
            return value
    return None


def uml_type(element: ET.Element) -> str:
    return (xattr(element, "type") or "").split(":")[-1]


def children(element: ET.Element, tag: str) -> list[ET.Element]:
    return [c for c in element if local(c.tag) == tag]


def of_type(root: ET.Element, kind: str) -> list[ET.Element]:
    return [e for e in root.iter() if uml_type(e) == kind]


class XmiDocument:
    def __init__(self, root: ET.Element):
        self.by_id: dict[str, ET.Element] = {}
        self.parent: dict[int, ET.Element] = {}
        for element in root.iter():
            ident = xattr(element, "id")
            if ident:
                self.by_id[ident] = element
            for child in element:
                self.parent[id(child)] = element

    def ref(self, element: ET.Element, name: str) -> ET.Element | None:
        """A reference given as an attribute (`type="id"`) or a child (`<type xmi:idref="id"/>` or `href`)."""
        value = element.get(name)
        if value:
            return self.by_id.get(value.split()[0])
        child = next((c for c in element if local(c.tag) == name), None)
        if child is None:
            return None
        target = xattr(child, "idref") or (child.get("href") or "").partition("#")[2]
        return self.by_id.get(target) if target in self.by_id else child

    def name(self, element: ET.Element | None) -> str:
        if element is None:
            return ""
        return element.get("name") or (element.get("href") or "").partition("#")[2] or ""


def texts(element: ET.Element, tag: str) -> list[str]:
    found = [c.text or "" for c in element if local(c.tag) == tag]
    attr = element.get(tag)
    return found or ([attr] if attr else [])


def literal(element: ET.Element | None, default: str) -> str:
    if element is None:
        return default
    value = element.get("value")
    if value is None:  # UML: a literal integer or unlimited natural with no value is 0
        return "0"
    return "*" if value in ("-1", "*") else value


def bounds_of(element: ET.Element) -> tuple[str, str]:
    lower = literal(next((c for c in element if local(c.tag) == "lowerValue"), None), "1")
    upper = literal(next((c for c in element if local(c.tag) == "upperValue"), None), "1")
    return lower, upper


def multiplicity_of(element: ET.Element) -> str:
    lower, upper = bounds_of(element)
    return lower if lower == upper else f"{lower}..{upper}"


def comment_text(element: ET.Element) -> str:
    comment = next((c for c in element if local(c.tag) == "ownedComment"), None)
    return " ".join(" ".join(texts(comment, "body")).split()) if comment is not None else ""


def located(element: ET.Element) -> str:
    return f"{uml_type(element) or local(element.tag)} {element.get('name') or xattr(element, 'id') or ''}".strip()
