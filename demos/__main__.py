"""`python -m demos ...`: list, validate and run scripted demo scenarios (ADR-0047, ADR-0048).

Exit codes: 0 PASS or PARTIAL (a printed PARTIAL line lists skipped acts), 1 failure, 2 usage, 3 NOT_RUN
(blocked scenario, or Playwright/Chrome unavailable: never reported as a pass).
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
import time
from pathlib import Path

from demos.lib import BrowserUnavailableError, Recorder, ephemeral_eija_server
from demos.manifest import build_manifest, write_manifest
from demos.prgif import cli as pr_gif
from demos.scenarios.registry import (
    ROOT,
    SCENARIOS,
    Scenario,
    check_consistency,
    manifest_warnings,
    render_markdown,
)

REGISTRY_MD = ROOT / "demos" / "scenarios" / "REGISTRY.md"
OUTPUT = ROOT / "demos" / "output"
EXIT_FAIL, EXIT_USAGE, EXIT_NOT_RUN = 1, 2, 3


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "list":
        for s in SCENARIOS:
            print(f"{s.status:<22} {s.key:<30} waits for: {', '.join(s.waits_for) or '-'}")
        return 0
    if args.command == "registry":
        return _registry(check=args.check)
    if args.command == "pr-gif":
        return pr_gif.run(args)
    return _run(args.key, dry_run=args.dry_run, headed=args.headed, seed=args.seed)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m demos", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show scenarios and their status")

    reg = sub.add_parser("registry", help="check or regenerate scenarios/REGISTRY.md")
    mode = reg.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail on drift, inconsistency or a bad manifest")
    mode.add_argument("--write", action="store_true", help="regenerate REGISTRY.md")

    run = sub.add_parser("run", help="run one scenario against a real ephemeral Studio")
    run.add_argument("key")
    run.add_argument("--dry-run", action="store_true", help="same interactions, no video/overlay/delays")
    run.add_argument("--headed", action="store_true", help="show the browser window while recording")
    run.add_argument(
        "--seed", type=int, default=0,
        help="seeds the typing cadence ONLY; recordings are not otherwise repeatable "
             "(timing, encoder and Studio state vary)",
    )
    pr_gif.add_parser(sub)  # GIFs for pull requests (ADR-0142, docs/engineering/PR-STANDARD.md)
    return parser


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
    for note in manifest_warnings():
        print(f"WARN {note}")
    if not problems:
        print(f"OK {len(SCENARIOS)} scenarios consistent with the code")
    return EXIT_FAIL if problems else 0


def _move_replacing(source: Path, destination: Path, *, attempts: int = 20, delay_s: float = 0.5) -> None:
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
            time.sleep(delay_s)


def _not_run(reason: str) -> int:
    print(f"NOT_RUN {reason}")
    return EXIT_NOT_RUN


def _blocker(scenario: Scenario) -> str | None:
    """Why this scenario cannot run here (a NOT_RUN reason), or None."""
    if scenario.status == "blocked":
        return f"{scenario.key}: blocked on lane(s) {', '.join(scenario.waits_for)} (ADR-0048)"
    if scenario.status == "unscripted":
        return f"{scenario.key}: no scenario script exists yet (every lane it needs has landed; ADR-0048)"
    # The harness imports Playwright lazily, so a missing package never fails at import time: check up front.
    if importlib.util.find_spec("playwright") is None:
        return f"{scenario.key}: prerequisite missing (playwright). Install with pip install -e .[demos]"
    return None


def _run(key: str, *, dry_run: bool, headed: bool, seed: int) -> int:
    scenario = next((s for s in SCENARIOS if s.key == key), None)
    if scenario is None:
        print(f"unknown scenario {key!r}; try `python -m demos list`", file=sys.stderr)
        return EXIT_USAGE
    blocker = _blocker(scenario)
    if blocker:
        return _not_run(blocker)
    try:
        skipped, new_video = _execute(scenario, dry_run=dry_run, headed=headed, seed=seed)
    except BrowserUnavailableError as error:
        # Only the browser LAUNCH maps to NOT_RUN; an error raised while a scenario runs is a failure.
        return _not_run(f"{key}: prerequisite missing ({error}). Playwright drives the installed Chrome.")
    return _report(key, dry_run=dry_run, skipped=skipped, new_video=new_video)


def _report(key: str, *, dry_run: bool, skipped: list[str], new_video: Path | None) -> int:
    result: dict[str, object] = {
        "scenario": key, "mode": "dry-run" if dry_run else "record",
        "status": "PARTIAL" if skipped else "PASS", "skipped": skipped,
    }
    if not dry_run:
        if new_video is None:
            print("FAIL no video was produced")
            return EXIT_FAIL
        manifest = _publish_recording(key, new_video, skipped)
        result.update(video=manifest["video"], video_sha256=manifest["video_sha256"])
    print(json.dumps(result, indent=2))
    if skipped:
        print(f"PARTIAL {key}: {len(skipped)} act(s) not exercised (exit 0; not a full pass):")
        for reason in skipped:
            print(f"  - {reason}")
    else:
        print(f"PASS {key}")
    return 0


def _execute(scenario: Scenario, *, dry_run: bool, headed: bool, seed: int) -> tuple[list[str], Path | None]:
    """Run against a real ephemeral Studio; returns (skipped acts, newly recorded video or None)."""
    module = importlib.import_module(scenario.module)
    out_dir = OUTPUT / scenario.key  # created only when recording: a dry run leaves no files behind
    before = set(out_dir.glob("*.webm")) if out_dir.exists() else set()
    with ephemeral_eija_server() as server, Recorder(headless=not headed).session(
        out_dir, dry_run=dry_run, seed=seed
    ) as scene:
        module.run(scene, server)
        skipped = list(scene.skipped)
    if dry_run:
        return skipped, None
    new = sorted(set(out_dir.glob("*.webm")) - before, key=lambda p: p.stat().st_mtime)
    return skipped, (new[-1] if new else None)


def _publish_recording(key: str, new_video: Path, skipped: list[str]) -> dict[str, object]:
    """Move the take to demos/output/<key>.webm and write its committed manifest."""
    final = OUTPUT / f"{key}.webm"
    _move_replacing(new_video, final)
    manifest = build_manifest(key, skipped=skipped, video=final)
    write_manifest(key, manifest)
    return manifest


if __name__ == "__main__":
    raise SystemExit(main())
