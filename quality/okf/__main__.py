"""``python -m quality.okf {sync,check,review}``: generate, gate and review the OKF bundle."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import codelink as cl
from .build import reorder, build, write
from .checks import CHECKS, format_report, run_checks
from .pages import Repo, dump_frontmatter, split_page

ROOT = Path(__file__).resolve().parents[2]


def cmd_sync(repo: Repo, _args: argparse.Namespace) -> int:
    bundle = build(repo)
    changed = write(repo, bundle)
    for note in bundle.notes:
        print(f"note: {note}")
    print(f"okf sync: {len(bundle.files)} files, {len(changed)} written")
    return 0


def cmd_check(repo: Repo, args: argparse.Namespace) -> int:
    only = tuple(args.only.split(",")) if args.only else CHECKS
    unknown = set(only) - set(CHECKS)
    if unknown:
        print(f"unknown check(s): {sorted(unknown)}; choose from {CHECKS}", file=sys.stderr)
        return 2
    report = run_checks(repo, only)
    print(format_report(report))
    return 0 if report.ok else 1


def cmd_review(repo: Repo, args: argparse.Namespace) -> int:
    """Record a `verified` event on pages whose linked sources still match their hashes.

    This records that *someone or something confirmed the page against its sources at the stated time*.
    The time is an explicit argument, never read from a clock, so the command is reproducible.
    """
    status = 0
    for name in args.pages:
        path = repo.bundle / name
        if not path.is_file():
            print(f"{name}: no such page", file=sys.stderr)
            status = 1
            continue
        meta, body = split_page(path.read_bytes().decode("utf-8").replace("\r\n", "\n"))
        stale = [e["resource"] for e in meta.get("sources") or []
                 if e["resource"].startswith(cl.SCHEME)
                 and cl.digest(repo.root, cl.parse_uri(e["resource"]), e.get("hash_method", "")) != e.get("sha256")]
        if stale:
            print(f"{name}: refusing to verify; sources changed since baseline: {stale} (run sync, re-read the page, then review)", file=sys.stderr)
            status = 1
            continue
        current = meta.get("verified")
        events = current if isinstance(current, list) else ([current] if current else [])
        events.append({"by": args.by, "at": args.at})
        meta["verified"] = events
        path.write_bytes((dump_frontmatter(reorder(meta)) + "\n" + body).encode("utf-8"))
        print(f"{name}: verified by {args.by} at {args.at}")
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m quality.okf", description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sync", help="regenerate machine-owned frontmatter, generated blocks and indexes")
    check = sub.add_parser("check", help="run the OKF gate (exit 1 on any finding)")
    check.add_argument("--only", help=f"comma-separated subset of {','.join(CHECKS)}")
    review = sub.add_parser("review", help="record a human/process verification on pages")
    review.add_argument("pages", nargs="+", help="bundle-relative page paths, e.g. symbols/domain/policy/check_policy.md")
    review.add_argument("--by", required=True, help="actor: human:<id>, process:<id> or <producer>/<version>")
    review.add_argument("--at", required=True, help="ISO 8601 datetime with UTC offset, e.g. 2026-09-28T09:00:00Z")
    args = parser.parse_args(argv)
    repo = Repo(args.root.resolve())
    return {"sync": cmd_sync, "check": cmd_check, "review": cmd_review}[args.command](repo, args)


if __name__ == "__main__":
    raise SystemExit(main())
