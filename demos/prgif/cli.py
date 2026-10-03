"""Argument parsing and orchestration for `python -m demos pr-gif ...`.

Exit codes follow `python -m demos`: 0 done, 1 failure, 2 usage, 3 NOT_RUN (Chrome, Playwright, ffmpeg or a
scenario's lanes missing; never reported as a pass).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from demos.lib import BrowserUnavailableError, Scene
from demos.prgif import browser, encode, publish, terminal
from demos.prgif.fit import DoesNotFitError, Limits
from demos.prgif.record import Take, record
from demos.scenarios.registry import ROOT

EXIT_FAIL, EXIT_USAGE, EXIT_NOT_RUN = 1, 2, 3


class _NotRunError(RuntimeError):
    pass


def add_parser(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    gif = sub.add_parser("pr-gif", help="record, convert and publish GIFs for pull requests")
    modes = gif.add_subparsers(dest="mode", required=True)

    web = modes.add_parser("browser", help="record a real Studio interaction")
    web.add_argument("--scenario", required=True, help="scenario key, `studio` (ephemeral Studio) or a URL")
    web.add_argument("--step", action="append", default=[], help="one step line (repeatable); see README")
    web.add_argument("--steps", type=Path, help="file with one step per line")
    web.add_argument("--viewport", default="1280x800", help="WIDTHxHEIGHT of the recorded page")
    web.add_argument("--headed", action="store_true")
    _common(web)

    term = modes.add_parser("terminal", help="run commands and record their real output")
    term.add_argument("--cmd", action="append", required=True, help="command to run (repeatable, in order)")
    term.add_argument("--cwd", type=Path, default=Path.cwd())
    term.add_argument("--title", default="", help="window title (default: the working directory name)")
    term.add_argument("--prompt", default="$")
    term.add_argument("--size", default="1200x720", help="WIDTHxHEIGHT of the terminal page")
    term.add_argument("--timeout", type=float, default=300.0, help="seconds per command before it is killed")
    term.add_argument("--max-gap", type=float, default=1.0, help="longest pause kept, in seconds")
    term.add_argument("--headed", action="store_true")
    _common(term)

    conv = modes.add_parser("convert", help="convert an existing video to a GIF within the limits")
    conv.add_argument("video", type=Path)
    conv.add_argument("--trim-start", type=float, default=0.0)
    _common(conv)

    pub = modes.add_parser("publish", help="commit a GIF to the orphan pr-media branch and push it")
    pub.add_argument("file", type=Path)
    pub.add_argument("--pr", type=int, required=True)
    pub.add_argument("--name", help="file name under pr/<n>/ (default: the file's name)")
    pub.add_argument("--remote", default="origin")
    pub.add_argument("--repo", type=Path, default=Path.cwd())


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--out", type=Path, required=True, help="GIF to write")
    parser.add_argument("--max-seconds", type=float, default=Limits().max_seconds)
    parser.add_argument("--max-width", type=int, default=Limits().max_width)
    parser.add_argument("--max-speedup", type=float, default=Limits().max_speedup)


def _limits(args: argparse.Namespace) -> Limits:
    limits = Limits(max_width=min(args.max_width, Limits().max_width),
                    max_seconds=min(args.max_seconds, Limits().max_seconds), max_speedup=args.max_speedup)
    if limits.max_speedup < 1:
        raise ValueError("--max-speedup must be at least 1")
    return limits


def _size(text: str) -> tuple[int, int]:
    width, _, height = text.lower().partition("x")
    if not (width.isdigit() and height.isdigit()):
        raise ValueError(f"expected WIDTHxHEIGHT, got {text!r}")
    return int(width), int(height)


def run(args: argparse.Namespace) -> int:
    handlers: dict[str, Callable[[argparse.Namespace], int]] = {
        "browser": _browser, "terminal": _terminal, "convert": _convert, "publish": _publish,
    }
    try:
        return handlers[args.mode](args)
    except (_NotRunError, encode.ToolMissingError, browser.ScenarioBlockedError, BrowserUnavailableError) as error:
        print(f"NOT_RUN {error}")
        return EXIT_NOT_RUN
    except DoesNotFitError as error:
        print(f"FAIL {error}")
        return EXIT_FAIL
    except ValueError as error:  # includes StepError: a bad step line or option is a usage error
        print(f"usage: {error}", file=sys.stderr)
        return EXIT_USAGE
    except (publish.PublishError, RuntimeError) as error:
        print(f"FAIL {error}")
        return EXIT_FAIL


def _preflight(*, needs_browser: bool) -> None:
    missing = encode.missing_tools()
    if needs_browser and importlib.util.find_spec("playwright") is None:
        missing.append("playwright (pip install -e .[demos])")
    if missing:
        raise _NotRunError(f"prerequisite missing: {', '.join(missing)}")


def _scratch() -> Path:
    base = ROOT / ".tmp"
    base.mkdir(exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="pr-gif-", dir=base))


def _finish(take: Take, out: Path, limits: Limits, extra: dict[str, object], scratch: Path | None = None) -> int:
    try:
        report = encode.video_to_gif(take.video, out, limits=limits, trim_start_s=take.lead_in_s)
    finally:
        if scratch is not None:
            shutil.rmtree(scratch, ignore_errors=True)  # the intermediate video; the GIF is the product
    summary = report.summary() | extra | {"skipped": list(take.skipped)}
    print(json.dumps(summary, indent=2))
    if report.timing.cut:
        print(f"WARN the recording was longer than {limits.max_seconds * limits.max_speedup:.0f}s of source; "
              "its tail was cut. Shorten the story rather than publishing a GIF that stops mid-action.")
    print(f"OK {out} ({report.fit.size} bytes, {report.fit.chosen.width}px, {report.fit.chosen.fps} fps)")
    return 0


def _browser(args: argparse.Namespace) -> int:
    lines = list(args.step) + (browser.read_steps_file(args.steps) if args.steps else [])
    server_context, act = browser.plan(args.scenario, browser.parse_steps(lines))
    limits, viewport = _limits(args), _size(args.viewport)
    _preflight(needs_browser=True)
    scratch = _scratch()
    with server_context as server:
        take = record(scratch, lambda scene: act(scene, server), viewport=viewport, headed=args.headed)
    return _finish(take, args.out, limits, {"source": args.scenario}, scratch)


def _terminal(args: argparse.Namespace) -> int:
    limits, size = _limits(args), _size(args.size)
    _preflight(needs_browser=True)
    cwd = args.cwd.resolve()
    runs = [terminal.run_command(cmd, cwd=cwd, timeout_s=args.timeout) for cmd in args.cmd]
    for item in runs:
        print(f"ran (exit {item.exit_code}, {item.seconds:.1f}s, {len(item.lines)} lines): {item.command}")
    events = terminal.build_timeline(runs, terminal.Pacing(max_gap_s=args.max_gap))
    scratch = _scratch()
    page = scratch / "terminal.html"
    page.write_text(terminal.render_page(events, title=args.title or cwd.name, prompt=args.prompt),
                    encoding="utf-8")
    total_ms = events[-1].at_ms

    def play(scene: Scene) -> None:
        scene.page.goto(page.as_uri())
        scene.page.evaluate("window.__start()")
        scene.page.wait_for_function("window.__done === true", timeout=total_ms + 30_000)

    take = record(scratch, play, viewport=size, headed=args.headed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    transcript_path = args.out.with_suffix(".transcript.json")
    terminal.write_transcript(transcript_path, runs, cwd)
    return _finish(take, args.out, limits, {"transcript": str(transcript_path),
                                            "exit_codes": [r.exit_code for r in runs]}, scratch)


def _convert(args: argparse.Namespace) -> int:
    limits = _limits(args)
    _preflight(needs_browser=False)
    return _finish(Take(args.video, args.trim_start, ()), args.out, limits, {"source": str(args.video)})


def _publish(args: argparse.Namespace) -> int:
    result = publish.publish(args.file, args.pr, repo=args.repo.resolve(), name=args.name, remote=args.remote)
    print(f"OK published {result.path} at {result.commit} on {publish.BRANCH}")
    if result.url:
        print(result.url)
        print(f"embed: ![{Path(result.path).stem}]({result.url})")
    else:
        print("the remote is not on GitHub, so there is no raw URL")
    return 0
