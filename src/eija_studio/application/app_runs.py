"""The app oracle's runs that start from a record the app itself creates (ADR-0242): who may start one and where it
starts, a run from a new record to each transition, the actions offered in each state, and the rule table shown.
Each answer is the kernel's, asked through `OracleSession`."""
from __future__ import annotations

from itertools import product
from typing import Any

from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack
from .oracle_session import UNKNOWN_ACTOR, OracleSession, absent, kernel_answer
from .runtime import initialise


def create_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]:
    """Every fixture actor, and one unknown actor, starting a record with valid values: the state and version it starts
    in, or the refusal. Revoked and unknown actors are refused as the kernel refuses them an action; a model that names
    its initiators refuses anyone else (ADR-0231); everyone else gets a record in the model's initial state."""
    declared = {a.id: a for a in pack.fixtures.actors}
    cases: list[dict[str, object]] = []
    for actor_id in [*sorted(declared), absent(UNKNOWN_ACTOR, set(declared))]:
        actor = declared.get(actor_id)
        if actor is None:
            expect: dict[str, object] = {"outcome": "REFUSED", "code": "UNKNOWN_ACTOR"}
        elif not actor.active:
            expect = {"outcome": "REFUSED", "code": "ACTOR_REVOKED"}
        else:
            session = OracleSession(pack, model, model.initial_state)
            try:
                item = initialise(session, "app", model, pack=pack, role=actor.role)  # type: ignore[arg-type]
            except DomainError as refused:
                expect = {"outcome": "REFUSED", "code": refused.code}
            else:
                expect = {"outcome": "CREATED", "state": item["state"], "version": item["version"]}
        cases.append({"actor": actor_id, "expect": expect})
    return cases


def _first_taker(pack: Pack, model: Workflow, state: str, action: str, values: dict[str, Any],
                 acted: list[tuple[str, str]]) -> tuple[str, dict[str, Any]] | None:
    """The first fixture actor (by id) the kernel lets take `action` from `state` on a record with these values and
    history, with the kernel's answer. The record has just entered `state`, as it has on a run through the app, so a
    time event leaving it is not yet due (ADR-0237) and the timer test, not a journey, covers it."""
    for actor in sorted(pack.fixtures.actors, key=lambda a: a.id):
        session = OracleSession(pack, model, state, values, waited=0.0)
        session.acted = list(acted)
        answer = kernel_answer(pack, model, session, actor.id, action, 0)
        if answer["outcome"] == "COMMITTED":
            return actor.id, answer
    return None


def _walks(pack: Pack, model: Workflow, values: dict[str, Any]) -> list[dict[str, Any]]:
    """Breadth first from the initial state: for each transition the kernel lets some fixture actor take, the shortest
    run that ends with it. Each state is entered once, by its first run."""
    runs: dict[str, list[dict[str, Any]]] = {model.initial_state: []}
    acted: dict[str, list[tuple[str, str]]] = {model.initial_state: []}
    frontier, found = [model.initial_state], []  # type: tuple[list[str], list[dict[str, Any]]]
    while frontier:
        following = []
        for state in frontier:
            for t in sorted((t for t in model.transitions if t.from_state == state), key=lambda t: t.id):
                taker = _first_taker(pack, model, state, t.action, values, acted[state])
                if taker is None:
                    continue
                walk = [*(dict(x) for x in runs[state]), {"actor": taker[0], "action": t.action}]
                found.append({"transition": t.id, "steps": walk})
                if t.to_state not in runs:
                    runs[t.to_state], acted[t.to_state] = walk, [*acted[state], (t.action, taker[0])]
                    following.append(t.to_state)
        frontier = following
    return sorted(found, key=lambda j: str(j["transition"]))


def _answer_steps(pack: Pack, model: Workflow, values: dict[str, Any], steps: list[dict[str, Any]]) -> None:
    """The kernel's answer, and what it writes, for each step of one run on one record."""
    session = OracleSession(pack, model, model.initial_state, values, waited=0.0)  # created just now, as by the app
    for n, step in enumerate(steps):
        version = int(session.item["version"])
        step["expected_version"] = version
        step["expect"] = kernel_answer(pack, model, session, step["actor"], step["action"], version, f"op-{n + 1}")
        step["written"] = {"audit": list(session.audited), "outbox": [list(q) for q in session.queued]}
        session.audited.clear()
        session.queued.clear()


def journeys(pack: Pack, model: Workflow, valid: dict[str, Any]) -> list[dict[str, Any]]:
    """For each transition, a record started through the app and walked to it: the shortest run from the initial state
    whose last step is that transition, each step taken by the first fixture actor the kernel allows, and the kernel's
    answer for each step on one record that remembers its values and who acted. A transition no run reaches is left
    out (the law proof reports what is unreachable). Unlike `oracle_cases`, nothing is seeded: the record is the
    app's own, created with valid values."""
    values = dict(valid)
    found = _walks(pack, model, values)
    for journey in found:
        _answer_steps(pack, model, values, journey["steps"])
    return found


def rules(model: Workflow) -> dict[str, dict[str, str]]:
    """The rule table the app shows: each action once, every state it leaves, where it leads and who takes it."""
    return {t.action: {"from": ", ".join(model.sources(t.action)), "to": t.to_state, "role": t.role} for t in model.transitions}


def options_cases(pack: Pack, model: Workflow, valid: dict[str, Any]) -> list[dict[str, Any]]:
    """What the app offers each fixture actor (and one unknown actor) on a record in each state that holds valid
    values: every action leaving that state, and whether the kernel would take it from there at version 0, with its
    refusal code when it would not."""
    values = dict(valid)
    declared = {a.id for a in pack.fixtures.actors}
    cases = []
    for state, actor in product(sorted(model.states), [*sorted(declared), absent(UNKNOWN_ACTOR, declared)]):
        offered = []
        for t in (t for t in model.transitions if t.from_state == state):
            answer = kernel_answer(pack, model, OracleSession(pack, model, state, values), actor, t.action, 0)
            offered.append({"action": t.action, "allowed": answer["outcome"] == "COMMITTED"} |
                           ({"code": answer["code"]} if answer["outcome"] == "REFUSED" else {}))
        cases.append({"state": state, "actor": actor, "options": offered})
    return cases
