"""Sequence diagrams the kernel checks (ADR-0185): can this model produce this interaction?

Each sequence (`domain.sequences`) is unfolded into its traces: an `opt` doubles them (with and without the operand), an
`alt` multiplies them by its operands, and a `neg` is tried in place and then undone. Every trace runs on fresh
records through `runtime.execute`, with the pack's fixture actors, against an in-memory unit of work, so each message's
verdict is the kernel's own answer, not a reading of the diagram:

* OK: the kernel committed the message on every trace that reaches it; the record's state after it is drawn as a UML
  state invariant on the record's lifeline, and the effects it performed as asynchronous messages.
* BROKEN: on some trace the kernel refused it. The refusal code and the trace's operand choices say why; the trace
  stops there, so later messages on it are not reached.
* A `neg` fragment HOLDS when the kernel refuses some message of its operand (with the code it names, if any), and is
  BROKEN when the kernel lets the whole forbidden trace through.

A sequence is PRODUCIBLE when nothing in it is BROKEN. With `base`, the model in force, every verdict is also worked
out on it, so a change shows which scenarios it breaks or fixes, and each message carries its action's status in the
change (`ghost_diff`, ADR-0176). `sequence_layout` places the result, so the page only draws boxes and arrows at
the coordinates it is given. What this does NOT establish: that a scenario is the right one, or anything
about actors the pack does not list; sequences are examples, the laws (ADR-0166) are the universal claims.
"""
from __future__ import annotations

import copy
import re
from collections import deque
from typing import Any

from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError, ExecuteCommand, Transition, Workflow
from eija_studio.domain.pack import Pack, pack_directory
from eija_studio.domain.sequences import Fragment, Interaction, Message, Operand, Sequences, load_sequences
from .ghost_diff import ghost_diff
from .sequence_layout import export, place
from .runtime import execute, initialise
from .simulation import MemorySession

FORMAT = "eija.sequence-check.v1"
CASE = "sequence"
MAX_PATHS = 64
MAX_DEFAULTS = 6
WHY = {
    "ACTION_DENIED": "{action} is not in the model",
    "STATE_DENIED": "{action} does not leave {state}",
    "ROLE_DENIED": "{actor} is a {role}; {action} is for a {needs}",
    "ASSIGNMENT_DENIED": "{actor} is not assigned, and {action} needs an assigned {needs}",
    "ACTOR_REVOKED": "{actor} is not active",
    "UNKNOWN_ACTOR": "{actor} is not one of the pack's actors",
}
LIMITS = ["Each sequence is one scenario run by the pack's fixture actors: it shows what those actors can do, not every real actor.",
          "Operands hold messages only; fragments do not nest. A neg is tried where it stands and then undone."]


# ---------------------------------------------------------------- the pack's sequences, or defaults from the model

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:30] or "state"


def record_name(pack: Pack) -> tuple[str, str]:
    """The record lifeline's default name and its class: `loan : Loan` when the pack has a data model."""
    data = data_for(pack)
    if data is None:
        return "record", "Record"
    return (_slug(data.record)[:24] if re.fullmatch(r"[a-z][a-z0-9-]*", _slug(data.record)) else "record"), data.record


def _actor_for(pack: Pack, t: Transition) -> str | None:
    """A fixture actor the kernel should let take `t`: the role, active, and assigned when the transition needs it."""
    fits = [a for a in pack.fixtures.actors if a.role == t.role and a.active and (a.assigned or "actor_assigned" not in t.guards)]
    return fits[0].id if fits else None


def _shortest(model: Workflow) -> dict[str, list[Transition]]:
    """The shortest path of transitions (by id, so the result is stable) from the initial state to every state."""
    paths: dict[str, list[Transition]] = {model.initial_state: []}
    queue = deque([model.initial_state])
    while queue:
        state = queue.popleft()
        for t in sorted((t for t in model.transitions if t.from_state == state), key=lambda t: t.id):
            if t.to_state not in paths:
                paths[t.to_state] = [*paths[state], t]
                queue.append(t.to_state)
    return paths


def _taken(pack: Pack, path: list[Transition]) -> tuple[Message, ...] | None:
    """The path as messages, each sent by an actor the kernel should let through; None when one has no such actor."""
    actors = [_actor_for(pack, t) for t in path]
    return tuple(Message(actor=a, action=t.action) for a, t in zip(actors, path, strict=True) if a) if all(actors) else None


def _reach(pack: Pack, model: Workflow, record: str, cls: str) -> list[Interaction]:
    """One scenario per final state the model reaches, taken by actors the kernel should let through."""
    paths, sources = _shortest(model), {t.from_state for t in model.transitions}
    found = [(state, _taken(pack, paths[state])) for state in model.states if paths.get(state) and state not in sources]
    return [Interaction(id=f"reach-{_slug(state)}", title=f"{cls} reaches {state}", records=(record,), steps=steps)
            for state, steps in found if steps]


def _outsider(pack: Pack, model: Workflow, record: str) -> list[Interaction]:
    """A `neg`: someone active in another role tries the first step, then someone in the role takes it."""
    first = next((t for t in sorted(model.transitions, key=lambda t: t.id) if t.from_state == model.initial_state and _actor_for(pack, t)), None)
    if first is None:
        return []
    outsider = next((a for a in pack.fixtures.actors if a.active and a.role != first.role), None)
    if outsider is None:
        return []
    forbidden = Fragment(fragment="neg", refused="ROLE_DENIED", operands=(Operand(steps=(Message(actor=outsider.id, action=first.action),)),))
    return [Interaction(id=f"only-{_slug(first.role)}-{_slug(first.action)}"[:40].rstrip("-"), title=f"Only the {first.role} role may {first.action}",
                        records=(record,), steps=(forbidden, Message(actor=str(_actor_for(pack, first)), action=first.action)))]


def default_sequences(pack: Pack, model: Workflow) -> Sequences:
    """Scenarios for a pack with no `sequences.json`: one per final state, and one `neg`. Generated from `model`, the
    model in force, so a change is checked against the scenarios it had."""
    record, cls = record_name(pack)
    found = _reach(pack, model, record, cls) + _outsider(pack, model, record)
    if not found:  # a model with no path any fixture actor can take still gets a sequence: its first step
        t = sorted(model.transitions, key=lambda t: t.id)[0]
        found.append(Interaction(id="first-step", title=f"{t.action} from {t.from_state}", records=(record,),
                                 steps=(Message(actor=pack.fixtures.actors[0].id, action=t.action),)))
    return Sequences(id=pack.id, sequences=tuple(found[:MAX_DEFAULTS]))


def sequences_for(pack: Pack, model: Workflow) -> tuple[Sequences, str]:
    """The sequences beside the pack's `pack.json` ("pack"), or scenarios generated from the model in force ("default")."""
    directory = pack_directory(pack)
    found = load_sequences(directory, pack.id) if directory is not None else None
    return (found, "pack") if found is not None else (default_sequences(pack, model), "default")


# ---------------------------------------------------------------- traces, run through the kernel

Event = tuple[str, str, Any]  # ("msg", ref, Message) or ("neg", ref, Fragment)
Seen = list[tuple[dict[str, Any], tuple[str, ...]]]  # a message's outcome on each trace that reached it


def _branches(i: int, step: Message | Fragment) -> list[tuple[list[Event], str | None]]:
    """The ways one step can go: a message or a neg one way; an opt with or without its operand; an alt each operand."""
    if isinstance(step, Message):
        return [([("msg", str(i), step)], None)]
    if step.fragment == "neg":
        return [([("neg", str(i), step)], None)]
    branches: list[tuple[list[Event], str | None]] = [
        ([("msg", f"{i}.{k}.{j}", m) for j, m in enumerate(o.steps)], f"{step.fragment} [{o.guard or 'operand ' + str(k + 1)}]")
        for k, o in enumerate(step.operands)]
    return [([], f"without opt [{step.operands[0].guard or 'operand'}]"), *branches] if step.fragment == "opt" else branches


def _traces(interaction: Interaction) -> list[tuple[list[Event], tuple[str, ...]]]:
    """Every trace the interaction allows, each with the operand choices that make it (shown when a trace breaks)."""
    traces: list[tuple[list[Event], tuple[str, ...]]] = [([], ())]
    for i, step in enumerate(interaction.steps):
        traces = [(events + more, (*via, choice) if choice else via) for events, via in traces for more, choice in _branches(i, step)]
        if len(traces) > MAX_PATHS:
            raise DomainError("SEQUENCE_TOO_BRANCHY", f"{interaction.id} has more than {MAX_PATHS} traces; split it")
    return traces


class _Trial:
    """One trace on fresh records in an in-memory unit of work; every message goes through `runtime.execute`."""

    def __init__(self, pack: Pack, model: Workflow, interaction: Interaction):
        self.pack, self.model, self.interaction, self.n = pack, model, interaction, 0
        self.session = MemorySession(pack)
        self.ids = {r: initialise(self.session, CASE, model, pack=pack)["id"] for r in interaction.records}  # type: ignore[arg-type]  # duck-typed port

    def send(self, m: Message) -> dict[str, Any]:
        self.n += 1
        item = self.session.instances[self.ids[self.interaction.record_of(m)]]
        command = ExecuteCommand(operation_id=f"seq-{self.n}", actor_id=m.actor, instance_id=item["id"], action=m.action,
                                 expected_version=item["version"])
        try:
            result = execute(self.session, CASE, self.model, command, pack=self.pack)  # type: ignore[arg-type]  # duck-typed port
        except DomainError as refused:
            return {"outcome": "REFUSED", "code": refused.code, "from": item["state"], "kernel": refused.message}
        return {"outcome": "COMMITTED", "from": item["state"], "to": result["instance"]["state"], "effects": result["effects"]}

    def neg(self, fragment: Fragment, ref: str) -> list[tuple[str, dict[str, Any]]]:
        """Try the forbidden operand, then undo it: a neg describes what must not happen, so nothing it did stays."""
        saved = copy.deepcopy((self.session.instances, self.session.operations, self.session.audit, self.session.outbox))
        tried = []
        for j, m in enumerate(fragment.operands[0].steps):
            tried.append((f"{ref}.0.{j}", self.send(m)))
            if tried[-1][1]["outcome"] == "REFUSED":
                break
        self.session.instances, self.session.operations, self.session.audit, self.session.outbox = saved
        return tried


def _run(pack: Pack, model: Workflow, interaction: Interaction) -> tuple[dict[str, Seen], dict[str, list[tuple[list[Any], tuple[str, ...]]]]]:
    """Each message's outcomes and each neg's tries, over every trace that reaches them."""
    sent: dict[str, Seen] = {}
    negs: dict[str, list[tuple[list[Any], tuple[str, ...]]]] = {}
    for events, via in _traces(interaction):
        trial = _Trial(pack, model, interaction)
        for kind, ref, item in events:
            if kind == "neg":
                tried = trial.neg(item, ref)
                negs.setdefault(ref, []).append((tried, via))
                for inner, outcome in tried:
                    sent.setdefault(inner, []).append((outcome, via))
                continue
            outcome = trial.send(item)
            sent.setdefault(ref, []).append((outcome, via))
            if outcome["outcome"] == "REFUSED":
                break
    return sent, negs


def _why(pack: Pack, model: Workflow, m: Message, outcome: dict[str, Any]) -> str:
    actor = next((a for a in pack.fixtures.actors if a.id == m.actor), None)
    t = next((t for t in model.transitions if t.action == m.action), None)
    template = WHY.get(outcome["code"])
    if template is None:
        return str(outcome["kernel"])
    return template.format(action=m.action, state=outcome["from"], actor=m.actor, role=actor.role if actor else "?",
                           needs=t.role if t else "?")


def _refused(pack: Pack, model: Workflow, m: Message, seen: Seen, in_neg: bool) -> dict[str, Any]:
    o, via = next((o, via) for o, via in seen if o["outcome"] == "REFUSED")
    named = list(via) if any(x["outcome"] != "REFUSED" for x, _ in seen) else []  # name the trace only when others get through
    return {"verdict": "REFUSED" if in_neg else "BROKEN", "code": o["code"], "states": [o["from"]], "via": named,
            "why": _why(pack, model, m, o) + (f" (on the trace {', '.join(named)})" if named else "")}


def _message_verdict(pack: Pack, model: Workflow, m: Message, seen: Seen, in_neg: bool) -> dict[str, Any]:
    if not seen:
        return {"verdict": "NOT_REACHED", "why": "Not reached: an earlier message on every trace to it was refused"}
    if any(o["outcome"] == "REFUSED" for o, _ in seen):
        return _refused(pack, model, m, seen, in_neg)
    return {"verdict": "COMMITTED" if in_neg else "OK", "before": sorted({o["from"] for o, _ in seen}),
            "states": sorted({o["to"] for o, _ in seen}), "effects": seen[0][0]["effects"], "via": [],
            "why": f"The kernel committed {m.action}" + (" on every trace" if len(seen) > 1 else "")}


def _neg_verdict(fragment: Fragment, tries: list[tuple[list[Any], tuple[str, ...]]]) -> dict[str, Any]:
    if not tries:
        return {"verdict": "NOT_REACHED", "why": "Not reached: an earlier message was refused"}
    for tried, via in tries:
        last = tried[-1][1]
        trace = f" (on the trace {', '.join(via)})" if via else ""
        if last["outcome"] != "REFUSED":
            return {"verdict": "BROKEN", "why": "The kernel let the whole forbidden trace through" + trace}
        if fragment.refused and last["code"] != fragment.refused:
            return {"verdict": "BROKEN", "code": last["code"], "why": f"The kernel refused with {last['code']}, not {fragment.refused}" + trace}
    codes = sorted({tried[-1][1]["code"] for tried, _ in tries})
    return {"verdict": "HOLDS", "code": codes[0], "why": "The kernel refused it: " + ", ".join(codes)}


def _verdicts(pack: Pack, model: Workflow, interaction: Interaction) -> dict[str, dict[str, Any]]:
    """Every message's and every neg's verdict, by reference (`3`, or `3.<operand>.<message>` inside a fragment)."""
    sent, negs = _run(pack, model, interaction)
    out: dict[str, dict[str, Any]] = {}
    for i, step in enumerate(interaction.steps):
        if isinstance(step, Message):
            out[str(i)] = _message_verdict(pack, model, step, sent.get(str(i), []), False)
            continue
        if step.fragment == "neg":
            out[str(i)] = _neg_verdict(step, negs.get(str(i), []))
        for k, operand in enumerate(step.operands):
            for j, m in enumerate(operand.steps):
                ref = f"{i}.{k}.{j}"
                out[ref] = _message_verdict(pack, model, m, sent.get(ref, []), step.fragment == "neg")
                if step.fragment == "neg" and not sent.get(ref) and out[str(i)]["verdict"] != "NOT_REACHED":
                    out[ref] = {"verdict": "NOT_TRIED", "why": "Not tried: the kernel refused an earlier message of the neg"}
    return out


def _producible(verdicts: dict[str, dict[str, Any]]) -> str:
    return "BROKEN" if any(v["verdict"] == "BROKEN" for v in verdicts.values()) else "PRODUCIBLE"


# ---------------------------------------------------------------- the check

def _status(ghost: dict[str, Any] | None, action: str) -> str:
    """The action's status in the change (ADR-0176): same, added, removed, changed or moved."""
    if ghost is None:
        return "same"
    edge = next((e for e in ghost["transitions"] if e["action"] == action and not e["key"].startswith("was:")), None)
    return str(edge["status"]) if edge else "same"


def _compare(placed: dict[str, Any], ghost: dict[str, Any] | None, was: dict[str, dict[str, Any]] | None) -> None:
    """Each message's action status in the change, and, against the model in force, each message's and neg's verdict there."""
    for m in placed["messages"]:
        m["change"] = _status(ghost, m["action"])
    if was is None:
        return
    for item in placed["messages"] + placed["fragments"]:
        if item["ref"] in was:
            item["was"] = was[item["ref"]]["verdict"]


def _one(pack: Pack, model: Workflow, interaction: Interaction, base: Workflow | None, ghost: dict[str, Any] | None, cls: str) -> dict[str, Any]:
    verdicts = _verdicts(pack, model, interaction)
    was = _verdicts(pack, base, interaction) if base is not None else None
    placed = place(pack, model, interaction, verdicts, cls)
    _compare(placed, ghost, was)
    verdict = _producible(verdicts)
    broken = [x for x in placed["messages"] + placed["fragments"] if x.get("verdict") == "BROKEN"]
    out = {"id": interaction.id, "title": interaction.title, "verdict": verdict, "first_problem": broken[0]["why"] if broken else None,
           "broken": len(broken), "messages": len(placed["messages"]), **placed, "export": export(interaction, placed)}
    if was is not None:
        before = _producible(was)
        out |= {"was": before, "change": "same" if before == verdict else "breaks" if verdict == "BROKEN" else "fixes"}
    return out


def _vocabulary(pack: Pack, model: Workflow) -> dict[str, Any]:
    """What the editor offers: the pack's fixture actors, and every action the model or the pack names."""
    return {"actors": [{"id": a.id, "role": a.role, "active": a.active, "assigned": a.assigned} for a in pack.fixtures.actors],
            "actions": sorted({t.action for t in model.transitions} | {a.id for a in pack.actions})}


def check_sequences(pack: Pack, model: Workflow, sequences: Sequences, base: Workflow | None = None) -> dict[str, Any]:
    """Every sequence checked by the kernel on `model`; with `base` (the model in force) also on it, for the change."""
    if sequences.id != pack.id:
        raise DomainError("SEQUENCES_PACK_MISMATCH", "The sequences belong to a different pack")
    before = base if base is not None and base.semantic_hash != model.semantic_hash else None
    ghost = ghost_diff(before, model) if before is not None else None
    cls = record_name(pack)[1]
    checked = [_one(pack, model, s, before, ghost, cls) for s in sequences.sequences]
    broken = sum(s["verdict"] == "BROKEN" for s in checked)
    return {"format": FORMAT, "model": model.semantic_hash, "base": (base or model).semantic_hash, "changed": before is not None,
            "document": sequences.model_dump(mode="json"), "digest": sequences.digest, "status": "BROKEN" if broken else "PRODUCIBLE",
            "counts": {"producible": len(checked) - broken, "broken": broken}, "sequences": checked, "limits": LIMITS,
            **_vocabulary(pack, model)}
