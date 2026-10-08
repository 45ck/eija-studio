"""Review a model change in PlayIDE instead of a pull request (ADR-0158).

A change is a pair of models: the one in force and the one the change would make. The review is built from three
readings of that pair, none of which the page computes:

* **What changed**, from `diff_summary`: every added, removed or changed state and transition, plus the knock-on
  effects nobody edited directly (a state that can no longer be reached, a state records can no longer leave).
* **How risky each change is**, by fixed rules that a reviewer can read: removing a path, changing who may act,
  dropping a guard or an effect are high; adding a path or moving one is medium; adding a state or a guard is low.
* **What it does when run.** Every fixture actor tries every action from every state on both models, and the kernel
  (`runtime.execute`) decides each attempt. Attempts whose outcome differs (allowed before and refused after, a new
  destination, different effects) are the behaviour diff. The same seeded simulation runs on both models too.

Each change that alters behaviour carries a question for the reviewer to answer before the kernel's answer is shown
(predict, then run). The review is read-only: it saves, approves and applies nothing.
"""
from __future__ import annotations

from collections import deque
from typing import Any

from eija_studio.domain.models import DomainError, ExecuteCommand, Transition, Workflow
from eija_studio.domain.pack import Pack
from .diagrams import diff_summary
from .runtime import execute, initialise
from .simulation import MemorySession, simulate

CASE = "review"
RISK_ORDER = {"high": 0, "medium": 1, "low": 2}
SIM_SEED, SIM_STEPS = 1, 500


def _reach(model: Workflow) -> dict[str, list[str]]:
    """The shortest list of actions that takes a new record to each reachable state (breadth first, by action id)."""
    paths: dict[str, list[str]] = {model.initial_state: []}
    queue = deque([model.initial_state])
    while queue:
        state = queue.popleft()
        for t in sorted(model.transitions, key=lambda t: t.id):
            if t.from_state == state and t.to_state not in paths:
                paths[t.to_state] = [*paths[state], t.action]
                queue.append(t.to_state)
    return paths


def _exits(model: Workflow, state: str) -> list[Transition]:
    return [t for t in model.transitions if t.from_state == state]


def _attempt(pack: Pack, model: Workflow, state: str, actor: dict[str, Any], action: str, n: int) -> dict[str, Any]:
    """One attempt decided by the kernel: a fresh record in `state`, then `actor` tries `action` on it."""
    if state not in model.states:
        return {"outcome": "NO_STATE"}
    session = MemorySession(pack)
    record = initialise(session, CASE, model, state=state, pack=pack)["id"]  # type: ignore[arg-type]  # duck-typed port
    command = ExecuteCommand(operation_id=f"review-{n}", actor_id=actor["id"], instance_id=record, action=action,
                             expected_version=0)
    try:
        result = execute(session, CASE, model, command, pack=pack)  # type: ignore[arg-type]
    except DomainError as refused:
        return {"outcome": "REFUSED", "code": refused.code}
    return {"outcome": "COMMITTED", "to": result["instance"]["state"], "effects": sorted(result["effects"])}


def _same(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Two outcomes are the same behaviour when both are refused (for whatever reason) or both lead to the same state
    with the same effects. A state that exists on only one side is a difference only if anything succeeds there."""
    def allowed(o: dict[str, Any]) -> tuple[str, tuple[str, ...]] | None:
        return (o["to"], tuple(o["effects"])) if o["outcome"] == "COMMITTED" else None
    return allowed(a) == allowed(b)


def behaviour_diff(pack: Pack, before: Workflow, after: Workflow) -> dict[str, Any]:
    """Every fixture actor tries every action from every state on both models; the attempts whose outcome differs."""
    actors = [a.model_dump() for a in pack.fixtures.actors]
    states = sorted(set(before.states) | set(after.states))
    actions = sorted({t.action for t in before.transitions} | {t.action for t in after.transitions})
    rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    n = 0
    for state in states:
        for action in actions:
            for actor in actors:
                n += 1
                was, now = _attempt(pack, before, state, actor, action, n), _attempt(pack, after, state, actor, action, n)
                if _same(was, now):
                    continue
                key = (state, action, repr(sorted(was.items())) + repr(sorted(now.items())))
                row = rows.setdefault(key, {"state": state, "action": action, "role": actor["role"], "actors": [],
                                            "before": was, "after": now})
                row["actors"].append(actor["id"])
    ordered = sorted(rows.values(), key=lambda r: (r["action"], r["state"], r["role"], r["actors"]))
    return {"attempts": n * 2, "actors": len(actors), "rows": [r | {"n": i} for i, r in enumerate(ordered, 1)]}


def _outcome_text(o: dict[str, Any]) -> str:
    if o["outcome"] == "NO_STATE":
        return "the state does not exist"
    if o["outcome"] == "REFUSED":
        return f"refused ({o['code']})"
    return f"→ {o['to']}" + (f", {', '.join(o['effects'])}" if o["effects"] else "")


def row_text(row: dict[str, Any]) -> str:
    who = row["role"] + (f" ({', '.join(row['actors'])})" if len(row["actors"]) < 3 else "")
    return (f"{who} tries {row['action']} on a record in {row['state']}: before {_outcome_text(row['before'])}; "
            f"after {_outcome_text(row['after'])}")


def _item(element: str, change: str, text: str, risk: str, reasons: list[str], actions: list[str] | None = None,
          states: list[str] | None = None, edited: bool = True) -> dict[str, Any]:
    return {"element": element, "change": change, "text": text, "risk": risk, "reasons": reasons,
            "actions": actions or [], "states": states or [], "edited": edited}


FIELD_LABEL = {"guards": "guard", "required_effects": "effect it must perform", "forbidden_effects": "effect it must never perform"}


def _field_reasons(field: dict[str, Any]) -> list[tuple[str, str]]:
    """What one changed field means, each reason with its risk."""
    name, was, now = field["field"], field["before"], field["after"]
    if name == "role":
        return [(f"Changes who may act: {was} → {now}.", "high")]
    if name in ("from_state", "to_state"):
        return [(f"Moves the {'source' if name == 'from_state' else 'target'}: {was} → {now}.", "medium")]
    if not isinstance(was, list):
        return [(f"Renames its id: {was} → {now}.", "low")]
    gone, new = sorted(set(was) - set(now)), sorted(set(now) - set(was))
    reasons = [(f"Drops {FIELD_LABEL[name]}: {', '.join(gone)}.", "high")] if gone else []
    if new:
        reasons.append((f"Adds {FIELD_LABEL[name]}: {', '.join(new)}.", "medium" if name == "required_effects" else "low"))
    return reasons


def _removed_item(t: Transition, after: Workflow, reach_after: dict[str, list[str]]) -> dict[str, Any]:
    reasons = [f"Deletes a path: {t.role} can no longer take {t.action} from {t.from_state} to {t.to_state}."]
    if t.to_state in after.states and t.to_state not in reach_after:
        reasons.append(f"Nothing else reaches {t.to_state}.")
    if t.from_state in after.states and not _exits(after, t.from_state):
        reasons.append(f"It was a way out of {t.from_state}; none is left.")
    return _item("transition:" + t.id, "removed", f"Remove {t.action}: {t.from_state} → {t.to_state}, by {t.role}",
                 "high", reasons, [t.action], [t.from_state, t.to_state])


def _added_item(t: Transition) -> dict[str, Any]:
    effects = ", ".join(t.required_effects) or "no effects"
    return _item("transition:" + t.id, "added", f"Add {t.action}: {t.from_state} → {t.to_state}, by {t.role}", "medium",
                 [f"A new path: {t.role} may move a record from {t.from_state} to {t.to_state} ({effects})."],
                 [t.action], [t.from_state, t.to_state])


def _transition_items(before: Workflow, after: Workflow, diff: dict[str, Any], reach_after: dict[str, list[str]]) -> list[dict[str, Any]]:
    a, b = {t.action: t for t in before.transitions}, {t.action: t for t in after.transitions}
    items = [_removed_item(a[action], after, reach_after) for action in diff["removed_actions"]]
    items += [_added_item(b[action]) for action in diff["added_actions"]]
    for action, fields in diff["changed_actions"].items():
        t, reasons = b[action], [r for f in fields for r in _field_reasons(f)]
        risk = min((level for _, level in reasons), key=RISK_ORDER.__getitem__, default="low")
        items.append(_item("transition:" + t.id, "changed", f"Change {action}: {t.from_state} → {t.to_state}, by {t.role}", risk,
                           [text for text, _ in reasons], [action], [t.from_state, t.to_state]))
    return items


def _state_items(before: Workflow, after: Workflow, diff: dict[str, Any]) -> list[dict[str, Any]]:
    items = [_item("state:" + s, "added", f"Add state {s}", "low", [f"A new state records can be in: {s}."], states=[s])
             for s in diff["added_states"]]
    items += [_item("state:" + s, "removed", f"Remove state {s}", "high",
                    [f"Records can no longer be in {s}; every transition into or out of it goes too."], states=[s])
              for s in diff["removed_states"]]
    if diff["initial_state"]:
        was, now = diff["initial_state"]["before"], diff["initial_state"]["after"]
        items.append(_item("initial", "changed", f"Start records in {now} instead of {was}", "high",
                           ["Changes where every new record starts."], states=[was, now]))
    return items


def _ripple_items(before: Workflow, after: Workflow, reach_before: dict[str, list[str]],
                  reach_after: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Consequences nobody edited directly: states that stop being reachable, and states records can no longer leave."""
    items = []
    for s in sorted(set(before.states) & set(after.states)):
        if s in reach_before and s not in reach_after:
            items.append(_item("state:" + s, "unreachable", f"{s} can no longer be reached", "high",
                               [f"Before, a record got there by {' → '.join(reach_before[s]) or 'starting there'}; now no path leads there."],
                               states=[s], edited=False))
        if _exits(before, s) and not _exits(after, s):
            items.append(_item("state:" + s, "dead_end", f"Records in {s} get stuck", "high",
                               [f"Before, records left {s} by {', '.join(t.action for t in _exits(before, s))}; now nothing leaves it."],
                               states=[s], edited=False))
    return items


def _rows_for(item: dict[str, Any], rows: list[dict[str, Any]]) -> list[int]:
    """The behaviour rows an item explains: its actions, or (for a state item) attempts from or into its states."""
    if item["actions"]:
        return [r["n"] for r in rows if r["action"] in item["actions"]]
    states = set(item["states"])
    return [r["n"] for r in rows if r["state"] in states
            or any(o["outcome"] == "COMMITTED" and o["to"] in states for o in (r["before"], r["after"]))]


def _question(item: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Predict, then run: one attempt whose outcome this change alters, asked before its kernel answer is shown."""
    picked = [r for r in rows if r["n"] in item["rows"]]
    if not picked:
        return None
    flips = [r for r in picked if (r["before"]["outcome"] == "COMMITTED") != (r["after"]["outcome"] == "COMMITTED")]
    r = (flips or picked)[0]
    allowed = r["after"]["outcome"] == "COMMITTED"
    return {"row": r["n"], "text": f"After this change, can a {r['role']} take {r['action']} on a record in {r['state']}?",
            "answer": "yes" if allowed else "no",
            "because": f"The kernel says {'yes' if allowed else 'no'}: {_outcome_text(r['after'])} (before: {_outcome_text(r['before'])})."}


def _simulation(pack: Pack, before: Workflow, after: Workflow) -> dict[str, Any]:
    def brief(run: dict[str, Any]) -> dict[str, Any]:
        return {"model": run["model"], "records": run["records"], "attempts": run["attempts"], "committed": run["committed"],
                "refused": run["refused"], "findings": [f["text"] for f in run["findings"] if f["severity"] == "warning"]}
    was, now = brief(simulate(pack, before, seed=SIM_SEED, steps=SIM_STEPS)), brief(simulate(pack, after, seed=SIM_SEED, steps=SIM_STEPS))
    return {"seed": SIM_SEED, "steps": SIM_STEPS, "before": was, "after": now,
            "new_findings": [f for f in now["findings"] if f not in was["findings"]],
            "gone_findings": [f for f in was["findings"] if f not in now["findings"]]}


def review_change(pack: Pack, before: Workflow, after: Workflow) -> dict[str, Any]:
    """Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently."""
    if before.id != pack.id or after.id != pack.id:
        raise DomainError("WORKFLOW_PACK_MISMATCH", "The workflow belongs to a different pack")
    diff = diff_summary(before, after)
    reach_before, reach_after = _reach(before), _reach(after)
    behaviour = behaviour_diff(pack, before, after)
    items = (_state_items(before, after, diff) + _transition_items(before, after, diff, reach_after)
             + _ripple_items(before, after, reach_before, reach_after))
    items.sort(key=lambda i: (RISK_ORDER[i["risk"]], not i["edited"], i["element"]))
    for n, item in enumerate(items, 1):
        item["n"] = n
        item["rows"] = _rows_for(item, behaviour["rows"])
        item["question"] = _question(item, behaviour["rows"])
    for row in behaviour["rows"]:
        row["text"] = row_text(row)
    return {
        "format": "eija.review.v1", "pack": pack.id, "before": before.semantic_hash, "after": after.semantic_hash,
        "changed": before.semantic_hash != after.semantic_hash, "diff": diff, "items": items, "behaviour": behaviour,
        "risk": {level: sum(1 for i in items if i["risk"] == level) for level in RISK_ORDER},
        "before_model": before.model_dump(mode="json"), "after_model": after.model_dump(mode="json"),
        "simulation": _simulation(pack, before, after),
        "limits": ["Behaviour is every fixture actor trying every action once from a fresh record in every state; "
                   "it does not cover guards that depend on data the fixtures do not vary.",
                   "Risk levels are fixed rules about the kind of change, not a judgement of the domain.",
                   "A review records what a person checked. It does not approve or apply the change: that stays with the "
                   "owner in the review workbench."],
    }
