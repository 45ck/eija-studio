"""PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and
Simulate, seeded simulated users whose every step the kernel decides (ADR-0152), the screen designer's check and
build of designed screens (ADR-0154), the component diagram read from the files the app is built from (ADR-0155), the chat's plan mode, whose accepted
steps can be previewed, built and simulated but never saved or applied from here (ADR-0156), the ripple of a plan
across every diagram with the follow-on edits the proposer suggests, each re-checked (ADR-0158), and the run bar's
seeded run log with breakpoints and Stop (ADR-0160).

Build & run reuses `eija build` (ADR-0150): the app is generated into the workspace, its kernel conformance tests run,
and only a PASSing app is started, as a separate local process on a free loopback port. One app runs at a time; a new
model's build replaces it and the IDE stops it on exit. The generated app has no access to the workspace database.
"""
from __future__ import annotations

import atexit
import os
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi.responses import FileResponse

from pydantic import Field

from eija_studio.application.components import app_components
from eija_studio.application.plan import preview_plan, propose_plan
from eija_studio.application.ripple import check_follow_ons, ripple
from eija_studio.application.simulation import MAX_BREAKPOINTS, MAX_STEPS, run_log, simulate
from eija_studio.domain.data import data_for
from eija_studio.domain.models import Contract, DomainError, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import apply_transactions
from eija_studio.domain.transactions import parse_transaction
from eija_studio.domain.screens import Screens, check_screens, parse_screens, screens_for, use_cases
from .app_build import app_files, build_into

START_TIMEOUT_S = 10.0


class BuildRequest(Contract):
    case_id: str | None = None  # None builds the active baseline; a case builds its candidate (or baseline if none yet)
    model: Workflow | None = None  # the model the page shows; if given, it must still be the one that would be built
    screens: dict[str, Any] | None = None  # screens edited in the designer (eija.screens.v1); None uses the pack's
    plan: list[dict[str, Any]] | None = Field(default=None, max_length=12)  # accepted chat-plan steps, tried on top


class PlanRequest(BuildRequest):
    request: str = Field(min_length=1, max_length=2000)


class PlanPreviewRequest(BuildRequest):
    steps: list[dict[str, Any]] = Field(min_length=1, max_length=12)
    accepted: list[bool] = Field(min_length=1, max_length=12)


class SimulateRequest(BuildRequest):
    seed: int = Field(default=1, ge=0, le=2**31 - 1)
    steps: int = Field(default=500, ge=1, le=MAX_STEPS)


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


def register(app, studio, web: Path) -> AppRunner:
    runner = AppRunner(lambda: Path(studio.store.directory) / "apps")

    @app.get("/play")
    def play_page():
        return FileResponse(web / "play.html")

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
            model = apply_transactions(model, [parse_transaction(step) for step in body.plan], studio.pack)
        return model

    @app.get("/api/play/data")
    def play_data():
        """The pack's data model for the class diagram, or null when the pack has none (ADR-0153)."""
        data = data_for(studio.pack)
        return {"data": data.model_dump(mode="json") if data else None, "digest": data.digest if data else None}

    def screens_of(body: BuildRequest, model: Workflow) -> Screens:
        if body.screens is not None:
            return parse_screens(body.screens, studio.pack.id)
        return screens_for(studio.pack, model, data_for(studio.pack))

    @app.post("/api/play/screens")
    def play_screens(body: BuildRequest):
        """The screens for the designer (the request's, else the pack's or the defaults) and their design problems."""
        model = resolve(body)
        screens, data = screens_of(body, model), data_for(studio.pack)
        return {"screens": screens.model_dump(mode="json"), "digest": screens.digest, "use_cases": use_cases(model),
                "problems": check_screens(screens, model, data)}

    def proposer():
        if studio.plan_proposer is None:
            raise DomainError("PLAN_UNAVAILABLE", "No plan proposer is configured")
        return studio.plan_proposer

    @app.post("/api/play/plan")
    def play_plan(body: PlanRequest):
        """Plan mode (ADR-0156): an untrusted plan of typed steps for the request, previewed with every step accepted."""
        return propose_plan(body.request, resolve(body.model_copy(update={"plan": None})), studio.pack, proposer())

    @app.post("/api/play/plan/preview")
    def play_plan_preview(body: PlanPreviewRequest):
        """What the accepted steps would make of the model. Nothing is saved or applied."""
        model = resolve(body.model_copy(update={"plan": None}))
        return preview_plan(model, studio.pack, [parse_transaction(step) for step in body.steps], body.accepted)

    @app.post("/api/play/components")
    def play_components(body: BuildRequest):
        """The component diagram of the app this model and these screens would build, read from its files (ADR-0155)."""
        model = resolve(body)
        screens = screens_of(body, model)
        files, manifest = app_files(studio.pack, model, screens)
        return app_components(files) | {"model": model.semantic_hash, "screens": screens.digest, "cases": manifest["oracle"]["cases"]}

    def built(model: Workflow, screens: Screens) -> tuple[tuple[dict[str, str], int] | DomainError, list[dict[str, Any]]]:
        try:
            files, manifest = app_files(studio.pack, model, screens)
        except DomainError as error:
            return error, []
        return (files, manifest["oracle"]["cases"]), app_components(files)["components"]

    @app.post("/api/play/ripple")
    def play_ripple(body: BuildRequest):
        """What the plan does to every diagram, and the proposer's follow-on edits, each re-checked (ADR-0158)."""
        base = resolve(body.model_copy(update={"plan": None}))
        candidate = resolve(body)
        # Before is the saved system with its pack's screens; screens edited in the designer are part of the change.
        before, after = screens_for(studio.pack, base, data_for(studio.pack)), screens_of(body, candidate)
        (old, _), (new, components) = built(base, before), built(candidate, after)
        data = data_for(studio.pack)
        report = ripple(base, candidate, data, (before, after), (old, new), components)
        document = proposer().follow_on(report, candidate, studio.pack) if report["problems"] else {"steps": []}
        return report | {"provider": proposer().name, "live": proposer().live,
                         "follow_ons": check_follow_ons(document, base, body.plan or [], studio.pack, candidate, after, data)}

    @app.post("/api/play/build")
    def play_build(body: BuildRequest):
        model = resolve(body)
        return runner.build_and_run(studio.pack, model, studio.identity_provider(), screens_of(body, model))

    @app.post("/api/play/simulate")
    def play_simulate(body: SimulateRequest):
        return simulate(studio.pack, resolve(body), seed=body.seed, steps=body.steps)

    @app.post("/api/play/run")
    def play_run(body: RunRequest):
        """The run bar (ADR-0160): every step of one seeded run, decided by the kernel, and where it stops."""
        return run_log(studio.pack, resolve(body), seed=body.seed, steps=body.steps, breakpoints=body.breakpoints,
                       break_on_refusal=body.break_on_refusal)

    @app.post("/api/play/stop")
    def play_stop():
        """The run bar's Stop: stop the built app if one is running."""
        return {"stopped": runner.stop()}

    return runner
