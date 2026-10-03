"""Locate, verify and run TLC (https://github.com/tlaplus/tlaplus), and parse what it prints.

Adopted, not written: TLC is the model checker. This module only (1) pins the released
`tla2tools.jar` by sha256 (`TOOLS.lock`), (2) runs it with the repository's temp/heap conventions and
(3) parses its text output. A missing Java or an unfetchable jar is reported as NOT_RUN by the caller,
never as a pass; a jar whose hash differs from the lock is a hard error.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import time
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCK = HERE / "TOOLS.lock"
CACHE = ROOT / ".cache" / "tla"
JAR = CACHE / "tla2tools.jar"
MIN_JAVA = 11  # tla2tools 1.7.x requires Java 11+; the reference PC has Temurin 17


class ToolError(RuntimeError):
    """The tool chain is present but wrong (hash mismatch, unusable output). Never a NOT_RUN."""


class NotRun(RuntimeError):
    """A prerequisite is missing (Java, network for the jar). Reported as NOT_RUN, never PASS."""


def load_lock() -> dict[str, Any]:
    return json.loads(LOCK.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def java_major() -> int:
    """Major version of the `java` on PATH; raises NotRun when there is none."""
    exe = shutil.which("java")
    if exe is None:
        raise NotRun("java is not on PATH")
    proc = subprocess.run([exe, "-version"], capture_output=True, text=True, timeout=60, check=False)  # noqa: S603 - fixed argv, no shell
    match = re.search(r'version "(\d+)(?:\.(\d+))?', proc.stderr + proc.stdout)
    if not match:
        raise NotRun("could not read the java version")
    major = int(match.group(1))
    return int(match.group(2) or 0) if major == 1 else major


def java_banner() -> str:
    proc = subprocess.run([shutil.which("java") or "java", "-version"], capture_output=True, text=True, timeout=60, check=False)  # noqa: S603 - fixed argv, no shell
    return (proc.stderr or proc.stdout).splitlines()[0].strip() if (proc.stderr or proc.stdout) else "unknown"


def ensure_jar(*, fetch: bool = True) -> Path:
    """Return the verified jar path. Downloads the pinned release once when `fetch` and absent."""
    lock = load_lock()
    if java_major() < MIN_JAVA:
        raise NotRun(f"java >= {MIN_JAVA} required")
    if not JAR.exists():
        if not fetch:
            raise NotRun("tla2tools.jar is not in .cache/tla (run without --no-fetch to download the pinned release)")
        CACHE.mkdir(parents=True, exist_ok=True)
        partial = JAR.with_suffix(".part")
        try:
            with urllib.request.urlopen(lock["url"], timeout=120) as response, partial.open("wb") as out:  # noqa: S310 (pinned https URL)
                shutil.copyfileobj(response, out)
        except OSError as exc:
            partial.unlink(missing_ok=True)
            raise NotRun(f"could not download tla2tools.jar ({type(exc).__name__})") from exc
        partial.replace(JAR)
    actual = sha256_file(JAR)
    if actual != lock["sha256"]:
        raise ToolError(f"tla2tools.jar sha256 {actual} does not match TOOLS.lock {lock['sha256']}")
    return JAR


# ----------------------------------------------------------------------------- value parsing

_TOKEN = re.compile(r'<<|>>|\|->|:>|@@|[\[\]{}(),]|"(?:[^"\\]|\\.)*"|-?\d+|[A-Za-z_][A-Za-z0-9_]*')


def parse_value(text: str) -> Any:
    """Parse a TLC-printed value: tuples -> tuple, records and functions -> dict, sets -> frozenset, TRUE/FALSE -> bool."""
    tokens = _TOKEN.findall(text)
    value, index = _parse(tokens, 0)
    if index != len(tokens):
        raise ValueError("trailing tokens in TLC value")
    return value


def _parse(tokens: list[str], i: int) -> tuple[Any, int]:
    tok = tokens[i]
    if tok == "<<":
        items: list[Any] = []
        i += 1
        while tokens[i] != ">>":
            value, i = _parse(tokens, i)
            items.append(value)
            if tokens[i] == ",":
                i += 1
        return tuple(items), i + 1
    if tok == "{":
        members: list[Any] = []
        i += 1
        while tokens[i] != "}":
            value, i = _parse(tokens, i)
            members.append(value)
            if tokens[i] == ",":
                i += 1
        return frozenset(members), i + 1
    if tok == "[":
        record: dict[str, Any] = {}
        i += 1
        while tokens[i] != "]":
            name = tokens[i]
            if tokens[i + 1] != "|->":
                raise ValueError("record field without |->")
            value, i = _parse(tokens, i + 2)
            record[name] = value
            if tokens[i] == ",":
                i += 1
        return record, i + 1
    if tok == "(":  # function: ( k :> v @@ k :> v )
        function: dict[Any, Any] = {}
        i += 1
        while tokens[i] != ")":
            name, i = _parse(tokens, i)
            if tokens[i] != ":>":
                raise ValueError("function entry without :>")
            function[name], i = _parse(tokens, i + 1)
            if tokens[i] == "@@":
                i += 1
        return function, i + 1
    if tok.startswith('"'):
        return json.loads(tok), i + 1
    if tok in ("TRUE", "FALSE"):
        return tok == "TRUE", i + 1
    if re.fullmatch(r"-?\d+", tok):
        return int(tok), i + 1
    raise ValueError(f"unexpected token {tok!r}")


def top_level_values(lines: Iterator[str]) -> Iterator[Any]:
    """Yield each tuple that TLC printed starting at column 0 (`PrintT` output).

    TLC pretty-prints over many lines; a value ends when its `<<`/`>>` nesting closes. Console
    messages never start with `<<`, so they are skipped."""
    buffer: list[str] = []
    depth = 0
    for line in lines:
        if not buffer and not line.startswith("<<"):
            continue
        buffer.append(line)
        for piece in _TOKEN.findall(line):
            depth += 1 if piece == "<<" else -1 if piece == ">>" else 0
        if depth == 0:
            text = "\n".join(buffer)
            buffer = []
            yield parse_value(text)


# ----------------------------------------------------------------------------- running TLC

@dataclass
class TlcRun:
    spec: str
    config: str
    returncode: int
    output: Path
    seconds: float
    version: str = ""
    generated: int = 0
    distinct: int = 0
    depth: int = 0
    result: str = "ERROR"  # PASS | VIOLATION | ERROR
    violated: str = ""  # invariant / property name
    violation_kind: str = ""
    trace: list[dict[str, Any]] = field(default_factory=list)  # variable values of each counterexample state


_VIOLATION = re.compile(r"^Error: (?:Invariant (\S+) is violated|Action property (\S+) is violated|Temporal properties were violated)")


def run_tlc(spec: Path, config: Path, work: Path, *, workers: int = 2, heap: str = "2g", timeout: int = 1800) -> TlcRun:
    """Run TLC on `spec` with `config`. Temp and state files stay inside `work` (inside the checkout)."""
    jar = ensure_jar(fetch=False)
    work.mkdir(parents=True, exist_ok=True)
    meta = work / f"states-{spec.stem}"
    shutil.rmtree(meta, ignore_errors=True)
    output = work / f"{spec.stem}.out.txt"
    cmd = ["java", "-XX:+UseParallelGC", f"-Xmx{heap}", f"-Djava.io.tmpdir={work}", f"-DTLA-Library={HERE}",
           "-cp", str(jar), "tlc2.TLC", "-workers", str(workers), "-metadir", str(meta),
           "-config", str(config), str(spec)]
    started = time.monotonic()
    with output.open("w", encoding="utf-8", newline="\n") as sink:
        proc = subprocess.run(cmd, stdout=sink, stderr=subprocess.STDOUT, cwd=work, timeout=timeout, check=False)  # noqa: S603 - fixed argv, no shell
    run = TlcRun(spec=spec.name, config=config.name, returncode=proc.returncode, output=output, seconds=round(time.monotonic() - started, 2))
    parse_summary(run)
    shutil.rmtree(meta, ignore_errors=True)
    return run


def parse_summary(run: TlcRun) -> None:
    """Fill a TlcRun from TLC's console text. Unrecognised output stays result == ERROR."""
    lines = run.output.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        m = re.match(r"^TLC2 Version (.*)$", line)
        if m and not run.version:
            run.version = m.group(1).strip()
        m = re.match(r"^(\d+) states generated, (\d+) distinct states found", line)
        if m:
            run.generated, run.distinct = int(m.group(1)), int(m.group(2))
        m = re.match(r"^The depth of the complete state graph search is (\d+)", line)
        if m:
            run.depth = int(m.group(1))
        if line.startswith("Model checking completed. No error has been found."):
            run.result = "PASS"
        m = _VIOLATION.match(line)
        if m and run.result != "VIOLATION":
            run.result = "VIOLATION"
            run.violated = m.group(1) or m.group(2) or ""
            run.violation_kind = "invariant" if m.group(1) else "action_property" if m.group(2) else "temporal"
    if run.result == "VIOLATION":
        run.trace = parse_trace(lines)
        run.depth = run.depth or len(run.trace)


def parse_trace(lines: list[str]) -> list[dict[str, Any]]:
    """Parse the counterexample: one dict of the spec variables per state."""
    states: list[dict[str, Any]] = []
    current: list[str] | None = None
    for line in lines:
        if re.match(r"^State \d+: ", line):
            if current is not None:
                states.append(_state_fields(current))
            current = []
        elif current is not None:
            if line.startswith(("Error:", "Finished in")) or re.match(r"^\d+ states generated", line):
                states.append(_state_fields(current))
                current = None
            else:
                current.append(line)
    if current is not None:
        states.append(_state_fields(current))
    return states


def _state_fields(block: list[str]) -> dict[str, Any]:
    text = "\n".join(block).strip()
    fields: dict[str, Any] = {}
    for chunk in re.split(r"(?m)^/\\ ", text):
        if not chunk.strip():
            continue
        name, _, value = chunk.partition(" = ")
        fields[name.strip()] = parse_value(value)
    return fields
