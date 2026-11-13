"""What an import keeps of the current class model, and how the candidate differs from it (ADR-0190, ADR-0245).

An attribute or association the file has but PlayIDE could not read is kept as the current model has it, in its place,
so a partly read class model never deletes it (as a partly read state machine removes nothing, issue #165). The
changes name classes and associations added, removed and changed, and a new record class. Pure: nothing is written.
"""
from __future__ import annotations

from typing import Any

from eija_studio.domain.data import DataModel


def _link_name(link: Any) -> str:
    return f"{link.source} -> {link.target}" + (f" ({link.role})" if link.role else "")


def _diff(old: dict[str, Any], new: dict[str, Any]) -> dict[str, list[str]]:
    return {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new)),
            "changed": sorted(n for n in set(new) & set(old) if new[n] != old[n])}


def changes(before: DataModel | None, after: DataModel) -> dict[str, Any]:
    """Classes added, removed and changed, and the same for associations, which a class's own fields do not show."""
    entities = before.entities if before else ()
    links = before.associations if before else ()
    return _diff({e.name: e for e in entities}, {e.name: e for e in after.entities}) | {
        "associations": _diff({_link_name(a): a for a in links}, {_link_name(a): a for a in after.associations}),
        "record": after.record if before is None or before.record != after.record else None}


_KEPT = "kept as the current model has it: the file has it, but it could not be read (see Not imported)"
_ENDS = ("source", "target", "role")


def _part(element: Any, key: str) -> Any:
    """A field of a candidate element (a dict) or of a current one (a model)."""
    return element[key] if isinstance(element, dict) else getattr(element, key)


def _restore(kept: list[Any], old: Any, key: Any, unread: set[tuple[str, ...]]) -> list[Any]:
    """Put each element of `old` the file has but PlayIDE could not read back where it was; those put back."""
    have = {key(x) for x in kept}
    back = [(i, e) for i, e in enumerate(old) if key(e) in unread and key(e) not in have]
    for i, element in back:
        kept.insert(min(i, len(kept)), element.model_dump(mode="json"))
    return [e for _, e in back]


def _keep_attributes(by_name: dict[str, dict[str, Any]], data: DataModel, report: Any) -> None:
    for entity in (e for e in data.entities if e.name in by_name):
        attributes = by_name[entity.name]["attributes"] = list(by_name[entity.name]["attributes"])
        key = lambda a, owner=entity.name: (owner, _part(a, "name"))  # noqa: E731
        for attr in _restore(attributes, entity.attributes, key, report.unread):
            report.add("defaulted", "class model", f"{entity.name}.{attr.name}", _KEPT)


def keep_unread(document: dict[str, Any], data: DataModel, report: Any) -> None:
    """An attribute or association the file has but PlayIDE could not read is kept as the current model has it, and
    the report says so (as a partial read of the state machine removes nothing, issue #165). Otherwise an attribute the
    file types in a way PlayIDE cannot read would be deleted from the class model by the import."""
    by_name = {e["name"]: e for e in document["entities"]}
    _keep_attributes(by_name, data, report)
    joined = [a for a in data.associations if a.source in by_name and a.target in by_name]
    key = lambda a: tuple(_part(a, k) for k in _ENDS)  # noqa: E731
    for link in _restore(document["associations"], joined, key, report.unread):
        report.add("defaulted", "class model", f"{link.kind} {link.source} -> {link.target}", _KEPT)
