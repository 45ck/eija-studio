"""Launch a real `eija serve` process for a scenario to drive, and tear it down afterwards.

Mirrors the launch/readiness pattern already used by `scripts/http_smoke.py` and
`scripts/browser_smoke.py` (log-file polling for the printed private launch URL, then a loopback
TCP probe) rather than inventing a second one.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[2]
STARTUP_TIMEOUT_S = 15


@dataclass(frozen=True)
class RunningServer:
    base_url: str
    token: str
    workspace: Path

    @property
    def launch_url(self) -> str:
        return f"{self.base_url}#{self.token}"

    def status(self) -> dict:
        """GET /api/status with the session token (read-only; same call the Studio makes on load)."""
        import httpx

        response = httpx.get(f"{self.base_url}/api/status", headers={"Authorization": f"Bearer {self.token}"},
                             trust_env=False, timeout=10)
        response.raise_for_status()
        return response.json()

    @property
    def release_fixture_matches(self) -> bool:
        """False on any modified checkout until the OWNER restamps (agents never stamp)."""
        return bool(self.status().get("trusted_fixture"))


@contextmanager
def ephemeral_eija_server(*, workspace: Path | None = None) -> Iterator[RunningServer]:
    """Start `eija serve` on an ephemeral loopback port against a throwaway (or given) workspace."""
    own_temp = workspace is None
    tmp_dir = Path(tempfile.mkdtemp(prefix="eija-demo-", dir=ROOT / ".tmp" if (ROOT / ".tmp").is_dir() else None))
    workspace = workspace or (tmp_dir / "workspace")
    log_path = tmp_dir / "server.log"
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    with log_path.open("w+", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "eija_studio", "serve", "--workspace", str(workspace), "--port", str(port)],
            env=env,
            stdout=log,
            stderr=log,
        )
        try:
            launch_url = _wait_for_ready(log_path, port)
            base_url, token = launch_url.split("#", 1)
            yield RunningServer(base_url=base_url.rstrip("/"), token=token, workspace=workspace)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    if own_temp:
        import shutil

        shutil.rmtree(tmp_dir, ignore_errors=True)


def _wait_for_ready(log_path: Path, port: int) -> str:
    import time

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
        time.sleep(0.1)
    raise RuntimeError(f"eija serve did not become ready within {STARTUP_TIMEOUT_S}s; see {log_path}")
