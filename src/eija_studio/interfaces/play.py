"""PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and
Simulate, seeded simulated users whose every step the kernel decides (ADR-0152), the screen designer's check and
build of designed screens (ADR-0154), the component diagram read from the files the app is built from (ADR-0155), the chat's plan mode, whose accepted
steps can be previewed, built and simulated but never saved or applied from here (ADR-0156), the ripple of a plan
across every diagram with the follow-on edits the proposer suggests, each re-checked (ADR-0158), the run bar's
seeded run log with breakpoints and Stop (ADR-0160), who can do what with reachability questions (ADR-0171), and the
review of a change as a UML diff whose behaviour the kernel runs on both sides (ADR-0175), and how a change looks:
the model in force and the change on one state machine, removed elements kept as ghosts (ADR-0176), and the law file
and the scenarios (test cases) as files a person can read, edit as a draft and run here, never saved from here (ADR-0177), and
the same scenarios drawn as UML sequence diagrams, every message run on the shown model and on the model in force (ADR-0195).

Build & run reuses `eija build` (ADR-0150): the app is generated into the workspace, its kernel conformance tests run,
and only a PASSing app is started, as a separate local process on a free loopback port. One app runs at a time; a new
model's build replaces it and the IDE stops it on exit. The generated app has no access to the workspace database.
"""
from __future__ import annotations

import atexit
import hashlib
import os
import socket
import subprocess
import sys
import threading
import time
from importlib.resources import files as resource_files
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi.responses import FileResponse

from pydantic import Field

from eija_studio.application.access import access, reach
from eija_studio import __version__
from eija_studio.application.api_contract import api_contract
from eija_studio.application.class_build import class_build
from eija_studio.application.components import app_components
from eija_studio.application.deployment import app_deployment
from eija_studio.application.landscape import landscape
from eija_studio.application.law_proof import compare_laws, prove_laws, with_laws
from eija_studio.application.ghost_diff import ghost_diff
from eija_studio.application.describe_system import update_tests
from eija_studio.application.data_steps import data_changes, draft_pack, parse_step, split
from eija_studio.application.plan import MAX_DRAFT_STEPS, preview_plan, propose_plan
from eija_studio.application.readiness import missing
from eija_studio.application.review import review_change
from eija_studio.application.ripple import check_follow_ons, ripple
from eija_studio.application.scenario_run import record_steps, run_scenarios
from eija_studio.application.screen_access import check_accessibility
from eija_studio.application.sequence_draft import scenarios_or_draft
from eija_studio.application.sequences import check_sequences
from eija_studio.application.simulation import MAX_BREAKPOINTS, MAX_STEPS, run_log, simulate
from eija_studio.domain.data import data_for
from eija_studio.domain.models import Contract, DomainError, Workflow
from eija_studio.domain.pack import PACK_FILE, Pack, load_pack, pack_directory
from eija_studio.domain.scenarios import parse_scenarios, scenarios_for
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.screens import Screens, check_screens, parse_screens, screens_for, use_cases
from .app_build import app_files, build_into
from .play_interop import register as register_interop

START_TIMEOUT_S = 10.0


class BuildRequest(Contract):
    case_id: str | None = None  # None builds the active baseline; a case builds its candidate (or baseline if none yet)
    model: Workflow | None = None  # the model the page shows; if given, it must still be the one that would be built
    screens: dict[str, Any] | None = None  # screens edited in the designer (eija.screens.v1); None uses the pack's
    plan: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_DRAFT_STEPS)  # accepted chat-plan steps, tried on top


class ChangeRequest(BuildRequest):
    # The steps of the rounds before the last (ADR-0201): given, the change shown is the last round's alone, from the
    # model with those steps to the model with every accepted step; None is the whole change from the model in force.
    since: list[dict[str, Any]] | None = Field(default=None, max_length=MAX_DRAFT_STEPS)
    scenarios: dict[str, Any] | None = None  # the Tests tab's draft (eija.scenarios.v1); None is the pack's (ADR-0216)


class PlanRequest(BuildRequest):
    request: str = Field(min_length=1, max_length=2000)


class PlanPreviewRequest(BuildRequest):
    steps: list[dict[str, Any]] = Field(min_length=1, max_length=MAX_DRAFT_STEPS)
    accepted: list[bool] = Field(min_length=1, max_length=MAX_DRAFT_STEPS)


class SimulateRequest(BuildRequest):
    seed: int = Field(default=1, ge=0, le=2**31 - 1)
    steps: int = Field(default=500, ge=1, le=MAX_STEPS)


class ReachRequest(BuildRequest):
    target: str = Field(min_length=1, max_length=60)
    without: str | None = Field(default=None, min_length=1, max_length=60)


class LawsRequest(BuildRequest):
    laws: list[dict[str, Any]] | None = Field(default=None, max_length=200)  # a draft of the law file; None is the pack's


class ScenariosRequest(BuildRequest):
    scenarios: dict[str, Any] | None = None  # a draft of scenarios.json (eija.scenarios.v1); None is the pack's


class TryRequest(BuildRequest):
    start: str | None = Field(default=None, min_length=1, max_length=60)
    steps: list[tuple[str, str]] = Field(min_length=1, max_length=40)  # (fixture actor, action) in turn


class RunRequest(SimulateRequest):
    breakpoints: list[str] = Field(default_factory=list, max_length=MAX_BREAKPOINTS)
    break_on_refusal: bool = False


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _listening(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.2)
        return probe.connect_ex(("127.0.0.1", port)) == 0


class AppRunner:
    """Builds apps under `root()` and keeps at most one of them running."""

    def __init__(self, root: Callable[[], Path]):
        self.root = root
        self.lock = threading.Lock()
        self.process: subprocess.Popen | None = None
        self.running: dict[str, Any] | None = None
        atexit.register(self.stop)

    def build_and_run(self, pack: Pack, model: Workflow, identity: dict[str, Any], screens: Screens) -> dict[str, Any]:
        with self.lock:
            data = data_for(pack)  # the same model with another data model or other screens is another app
            key = model.semantic_hash[:12] + (f"-{data.digest[:8]}" if data else "") + f"-{screens.digest[:8]}"
            # Who holds each role is part of the app too (ADR-0215): a round that only sets a role's kind is another app.
            kinds = "".join(sorted(f"{r.id}={r.kind};" for r in pack.roles))
            key += "-" + hashlib.sha256(kinds.encode()).hexdigest()[:8]
            out = self.root() / key
            manifest = build_into(out, pack, model, identity, screens=screens)
            result = {"model": model.semantic_hash, "screens": screens.digest, "cases": manifest["oracle"]["cases"],
                      "conformance": manifest["conformance"], "kernel_source_review": manifest["kernel_source_review"],
                      "files": len(manifest["files"]), "url": None}
            if manifest["conformance"]["status"] != "PASS":
                self._stop()  # never leave an older app running as if it were this model's
                return result
            return result | {"url": self._start(out, key)}

    def _start(self, out: Path, key: str) -> str:
        alive = self.process is not None and self.process.poll() is None
        if alive and self.running and self.running["key"] == key:
            return self.running["url"]
        self._stop()
        port = _free_port()
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}
        env["PORT"] = str(port)
        self.process = subprocess.Popen([sys.executable, "run.py"], cwd=out, env=env,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + START_TIMEOUT_S
        while not _listening(port):
            if self.process.poll() is not None or time.monotonic() > deadline:
                self._stop()
                raise DomainError("APP_START_FAILED", "The built app did not start")
            time.sleep(0.05)
        self.running = {"key": key, "url": f"http://127.0.0.1:{port}/"}
        return self.running["url"]

    def _stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process, self.running = None, None

    def stop(self) -> bool:
        """Stop the running app, if any; say whether one was running."""
        with self.lock:
            was = self.process is not None and self.process.poll() is None
            self._stop()
            return was


def pack_file(pack: Pack, name: str) -> str:
    """Where one of the pack's files is, as its owner would find it: relative to the working directory when under it
    (packs/<id>/pack.json), else from the home folder (~/PlayIDE/support-desk/pack.json), else in full."""
    folder = pack_directory(pack)
    if folder is None:
        return f"packs/{pack.id}/{name}"
    path = folder / name
    for base, prefix in ((Path.cwd(), ""), (Path.home(), "~/")):
        if path.is_relative_to(base):
            return prefix + path.relative_to(base).as_posix()
    return path.as_posix()


def register(app, studio, web: Path, own: Callable[[], bool] = lambda: False) -> AppRunner:
    """`own` says whether the system open now is one the person started (in the systems home): its vocabulary grows
    as a plan names new actions and roles (ADR-0201). A shipped pack's vocabulary is fixed."""
    runner = AppRunner(lambda: Path(studio.store.directory) / "apps")

    @app.get("/play")
    def play_page():
        return FileResponse(web / "play.html")

    def pack_of(steps: list[dict[str, Any]] | None) -> Pack:
        """The open system's pack, with what these plan steps name but it does not declare yet declared as a sketch
        declares it, and their data-model steps applied to its class diagram, on a system the person started (ADR-0201,
        ADR-0202); a draft held in memory, never written."""
        if not steps:
            return studio.pack
        return draft_pack(studio.pack, [parse_step(step) for step in steps], own())

    def resolve(body: BuildRequest) -> Workflow:
        """The model the request is about: the active baseline, or a case's candidate (its baseline if none yet)."""
        if body.case_id is None:
            with studio.store.transaction() as u:
                model = Workflow.model_validate(u.active()["model"])
        else:
            baseline, candidate = studio.workflows(body.case_id)
            model = candidate or baseline
        if body.model is not None and body.model.semantic_hash != model.semantic_hash:
            raise DomainError("MODEL_CHANGED", "The model changed since the page loaded; reload and try again")
        if body.plan:  # trying accepted plan steps: applied here, through the policy, never taken from the page
            transactions = split([parse_step(step) for step in body.plan])[0]
            model = apply_transactions(model, transactions, pack_of(body.plan)) if transactions else model
        return model

    @app.get("/api/play/data")
    def play_data():
        """The pack's data model for the class diagram, or null when the pack has none (ADR-0153)."""
        data = data_for(studio.pack)
        return {"data": data.model_dump(mode="json") if data else None, "digest": data.digest if data else None,
                "build": class_build(data) if data else None}

    @app.get("/api/play/roles")
    def play_roles():
        """Each role with the kind of actor that holds it (ADR-0210): a person, an AI agent, a timer or an external system."""
        return {"roles": [{"id": r.id, "kind": r.kind, "description": r.description} for r in studio.pack.roles]}

    def accessibility(screens: Screens, model: Workflow, data: Any) -> dict[str, Any]:
        page = resource_files("eija_studio.resources").joinpath("appgen", "web")
        def read(name: str) -> str:
            return page.joinpath(name).read_text(encoding="utf-8")
        return check_accessibility(screens, model, data, theme_css=read("app.css.tmpl"), page_js=read("app.js.tmpl"),
                                   page_html=read("index.html.tmpl"))

    def screens_of(body: BuildRequest, model: Workflow) -> Screens:
        if body.screens is not None:
            return parse_screens(body.screens, studio.pack.id)
        return screens_for(studio.pack, model, data_for(pack_of(body.plan)))  # the files beside pack.json, as for any draft

    @app.post("/api/play/screens")
    def play_screens(body: BuildRequest):
        """The screens for the designer (the request's, else the pack's or the defaults) and their design problems."""
        model = resolve(body)
        screens, data = screens_of(body, model), data_for(pack_of(body.plan))
        return {"screens": screens.model_dump(mode="json"), "digest": screens.digest, "use_cases": use_cases(model),
                "problems": check_screens(screens, model, data), "accessibility": accessibility(screens, model, data)}

    def proposer():
        if studio.plan_proposer is None:
            raise DomainError("PLAN_UNAVAILABLE", "No plan proposer is configured")
        return studio.plan_proposer

    @app.post("/api/play/plan")
    def play_plan(body: PlanRequest):
        """Plan mode (ADR-0156): an untrusted plan of typed steps for the request, previewed with every step accepted."""
        # On a system you started, earlier rounds of the work in progress (body.plan) are kept and the new steps are
        # planned on top of them (ADR-0201); on a shipped pack a new plan replaces the last, as before.
        grows = own()
        on_top = body if grows else body.model_copy(update={"plan": None})
        return propose_plan(body.request, resolve(on_top), pack_of(on_top.plan), proposer(), grows=grows) | {"on_top": bool(grows and body.plan)}

    @app.post("/api/play/plan/preview")
    def play_plan_preview(body: PlanPreviewRequest):
        """What the accepted steps would make of the model. Nothing is saved or applied."""
        model = resolve(body.model_copy(update={"plan": None}))
        return preview_plan(model, studio.pack, [parse_step(step) for step in body.steps], body.accepted, grows=own())

    @app.post("/api/play/components")
    def play_components(body: BuildRequest):
        """The component diagram of the app this model and these screens would build, read from its files (ADR-0155)."""
        model = resolve(body)
        screens = screens_of(body, model)
        files, manifest = app_files(pack_of(body.plan), model, screens)
        return app_components(files) | {"model": model.semantic_hash, "screens": screens.digest, "cases": manifest["oracle"]["cases"],
                                        "deployment": app_deployment(files, __version__)}

    @app.post("/api/play/api-contract")
    def play_api_contract(body: BuildRequest):
        """The OpenAPI 3.1 document of the app this model builds (ADR-0207): its routes, request bodies and refusals."""
        model, pack = resolve(body), pack_of(body.plan)
        return api_contract(pack, model, data_for(pack))

    def built(pack: Pack, model: Workflow, screens: Screens) -> tuple[tuple[dict[str, str], int] | DomainError, list[dict[str, Any]]]:
        try:
            files, manifest = app_files(pack, model, screens)
        except DomainError as error:
            return error, []
        return (files, manifest["oracle"]["cases"]), app_components(files)["components"]

    def before_of(body: ChangeRequest) -> Workflow:
        """What the change shown is read against: the model in force, or with `since` the earlier rounds applied."""
        return baseline(body) if body.since is None else resolve(body.model_copy(update={"plan": body.since}))

    @app.post("/api/play/ripple")
    def play_ripple(body: ChangeRequest):
        """What the plan does to every diagram, and the proposer's follow-on edits, each re-checked (ADR-0158). With
        `since`, what its last round does (ADR-0201); the follow-ons are still for the whole plan."""
        base = resolve(body.model_copy(update={"plan": None}))
        candidate = resolve(body)
        start = base if body.since is None else before_of(body)
        # Before is the saved system with its pack's screens; screens edited in the designer are part of the change.
        pack, earlier = pack_of(body.plan), pack_of(body.since)
        data, data_before = data_for(pack), data_for(earlier)
        before, after = screens_for(studio.pack, start, data_before), screens_of(body, candidate)
        (old, _), (new, components) = built(earlier, start, before), built(pack, candidate, after)
        pack_tests = parse_scenarios(body.scenarios, studio.pack.id) if body.scenarios is not None else scenarios_for(studio.pack)
        scenarios = check_sequences(pack, candidate, scenarios_or_draft(pack, pack_tests, start)[0], start)
        others, _ = siblings(pack.id)  # the system this workflow is part of, before and after (ADR-0203, #146)
        system = (landscape(pack.id, [(earlier, data_before, start), *others]), landscape(pack.id, [(pack, data, candidate), *others])) if others else None
        report = ripple(start, candidate, data, (before, after), (old, new), components, scenarios, data_changes(data_before, data), system, data_before)
        document = proposer().follow_on(report, candidate, pack) if report["problems"] else {"steps": []}
        return report | {"provider": proposer().name, "live": proposer().live,
                         "follow_ons": check_follow_ons(document, base, body.plan or [], pack, candidate, after, data)}

    def baseline(body: BuildRequest) -> Workflow:
        """The model in force: the active baseline, or the case's baseline. A change is reviewed against it."""
        if body.case_id is None:
            with studio.store.transaction() as u:
                return Workflow.model_validate(u.active()["model"])
        return studio.workflows(body.case_id)[0]

    @app.post("/api/play/diff")
    def play_diff(body: ChangeRequest):
        """How the change shown looks (ADR-0176): a case's candidate and any accepted plan steps, against the model in
        force (or, with `since`, the last round against the rounds before it, ADR-0201), as one union of both state
        machines. Read-only."""
        return ghost_diff(before_of(body), resolve(body))

    @app.post("/api/play/ready")
    def play_ready(body: ScenariosRequest):
        """What's missing (ADR-0216): every view's row, ready or what it lacks, for the model shown with any accepted plan
        steps and the Tests tab's draft. Read-only."""
        model, pack = resolve(body), pack_of(body.plan)
        return missing(pack, model, data_for(pack), screens_of(body, model), scenarios_of(body))

    @app.post("/api/play/tests/update")
    def play_tests_update(body: ScenariosRequest):
        """The tests recorded again on the model shown (ADR-0216): failing ones re-recorded or dropped, new ways to an end
        state added. A draft for the Tests tab; nothing is written."""
        model, pack = resolve(body), pack_of(body.plan)
        data = data_for(pack)
        return update_tests(pack, model, scenarios_of(body), data.record if data is not None else "Record")

    @app.post("/api/play/review")
    def play_review(body: BuildRequest):
        """Review the change shown (a case's candidate and any accepted plan steps) against the model in force (ADR-0175).
        Read-only: nothing is saved, approved or applied."""
        before, after = baseline(body), resolve(body)
        return review_change(pack_of(body.plan), before, after) | {"ghost": ghost_diff(before, after)}  # drawn as in ADR-0176

    @app.post("/api/play/sequences")
    def play_sequences(body: ScenariosRequest):
        """The pack's scenarios (or a draft of them, shared with the Tests tab) drawn as sequence diagrams, each step run
        through the kernel on the shown model and, when it differs, on the model in force (ADR-0195). Read-only."""
        before, after = baseline(body), resolve(body)
        pack = pack_of(body.plan)
        if body.scenarios is not None:
            return check_sequences(pack, after, scenarios_of(body), before) | {"source": "edited"}
        scenarios, source = scenarios_or_draft(pack, scenarios_for(studio.pack), before)
        return check_sequences(pack, after, scenarios, before) | {"source": source}

    @app.post("/api/play/build")
    def play_build(body: BuildRequest):
        model = resolve(body)
        return runner.build_and_run(pack_of(body.plan), model, studio.identity_provider(), screens_of(body, model))

    @app.post("/api/play/simulate")
    def play_simulate(body: SimulateRequest):
        return simulate(pack_of(body.plan), resolve(body), seed=body.seed, steps=body.steps)

    @app.post("/api/play/run")
    def play_run(body: RunRequest):
        """The run bar (ADR-0160): every step of one seeded run, decided by the kernel, and where it stops."""
        return run_log(pack_of(body.plan), resolve(body), seed=body.seed, steps=body.steps, breakpoints=body.breakpoints,
                       break_on_refusal=body.break_on_refusal)

    @app.post("/api/play/laws")
    def play_laws(body: LawsRequest):
        """The pack's laws, each proved over every run the kernel allows on this model (ADR-0166). With a draft of the
        law file, the draft is checked and proved instead, and what it changes is listed; nothing is saved (ADR-0177)."""
        grown = pack_of(body.plan)
        pack = grown if body.laws is None else with_laws(grown, body.laws)
        report = prove_laws(pack, resolve(body))
        file: dict[str, Any] = {"path": pack_file(studio.pack, "pack.json"), "section": "laws",
                "laws": [law.model_dump(mode="json", exclude_none=True) for law in studio.pack.laws],
                "verifiers": [v.model_dump(mode="json", exclude_none=True) for v in studio.pack.verifiers]}
        if body.laws is not None:
            file |= {"draft": compare_laws(grown, pack), "draft_pack": pack.model_dump(mode="json", exclude_none=True)}
        return report | {"file": file}

    def scenarios_of(body: ScenariosRequest):
        return parse_scenarios(body.scenarios, studio.pack.id) if body.scenarios is not None else scenarios_for(studio.pack)

    @app.post("/api/play/tests")
    def play_tests(body: ScenariosRequest):
        """The pack's scenarios (or a draft of them), each run by the kernel on the model shown (ADR-0177)."""
        scenarios = scenarios_of(body)
        pack = pack_of(body.plan)
        return run_scenarios(pack, resolve(body), scenarios) | {
            "file": {"path": pack_file(studio.pack, "scenarios.json"), "document": scenarios.model_dump(mode="json", exclude_none=True)},
            "actors": [a.model_dump(mode="json") for a in pack.fixtures.actors]}

    @app.post("/api/play/tests/try")
    def play_tests_try(body: TryRequest):
        """What the kernel does for these steps, written as scenario steps that expect it: how a test is added."""
        return {"steps": record_steps(pack_of(body.plan), resolve(body), body.start, body.steps)}

    @app.post("/api/play/access")
    def play_access(body: BuildRequest):
        """Who can do what (ADR-0171): role by state, each cell tried in the kernel; with a plan, what it changes."""
        model = resolve(body)
        return access(pack_of(body.plan), model, resolve(body.model_copy(update={"plan": None})) if body.plan else None)

    def siblings(focus: str) -> tuple[list[tuple[Pack, Any, Workflow]], list[str]]:
        """The workflows in the folders beside the open one (ADR-0203), each as in force, and the folders not read:
        refused by the kernel's pack check, or a second folder with an id already read (the open one is read first)."""
        found: list[tuple[Pack, Any, Workflow]] = []
        unreadable: list[str] = []
        folder = pack_directory(studio.pack)
        for sibling in sorted(folder.parent.iterdir()) if folder is not None else ():
            if sibling == folder or not (sibling / PACK_FILE).is_file():
                continue
            try:
                other = load_pack(sibling)
            except (DomainError, OSError):
                unreadable.append(sibling.name)
                continue
            if other.id == focus or any(other.id == known.id for known, _, _ in found):  # two folders, one id: ambiguous
                unreadable.append(f"{sibling.name} (its id {other.id} is taken)")
            else:
                found.append((other, data_for(other), other.model))
        return found, unreadable

    @app.post("/api/play/landscape")
    def play_landscape(body: BuildRequest):
        """The system this workflow is part of (ADR-0203): the packs beside it that share a class with it, as one UML
        component diagram, and where their class diagrams disagree. The open one is the model and data model shown."""
        pack = pack_of(body.plan)
        others, unreadable = siblings(pack.id)
        return landscape(pack.id, [(pack, data_for(pack), resolve(body)), *others], unreadable)

    @app.post("/api/play/reach")
    def play_reach(body: ReachRequest):
        """Can a record reach a state without a role? A proof, a kernel-replayed path, or NOT_SHOWN (ADR-0171)."""
        return reach(pack_of(body.plan), resolve(body), body.target, body.without)

    @app.post("/api/play/stop")
    def play_stop():
        """The run bar's Stop: stop the built app if one is running."""
        return {"stopped": runner.stop()}

    register_interop(app, studio, resolve, BuildRequest, pack_of)  # UML export and import (ADR-0190)
    return runner
