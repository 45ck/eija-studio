"""Bounded, tree-killing subprocess execution for agent CLIs.

This module knows nothing about models. It establishes: no shell, prompt on stdin, output capped while it is
produced (not after), a wall-clock deadline, and on timeout/overflow the whole process TREE is killed. It does
NOT establish that the CLI itself is sandboxed; each adapter must also switch the CLI's own tools off.

Tree kill, three layers: a Windows Job Object (``_winjob``) or a POSIX process group follows descendants by
membership; psutil (OSS, https://github.com/giampaolo/psutil) snapshots descendants right after start and again
every 50 ms so a reparented one is still known; ``taskkill /T /F`` is the Windows fallback when psutil is
absent. A descendant that deliberately breaks away (a double fork with ``setsid`` before the first snapshot on
POSIX, ``CREATE_BREAKAWAY_FROM_JOB`` where the job allows it) can survive; see docs/providers.md.
"""
from __future__ import annotations

import contextlib
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import IO, Any, Protocol

from ._winjob import JobObject, attach

try:  # optional accelerator; the lane extra pins it, the kernel does not require it
    import psutil as _psutil
except ImportError:  # pragma: no cover - exercised by tests through monkeypatching
    _psutil = None

MAX_STREAM_BYTES = 262144
SCAN_INTERVAL = 0.05
POLL_INTERVAL = 0.02


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
                 cwd: str | None = None) -> subprocess.CompletedProcess[str]: ...


# ---- killing ---------------------------------------------------------------------------------------------
def _descendants(pid: int) -> list[Any]:
    if _psutil is None:
        return []
    try:
        return list(_psutil.Process(pid).children(recursive=True))
    except (_psutil.Error, OSError):
        return []


def _kill_group_or_taskkill(process: subprocess.Popen[bytes]) -> None:
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        if sys.platform != "win32":
            os.killpg(process.pid, signal.SIGKILL)
        elif _psutil is None:
            taskkill = shutil.which("taskkill")
            if taskkill:
                subprocess.run([taskkill, "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=15, check=False)


def _kill_quietly(victim: Any) -> None:
    with contextlib.suppress(Exception):  # already gone or access denied: best effort
        victim.kill()


def kill_process_tree(process: subprocess.Popen[bytes], known: dict[int, Any] | None = None) -> None:
    """Kill ``process`` and every descendant seen so far (``known``, refreshed while it ran) or still linked now.

    Never raises. A descendant that was reparented (its parent exited) before it was ever observed survives
    unless a Windows job or a POSIX process group covers it.
    """
    victims = list({v.pid: v for v in [*(known or {}).values(), *_descendants(process.pid)]}.values())
    _kill_group_or_taskkill(process)
    for victim in victims:
        _kill_quietly(victim)
    with contextlib.suppress(OSError):
        process.kill()
    if _psutil is not None and victims:
        _psutil.wait_procs(victims, timeout=5)


class _TreeGuard:
    """Everything needed to kill one run's tree: a job (Windows), remembered descendants, the process itself."""

    def __init__(self, process: subprocess.Popen[bytes]) -> None:
        self.process = process
        self.known: dict[int, Any] = {}
        self.job: JobObject | None = attach(process.pid)
        self._next_scan = 0.0
        self.observe()

    def observe(self) -> None:
        """Remember current descendants (rate limited) in case a parent exits before the kill."""
        now = time.monotonic()
        if _psutil is not None and now >= self._next_scan:
            self.known.update({d.pid: d for d in _descendants(self.process.pid)})
            self._next_scan = now + SCAN_INTERVAL

    def kill(self) -> None:
        if self.job is not None:
            self.job.terminate()
        kill_process_tree(self.process, self.known)

    def release(self) -> None:
        if self.job is not None:
            self.job.close()  # kill-on-close reaps anything still in the job


# ---- capture ---------------------------------------------------------------------------------------------
class _Capture:
    """Reads one pipe on a thread, stopping (and flagging) at the byte cap."""

    def __init__(self, stream: Any, limit: int, overflow: threading.Event) -> None:  # a BufferedReader (has read1)
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

    def close(self, grace: float) -> None:
        """Close the pipe ONLY if its reader thread finished.

        Closing a stream a thread is blocked reading waits on the buffer lock, forever if a descendant that
        escaped the kill still holds the pipe. In that case the daemon thread and the pipe are left to be
        reaped when that descendant dies; the caller has already raised its timeout.
        """
        self.thread.join(grace)
        if not self.thread.is_alive():
            with contextlib.suppress(OSError):
                self._stream.close()


def _feed(stream: IO[bytes], data: bytes) -> None:
    try:
        stream.write(data)
    except OSError:
        pass
    finally:
        with contextlib.suppress(OSError):
            stream.close()


def _spawn(args: list[str], env: dict[str, str], cwd: str | None) -> subprocess.Popen[bytes]:
    """Start the child: no shell, its own process group/session so the tree can be signalled as a unit."""
    extra: dict[str, Any] = {}
    if sys.platform == "win32":
        extra["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    else:
        extra["start_new_session"] = True
    return subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=cwd,
                            shell=False, **extra)


def _pipes(process: subprocess.Popen[bytes]) -> tuple[IO[bytes], IO[bytes], IO[bytes]]:
    if process.stdin is None or process.stdout is None or process.stderr is None:
        raise RuntimeError("pipes were requested at spawn")
    return process.stdin, process.stdout, process.stderr


# ---- run -------------------------------------------------------------------------------------------------
def _wait_for_exit(guard: _TreeGuard, out: _Capture, overflow: threading.Event, deadline: float) -> None:
    """Poll until the process exits. Raises (after killing the tree) on output overflow or deadline."""
    process = guard.process
    while process.poll() is None:
        if overflow.is_set():
            guard.kill()
            raise CliOutputLimit
        if time.monotonic() >= deadline:
            guard.kill()
            out.thread.join(2)
            raise CliTimeout(out.text())
        guard.observe()
        time.sleep(POLL_INTERVAL)


def _drain(guard: _TreeGuard, captures: tuple[_Capture, _Capture], overflow: threading.Event, deadline: float) -> None:
    """After the main process exited: its pipes must reach EOF. A descendant keeping them open is a hung tree."""
    for capture in captures:
        capture.thread.join(max(0.0, deadline - time.monotonic()) + 1)
    if any(capture.thread.is_alive() for capture in captures):
        guard.kill()
        raise CliTimeout(captures[0].text())
    if overflow.is_set():
        raise CliOutputLimit


def run_bounded(args: list[str], *, input: str | None, env: dict[str, str], timeout: float,
                cwd: str | None = None, max_bytes: int = MAX_STREAM_BYTES) -> subprocess.CompletedProcess[str]:
    """Run ``args`` without a shell. Raises CliTimeout / CliOutputLimit after killing the whole tree.

    Establishes bounded capture and a deadline. Does not interpret the output or the exit code.
    """
    process = _spawn(args, env, cwd)
    guard = _TreeGuard(process)
    overflow = threading.Event()
    stdin, stdout, stderr = _pipes(process)
    out, err = _Capture(stdout, max_bytes, overflow), _Capture(stderr, max_bytes, overflow)
    feeder = threading.Thread(target=_feed, args=(stdin, (input or "").encode("utf-8")), daemon=True)
    feeder.start()
    deadline = time.monotonic() + timeout
    try:
        _wait_for_exit(guard, out, overflow, deadline)
        _drain(guard, (out, err), overflow, deadline)
    except (CliTimeout, CliOutputLimit):
        raise
    except BaseException:
        guard.kill()
        raise
    finally:
        guard.release()
        feeder.join(1)
        out.close(1.0)
        err.close(1.0)
    return subprocess.CompletedProcess(args, process.returncode, out.text(), err.text())


# ---- executable resolution -------------------------------------------------------------------------------
_SHIM_LAUNCH = re.compile(r'"%_prog%"\s+(?P<tail>.*?)\s*%\*', re.DOTALL)
_TOKEN = re.compile(r'"([^"]*)"|(\S+)')


def _shim_interpreter(base: Path, shim_name: str) -> str:
    node = base / "node.exe"
    interpreter = str(node) if node.is_file() else shutil.which("node")
    if not interpreter:
        raise CliShimUnsupported("node not found for " + shim_name)
    return interpreter


def _shim_argv(tail: str, base: Path, shim_name: str) -> list[str]:
    """Tokenise the tail of an npm shim's launch line; any leftover ``%`` variable means it is not the known shape."""
    argv: list[str] = []
    for quoted, bare in _TOKEN.findall(tail):
        token = (quoted or bare).replace("%dp0%", str(base) + os.sep)
        if "%" in token:
            raise CliShimUnsupported(shim_name)
        argv.append(os.path.normpath(token) if quoted else token)
    scripts = [a for a in argv if not a.startswith("-")]
    if not scripts or not Path(scripts[0]).is_file():
        raise CliShimUnsupported(shim_name)
    return argv


def _unwrap_node_shim(shim: Path) -> list[str]:
    """Turn an npm ``.cmd`` shim into ``[node, script, ...]`` so cmd.exe is never involved (BatBadBut).

    Only the exact shape npm generates is accepted; anything else is refused rather than run through cmd.exe.
    """
    match = _SHIM_LAUNCH.search(shim.read_text(encoding="utf-8", errors="replace"))
    if not match:
        raise CliShimUnsupported(shim.name)
    interpreter = _shim_interpreter(shim.parent, shim.name)
    return [interpreter, *_shim_argv(match.group("tail"), shim.parent, shim.name)]


def resolve_command(executable: str) -> list[str]:
    """Resolve a CLI name to an argv prefix that CreateProcess/execve can run directly.

    Raises FileNotFoundError when absent and CliShimUnsupported for a shim that would need cmd.exe.
    """
    found = shutil.which(executable)
    if not found:
        raise FileNotFoundError(executable)
    if sys.platform == "win32":
        suffix = Path(found).suffix.lower()
        if suffix in (".cmd", ".bat"):
            return _unwrap_node_shim(Path(found))
        if suffix not in (".exe", ".com"):
            raise CliShimUnsupported(Path(found).name)
    return [found]
