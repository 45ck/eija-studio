"""Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the
follow-on edits that would keep them in agreement.

PlayIDE draws five diagrams of one system: the state machine, the class diagram, the use cases, the screens and the
components of the built app, beside the sequence diagrams that are its scenarios (ADR-0185). Only the state machine, the data model and the screens are authored; the others are
read from them (ADR-0153 to ADR-0155). So a change to the state machine ripples: a new action is a new use case and
needs a screen, a removed one leaves its screen pointing at nothing (and the app can no longer be built), a new state
is a new literal of the record's state enumeration, and the generated code changes. `ripple` computes all of it
deterministically from the two models, the screens and the two builds' files. It is a review aid: the kernel, the
policy and the conformance tests still decide.

Follow-on edits come from the plan proposer, so they are untrusted like any AI step. `check_follow_ons` re-checks each
one: a state-machine step through the policy, a screen step through the screen design check. Nothing is saved.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from eija_studio.domain.data import DataModel
from eija_studio.domain.laws import reachable
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.screens import Screen, Screens, check_screens, default_screen, use_cases
from eija_studio.domain.transactions import Transaction, parse_transaction
from .diagrams import diff_summary
from .plan import describe

FORMAT = "eija.ripple.v1"
MAX_FOLLOW_ONS = 8
Build = tuple[dict[str, str], int] | DomainError  # a build's files and conformance cases, or why it cannot be built


def _item(change: str, text: str, ref: str | None = None, code: str | None = None) -> dict[str, Any]:
    """One effect on one diagram. `change` is added, removed, changed, warning (the app still builds) or problem."""
    return {"change": change, "text": text, "ref": ref, "code": code}


def _unreachable(model: Workflow) -> set[str]:
    return set(model.states) - reachable(((t.from_state, t.to_state) for t in model.transitions), model.initial_state)


def _exits(model: Workflow) -> set[str]:
    return {t.from_state for t in model.transitions}


def _state_items(base: Workflow, candidate: Workflow) -> list[dict[str, Any]]:
    diff = diff_summary(base, candidate)
    items = [_item("added", f"Adds state {s}", "state:" + s) for s in diff["added_states"]]
    items += [_item("removed", f"Removes state {s}", "state:" + s) for s in diff["removed_states"]]
    items += [_item("added", f"Adds {a}", "action:" + a) for a in diff["added_actions"]]
    items += [_item("removed", f"Removes {a}", "action:" + a) for a in diff["removed_actions"]]
    items += [_item("changed", f"Changes {a}", "action:" + a) for a in diff["changed_actions"]]
    if diff["initial_state"]:
        items.append(_item("changed", f"Records now start in {candidate.initial_state}", "state:" + candidate.initial_state))
    items += [_item("warning", f"No record can ever reach {s}: no transition leads into it", "state:" + s, "STATE_UNREACHABLE")
              for s in sorted(_unreachable(candidate) - _unreachable(base))]
    items += [_item("warning", f"Records in {s} are now stuck: no transition leaves it", "state:" + s, "STATE_NO_EXIT")
              for s in sorted((_exits(base) - _exits(candidate)) & set(candidate.states))]
    return items


def enumeration(data: DataModel) -> str:
    """The name of the record's state enumeration on the class diagram: its literals are the state machine's states."""
    return data.record + "State"


def _class_items(base: Workflow, candidate: Workflow, data: DataModel | None) -> list[dict[str, Any]]:
    if data is None:
        return []
    name = enumeration(data)
    return ([_item("added", f"{name} gains the literal {s}", "literal:" + s) for s in candidate.states if s not in base.states]
            + [_item("removed", f"{name} loses the literal {s}", "literal:" + s) for s in base.states if s not in candidate.states])


def _associations(model: Workflow) -> set[tuple[str, str]]:
    return {(t.role, t.action) for t in model.transitions}


def _use_case_items(base: Workflow, candidate: Workflow) -> list[dict[str, Any]]:
    before, after = use_cases(base), use_cases(candidate)
    items = [_item("added", f"New use case {c}", "action:" + str(c)) for c in after if c not in before]
    items += [_item("removed", f"Use case {c} is gone", "action:" + str(c)) for c in before if c not in after]
    return items + _actor_items(base, candidate, after)


def _actor_items(base: Workflow, candidate: Workflow, after: list[str | None]) -> list[dict[str, Any]]:
    """Associations (a role takes an action) and actors added or gone."""
    items: list[dict[str, Any]] = []
    old, new = _associations(base), _associations(candidate)
    items += [_item("added", f"{role} now takes {action}", "role:" + role) for role, action in sorted(new - old)]
    items += [_item("removed", f"{role} no longer takes {action}", "role:" + role) for role, action in sorted(old - new)
              if action in after]
    roles_before, roles_after = {r for r, _ in old}, {r for r, _ in new}
    items += [_item("added", f"New actor {r}", "role:" + r) for r in sorted(roles_after - roles_before)]
    return items + [_item("removed", f"Actor {r} is gone", "role:" + r) for r in sorted(roles_before - roles_after)]


def _named(case: str | None) -> str:
    return case or "Creating a record"


def _screen_items(before: Screens, after: Screens, base: Workflow, candidate: Workflow, data: DataModel | None) -> list[dict[str, Any]]:
    items = [_item("added", f"{_named(s.use_case)} gets a default screen", "screen:" + str(s.use_case))
             for s in after.screens if before.screen(s.use_case) is None]
    items += [_item("removed", f"The screen for {_named(s.use_case)} is dropped", "screen:" + str(s.use_case))
              for s in before.screens if after.screen(s.use_case) is None]
    old = {(p["code"], p["use_case"]) for p in check_screens(before, base, data)}
    return items + [_item("problem", p["text"], "screen:" + str(p["use_case"]), p["code"])
                    for p in check_screens(after, candidate, data) if (p["code"], p["use_case"]) not in old]


def _owners(components: Iterable[dict[str, Any]]) -> dict[str, str]:
    return {path: c["id"] for c in components for path in c["files"]}


def _changed(old: dict[str, str], new: dict[str, str]) -> set[str]:
    return {path for path in set(old) | set(new) if old.get(path) != new.get(path)}


def _component_items(before: Build, after: Build, owners: dict[str, str]) -> list[dict[str, Any]]:
    if isinstance(after, DomainError):
        return [_item("problem", f"The app cannot be built: {after.message}", None, after.code)]
    if isinstance(before, DomainError):
        return [_item("changed", "The app can be built again", None)]
    paths = _changed(before[0], after[0])
    drawn = sorted({owners[path] for path in paths if path in owners})
    items = [_item("changed", f"{c} is regenerated", "component:" + c) for c in drawn]
    loose = sorted(path for path in paths if path not in owners)
    return items + ([_item("changed", f"Also regenerated: {', '.join(loose)}")] if loose else [])


def _sequence_items(checked: dict[str, Any] | None) -> list[dict[str, Any]]:
    """The scenarios the change stops the kernel producing (a warning: the app still builds) or starts producing."""
    items = []
    for s in (checked or {}).get("sequences", []):
        if s.get("change") == "breaks":
            items.append(_item("warning", f"Breaks the sequence \u201c{s['title']}\u201d: {s['first_problem']}", "sequence:" + s["id"], "SEQUENCE_BROKEN"))
        elif s.get("change") == "fixes":
            items.append(_item("changed", f"The kernel now produces the sequence \u201c{s['title']}\u201d", "sequence:" + s["id"]))
    return items


def ripple(base: Workflow, candidate: Workflow, data: DataModel | None, screens: tuple[Screens, Screens],
           builds: tuple[Build, Build], components: Iterable[dict[str, Any]], sequences: dict[str, Any] | None = None) -> dict[str, Any]:
    """Every diagram's effects of going from `base` to `candidate`. `screens` and `builds` are each (before, after);
    `components` are the after build's components (each with its `files`), naming whose files changed; `sequences` is
    `application.sequences.check_sequences` of the scenarios on `candidate` against `base`."""
    before, after = screens
    diagrams = {
        "states": _state_items(base, candidate),
        "classes": _class_items(base, candidate, data),
        "usecases": _use_case_items(base, candidate),
        "screens": _screen_items(before, after, base, candidate, data),
        "components": _component_items(builds[0], builds[1], _owners(components)),
        "sequences": _sequence_items(sequences),
    }
    cases = [None if isinstance(b, DomainError) else b[1] for b in builds]
    problems = [i for items in diagrams.values() for i in items if i["change"] in ("problem", "warning")]
    return {"format": FORMAT, "model": candidate.semantic_hash, "diagrams": diagrams,
            "conformance": {"cases_before": cases[0], "cases_after": cases[1]}, "problems": problems,
            "agree": not any(i["change"] == "problem" for i in problems)}


def _without(screens: Screens, case: Any) -> tuple[Screens, str, dict[str, Any]]:
    kept = tuple(s for s in screens.screens if s.use_case != case)
    if len(kept) == len(screens.screens) or not kept:
        raise DomainError("FOLLOW_ON_INVALID", f"There is no screen for {case} to remove")
    return Screens(id=screens.id, screens=kept), f"Remove the screen for {case}", {"op": "remove", "use_case": case}


def _screen_step(step: Any, screens: Screens, data: DataModel | None) -> tuple[Screens, str, dict[str, Any]]:
    """The screens with one proposed screen step applied, the step in words, and the step as checked. An added screen
    without a design is the use case's default screen."""
    if not isinstance(step, dict) or step.get("op") not in ("add", "remove"):
        raise DomainError("FOLLOW_ON_INVALID", "A screen step adds or removes one screen")
    if step["op"] == "remove":
        return _without(screens, step.get("use_case"))
    try:
        screen = Screen.model_validate(step["screen"]) if "screen" in step else default_screen(step.get("use_case"), data)
    except ValueError:
        raise DomainError("FOLLOW_ON_INVALID", "The proposed screen is malformed") from None
    text = f"Add a screen for {screen.use_case or 'creating a record'}: {screen.title}"
    return Screens(id=screens.id, screens=(*screens.screens, screen)), text, {"op": "add", "screen": screen.model_dump(mode="json")}


def _check_screen(step: Any, candidate: Workflow, screens: Screens, data: DataModel | None) -> dict[str, Any]:
    now = len(check_screens(screens, candidate, data))
    try:
        changed, text, checked = _screen_step(step, screens, data)
    except DomainError as error:
        return {"status": "does_not_apply", "text": "A screen step", "code": error.code, "message": error.message}
    left = check_screens(changed, candidate, data)
    status = "applies" if len(left) < now else "does_not_apply"
    return {"status": status, "text": text, "screen_step": checked, "screens": changed.model_dump(mode="json"), "problems_left": len(left),
            **({} if status == "applies" else {"code": "FOLLOW_ON_FIXES_NOTHING", "message": "It does not fix a design problem"})}


def _state_warnings(base: Workflow, model: Workflow) -> int:
    return sum(1 for item in _state_items(base, model) if item["change"] == "warning")


def _check_transaction(step: Any, base: Workflow, plan: list[Transaction], pack: Pack) -> dict[str, Any]:
    """Applies only if the policy allows it on top of the plan and it leaves fewer state-machine warnings."""
    try:
        tx = parse_transaction(step)
    except DomainError as error:
        return {"status": "does_not_apply", "text": "A state-machine step", "code": error.code, "message": error.message}
    shown = {"text": describe(tx), "transaction": tx.model_dump(mode="json")}
    try:
        candidate, after = apply_transactions(base, plan, pack), apply_transactions(base, [*plan, tx], pack)
    except DomainError as error:
        codes = (error.details or {}).get("codes", [error.code])
        return shown | {"status": "does_not_apply", "code": ", ".join(codes), "message": error.message}
    if _state_warnings(base, after) >= _state_warnings(base, candidate):
        return shown | {"status": "does_not_apply", "code": "FOLLOW_ON_FIXES_NOTHING", "message": "It does not fix a state-machine warning"}
    return shown | {"status": "applies"}


def check_follow_ons(document: Any, base: Workflow, plan: list[Any], pack: Pack, candidate: Workflow,
                     screens: Screens, data: DataModel | None) -> list[dict[str, Any]]:
    """The proposer's follow-on steps, each re-checked on its own on top of the plan: a state-machine step through
    the policy (`base` with `plan` and the step), a screen step by the design check of `screens` against `candidate`."""
    steps = document.get("steps") if isinstance(document, dict) else None
    if not isinstance(steps, list):
        raise DomainError("FOLLOW_ON_INVALID", "The proposer did not return follow-on steps")
    kept = [parse_transaction(step) for step in plan]
    checked = []
    for n, raw in enumerate(steps[:MAX_FOLLOW_ONS], 1):
        step = raw if isinstance(raw, dict) else {}
        result = (_check_transaction(step["transaction"], base, kept, pack) if "transaction" in step
                  else _check_screen(step.get("screen"), candidate, screens, data))
        checked.append({"n": n, "why": str(step.get("why", ""))[:300], "fixes": str(step.get("fixes", ""))[:80]} | result)
    return checked
