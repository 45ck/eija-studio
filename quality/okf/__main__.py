"""``python -m quality.okf {sync,check,review}``: generate, gate and review the OKF bundle."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import codelink as cl
from .build import build, reorder, write
from .checks import CHECKS, current_sources_sha, format_report, run_checks, valid_actor, valid_iso
from .pages import RESERVED, Repo, dump_frontmatter, human_sha256, sources_sha256, split_page

ROOT = Path(__file__).resolve().parents[2]


def cmd_sync(repo: Repo, _args: argparse.Namespace) -> int:
    """Regenerate machine-owned content. Does NOT re-review prose: `notes_baseline` of curated pages is left as is."""
    try:
        bundle = build(repo)
    except (SyntaxError, cl.Unresolved, ValueError) as exc:
        print(f"okf sync: cannot build the bundle: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    changed = write(repo, bundle)
    for note in bundle.notes:
        print(f"note: {note}")
    print(f"okf sync: {len(bundle.files)} files, {len(changed)} written")
    if changed:
        print("note: add a dated bullet to okf/log.md describing what changed (sync never writes the log)")
    stale_notes = [f for f in run_checks(repo, ("codelinks",)).findings if f.code == "NOTES_STALE"]
    if stale_notes:
        print(f"note: {len(stale_notes)} page(s) have hand-written Notes not re-read since their source changed; the gate stays red until "
              "`python -m quality.okf review` is run on each: " + ", ".join(f.path for f in stale_notes))
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


def _review_target(repo: Repo, name: str) -> tuple[Path | None, str | None]:
    """(page path, None) for a concept page inside the bundle, else (None, why not)."""
    target = (repo.bundle / name).resolve()
    if not target.is_relative_to(repo.bundle.resolve()) or target.suffix != ".md" or target.name in RESERVED:
        return None, "not a concept page inside the bundle"
    if not target.is_file():
        return None, "no such page"
    return target, None


def _review_page(repo: Repo, name: str, by: str, at: str) -> str | None:
    """Record a review of one page. Returns an error message, or None on success."""
    target, error = _review_target(repo, name)
    if target is None:
        return error
    try:
        meta, body = split_page(target.read_bytes().decode("utf-8").replace("\r\n", "\n"))
        current = current_sources_sha(repo, meta)
    except (ValueError, KeyError, TypeError, cl.Unresolved) as exc:
        return f"cannot review: {type(exc).__name__}: {exc}"
    if meta.get("sources") and current is None:
        return "refusing to review; the page's sources cannot be resolved"
    if current != sources_sha256(meta.get("sources")):
        return "refusing to review; a source changed since the page was baselined (run sync, re-read the page, then review)"
    history = meta.get("verified")
    events = history if isinstance(history, list) else ([history] if history else [])
    events.append({"by": by, "at": at, "notes_sha256": human_sha256(body), "sources_sha256": current})
    meta["verified"] = events
    if current is not None:
        meta["notes_baseline"] = current
    target.write_bytes((dump_frontmatter(reorder(meta)) + "\n" + body).encode("utf-8"))
    return None


def cmd_review(repo: Repo, args: argparse.Namespace) -> int:
    """Record that an actor re-read a page against its current sources; only this command advances `notes_baseline`.

    The entry is bound to the page's current prose and source hashes, so editing the prose or the code later
    stops it counting toward the trust tier. `--by` is a self-declared label: the tool cannot authenticate it,
    and an agent must use `process:<id>`, never `human:<id>`. `--at` is an explicit argument, never a clock read.
    """
    if not valid_actor(args.by):
        print(f"--by must be human:<id>, process:<id> or <producer>/<version>, got {args.by!r}", file=sys.stderr)
        return 2
    if not valid_iso(args.at):
        print(f"--at must be ISO 8601 with a UTC offset, e.g. 2026-09-28T09:00:00Z, got {args.at!r}", file=sys.stderr)
        return 2
    status = 0
    for name in args.pages:
        error = _review_page(repo, name, args.by, args.at)
        if error:
            print(f"{name}: {error}", file=sys.stderr)
            status = 1
        else:
            print(f"{name}: reviewed by {args.by} at {args.at} (self-declared actor)")
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m quality.okf", description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sync", help="regenerate machine-owned frontmatter, generated blocks and indexes")
    check = sub.add_parser("check", help="run the OKF gate (exit 1 on any finding)")
    check.add_argument("--only", help=f"comma-separated subset of {','.join(CHECKS)}")
    review = sub.add_parser("review", help="record that an actor re-read pages against their current sources (clears NOTES_STALE)")
    review.add_argument("pages", nargs="+", help="bundle-relative page paths, e.g. symbols/domain/policy/check_policy.md")
    review.add_argument("--by", required=True, help="actor: human:<id> (self-declared, unauthenticated), process:<id> or <producer>/<version>; agents use process:<id>")
    review.add_argument("--at", required=True, help="ISO 8601 datetime with UTC offset, e.g. 2026-09-28T09:00:00Z")
    args = parser.parse_args(argv)
    repo = Repo(args.root.resolve())
    return {"sync": cmd_sync, "check": cmd_check, "review": cmd_review}[args.command](repo, args)


if __name__ == "__main__":
    raise SystemExit(main())
