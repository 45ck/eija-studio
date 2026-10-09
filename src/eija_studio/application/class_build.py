"""What the built app does with each part of the class diagram (#145, ADR-0205): the record class is built and checked;
the other classes and the associations are drawn but not built. The diagram says which is which, so nobody reads an
association as a rule the app enforces.

The built app (ADR-0150, ADR-0153) stores records of the record class only and checks their attribute values. It never
stores another class, never looks one up and never checks a multiplicity. A record attribute that names an associated
class (`memberCard` beside `borrower: Member`) is the usual hand-written stand-in for the association: the app checks the
text, not that such a member exists.

Pure: reads the data model only.
"""
from __future__ import annotations

import re
from typing import Any

from eija_studio.domain.data import Association, Attribute, DataModel

FORMAT = "eija.class-build.v1"


def _stem(name: str) -> str:
    """The leading lower-case word of a camelCase name: `memberCard` → `member`."""
    return re.split(r"(?=[A-Z0-9])", name, maxsplit=1)[0].lower()


def _ends(data: DataModel, link: Association) -> tuple[str, str] | None:
    """(record end's class, other class) when one end of the association is the record class."""
    if link.source == data.record:
        return link.source, link.target
    if link.target == data.record:
        return link.target, link.source
    return None


def _shadow(data: DataModel, n: int, other: str, attribute: Attribute) -> dict[str, Any]:
    return {"code": "ATTRIBUTE_STANDS_IN_FOR_ASSOCIATION", "severity": "consider",
            "subject": [f"class:{data.record}", f"attribute:{data.record}.{attribute.name}", f"assoc:{n}"],
            "message": f"{data.record}.{attribute.name} holds plain {attribute.type}: the app checks the value, not that "
                       f"such a {other} exists. The association to {other} is drawn, not built."}


def _shadows(data: DataModel) -> list[dict[str, Any]]:
    """Record attributes that stand in for an association to another class."""
    found = []
    record = data.entity(data.record)
    for n, link in enumerate(data.associations):
        ends = _ends(data, link)
        if ends is None:
            continue
        names = {ends[1].lower(), link.role.lower()} - {""}
        found += [_shadow(data, n, ends[1], a) for a in record.attributes if _stem(a.name) in names]
    return found


def class_build(data: DataModel) -> dict[str, Any]:
    """Which classes and associations the built app stores and checks, and what to consider about the rest."""
    others = sorted(e.name for e in data.entities if e.name != data.record)
    drawn = [{"index": n, "source": a.source, "target": a.target, "role": a.role,
              "message": f"{a.source} to {a.target}{f' ({a.role})' if a.role else ''} is drawn, not built: the app stores "
                         f"{data.record} records only and checks no multiplicity."}
             for n, a in enumerate(data.associations)]
    return {
        "format": FORMAT,
        "built": [data.record],
        "drawn_only": others,
        "associations": drawn,
        "findings": _shadows(data),
        "limits": [f"Only {data.record} is built: its attributes are the app's form, checked on the server. "
                   "Other classes and associations are design; building them needs records of several classes (#65)."],
    }
