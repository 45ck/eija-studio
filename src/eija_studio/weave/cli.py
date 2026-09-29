"""``eija index | lint | impact``: the weave commands. Read-only, offline, no workspace or provider needed.

Only ``index --write-baseline`` writes anything (the baseline of accepted binding digests); it is a human decision
and is not exposed to agents.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from eija_studio import __version__
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACK_FILE, Pack, default_location, load_pack

from .impact import UnknownTarget, impact
from .index import Graph, build_index
from .metamodel import WeaveUnavailable
from .rules import LintResult, exit_status, lint, load_baseline, to_sarif, write_baseline
from .sarif import dumps_sarif

BASELINE_NAME = Path(".eija") / "weave-baseline.json"


def _load(args: argparse.Namespace) -> tuple[Path, Pack, Graph]:
    location = Path(args.pack) if args.pack else default_location()
    pack_file = location / PACK_FILE if location.is_dir() else location
    root = Path(args.root).resolve()
    pack = load_pack(location)
    return root, pack, build_index(root, pack, pack_file)


def _baseline_path(args: argparse.Namespace, root: Path) -> Path:
    return Path(args.baseline) if args.baseline else root / BASELINE_NAME


def _emit(value: object) -> None:
    sys.stdout.write(json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def index_command(args: argparse.Namespace) -> int:
    root, _pack, graph = _load(args)
    summary = {"pack": graph.pack_id, "root_hash": graph.root_hash, **graph.counts()}
    if args.write_baseline:
        summary["baseline"] = {"path": str(_baseline_path(args, root)), "bindings": write_baseline(_baseline_path(args, root), graph)}
    if args.json:
        summary |= {"gap_list": graph.gaps, "graph": graph.rows()}
    _emit(summary)
    return 0


def _summary(result: LintResult) -> dict[str, object]:
    return {"verdict": result.verdict, "verdicts": result.verdicts, "root_hash": result.root_hash,
            "findings": [{"rule": f["rule"], "uri": f["uri"], "args": f["args"]} for f in result.findings],
            "not_run": result.not_run, "extraction_gaps": result.gaps}


def lint_command(args: argparse.Namespace) -> int:
    root, _pack, graph = _load(args)
    result = lint(graph, load_baseline(_baseline_path(args, root)))
    if args.sarif:
        sys.stdout.write(dumps_sarif(to_sarif(root, result, __version__)))
    else:
        _emit(_summary(result))
    return exit_status(result, os.environ.get("EIJA_ALLOW_NOT_RUN") == "1")


def impact_command(args: argparse.Namespace) -> int:
    _root, _pack, graph = _load(args)
    try:
        report = impact(graph, args.target)
    except UnknownTarget as error:
        raise DomainError("TARGET_UNKNOWN", str(error)) from None
    _emit(report)
    return 0 if report["certificate"] == "accepted" else 2


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="Repository to index (default: the current directory)")
    parser.add_argument("--pack", help="Domain pack directory or pack.json (default: $EIJA_PACK or packs/default.json)")
    parser.add_argument("--baseline", help=f"Accepted binding digests (default: ROOT/{BASELINE_NAME.as_posix()})")


def add_parsers(subs: argparse._SubParsersAction) -> None:
    index = subs.add_parser("index", help="Index a repository through a domain pack; print counts and the root hash")
    _common(index)
    index.add_argument("--json", action="store_true", help="Also print every node and edge row")
    index.add_argument("--write-baseline", action="store_true", help="Accept the current binding digests (a human decision)")
    lint_p = subs.add_parser("lint", help="Check the index: WV-001 dangling, WV-002 ill-typed, WV-005 suspect binding (exit 0 PASS, 1 FAIL, 2 NOT_RUN)")
    _common(lint_p)
    lint_p.add_argument("--sarif", action="store_true", help="Print SARIF 2.1.0 instead of the summary")
    impact_p = subs.add_parser("impact", help="What a change to a term, state, transition, role or law affects, with witness paths")
    _common(impact_p)
    impact_p.add_argument("target", help="A node id, state:X, transition:X, role:X, law:X or a term id")


def _guarded(handler):
    def run(args: argparse.Namespace) -> int:
        try:
            return handler(args)
        except WeaveUnavailable as error:
            raise DomainError("WEAVE_UNAVAILABLE", str(error)) from None
    return run


COMMANDS = {"index": _guarded(index_command), "lint": _guarded(lint_command), "impact": _guarded(impact_command)}
