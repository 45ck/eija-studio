"""PlayIDE routes: the visual UML canvas page, and Build & run of the model as a live app beside it (ADR-0151).

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

from eija_studio.domain.models import Contract, DomainError, Workflow
from eija_studio.domain.pack import Pack
from .app_build import build_into

START_TIMEOUT_S = 10.0


class BuildRequest(Contract):
    case_id: str | None = None  # None builds the active baseline; a case builds its candidate (or baseline if none yet)
    model: Workflow | None = None  # the model the page shows; if given, it must still be the one that would be built


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

    def build_and_run(self, pack: Pack, model: Workflow, identity: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            out = self.root() / model.semantic_hash[:12]
            manifest = build_into(out, pack, model, identity)
            result = {"model": model.semantic_hash, "cases": manifest["oracle"]["cases"],
                      "conformance": manifest["conformance"], "kernel_source_review": manifest["kernel_source_review"],
                      "files": len(manifest["files"]), "url": None}
            if manifest["conformance"]["status"] != "PASS":
                self._stop()  # never leave an older app running as if it were this model's
                return result
            return result | {"url": self._start(out, model.semantic_hash)}

    def _start(self, out: Path, model_hash: str) -> str:
        alive = self.process is not None and self.process.poll() is None
        if alive and self.running and self.running["model"] == model_hash:
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
        self.running = {"model": model_hash, "url": f"http://127.0.0.1:{port}/"}
        return self.running["url"]

    def _stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process, self.running = None, None

    def stop(self) -> None:
        with self.lock:
            self._stop()


def register(app, studio, web: Path) -> AppRunner:
    runner = AppRunner(lambda: Path(studio.store.directory) / "apps")

    @app.get("/play")
    def play_page():
        return FileResponse(web / "play.html")

    @app.post("/api/play/build")
    def play_build(body: BuildRequest):
        if body.case_id is None:
            with studio.store.transaction() as u:
                model = Workflow.model_validate(u.active()["model"])
        else:
            baseline, candidate = studio.workflows(body.case_id)
            model = candidate or baseline
        if body.model is not None and body.model.semantic_hash != model.semantic_hash:
            raise DomainError("MODEL_CHANGED", "The model changed since the page loaded; reload and build again")
        return runner.build_and_run(studio.pack, model, studio.identity_provider())

    return runner
