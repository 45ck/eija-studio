"""Run an Alloy model as a pinned, sandboxed-by-convention external process and report PASS, FAIL or NOT_RUN.

    python graph/formal/run_alloy.py graph/formal/alloy/certificates.als [--solver sat4j]
    EIJA_ALLOY_JAR=path/to/org.alloytools.alloy.dist.jar python graph/formal/run_alloy.py MODEL.als

Rules (they mirror the tla and bend lanes: exact sentinel plus exit code, pinned digest, NOT_RUN when absent):

* The jar must have the sha256 pinned in TOOLS.lock, otherwise NOT_RUN ("untrusted tool"), never a run.
* Java missing, jar missing or a timeout give NOT_RUN. A timeout is not a verdict.
* PASS only if the process exits 0, Alloy's receipt lists exactly the commands found in the model text, and
  every command's outcome equals its ``expect`` clause (``expect 0``: no instance, i.e. no counterexample
  within the scope; ``expect 1``: an instance exists). A command without an ``expect`` clause is FAIL: a
  model must say what it expects, or a vacuous run could pass.
* Output is canonical JSON containing the model's sha256 (LF-folded) and the per-command outcome. Alloy's
  own receipt carries timestamps, time zone and durations; none of them is copied.
* Every model must declare its bound. ``UNSAT`` here means: no counterexample within that scope.

Exit codes: 0 PASS, 1 FAIL, 2 NOT_RUN.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCK = json.loads((HERE / "TOOLS.lock").read_text(encoding="utf-8"))["alloy"]
DEFAULT_JARS = [ROOT / ".tmp" / "tools" / "alloy-6.2.0.jar", HERE / "tools" / "alloy-6.2.0.jar"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def declared_commands(text: str) -> list[dict]:
    """Commands in source order: name (or None for an anonymous block), kind, expect. Comments stripped."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(//|--)[^\n]*", "", text)
    out = []
    for m in re.finditer(r"^\s*(check|run)\b([^\n]*)$", text, re.M):
        rest = m.group(2)
        expect = re.search(r"\bexpect\s+(\d+)\s*$", rest)
        name = re.match(r"\s+(\w+)", rest)
        out.append({"kind": m.group(1), "name": name.group(1) if name and name.group(1) != "for" else None,
                    "expect": int(expect.group(1)) if expect else None})
    return out


def not_run(reason: str) -> dict:
    return {"verdict": "NOT_RUN", "reason": reason}


def run(model: Path, timeout: int = 900, solver: str | None = None) -> dict:
    jar_env = os.environ.get("EIJA_ALLOY_JAR")
    jars = [Path(jar_env)] if jar_env else DEFAULT_JARS
    jar = next((j for j in jars if j.is_file()), None)
    if jar is None:
        return not_run("Alloy jar not found (set EIJA_ALLOY_JAR or place it under .tmp/tools/)")
    if sha256_file(jar) != LOCK["sha256"]:
        return not_run("Alloy jar sha256 differs from TOOLS.lock: untrusted tool")
    java = shutil.which("java")
    if java is None:
        return not_run("java not found")
    commands = declared_commands(model.read_text(encoding="utf-8"))
    if not commands:
        return {"verdict": "FAIL", "reason": "the model declares no check or run command"}
    if any(c["expect"] is None for c in commands):
        return {"verdict": "FAIL", "reason": "every command must carry an expect clause"}
    tmp = ROOT / ".tmp"
    tmp.mkdir(exist_ok=True)
    out_dir = tmp / "alloy-run" / model.stem
    shutil.rmtree(out_dir, ignore_errors=True)  # a stale receipt must never be read as this run's
    env = dict(os.environ, TMP=str(tmp), TEMP=str(tmp))
    cmd = [java, "-jar", str(jar), "exec", "-f", "-q", "-s", solver or LOCK["solver"], "-t", "json", "-o", str(out_dir), str(model)]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout, env=env, cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        return not_run(f"timeout after {timeout}s: no verdict")
    detail = [ln.strip() for ln in (proc.stdout + proc.stderr).decode("utf-8", "replace").splitlines()
              if ln.strip() and not ln.startswith("c ")][:3]
    receipt_path = out_dir / "receipt.json"
    if proc.returncode != 0 and not receipt_path.is_file():
        return {"verdict": "FAIL", "reason": f"alloy exited {proc.returncode} without a receipt", "detail": detail}
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    got = receipt["commands"]
    if len(got) != len(commands):
        return {"verdict": "FAIL", "reason": f"receipt lists {len(got)} commands, the model declares {len(commands)}"}
    results = []
    for (key, entry), declared in zip(got.items(), commands, strict=False):
        found = bool(entry.get("solution"))
        expected = declared["expect"]
        results.append({"command": declared["name"] or key, "kind": entry["type"], "instance_found": found,
                        "expect": expected, "as_expected": found == bool(expected)})
    ok = all(r["as_expected"] for r in results) and proc.returncode == 0  # Alloy itself exits 1 on an expect mismatch
    return {"verdict": "PASS" if ok else "FAIL", "alloy_exit_code": proc.returncode, "detail": detail if not ok else [],
            "model_sha256_lf": model_digest(model), "alloy": LOCK["release"], "solver": solver or LOCK["solver"], "commands": results,
            "sentinel": f"ALLOY COMMANDS AS EXPECTED {sum(r['as_expected'] for r in results)}/{len(results)}",
            "meaning": "expect 0: no counterexample within the declared scope (bounded, not a proof); expect 1: an instance exists"}


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    solver = None
    if "--solver" in argv:
        i = argv.index("--solver")
        solver = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    result = run(Path(argv[0]), solver=solver)
    sys.stdout.buffer.write((json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + chr(10)).encode("ascii"))
    return {"PASS": 0, "FAIL": 1, "NOT_RUN": 2}[result["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
