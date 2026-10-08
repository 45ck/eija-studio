"""Measure how often a hash-anchored link would go stale, per hash granularity, on a real git history.

Question: if a trace link stores the hash of the thing it points at, how quickly does that hash stop
matching, and how much of the mismatch is noise (formatting, comments, docstrings) versus a change to
behaviour or interface? The answer depends on WHAT is hashed. This script replays a repository's
first-parent history and, for every (function or method, baseline commit) pair, asks whether the hash
computed under each method still matches H commits later.

It measures hash SENSITIVITY on one repository. It does not measure whether a link is still TRUE: a
changed hash means "the target changed since baseline", never "the link is now wrong".

Determinism: no wall clock, sorted iteration, canonical JSON output, git object ids in the output.
The Python version is recorded because ``ast.dump`` output differs between Python versions.

Usage: python graph/bench/traceability_staleness.py REPO_PATH [--ref HEAD] [--commits 600]
         [--glob 'doorstop/core/*.py'] [--horizons 10,50,100,300]
"""
from __future__ import annotations

import argparse
import ast
import copy
import fnmatch
import hashlib
import itertools
import json
import subprocess
import sys
from typing import Any

METHODS = ("file_bytes", "file_ast", "symbol_ast_with_doc", "symbol_ast_no_doc", "symbol_signature")


def git(repo: str, *args: str) -> bytes:
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip())
    return proc.stdout


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_doc(node: ast.AST) -> ast.AST:
    body = getattr(node, "body", None)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        node = copy.deepcopy(node)  # do not mutate the shared tree
        node.body = node.body[1:] or [ast.Pass()]  # type: ignore[attr-defined]
    return node


def symbols(tree: ast.Module) -> dict[str, ast.AST]:
    """Top-level functions and ``Class.method`` (one level). Classes themselves are not links."""
    out: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for inner in node.body:
                if isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out[f"{node.name}.{inner.name}"] = inner
    return out


def signature(node: ast.AST) -> str:
    fn: Any = node
    return ast.dump(ast.Tuple(elts=[ast.Constant(fn.name), fn.args, ast.List(elts=fn.decorator_list),
                                    fn.returns or ast.Constant(None)]))


def version_hashes(text: str) -> tuple[str, str, dict[str, dict[str, str]]] | None:
    text = text.replace("\r\n", "\n")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    per: dict[str, dict[str, str]] = {}
    for name, node in sorted(symbols(tree).items()):
        per[name] = {
            "symbol_ast_with_doc": sha(ast.dump(node)),
            "symbol_ast_no_doc": sha(ast.dump(strip_doc(node))),
            "symbol_signature": sha(signature(node)),
        }
    return sha(text), sha(ast.dump(tree)), per


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--commits", type=int, default=600)
    ap.add_argument("--glob", default="*.py")
    ap.add_argument("--horizons", default="10,50,100,300")
    a = ap.parse_args()
    horizons = sorted(int(x) for x in a.horizons.split(","))

    commits = git(a.repo, "log", "--first-parent", "--format=%H", f"-n{a.commits}", a.ref).decode().split()
    commits.reverse()  # oldest first
    index = {c: i for i, c in enumerate(commits)}
    head = commits[-1]
    first = commits[0]
    names = git(a.repo, "ls-tree", "-r", "--name-only", head).decode().splitlines()
    paths = sorted(n for n in names if fnmatch.fnmatch(n, a.glob))

    # per-pair sensitivity and survival accumulators
    pair_total = 0
    pair_changed = dict.fromkeys(METHODS, 0)
    file_versions = 0
    file_bytes_changed_ast_same = 0
    surv: dict[int, dict[str, int]] = {h: dict.fromkeys(METHODS, 0) | {"total": 0, "broken": 0} for h in horizons}
    unparsable = 0
    files_used = 0

    for path in paths:
        touching = git(a.repo, "log", "--first-parent", "--format=%H", f"-n{a.commits}", a.ref, "--", path).decode().split()
        touching = sorted((c for c in touching if c in index), key=index.__getitem__)
        # the version live at the window start is the file as of `first`
        versions: list[tuple[int, tuple[str, str, dict[str, dict[str, str]]]]] = []
        try:
            base = git(a.repo, "show", f"{first}:{path}").decode("utf-8")
            vh = version_hashes(base)
            if vh:
                versions.append((0, vh))
        except RuntimeError:
            pass
        for c in touching:
            try:
                text = git(a.repo, "show", f"{c}:{path}").decode("utf-8")
            except RuntimeError:
                continue  # deleted in this commit
            vh = version_hashes(text)
            if vh is None:
                unparsable += 1
                continue
            if versions and versions[-1][0] == index[c]:
                versions[-1] = (index[c], vh)
            else:
                versions.append((index[c], vh))
        if len(versions) < 2:
            continue
        files_used += 1

        def live_at(i: int) -> tuple[str, str, dict[str, dict[str, str]]]:
            best = versions[0][1]
            for at, v in versions:
                if at <= i:
                    best = v
            return best

        for (_i0, v0), (_i1, v1) in itertools.pairwise(versions):
            file_versions += 1
            if v0[0] != v1[0] and v0[1] == v1[1]:
                file_bytes_changed_ast_same += 1
            for name, h0 in v0[2].items():
                if name in v1[2]:
                    pair_total += 1
                    for m in METHODS[2:]:
                        pair_changed[m] += h0[m] != v1[2][name][m]
                    pair_changed["file_bytes"] += v0[0] != v1[0]
                    pair_changed["file_ast"] += v0[1] != v1[1]

        for at0, v0 in versions:
            for h in horizons:
                if at0 + h > len(commits) - 1:
                    continue
                vt = live_at(at0 + h)
                for name, h0 in v0[2].items():
                    surv[h]["total"] += 1
                    if name not in vt[2]:
                        surv[h]["broken"] += 1
                        continue
                    surv[h]["file_bytes"] += vt[0] != v0[0]
                    surv[h]["file_ast"] += vt[1] != v0[1]
                    for m in METHODS[2:]:
                        surv[h][m] += vt[2][name][m] != h0[m]

    result = {
        "repo_head": head,
        "window_first_commit": first,
        "commits_in_window": len(commits),
        "glob": a.glob,
        "files_with_history": files_used,
        "python": sys.version.split()[0],
        "file_versions_compared": file_versions,
        "file_versions_bytes_changed_but_ast_identical": file_bytes_changed_ast_same,
        "unparsable_versions_skipped": unparsable,
        "per_commit_pairs": pair_total,
        "per_commit_stale_rate": {m: round(pair_changed[m] / pair_total, 4) if pair_total else None for m in METHODS},
        "survival_by_horizon": {
            str(h): {
                "link_baselines": surv[h]["total"],
                "target_symbol_missing_rate": round(surv[h]["broken"] / surv[h]["total"], 4) if surv[h]["total"] else None,
                "hash_mismatch_rate_given_symbol_present": {
                    m: (round(surv[h][m] / (surv[h]["total"] - surv[h]["broken"]), 4)
                        if surv[h]["total"] - surv[h]["broken"] else None)
                    for m in METHODS
                },
            }
            for h in horizons
        },
    }
    sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
