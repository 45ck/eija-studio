"""Ephemeral `eija serve` for measurement: real CLI, real Uvicorn, loopback TCP, offline provider.

This is the lane's OWN throw-away server on a workspace inside the checkout (never the owner's
workspace, never a provider call). The server prints its private launch link to `server.log` in the
scratch directory; that directory (token included) is deleted when the context exits, on success or
failure, so the token never outlives the run.
"""
from __future__ import annotations

import contextlib
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[2]


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def studio_server(label: str, identity: str = "harness", timeout: float = 30.0) -> Iterator[str]:
    """Yield the launch URL (with session fragment) of a fresh server on a fresh workspace.

    identity="harness": quality.hci.serve_harness (kernel-test identity; approval reachable on unstamped
    source). identity="release": the real `eija serve`, whose approval needs a release-stamped build.
    """
    scratch = ROOT / ".tmp" / "hci" / f"{label}-{os.getpid()}"
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True)
    try:
        with _serve(scratch, identity, timeout) as url:
            yield url
    finally:  # runs when the caller's block raises too: no stale scratch dir, no leftover launch token
        shutil.rmtree(scratch, ignore_errors=True)


@contextlib.contextmanager
def _serve(scratch: Path, identity: str, timeout: float) -> Iterator[str]:
    port = free_port()
    log = scratch / "server.log"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    env["TMP"] = env["TEMP"] = str(scratch)  # D: is a slow HDD; keep temp inside the checkout
    env.pop("EIJA_PROVIDER", None)
    with log.open("w+") as output:
        if identity == "release":
            command = [sys.executable, "-m", "eija_studio", "serve", "--provider", "offline"]
        elif identity == "harness":
            env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + str(ROOT)
            command = [sys.executable, "-m", "quality.hci.serve_harness"]
        else:
            raise ValueError("identity must be 'harness' or 'release'")
        process = subprocess.Popen(command + ["--workspace", str(scratch / "workspace"), "--port", str(port)],
                                   env=env, stdout=output, stderr=output, cwd=str(ROOT))
        try:
            url = None
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError("eija serve exited early; see " + str(log))
                for line in log.read_text(errors="replace").splitlines():
                    if line.startswith("http://127.0.0.1:"):
                        url = line.strip()
                if url:
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                            break
                    except OSError:
                        pass
                time.sleep(0.1)
            else:
                raise RuntimeError("eija serve did not accept connections within %.0fs" % timeout)
            yield url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
