"""Ephemeral `eija serve` for measurement: real CLI, real Uvicorn, loopback TCP, offline provider.

This is the lane's OWN throw-away server on a workspace inside the checkout (never the owner's
workspace, never a provider call). The private launch link is consumed by the browser we drive; it
is not logged or written anywhere except the scratch server log, which is deleted with the workspace.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IDENTITIES = ("harness", "release")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _command(identity: str, workspace: Path, port: int) -> list[str]:
    """argv of the server for an identity. `harness` is the labelled kernel-test stand-in; `release` is the real CLI."""
    if identity == "release":
        base = [sys.executable, "-m", "eija_studio", "serve", "--provider", "offline"]
    elif identity == "harness":
        base = [sys.executable, "-m", "quality.hci.serve_harness"]
    else:
        raise ValueError("identity must be one of " + ", ".join(IDENTITIES))
    return [*base, "--workspace", str(workspace), "--port", str(port)]


def _environment(identity: str, scratch: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + str(ROOT) if identity == "harness" else "")
    env["TMP"] = env["TEMP"] = str(scratch)  # D: is a slow HDD; keep temp inside the checkout
    env.pop("EIJA_PROVIDER", None)
    return env


def _launch_url(log: Path) -> str | None:
    for line in log.read_text(errors="replace").splitlines():
        if line.startswith("http://127.0.0.1:"):
            return line.strip()
    return None


def _accepts_connections(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            return True
    except OSError:
        return False


def _wait_ready(process: subprocess.Popen, log: Path, port: int, timeout: float) -> str:
    """The launch URL once the server prints it and accepts connections; RuntimeError otherwise."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("eija serve exited early; see " + str(log))
        url = _launch_url(log)
        if url and _accepts_connections(port):
            return url
        time.sleep(0.1)
    raise RuntimeError(f"eija serve did not accept connections within {timeout:.0f}s")


def _remove_tree(path: Path, attempts: int = 25) -> None:
    """Delete a scratch tree; on Windows a file can stay locked for a moment after its process exits, so retry briefly."""
    for _ in range(attempts):
        shutil.rmtree(path, ignore_errors=True)
        if not path.exists():
            return
        time.sleep(0.2)


def _stop(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@contextlib.contextmanager
def _serve(scratch: Path, identity: str, timeout: float) -> Iterator[str]:
    """Run one server for `identity` on a workspace inside `scratch`; yield its launch URL, always stop the process."""
    port = free_port()
    log = scratch / "server.log"
    command = _command(identity, scratch / "workspace", port)
    with log.open("w+") as output:
        process = subprocess.Popen(command, env=_environment(identity, scratch), stdout=output, stderr=output, cwd=str(ROOT))  # noqa: S603 - fixed argv, no shell
        try:
            yield _wait_ready(process, log, port, timeout)
        finally:
            _stop(process)


@contextlib.contextmanager
def studio_server(label: str, identity: str = "harness", timeout: float = 30.0) -> Iterator[str]:
    """Yield the launch URL (with session fragment) of a fresh server on a fresh workspace.

    identity="harness": quality.hci.serve_harness (kernel-test identity; approval reachable on unstamped
    source). identity="release": the real `eija serve`, whose approval needs a release-stamped build.
    The scratch directory (which holds server.log with the private launch token) is deleted when the
    context exits, on success or failure.
    """
    if identity not in IDENTITIES:
        raise ValueError("identity must be one of " + ", ".join(IDENTITIES))
    scratch = ROOT / ".tmp" / "hci" / f"{label}-{os.getpid()}"
    _remove_tree(scratch)
    scratch.mkdir(parents=True)
    try:
        with _serve(scratch, identity, timeout) as url:
            yield url
    finally:
        _remove_tree(scratch)
