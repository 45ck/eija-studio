"""Run real commands, capture their real output with timing, and replay it as a terminal page for recording.

Nothing on the page is invented: every output line is a line the command printed (ANSI colour codes removed,
carriage-return progress collapsed to its final state), in the order printed. Only time is edited: a pause
longer than `max_gap_s` is shortened to it, so a slow command does not produce a GIF of an idle screen. The
captured transcript (real offsets, exit codes) is written next to the GIF so a reviewer can audit it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*(?:\x07|\x1b\\)")


@dataclass(frozen=True)
class Line:
    t: float  # seconds since the command started (measured)
    text: str


@dataclass(frozen=True)
class CommandRun:
    command: str
    lines: tuple[Line, ...]
    exit_code: int
    seconds: float
    timed_out: bool = False


@dataclass(frozen=True)
class Pacing:
    """How the replay is paced. Only pauses are shortened; the output is never altered."""

    pre_type_ms: int = 500
    char_ms: int = 38
    max_type_ms: int = 1800
    enter_ms: int = 350
    max_gap_s: float = 1.0
    between_ms: int = 900
    hold_ms: int = 2600


@dataclass(frozen=True)
class Event:
    at_ms: int
    kind: str  # prompt | type | out | exit | end
    text: str = ""
    char_ms: int = 0


def clean(raw: str) -> str:
    """Strip ANSI escapes and keep only the final state of a carriage-return progress line."""
    text = _ANSI.sub("", raw.rstrip("\r\n"))
    if "\r" in text:
        text = text.rsplit("\r", 1)[-1]
    return text.expandtabs(4)


def _child_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(NO_COLOR="1", PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8", TERM="dumb")
    env.pop("FORCE_COLOR", None)
    return env


def run_command(command: str, *, cwd: Path, timeout_s: float) -> CommandRun:
    """Run `command` through the platform shell (the caller typed it, as in a terminal) and time each line."""
    start = time.monotonic()
    # shell=True on purpose: the command is the caller's own terminal command, recorded as typed.
    process = subprocess.Popen(  # noqa: S602
        command, shell=True, cwd=cwd, env=_child_env(), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    fired = threading.Event()

    def kill() -> None:
        fired.set()
        process.kill()

    timer = threading.Timer(timeout_s, kill)
    timer.start()
    lines: list[Line] = []
    try:
        stdout = process.stdout
        if stdout is None:  # pragma: no cover - guaranteed by stdout=PIPE
            raise RuntimeError("no stdout pipe")
        for raw in iter(stdout.readline, b""):
            lines.append(Line(round(time.monotonic() - start, 3), clean(raw.decode("utf-8", "replace"))))
        code = process.wait()
    finally:
        timer.cancel()
    return CommandRun(command, tuple(lines), code, round(time.monotonic() - start, 3), fired.is_set())


@dataclass
class _Clock:
    now_ms: int = 0
    events: list[Event] = field(default_factory=list)

    def emit(self, kind: str, text: str = "", char_ms: int = 0) -> None:
        self.events.append(Event(self.now_ms, kind, text, char_ms))

    def advance(self, ms: float) -> None:
        self.now_ms += max(0, int(ms))


def _replay_command(clock: _Clock, run: CommandRun, pacing: Pacing) -> None:
    clock.emit("prompt")
    clock.advance(pacing.pre_type_ms)
    char_ms = min(pacing.char_ms, pacing.max_type_ms // max(1, len(run.command)))
    clock.emit("type", run.command, char_ms)
    clock.advance(char_ms * len(run.command) + pacing.enter_ms)
    previous = 0.0
    for line in run.lines:
        clock.advance(min(line.t - previous, pacing.max_gap_s) * 1000)
        previous = line.t
        clock.emit("out", line.text)
    clock.advance(min(run.seconds - previous, pacing.max_gap_s) * 1000)
    clock.emit("exit", "timed out" if run.timed_out else str(run.exit_code))
    clock.advance(pacing.between_ms)


def build_timeline(runs: Sequence[CommandRun], pacing: Pacing = Pacing()) -> list[Event]:
    clock = _Clock()
    for run in runs:
        _replay_command(clock, run, pacing)
    clock.emit("prompt")
    clock.advance(pacing.hold_ms)
    clock.emit("end")
    return clock.events


def transcript(runs: Sequence[CommandRun], cwd: Path) -> dict[str, object]:
    return {"cwd": str(cwd), "runs": [asdict(run) for run in runs]}


def render_page(events: Sequence[Event], *, title: str, prompt: str) -> str:
    """A self-contained page. Output is inserted with textContent, so printed text can never become markup."""
    payload = json.dumps({"events": [asdict(e) for e in events], "prompt": prompt, "title": title})
    return _PAGE.replace("__DATA__", payload.replace("</", "<\\/"))


def write_transcript(path: Path, runs: Sequence[CommandRun], cwd: Path) -> None:
    path.write_text(json.dumps(transcript(runs, cwd), indent=2) + "\n", encoding="utf-8")


# Colours are fixed (a GIF has no colour scheme): a dark terminal inside a mid-grey frame reads as a bounded
# window on both GitHub's light and dark backgrounds.
_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>terminal</title><style>
html,body{margin:0;height:100%;background:#57606a}
body{display:flex;align-items:stretch;justify-content:stretch;padding:18px;box-sizing:border-box}
.win{flex:1;display:flex;flex-direction:column;background:#0d1117;border:1px solid #8c959f;border-radius:10px;
  overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.35)}
.bar{display:flex;align-items:center;gap:8px;padding:10px 14px;background:#161b22;border-bottom:1px solid #30363d;
  color:#8b949e;font:13px system-ui,sans-serif}
.dot{width:12px;height:12px;border-radius:50%}
.title{margin-left:10px}
#screen{flex:1;overflow:hidden;padding:14px 18px;color:#e6edf3;
  font:15px/1.45 "Cascadia Mono",Consolas,"DejaVu Sans Mono",Menlo,monospace;white-space:pre-wrap;word-break:break-all}
.prompt{color:#7ee787;font-weight:600}
.cmd{color:#ffffff;font-weight:600}
.exit{color:#ff7b72}
.caret{display:inline-block;width:.6em;background:#e6edf3;animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
</style></head><body><div class="win"><div class="bar">
<span class="dot" style="background:#ff5f57"></span><span class="dot" style="background:#febc2e"></span>
<span class="dot" style="background:#28c840"></span><span class="title" id="title"></span></div>
<div id="screen"></div></div>
<script>
const DATA = __DATA__;
const screen = document.getElementById('screen');
document.getElementById('title').textContent = DATA.title;
const caret = document.createElement('span'); caret.className = 'caret'; caret.textContent = ' ';
let line = null;
function newLine(){ line = document.createElement('div'); screen.appendChild(line); screen.scrollTop = screen.scrollHeight; }
function addSpan(cls, text){ const s = document.createElement('span'); s.className = cls; s.textContent = text;
  line.appendChild(s); return s; }
const handlers = {
  prompt(){ newLine(); addSpan('prompt', DATA.prompt + ' '); line.appendChild(caret); },
  type(e){ const s = addSpan('cmd', ''); line.appendChild(caret); let i = 0;
    const step = () => { s.textContent = e.text.slice(0, ++i); if (i < e.text.length) setTimeout(step, e.char_ms); };
    if (e.text.length) step(); },
  out(e){ caret.remove(); newLine(); line.textContent = e.text || ' '; screen.scrollTop = screen.scrollHeight; },
  exit(e){ caret.remove(); if (e.text !== '0') { newLine(); addSpan('exit', '[exit ' + e.text + ']'); } },
  end(){ window.__done = true; },
};
window.__done = false;
window.__start = () => { for (const e of DATA.events) setTimeout(() => handlers[e.kind](e), e.at_ms); };
</script></body></html>
"""
