"""What `pr-gif browser` records: a registered scenario, the ephemeral Studio plus steps, or a URL plus steps.

Steps are one line each, `<verb> <argument>`, with `|` separating a selector from text:

    click #create              type #request | Let teachers sign off excursions.
    expect #notice | Created   highlight #options article
    caption Words to show      wait 800
    wait-for body:not([aria-busy])
    goto http://127.0.0.1:8000/other

Every step drives the real page through `demos.lib.Scene`, so `expect` fails the recording when the page does
not show the text: a GIF is never made of a flow that did not happen.
"""
from __future__ import annotations

import importlib
from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass
from pathlib import Path

from demos.lib import RunningServer, Scene, ephemeral_eija_server
from demos.scenarios.registry import SCENARIOS

STUDIO = "studio"  # the ephemeral offline Studio, driven by --step lines
_WITH_TEXT = {"type", "expect"}
_VERBS = {"click", "type", "expect", "highlight", "caption", "wait", "wait-for", "goto"}


class StepError(ValueError):
    """A step line that cannot be parsed: a usage error."""


class ScenarioBlockedError(RuntimeError):
    """The scenario waits for other lanes (ADR-0048): NOT_RUN."""


@dataclass(frozen=True)
class Step:
    verb: str
    target: str = ""
    text: str = ""


def parse_step(line: str) -> Step:
    verb, _, rest = line.strip().partition(" ")
    rest = rest.strip()
    if verb not in _VERBS:
        raise StepError(f"unknown step verb {verb!r} in {line!r}; expected one of {sorted(_VERBS)}")
    if not rest:
        raise StepError(f"step {line!r} needs an argument")
    if verb in _WITH_TEXT:
        target, sep, text = rest.partition("|")
        if not sep or not target.strip():
            raise StepError(f"step {line!r} needs '<selector> | <text>'")
        return Step(verb, target.strip(), text.strip())
    if verb == "wait" and not rest.isdigit():
        raise StepError(f"wait takes milliseconds, got {rest!r}")
    return Step(verb, rest)


def parse_steps(lines: Sequence[str]) -> list[Step]:
    return [parse_step(line) for line in lines if line.strip() and not line.lstrip().startswith("#")]


def read_steps_file(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def apply_step(scene: Scene, step: Step) -> None:
    actions: dict[str, Callable[[], None]] = {
        "click": lambda: scene.click(step.target),
        "type": lambda: scene.type_text(step.target, step.text, clear=True),
        "expect": lambda: scene.expect_text(step.target, step.text),
        "highlight": lambda: scene.highlight(step.target),
        "caption": lambda: scene.caption(step.target),
        "wait": lambda: scene.wait(int(step.target)),
        "wait-for": lambda: scene.wait_for(step.target),
        "goto": lambda: scene.goto(step.target),
    }
    actions[step.verb]()


def _is_url(source: str) -> bool:
    return source.startswith(("http://", "https://", "file:"))


def plan(source: str, steps: Sequence[Step]) -> tuple[AbstractContextManager[RunningServer | None],
                                                         Callable[[Scene, RunningServer | None], None]]:
    """Return (server context, act) for a scenario key, `studio`, or a URL. Raises on a bad combination."""
    if _is_url(source):
        return nullcontext(None), _steps_act(steps, start=source)
    if source == STUDIO:
        return ephemeral_eija_server(), _steps_act(steps, start=None)
    return ephemeral_eija_server(), _scenario_act(source, steps)


def _steps_act(steps: Sequence[Step], *, start: str | None) -> Callable[[Scene, RunningServer | None], None]:
    if not steps:
        raise StepError("a URL or `studio` needs at least one --step (or --steps FILE)")

    def act(scene: Scene, server: RunningServer | None) -> None:
        scene.goto(start or _launch_url(server))
        if server is not None:
            scene.wait_for("body:not([aria-busy])")  # the Studio ignores clicks until its startup request ends
        scene.wait(600)
        for step in steps:
            apply_step(scene, step)
        scene.wait(1500)  # let the viewer read the final state before the GIF loops

    return act


def _launch_url(server: RunningServer | None) -> str:
    if server is None:
        raise RuntimeError("no server and no URL to start from")
    return server.launch_url


def _scenario_act(key: str, steps: Sequence[Step]) -> Callable[[Scene, RunningServer | None], None]:
    scenario = next((s for s in SCENARIOS if s.key == key), None)
    if scenario is None:
        raise StepError(f"unknown scenario {key!r}: use a key from `python -m demos list`, `studio`, or a URL")
    if scenario.status == "blocked":
        raise ScenarioBlockedError(f"{key}: blocked on lane(s) {', '.join(scenario.depends_on)} (ADR-0048)")
    if steps:
        raise StepError("--step applies to a URL or `studio`; a registered scenario is already scripted")
    module = importlib.import_module(scenario.module)

    def act(scene: Scene, server: RunningServer | None) -> None:
        if server is None:
            raise RuntimeError("a scenario needs the ephemeral Studio")
        module.run(scene, server)

    return act
