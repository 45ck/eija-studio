"""Bounded, tree-killing subprocess execution for agent CLIs.

This module knows nothing about models. It establishes: no shell, prompt on stdin, output capped while it is
produced (not after), a wall-clock deadline, and on timeout/overflow the whole process TREE is killed. It does
NOT establish that the CLI itself is sandboxed; each adapter must also switch the CLI's own tools off.

Tree kill: psutil (OSS, https://github.com/giampaolo/psutil) snapshots the descendants before anything is
killed; POSIX additionally kills the process group (children start in their own session) and Windows falls
back to ``taskkill /T /F`` when psutil is absent. A descendant that deliberately detaches from the tree
before the snapshot (double fork, ``setsid`` after we looked) can survive; see docs/providers.md.
"""
from __future__ import annotations
import os
import re
import shutil
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Protocol

try:  # optional accelerator; the lane extra pins it, the kernel does not require it
    import psutil as _psutil
except ImportError:  # pragma: no cover - exercised by tests through monkeypatching
    _psutil = None

MAX_STREAM_BYTES = 262144
_IS_WINDOWS = os.name == "nt"


class CliTimeout(Exception):
    """The deadline passed and the process tree was killed. ``stdout`` holds what was captured (bounded)."""

    def __init__(self, stdout: str = "") -> None:
        super().__init__("timeout")
        self.stdout = stdout


class CliOutputLimit(Exception):
    """A stream exceeded its byte cap; the process tree was killed."""


class CliShimUnsupported(Exception):
    """An executable would need cmd.exe (a .cmd/.bat we cannot unwrap). Refused: argument-injection risk."""


class Runner(Protocol):
    """Injectable process runner. Real one: ``run_bounded``. Tests pass a mock with the same signature."""

    def __call__(self, args: list[str], *, input: str | None, env: dict[str, str], timeout: float,
                 cwd: str | None = None) -> subprocess.CompletedProcess: ...


def _descendants(pid: int) -> list:
    if _psutil is None:
        return []
    try:
        return _psutil.Process(pid).children(recursive=True)
    except (_psutil.Error, OSError):
        return []


def kill_process_tree(process: subprocess.Popen, known: dict | None = None) -> None:
    """Kill ``process`` and every descendant seen so far (``known``, refreshed while it ran) or still linked now.

    Never raises. A descendant that was reparented (its parent exited) before it was ever observed survives.
    """
    victims = list({v.pid: v for v in [*(known or {}).values(), *_descendants(process.pid)]}.values())
    try:
        if _IS_WINDOWS:
            if _psutil is None:
                taskkill = shutil.which("taskkill")
                if taskkill:
                    subprocess.run([taskkill, "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=15, check=False)
        else:
            os.killpg(process.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        pass
    for victim in victims:
        try:
            victim.kill()
        except Exception:  # noqa: BLE001 - already gone / access denied: best effort
            pass
    try:
        process.kill()
    except OSError:
        pass
    if _psutil is not None and victims:
        _psutil.wait_procs(victims, timeout=5)


class _Capture:
    """Reads one pipe on a thread, stopping (and flagging) at the byte cap."""

    def __init__(self, stream, limit: int, overflow: threading.Event) -> None:
        self.chunks: list[bytes] = []
        self.size = 0
        self._stream, self._limit, self._overflow = stream, limit, overflow
        self.thread = threading.Thread(target=self._pump, daemon=True)
        self.thread.start()

    def _pump(self) -> None:
        try:
            while True:
                chunk = self._stream.read1(65536)
                if not chunk:
                    return
                self.size += len(chunk)
                if self.size > self._limit:
                    self._overflow.set()
                    return
                self.chunks.append(chunk)
        except (OSError, ValueError):
            return

    def text(self) -> str:
        return b"".join(self.chunks).decode("utf-8", errors="replace")


def _feed(stream, data: bytes) -> None:
    try:
        stream.write(data)
    except OSError:
        pass
    finally:
        try:
            stream.close()
        except OSError:
            pass


def run_bounded(args: list[str], *, input: str | None, env: dict[str, str], timeout: float,
                cwd: str | None = None, max_bytes: int = MAX_STREAM_BYTES) -> subprocess.CompletedProcess:
    """Run ``args`` without a shell. Raises CliTimeout / CliOutputLimit after killing the whole tree.

    Establishes bounded capture and a deadline. Does not interpret the output or the exit code.
    """
    flags = (subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW) if _IS_WINDOWS else 0
    process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=cwd,
                               shell=False, start_new_session=not _IS_WINDOWS, creationflags=flags)
    overflow = threading.Event()
    out, err = _Capture(process.stdout, max_bytes, overflow), _Capture(process.stderr, max_bytes, overflow)
    feeder = threading.Thread(target=_feed, args=(process.stdin, (input or "").encode("utf-8")), daemon=True)
    feeder.start()
    deadline = time.monotonic() + timeout
    known: dict[int, object] = {}
    next_scan = time.monotonic() + 0.3
    try:
        while process.poll() is None:
            if overflow.is_set():
                kill_process_tree(process, known)
                raise CliOutputLimit()
            if time.monotonic() >= deadline:
                kill_process_tree(process, known)
                out.thread.join(2)
                raise CliTimeout(out.text())
            if _psutil is not None and time.monotonic() >= next_scan:
                known.update({d.pid: d for d in _descendants(process.pid)})  # remember them in case a parent exits first
                next_scan = time.monotonic() + 0.3
            time.sleep(0.02)
        for capture in (out, err):
            capture.thread.join(max(0.0, deadline - time.monotonic()) + 1)
        if out.thread.is_alive() or err.thread.is_alive():
            # A grandchild kept the pipe open after the main process exited: treat as a hung tree.
            kill_process_tree(process, known)
            raise CliTimeout(out.text())
        if overflow.is_set():
            raise CliOutputLimit()
    except BaseException:
        kill_process_tree(process, known)
        raise
    finally:
        feeder.join(1)
        for stream in (process.stdout, process.stderr):
            try:
                stream.close()
            except OSError:
                pass
    return subprocess.CompletedProcess(args, process.returncode, out.text(), err.text())


_SHIM_LAUNCH = re.compile(r'"%_prog%"\s+(?P<tail>.*?)\s*%\*', re.DOTALL)
_TOKEN = re.compile(r'"([^"]*)"|(\S+)')


def _unwrap_node_shim(shim: Path) -> list[str]:
    """Turn an npm ``.cmd`` shim into ``[node, script, ...]`` so cmd.exe is never involved (BatBadBut).

    Only the exact shape npm generates is accepted; anything else is refused rather than run through cmd.exe.
    """
    text = shim.read_text(encoding="utf-8", errors="replace")
    match = _SHIM_LAUNCH.search(text)
    if not match:
        raise CliShimUnsupported(shim.name)
    base = shim.parent
    node = base / "node.exe"
    interpreter = str(node) if node.is_file() else shutil.which("node")
    if not interpreter:
        raise CliShimUnsupported("node not found for " + shim.name)
    argv: list[str] = []
    for quoted, bare in _TOKEN.findall(match.group("tail")):
        token = (quoted or bare).replace("%dp0%", str(base) + os.sep)
        if "%" in token:
            raise CliShimUnsupported(shim.name)
        argv.append(os.path.normpath(token) if quoted else token)
    scripts = [a for a in argv if not a.startswith("-")]
    if not scripts or not Path(scripts[0]).is_file():
        raise CliShimUnsupported(shim.name)
    return [interpreter, *argv]


def resolve_command(executable: str) -> list[str]:
    """Resolve a CLI name to an argv prefix that CreateProcess/execve can run directly.

    Raises FileNotFoundError when absent and CliShimUnsupported for a shim that would need cmd.exe.
    """
    found = shutil.which(executable)
    if not found:
        raise FileNotFoundError(executable)
    suffix = Path(found).suffix.lower()
    if _IS_WINDOWS and suffix in (".cmd", ".bat"):
        return _unwrap_node_shim(Path(found))
    if _IS_WINDOWS and suffix not in (".exe", ".com"):
        raise CliShimUnsupported(Path(found).name)
    return [found]

