"""Where a scenario's sequence diagram is drawn, and its export (ADR-0195).

`place` lays a checked scenario out deterministically (`application.sequences`): lifeline columns in order of first
use (actors, then the record, then effect channels) and rows top to bottom, so the page only draws boxes and arrows at
the coordinates it is given. The record's start state is the first state invariant. A refused step gets a reply; a
committed one gets the record's state as a UML state invariant and its effects as asynchronous messages; a step that
expects a refusal sits in a `neg` frame. `export` writes the same sequence as Mermaid and PlantUML through the
existing `diagram_emitters`.
"""
from __future__ import annotations

import re
from typing import Any

from eija_studio.domain.pack import Pack
from eija_studio.domain.scenarios import Scenario
from .diagram_emitters import emit
from .diagrams import Fragment as DiagramFragment, Message as DiagramMessage, Note, Participant, Sequence

# Layout, in pixels: each kind of lifeline's column width, and the height of each kind of row.
# Effects are UML lost messages: arrows from the record that end LOST pixels to its right, with no lifeline of their own.
WIDTH = {"actor": 150, "record": 190, "effect": 0}
LEFT, HEAD_Y, HEAD_H, LOST = 24, 16, 56, 190
ROW = {"message": 40, "reply": 30, "invariant": 36, "effect": 26, "frame": 34, "end": 16}


class _Layout:
    """Lifeline columns in order of first use (actors, then the record, then effect channels) and rows top to bottom."""

    def __init__(self, pack: Pack, scenario: Scenario, steps: list[dict[str, Any]], record: tuple[str, str]):
        roles = {a.id: a.role for a in pack.fixtures.actors}
        self.lifelines: dict[str, dict[str, Any]] = {}
        self.right = LEFT
        for s in scenario.steps:
            role = roles.get(s.actor, "?")
            kind = pack.role_kind(roles.get(s.actor, "")) or "human"  # ADR-0210: an agent, timer or system says so
            keyword = "" if kind == "human" else f"«{kind}» "
            head = f"{s.actor}\n: {role}" if kind == "human" else f"«{kind}»\n{s.actor} : {role}"
            key = self._lifeline("actor", s.actor, f"{keyword}{s.actor} : {role}", head)
            self.lifelines[key]["actor_kind"] = kind
        self.record = self._lifeline("record", record[0], f"{record[0]} : {record[1]}", f"{record[0]} : {record[1]}")
        for v in steps:
            for effect in v["effects"]:
                channel = effect.split(":", 1)[0] if ":" in effect else "Effects"
                self._lifeline("effect", channel, f"«effect» {channel}", f"«effect»\n{channel}")
        self.y = HEAD_Y + HEAD_H + 26
        self.items: dict[str, list[dict[str, Any]]] = {k: [] for k in ("messages", "replies", "invariants", "effects", "fragments", "activations")}

    def _lifeline(self, kind: str, name: str, label: str, head: str) -> str:
        """A lifeline in the next column; `head` is its label as drawn, broken over two lines where it is long."""
        key = f"{kind}:{name}"
        if key not in self.lifelines:
            x = self.lifelines[self.record]["x"] + LOST if kind == "effect" else self.right + WIDTH[kind] // 2
            self.lifelines[key] = {"id": key, "kind": kind, "name": name, "label": label, "head": head, "x": x, "width": WIDTH[kind] - 16}
            self.right += WIDTH[kind]
        return key

    def row(self, kind: str) -> int:
        at = self.y + ROW[kind] // 2
        self.y += ROW[kind]
        return at

    def x(self, key: str) -> int:
        return int(self.lifelines[key]["x"])


def _outcome(layout: _Layout, ref: str, actor: str, v: dict[str, Any]) -> list[str]:
    """What came back from a call: a refusal reply, or the state invariant and the effects. Returns the lifelines touched."""
    record, touched = layout.record, [actor, layout.record]
    if v["code"]:
        layout.items["replies"].append({"ref": ref, "from": record, "to": actor, "y": layout.row("reply"),
                                        "label": f"refused: {v['code']}", "tone": "expected" if v["verdict"] == "HOLDS" else "bad"})
    for state in v["states"]:
        layout.items["invariants"].append({"ref": ref, "lifeline": record, "y": layout.row("invariant"), "text": "{" + state + "}",
                                           "tone": "bad" if v["verdict"] == "BROKEN" else "ok"})
    for effect in v["effects"]:
        channel = "effect:" + (effect.split(":", 1)[0] if ":" in effect else "Effects")
        layout.items["effects"].append({"ref": ref, "from": record, "to": channel, "y": layout.row("effect"), "label": effect.replace(":", ": ", 1)})
        touched.append(channel)
    return touched


def _place_step(layout: _Layout, ref: str, v: dict[str, Any]) -> list[str]:
    """A call arrow from the step's actor to the record, then its outcome."""
    step = v["step"]
    actor = f"actor:{step['actor']}"
    t = (step.get("cells") or [])
    layout.items["messages"].append({"ref": ref, "from": actor, "to": layout.record, "y": layout.row("message"), "label": f"{step['action']}()",
                                     "action": step["action"], "actor": step["actor"], "role": step.get("role"), "before": step["from"],
                                     "expect": step["expect"], "transition": next((c[11:] for c in t if c.startswith("transition:")), None),
                                     **{k: v[k] for k in ("verdict", "why", "code", "states")}})
    touched = _outcome(layout, ref, actor, v)
    y0 = layout.items["messages"][-1]["y"]  # the record is active from the call until its outcome is drawn
    layout.items["activations"].append({"ref": ref, "lifeline": layout.record, "y0": y0, "y1": max(layout.y - 10, y0 + 18)})
    return touched


def place(pack: Pack, scenario: Scenario, start: str, steps: list[dict[str, Any]], record: tuple[str, str]) -> dict[str, Any]:
    layout = _Layout(pack, scenario, steps, record)
    layout.items["invariants"].append({"ref": "start", "lifeline": layout.record, "y": layout.row("invariant"), "text": "{" + start + "}", "tone": "ok"})
    for i, v in enumerate(steps):
        refused = v["step"]["expect"].get("refused")
        if not refused:
            _place_step(layout, str(i), v)
            continue
        top = layout.y
        layout.row("frame")
        xs = [layout.x(key) for key in _place_step(layout, str(i), v)]
        layout.row("end")
        layout.items["fragments"].append({"ref": str(i), "operator": "neg", "x0": min(xs) - 66, "x1": max(xs) + 66, "y0": top, "y1": layout.y - 4,
                                          "operands": [{"guard": f"refused: {refused}", "y": top + ROW["frame"] - 8}], "refused": refused,
                                          "verdict": v["verdict"], "why": v["why"]})
    lost = any(ll["kind"] == "effect" for ll in layout.lifelines.values())
    width = layout.right + LEFT + (LOST - WIDTH["record"] // 2 + 70 if lost else 0)
    return {"lifelines": list(layout.lifelines.values()), **layout.items, "width": width, "height": layout.y + 30,
            "head": {"y": HEAD_Y, "height": HEAD_H}}


def _rows(placed: dict[str, Any], ids: dict[str, str]) -> dict[str, list[DiagramMessage | Note]]:
    """Each step's arrows and its state invariants (as notes on the record's lifeline), top to bottom, by reference."""
    rows: dict[str, list[tuple[int, DiagramMessage | Note]]] = {}
    for kind in ("messages", "replies", "effects"):
        for m in placed[kind]:
            rows.setdefault(m["ref"], []).append((m["y"], DiagramMessage(ids[m["from"]], ids[m["to"]], m["label"], reply=kind == "replies")))
    for v in placed["invariants"]:
        rows.setdefault(v["ref"], []).append((v["y"], Note((ids[v["lifeline"]],), v["text"])))
    return {ref: [item for _, item in sorted(items, key=lambda r: r[0])] for ref, items in rows.items()}


def export(title: str, placed: dict[str, Any]) -> dict[str, str]:
    """The sequence as Mermaid and PlantUML text, through `diagram_emitters`, state invariants as notes (Mermaid has no
    neg: it is written as opt)."""
    ids = {ll["id"]: re.sub(r"[^A-Za-z0-9_]", "_", ll["name"]) for ll in placed["lifelines"]}
    by_ref = _rows(placed, ids)
    negs = {f["ref"]: f for f in placed["fragments"]}
    steps = list[Any](by_ref.get("start", []))
    for m in placed["messages"]:
        drawn = tuple(by_ref[m["ref"]])
        steps += [DiagramFragment(negs[m["ref"]]["operands"][0]["guard"], drawn, operator="neg")] if m["ref"] in negs else list(drawn)
    sequence = Sequence(title, tuple(Participant(ids[ll["id"]], ll["label"]) for ll in placed["lifelines"]), tuple(steps))
    return {fmt: emit(sequence, fmt) for fmt in ("mermaid", "plantuml")}
