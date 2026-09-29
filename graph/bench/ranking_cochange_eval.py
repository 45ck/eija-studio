"""MEASUREMENT: does a static import graph predict which other files change together with a seed file?

Question behind docs/weave/design/impact-ranking-and-confidence.md section 5.6 (relevance ranking): for a
change that touches one file, which ranker puts the files that developers really changed in the same
commit nearest the top? Rankers compared, all over the same static module graph. The graph is built from the
PARENT tree of each scored commit, so an import added by the commit being scored is not in the graph (no
look-ahead). Files the commit adds are not in that graph: they are neither candidates nor targets.

    random             deterministic pseudo-random order (sha256 of commit and id): the floor
    dir_proximity      longest shared path prefix (a naive baseline that needs no graph)
    bfs_undirected     hop distance on the undirected import graph (RepoGraph-style k-hop)
    impact_closure     dependents first (the kernel closure direction), then undirected hop distance
    ppr_*              personalised PageRank in bit-exact integers (impact_math_reference.ppr_int, bits = 20, K = 66)

Ground truth is co-change: files changed in the same commit as the seed. That is a proxy, not impact
truth: a co-changed file may be unrelated (a bulk edit), and a truly impacted file may be untouched.
Threats to validity are printed in the report. Nothing here shows an effect on agent success.

Determinism: pinned HEAD sha in the output, history read from that HEAD, rename detection off (so a git
configuration cannot change the changed-file lists), sorted iteration, integer ranking, seeded bootstrap with
random.Random(BOOT_SEED); floats only in the rounded summary. No clock.

Usage: python graph/bench/ranking_cochange_eval.py REPO_PATH [--commits 600] [--max-files 25]
           [--max-seeds 3] [--exclude PREFIX ...] [--out graph/bench/results/NAME.json]
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("impact_math_reference", HERE / "impact_math_reference.py")
ref = importlib.util.module_from_spec(spec)
sys.modules["impact_math_reference"] = ref
spec.loader.exec_module(ref)

BOOT_SEED = 20260929
KS = (5, 10, 20)
PPR_BITS = 20
NUL = bytes([0])
TAB = bytes([9])
LF = bytes([10])


def git(repo: str, *args: str) -> str:
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True)
    return p.stdout.decode("utf-8", "replace")


def module_name(path: str) -> str:
    parts = path[:-3].split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if parts and parts[0] == "src":
        parts = parts[1:]
    return ".".join(parts)


class BlobReader:
    """One persistent `git cat-file --batch` process: bytes of a blob by object id, no working tree needed."""

    def __init__(self, repo: str) -> None:
        self.p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)

    def read(self, sha: str) -> bytes:
        assert self.p.stdin is not None and self.p.stdout is not None
        self.p.stdin.write(sha.encode("ascii") + LF)
        self.p.stdin.flush()
        header = self.p.stdout.readline().split()
        if len(header) != 3 or header[1] != b"blob":
            raise RuntimeError(f"cat-file failed for {sha}: {header!r}")
        data = self.p.stdout.read(int(header[2]))
        self.p.stdout.read(1)  # the LF after the content
        return data

    def close(self) -> None:
        assert self.p.stdin is not None
        self.p.stdin.close()
        self.p.wait()


def tree_files(repo: str, rev: str, exclude: list[str]) -> dict[str, str]:
    """path -> blob sha of every tracked .py file in the tree of `rev` (not excluded by prefix)."""
    out = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "-z", rev], capture_output=True, check=True).stdout
    files: dict[str, str] = {}
    for entry in out.split(NUL):
        if not entry:
            continue
        meta, _, path_b = entry.partition(TAB)
        _mode, kind, sha = meta.decode("ascii").split()
        path = path_b.decode("utf-8", "replace")
        if kind == "blob" and path.endswith(".py") and not any(path.startswith(x) for x in exclude):
            files[path] = sha
    return files


def raw_import_names(path: str, src: str) -> list[str]:
    """Candidate dotted module names a file imports (static, syntactic, may miss dynamic imports)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    is_init = path.endswith("/__init__.py") or path == "__init__.py"
    pkg = module_name(path) if is_init else ".".join(module_name(path).split(".")[:-1])
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = pkg.split(".") if pkg else []
                parts = parts[: max(0, len(parts) - (node.level - 1))]
                base = ".".join(p for p in [".".join(parts), base] if p)
            names += [base] + [f"{base}.{a.name}" for a in node.names if a.name != "*"]
    return names


def build_graph(files: dict[str, str], reader: BlobReader,
                cache: dict[tuple[str, str], list[str]]) -> dict[str, set[str]]:
    """imports[u] = set of files in this tree that u imports. Parsed names are cached by (path, blob sha)."""
    by_name: dict[str, str] = {}
    for f in sorted(files):
        by_name.setdefault(module_name(f), f)
    imports: dict[str, set[str]] = {f: set() for f in files}
    for f in sorted(files):
        key = (f, files[f])
        if key not in cache:
            cache[key] = raw_import_names(f, reader.read(files[f]).decode("utf-8", "replace"))
        for name in cache[key]:
            cand = name
            while cand:
                if cand in by_name:
                    if by_name[cand] != f:
                        imports[f].add(by_name[cand])
                    break
                cand = cand.rpartition(".")[0]
    return imports


def bfs_dist(adj: dict[str, list[str]], src: str) -> dict[str, int]:
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def recall_at(rank: list[str], targets: set[str], k: int) -> float:
    return len(set(rank[:k]) & targets) / len(targets)


def reciprocal_first(rank: list[str], targets: set[str]) -> float:
    for i, n in enumerate(rank, 1):
        if n in targets:
            return 1.0 / i
    return 0.0


def make_weights(imports: dict[str, set[str]], dependents: dict[str, set[str]], fwd: int, rev: int,
                 damp: bool) -> dict[tuple[str, str], int]:
    """Relevance arcs. u imports v: impact flows v -> u (weight fwd), context flows u -> v (weight rev).

    The weight of x -> y is the SUM over all links joining x and y (mutual imports add both contributions).
    Hub damping multiplies the weight of every arc into y by 65536 // (1 + deg(y)), deg = distinct neighbours.
    """
    w: dict[tuple[str, str], int] = {}
    for u in sorted(imports):
        for v in sorted(imports[u]):
            for (a, b, wt) in ((v, u, fwd), (u, v, rev)):
                if wt:
                    w[(a, b)] = w.get((a, b), 0) + wt
    if damp:
        deg = {f: len(imports[f] | dependents[f]) for f in imports}
        w = {(a, b): wt * (65536 // (1 + deg[b])) for (a, b), wt in w.items()}
    return w


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--commits", type=int, default=600)
    ap.add_argument("--max-files", type=int, default=25)
    ap.add_argument("--max-seeds", type=int, default=3)
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    repo = args.repo
    head = git(repo, "rev-parse", "HEAD").strip()
    reader = BlobReader(repo)
    blob_cache: dict[tuple[str, str], list[str]] = {}
    tree_cache: dict[str, dict[str, str]] = {}
    log = git(repo, "log", "--no-merges", "--no-renames", f"-n{args.commits}", "--name-only",
              "--pretty=format:@@%H %P", head)
    commits: list[tuple[str, str, list[str]]] = []
    for block in log.split("@@")[1:]:
        lines = block.splitlines()
        head_fields = lines[0].split()
        if len(head_fields) != 2:  # a root commit has no parent tree to build the graph from
            continue
        sha, parent = head_fields
        if parent not in tree_cache:
            tree_cache[parent] = tree_files(repo, parent, args.exclude)
        changed = sorted({x for x in lines[1:] if x in tree_cache[parent]})
        if 2 <= len(changed) <= args.max_files:
            commits.append((sha, parent, changed))
    configs_spec = {
        # the fixed-step spec of the agent-interface aspect (docs/weave/design/agent-interface-and-context-packs.md
        # section 5.3): damping 0.85 = alpha 3/20, T = 30 iterations, undirected weights; run through ppr_int
        "ppr_a3/20_T30_agents_spec": ((3, 20), (1, 1, False), 30),
        "ppr_a3/20_converged_sym": ((3, 20), (1, 1, False), None),  # same alpha as the agents spec, run to convergence
        "ppr_a1/5_sym": ((1, 5), (1, 1, False), None),
        "ppr_a1/3_sym": ((1, 3), (1, 1, False), None),
        "ppr_a1/2_sym": ((1, 2), (1, 1, False), None),
        "ppr_a1/10_sym": ((1, 10), (1, 1, False), None),
        "ppr_a1/5_impact2x": ((1, 5), (2, 1, False), None),
        "ppr_a1/5_hubdamped": ((1, 5), (1, 1, True), None),
    }
    names = ["random", "dir_proximity", "bfs_undirected", "impact_closure"] + sorted(configs_spec)
    per_commit: dict[str, list[dict[str, float]]] = {n: [] for n in names}
    pairs = 0
    node_counts: list[int] = []
    arc_counts: list[int] = []
    expected_recall: dict[int, float] = dict.fromkeys(KS, 0.0)
    for sha, parent, changed in commits:
        nodes = sorted(tree_cache[parent])
        imports = build_graph(tree_cache[parent], reader, blob_cache)
        dependents: dict[str, set[str]] = {f: set() for f in nodes}
        for u, vs in imports.items():
            for v in vs:
                dependents[v].add(u)
        node_counts.append(len(nodes))
        arc_counts.append(sum(len(v) for v in imports.values()))
        und = {f: sorted(imports[f] | dependents[f]) for f in nodes}
        affects = {f: sorted(dependents[f]) for f in nodes}  # a change to f affects the modules that import it
        configs = {name: (alpha, make_weights(imports, dependents, *wspec), iters)
                   for name, (alpha, wspec, iters) in configs_spec.items()}
        seeds = sorted(changed, key=lambda p: hashlib.sha256((sha + p).encode()).hexdigest())[: args.max_seeds]
        acc: dict[str, list[dict[str, float]]] = {n: [] for n in names}
        for s in seeds:
            targets = set(changed) - {s}
            cands = [n for n in nodes if n != s]
            pairs += 1
            d_und = bfs_dist(und, s)
            d_imp = bfs_dist(affects, s)
            sp = s.split("/")

            def shared(n: str) -> int:
                c = 0
                for a, b in zip(sp, n.split("/")):
                    if a != b:
                        break
                    c += 1
                return c

            ranks = {
                "random": sorted(cands, key=lambda n: hashlib.sha256((sha + n).encode()).hexdigest()),
                "dir_proximity": sorted(cands, key=lambda n: (-shared(n), n)),
                "bfs_undirected": sorted(cands, key=lambda n: (d_und.get(n, 10**9), n)),
                "impact_closure": sorted(cands, key=lambda n: (d_imp.get(n, 10**9), d_und.get(n, 10**9), n)),
            }
            for name, (alpha, w, iters) in configs.items():
                r = ref.ppr_int(nodes, w, {s: 1}, alpha=alpha, bits=PPR_BITS, iterations=iters)
                ranks[name] = [n for n in r["ranking"] if n != s]
            for name in names:
                rk = ranks[name]
                m = {f"recall@{k}": recall_at(rk, targets, k) for k in KS}
                m["mrr"] = reciprocal_first(rk, targets)
                acc[name].append(m)
            for k in KS:
                expected_recall[k] += min(k, len(cands)) / len(cands)
        for name in names:
            per_commit[name].append({k: sum(m[k] for m in acc[name]) / len(acc[name]) for k in acc[name][0]})
    metrics = sorted(per_commit["random"][0]) if commits else []
    half = len(commits) // 2
    groups = {"all": list(range(len(commits))), "test_newer_half": list(range(half)),
              "tune_older_half": list(range(half, len(commits)))}
    rng = random.Random(BOOT_SEED)

    def mean(name: str, metric: str, idx: list[int]) -> float:
        vals = per_commit[name]
        return sum(vals[i][metric] for i in idx) / max(1, len(idx))

    def ci(members: list[int], fn) -> list[float]:
        if not members:
            return [0.0, 0.0]
        xs = sorted(fn([members[rng.randrange(len(members))] for _ in members]) for _ in range(1000))
        return [round(xs[24], 4), round(xs[974], 4)]

    summary: dict = {}
    paired: dict = {}
    for gname, members in groups.items():
        summary[gname] = {name: {m: {"mean": round(mean(name, m, members), 4),
                                     "ci95": ci(members, lambda idx, m=m, name=name: mean(name, m, idx))}
                                 for m in metrics} for name in names}
        paired[gname] = {}
        for base in ("bfs_undirected", "dir_proximity"):
            paired[gname]["vs_" + base] = {
                name: {m: {"mean_diff": round(mean(name, m, members) - mean(base, m, members), 4),
                           "ci95": ci(members, lambda idx, m=m, name=name, base=base: mean(name, m, idx) - mean(base, m, idx))}
                       for m in ("recall@10", "mrr")} for name in names if name != base}
    ppr_names = sorted(n for n in names if n.startswith("ppr_"))
    chosen = max(ppr_names, key=lambda n: (mean(n, "recall@10", groups["tune_older_half"]), n)) if commits else None
    head_files = tree_files(repo, head, args.exclude)
    report = {
        "schema": "eija.weave.ranking-cochange-eval.v2", "label": "MEASUREMENT",
        "repo_head": head, "python": sys.version.split()[0],
        "graph": {"built_at": "the parent tree of each scored commit (no look-ahead)",
                  "nodes_at_pinned_head": len(head_files),
                  "nodes_per_commit_min_max": [min(node_counts, default=0), max(node_counts, default=0)],
                  "import_arcs_per_commit_min_max": [min(arc_counts, default=0), max(arc_counts, default=0)],
                  "language": "python", "edges": "static ast imports"},
        "params": {"commits_scanned": args.commits, "max_files_per_commit": args.max_files,
                   "max_seeds_per_commit": args.max_seeds, "exclude": sorted(args.exclude), "bootstrap": 1000,
                   "bootstrap_seed": BOOT_SEED, "ppr_bits": PPR_BITS, "rename_detection": "off (--no-renames)"},
        "commits_used": len(commits), "seed_target_pairs": pairs,
        "random_expected_recall_mean_over_pairs": {f"recall@{k}": round(expected_recall[k] / max(1, pairs), 4) for k in KS},
        "split": {"rule": "commits are newest first; the newer half is the test half, the older half tunes",
                  "tune_commits": len(groups["tune_older_half"]), "test_commits": len(groups["test_newer_half"]),
                  "ppr_config_chosen_on_tune_half_by_recall@10": chosen},
        "summary": summary, "paired_differences": paired,
        "threats_to_validity": [
            "co-change is a proxy for impact, not ground truth (bulk edits, missing consequences)",
            "the graph is built at each commit's parent, so there is no look-ahead from imports added by the scored commit; "
            "files the commit adds are absent from that graph and excluded from targets, which favours no ranker but shrinks the target set",
            "with rename detection off, a renamed file appears as the old path (a target, present in the parent graph) and a new path (excluded)",
            "static imports only: dynamic imports, data files and non-Python files are invisible",
            "one language, one repository per run; tuning parameters were chosen by looking at this data",
            "parameters were chosen on the older half and scored on the newer half; the halves are not independent (same files, same authors)",
        ],
    }
    reader.close()
    text = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    if args.out:
        Path(args.out).write_bytes(text.encode("ascii"))
    else:
        sys.stdout.buffer.write(text.encode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
