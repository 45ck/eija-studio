"""`python -m demos ...`: list, validate and run scripted demo scenarios (ADR-0047, ADR-0048)."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import sys
import time
from pathlib import Path

from demos.scenarios.registry import ROOT, SCENARIOS, check_consistency, render_markdown

REGISTRY_MD = ROOT / "demos" / "scenarios" / "REGISTRY.md"
OUTPUT = ROOT / "demos" / "output"
RECORDINGS = ROOT / "demos" / "recordings"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m demos", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show scenarios and their status")

    reg = sub.add_parser("registry", help="check or regenerate scenarios/REGISTRY.md")
    mode = reg.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail on drift or inconsistency")
    mode.add_argument("--write", action="store_true", help="regenerate REGISTRY.md")

    run = sub.add_parser("run", help="run one scenario against a real ephemeral Studio")
    run.add_argument("key")
    run.add_argument("--dry-run", action="store_true", help="same interactions, no video/overlay/delays")
    run.add_argument("--headed", action="store_true", help="show the browser window while recording")
    run.add_argument("--seed", type=int, default=0, help="typing-cadence seed (recordings are repeatable)")
    args = parser.parse_args(argv)

    if args.command == "list":
        for s in SCENARIOS:
            print(f"{s.status:<22} {s.key:<30} waits for: {', '.join(s.depends_on) or '-'}")
        return 0
    if args.command == "registry":
        return _registry(check=args.check)
    return _run(args.key, dry_run=args.dry_run, headed=args.headed, seed=args.seed)


def _registry(*, check: bool) -> int:
    expected = render_markdown()
    if not check:
        REGISTRY_MD.write_bytes(expected.encode("utf-8"))
        print(f"wrote {REGISTRY_MD.relative_to(ROOT)}")
        return 0
    problems = check_consistency()
    actual = REGISTRY_MD.read_bytes().decode("utf-8") if REGISTRY_MD.exists() else ""
    if actual != expected:
        problems.append("REGISTRY.md is out of date: run `python -m demos registry --write`")
    for problem in problems:
        print(f"FAIL {problem}")
    if not problems:
        print(f"OK {len(SCENARIOS)} scenarios consistent with the code")
    return 1 if problems else 0


def _move_replacing(source: Path, destination: Path, *, attempts: int = 20) -> None:
    """Move `source` over `destination`, retrying: on Windows the browser, an indexer or antivirus can
    hold either file for a moment after the recording context closes (WinError 5/32)."""
    for attempt in range(attempts):
        try:
            destination.unlink(missing_ok=True)
            source.replace(destination)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.5)


def _run(key: str, *, dry_run: bool, headed: bool, seed: int) -> int:
    scenario = next((s for s in SCENARIOS if s.key == key), None)
    if scenario is None:
        print(f"unknown scenario {key!r}; try `python -m demos list`", file=sys.stderr)
        return 2
    if scenario.status == "blocked":
        print(f"NOT_RUN {key}: blocked on lane(s) {', '.join(scenario.depends_on)} (ADR-0048)")
        return 3
    try:
        from demos.lib import Recorder, ephemeral_eija_server
    except ImportError as error:  # playwright missing is a missing prerequisite, not a pass
        print(f"NOT_RUN prerequisite missing: {error}. Install with `pip install -e \".[demos]\"`.")
        return 3

    module = importlib.import_module(scenario.module)
    out_dir = OUTPUT / key
    before = set(out_dir.glob("*.webm")) if out_dir.exists() else set()
    with ephemeral_eija_server() as server, Recorder(headless=not headed).session(
        out_dir, dry_run=dry_run, seed=seed
    ) as scene:
        module.run(scene, server)
        skipped = list(scene.skipped)

    result = {"scenario": key, "mode": "dry-run" if dry_run else "record",
              "status": "PARTIAL" if skipped else "PASS", "skipped": skipped}
    if not dry_run:
        new = sorted(set(out_dir.glob("*.webm")) - before, key=lambda p: p.stat().st_mtime)
        if not new:
            print("FAIL no video was produced")
            return 1
        final = OUTPUT / f"{key}.webm"
        final.parent.mkdir(parents=True, exist_ok=True)
        _move_replacing(new[-1], final)
        result["video"] = str(final.relative_to(ROOT))
        result["video_sha256"] = hashlib.sha256(final.read_bytes()).hexdigest()
        result["video_bytes"] = final.stat().st_size
        result["platform"] = f"{platform.system()} {platform.release()} / Python {platform.python_version()}"
        RECORDINGS.mkdir(parents=True, exist_ok=True)
        (RECORDINGS / f"{key}.json").write_bytes((json.dumps(result, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
