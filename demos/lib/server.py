"""Launch a real `eija serve` process for a scenario to drive, and tear it down afterwards.

Mirrors the launch/readiness pattern already used by `scripts/http_smoke.py` and
`scripts/browser_smoke.py` (log-file polling for the printed private launch URL, then a loopback
TCP probe) rather than inventing a second one.

Teardown matters on Windows: `Popen.terminate()` kills only the launcher, while the real server child keeps
`server.log` open, so the whole process tree is killed and the scratch directory removed with retries.
"""
from __future__ import annotations

import contextlib
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
STARTUP_TIMEOUT_S = 15
_IS_WINDOWS = sys.platform == "win32"


@dataclass(frozen=True)
class RunningServer:
    base_url: str
    token: str
    workspace: Path

    @property
    def launch_url(self) -> str:
        return f"{self.base_url}#{self.token}"

    def status(self) -> dict[str, Any]:
        """GET /api/status with the session token (read-only; same call the Studio makes on load)."""
        response = httpx.get(
            f"{self.base_url}/api/status",
            headers={"Authorization": f"Bearer {self.token}"},
            trust_env=False,
            timeout=10,
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()
        return body

    @property
    def release_fixture_matches(self) -> bool:
        """False on any modified checkout until the OWNER restamps (agents never stamp)."""
        return bool(self.status().get("trusted_fixture"))


@contextmanager
def ephemeral_eija_server(*, workspace: Path | None = None) -> Iterator[RunningServer]:
    """Start `eija serve` on an ephemeral loopback port against a throwaway (or given) workspace.

    The provider is forced to `offline` so an `EIJA_PROVIDER` in the developer's shell can never change what a
    scenario shows (a demo must not spend money or reach a network)."""
    scratch = ROOT / ".tmp"
    scratch.mkdir(exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix="eija-demo-", dir=scratch))
    workspace = workspace or (tmp_dir / "workspace")
    log_path = tmp_dir / "server.log"
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    argv = [sys.executable, "-m", "eija_studio", "serve", "--provider", "offline",
            "--workspace", str(workspace), "--port", str(port)]
    process: subprocess.Popen[bytes] | None = None
    try:
        with log_path.open("w+", encoding="utf-8") as log:
            # Fixed argv, no shell: nothing here is user-controlled.
            process = subprocess.Popen(  # noqa: S603
                argv, env=env, stdout=log, stderr=log, start_new_session=not _IS_WINDOWS,
            )
            try:
                launch_url = _wait_for_ready(process, log_path, port)
                base_url, token = launch_url.split("#", 1)
                yield RunningServer(base_url=base_url.rstrip("/"), token=token, workspace=workspace)
            finally:
                _kill_process_tree(process)
    finally:
        _remove_tree(tmp_dir)


def _kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    """Kill the launcher AND its children, then reap it. Idempotent."""
    if process.poll() is None:
        if _IS_WINDOWS:
            # `taskkill` ships with Windows; /T = whole tree, /F = force. Fixed argv, integer pid.
            subprocess.run(  # noqa: S603
                ["taskkill", "/T", "/F", "/PID", str(process.pid)],  # noqa: S607
                capture_output=True, check=False, timeout=30,
            )
        else:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def _remove_tree(path: Path, *, attempts: int = 20, delay_s: float = 0.5) -> bool:
    """Remove a scratch directory, retrying: Windows releases a killed child's file handles a moment late.

    Returns False (after a warning) rather than raising, so cleanup never masks the scenario's own error."""
    for attempt in range(attempts):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            return True
        except OSError:
            if attempt < attempts - 1:
                time.sleep(delay_s)
        else:
            return True
    sys.stderr.write(f"warning: could not remove scratch directory {path}\n")
    return False


def _wait_for_ready(process: subprocess.Popen[bytes], log_path: Path, port: int) -> str:
    """Return the private launch URL once it is printed and connectable; fail fast if the server dies."""
    deadline = time.monotonic() + STARTUP_TIMEOUT_S
    url: str | None = None
    while time.monotonic() < deadline:
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("http://127.0.0.1:"):
                url = line.strip()
        if url:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    return url
            except OSError:
                pass
        if process.poll() is not None:
            raise RuntimeError(
                f"eija serve exited (code {process.returncode}) before it was ready:\n{_log_tail(log_path)}"
            )
        time.sleep(0.1)
    raise RuntimeError(
        f"eija serve did not become ready within {STARTUP_TIMEOUT_S}s:\n{_log_tail(log_path)}"
    )


def _log_tail(log_path: Path) -> str:
    return log_path.read_text(encoding="utf-8", errors="replace")[-800:]
