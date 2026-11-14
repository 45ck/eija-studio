"""State names as a file gives them back, matched to the model in force before the difference is planned (ADR-0253).

Two things make a file's name differ from the model's when the person did not change it, or changed only the name:

* Spacing. Every format reads a name with its whitespace collapsed (a draw.io label wraps; PlantUML and Mermaid read
  one line), so a state named with a tab, two spaces or a trailing space comes back as another name. A file name that
  equals exactly one model state once spacing is collapsed is that state.
* Renaming. A file is a picture, not a log of edits: a state renamed in it looks like one state removed and another
  added. Planned that way, the removal is refused while the state is a composite's initial state and the new state
  joins no composite (ADR-0240). When a removed state and an added state carry exactly the same arrows, and no other
  pair does, the import plans `rename_state`, the edit the kernel already has, which keeps everything that names it.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
from typing import Any

from eija_studio.domain.models import Workflow

from .model import Edge, Parsed


def spaced(text: str) -> str:
    """`text` as a UML file gives it back: whitespace runs collapsed to one space, none at either end."""
    return " ".join(text.split())


def same_names(model: Workflow, parsed: Parsed) -> dict[str, str]:
    """Read names that are a model state but for spacing, mapped to that state in `parsed`; returns what was mapped."""
    if parsed.states is None:
        return {}
    by_spacing: dict[str, list[str]] = {}
    for state in model.states:
        by_spacing.setdefault(spaced(state), []).append(state)
    names = {name: by_spacing[name][0] for name in parsed.states
             if name not in model.states and len(by_spacing.get(name, ())) == 1 and by_spacing[name][0] not in parsed.states}
    if names:
        _rename_read(parsed, names)
    return names


def _rename_read(parsed: Parsed, names: dict[str, str]) -> None:
    parsed.states = [names.get(s, s) for s in parsed.states or []]
    parsed.initial = names.get(parsed.initial, parsed.initial) if parsed.initial is not None else None
    parsed.edges = [replace(e, source=names.get(e.source, e.source), target=names.get(e.target, e.target)) for e in parsed.edges]


def _arrows_of_model(model: Workflow, state: str) -> Counter[tuple[str, str]]:
    return Counter([(t.action, "out") for t in model.transitions if t.from_state == state]
                   + [(t.action, "in") for t in model.transitions if t.to_state == state])


def _arrows_of_file(wanted: list[tuple[Edge, str, str]], state: str) -> Counter[tuple[str, str]]:
    return Counter([(action, "out") for edge, action, _ in wanted if edge.source == state]
                   + [(action, "in") for edge, action, _ in wanted if edge.target == state])


def _pair(old: str, arrows: Counter[tuple[str, str]], gone: dict[str, Counter[tuple[str, str]]],
          new: dict[str, Counter[tuple[str, str]]]) -> str | None:
    """The one added state carrying exactly `old`'s arrows, when no other removed state carries them too."""
    matches = [s for s, theirs in new.items() if theirs == arrows]
    alike = [s for s, theirs in gone.items() if theirs == arrows]
    return matches[0] if arrows and len(matches) == 1 and alike == [old] else None


def renames(model: Workflow, parsed: Parsed, wanted: list[tuple[Edge, str, str]]) -> list[dict[str, Any]]:
    """`rename_state` steps for each removed state whose arrows only one added state carries, and the other way round."""
    read = parsed.states or []
    gone = {s: _arrows_of_model(model, s) for s in model.states if s not in read}
    new = {s: _arrows_of_file(wanted, s) for s in read if s not in model.states}
    pairs = ((old, _pair(old, arrows, gone, new)) for old, arrows in gone.items())
    return [{"kind": "rename_state", "state": old, "to": to} for old, to in pairs if to is not None]
