"""Where a checked sequence is drawn, and its export (ADR-0185).

`place` lays a sequence out deterministically from the kernel's verdicts (`application.sequences`): lifeline columns in
order of first use (actors, then records, then effect channels) and rows top to bottom, so the page only draws boxes
and arrows at the coordinates it is given. A refused message gets a reply; a committed one gets the record's state as a
UML state invariant and its effects as asynchronous messages. `export` writes the same sequence as Mermaid and
PlantUML through the existing `diagram_emitters`.
"""
from __future__ import annotations

import re
from typing import Any

from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.sequences import Interaction, Message, messages
from .diagram_emitters import emit
from .diagrams import Fragment as DiagramFragment, Message as DiagramMessage, Participant, Sequence

# Layout, in pixels: lifeline columns and the height of each kind of row.
COLUMN, LEFT, HEAD_Y, HEAD_H = 180, 100, 16, 46
ROW = {"message": 40, "reply": 30, "invariant": 36, "effect": 28, "frame": 34, "operand": 30, "end": 16}


class _Layout:
    """Lifeline columns in order of first use (actors, then records, then effect channels) and rows top to bottom."""

    def __init__(self, pack: Pack, interaction: Interaction, verdicts: dict[str, dict[str, Any]], cls: str):
        roles = {a.id: a.role for a in pack.fixtures.actors}
        self.lifelines: dict[str, dict[str, Any]] = {}
        for m in messages(interaction.steps):
            self._lifeline("actor", m.actor, f"{m.actor} : {roles.get(m.actor, '?')}")
        for r in interaction.records:
            self._lifeline("record", r, f"{r} : {cls}")
        for v in verdicts.values():
            for effect in v.get("effects", []):
                channel = effect.split(":", 1)[0] if ":" in effect else "Effects"
                self._lifeline("effect", channel, f"«effect» {channel}")
        self.y = HEAD_Y + HEAD_H + 26
        self.items: dict[str, list[dict[str, Any]]] = {k: [] for k in ("messages", "replies", "invariants", "effects", "fragments")}

    def _lifeline(self, kind: str, name: str, label: str) -> None:
        key = f"{kind}:{name}"
        if key not in self.lifelines:
            self.lifelines[key] = {"id": key, "kind": kind, "name": name, "label": label, "x": LEFT + COLUMN * len(self.lifelines)}

    def row(self, kind: str) -> int:
        at = self.y + ROW[kind] // 2
        self.y += ROW[kind]
        return at

    def x(self, key: str) -> int:
        return int(self.lifelines[key]["x"])


def _place_message(layout: _Layout, interaction: Interaction, ref: str, m: Message, v: dict[str, Any], model: Workflow) -> list[str]:
    """A call arrow, then what came back: a refusal reply, or the state invariant and the effects. Returns the lifelines it touched."""
    actor, record = f"actor:{m.actor}", f"record:{interaction.record_of(m)}"
    t = next((t for t in model.transitions if t.action == m.action), None)
    layout.items["messages"].append({"ref": ref, "from": actor, "to": record, "y": layout.row("message"), "label": f"{m.action}()",
                                     "action": m.action, "actor": m.actor, "record": interaction.record_of(m),
                                     "transition": t.id if t else None, **v})
    touched = [actor, record]
    if v["verdict"] in ("BROKEN", "REFUSED"):
        layout.items["replies"].append({"ref": ref, "from": record, "to": actor, "y": layout.row("reply"),
                                        "label": f"refused: {v['code']}", "tone": "bad" if v["verdict"] == "BROKEN" else "expected"})
    elif v["verdict"] == "OK":
        layout.items["invariants"].append({"ref": ref, "lifeline": record, "y": layout.row("invariant"), "text": "{" + " | ".join(v["states"]) + "}"})
        for effect in v["effects"]:
            channel = "effect:" + (effect.split(":", 1)[0] if ":" in effect else "Effects")
            layout.items["effects"].append({"ref": ref, "from": record, "to": channel, "y": layout.row("effect"), "label": effect.split(":", 1)[-1]})
            touched.append(channel)
    return touched


def place(pack: Pack, model: Workflow, interaction: Interaction, verdicts: dict[str, dict[str, Any]], cls: str) -> dict[str, Any]:
    layout = _Layout(pack, interaction, verdicts, cls)
    for i, step in enumerate(interaction.steps):
        if isinstance(step, Message):
            _place_message(layout, interaction, str(i), step, verdicts[str(i)], model)
            continue
        top, touched, operands = layout.y, [], []
        layout.row("frame")
        for k, operand in enumerate(step.operands):
            operands.append({"guard": operand.guard, "y": layout.row("operand") if k else top + ROW["frame"] - 8})
            for j, m in enumerate(operand.steps):
                touched += _place_message(layout, interaction, f"{i}.{k}.{j}", m, verdicts[f"{i}.{k}.{j}"], model)
        layout.row("end")
        xs = [layout.x(key) for key in touched]
        frame = {"ref": str(i), "operator": step.fragment, "x0": min(xs) - 90, "x1": max(xs) + 90, "y0": top, "y1": layout.y - 4,
                 "operands": operands, "refused": step.refused}
        layout.items["fragments"].append(frame | (verdicts.get(str(i)) or {}))
    width = LEFT + COLUMN * max(len(layout.lifelines) - 1, 0) + LEFT
    return {"lifelines": list(layout.lifelines.values()), **layout.items, "width": width, "height": layout.y + 30,
            "head": {"y": HEAD_Y, "height": HEAD_H}}


def _drawn(placed: dict[str, Any], ids: dict[str, str]) -> dict[str, list[DiagramMessage]]:
    """Each message's call, then its reply or its effects, by reference."""
    by_ref: dict[str, list[DiagramMessage]] = {}
    for kind in ("messages", "replies", "effects"):
        for m in placed[kind]:
            by_ref.setdefault(m["ref"], []).append(DiagramMessage(ids[m["from"]], ids[m["to"]], m["label"], reply=kind == "replies"))
    return by_ref


def export(interaction: Interaction, placed: dict[str, Any]) -> dict[str, str]:
    """The sequence as Mermaid and PlantUML text, through `diagram_emitters` (Mermaid has no neg: it is written as opt)."""
    ids = {ll["id"]: re.sub(r"[^A-Za-z0-9_]", "_", ll["name"]) for ll in placed["lifelines"]}
    by_ref, steps = _drawn(placed, ids), list[Any]()
    for i, step in enumerate(interaction.steps):
        if isinstance(step, Message):
            steps += by_ref.get(str(i), [])
            continue
        operands = [(o.guard or step.fragment, tuple(m for j in range(len(o.steps)) for m in by_ref.get(f"{i}.{k}.{j}", [])))
                    for k, o in enumerate(step.operands)]
        steps.append(DiagramFragment(operands[0][0], operands[0][1], operator=step.fragment, alternatives=tuple(operands[1:])))
    sequence = Sequence(interaction.title, tuple(Participant(ids[ll["id"]], ll["label"]) for ll in placed["lifelines"]), tuple(steps))
    return {fmt: emit(sequence, fmt) for fmt in ("mermaid", "plantuml")}
