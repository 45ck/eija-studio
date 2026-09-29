"""Run targets on at most two workers and assemble the mutants. Each (target, shard) is an isolated job.

A full run takes tens of minutes on a loaded PC, so a finished job is cached under `.tmp/mutation-cache/`,
keyed by a fingerprint of everything its result depends on. `--resume` reuses a job whose fingerprint still
matches; without it every job runs, so a release run is never satisfied by a stale result.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from .engine import engine_version, run_target
from .model import Mutant, tally
from .targets import Target

MAX_WORKERS = 2  # 10 lanes share one 16 GB PC; this is a hard ceiling, not a default
_TOOLING = ("targets.py", "model.py", "eija_operators.py")  # inputs that change results; engine.py only orchestrates


def fingerprint(root: Path, target: Target, sample: int | None, shard: tuple[int, int]) -> str:
    """Hash of every input a job's result depends on: the code under test, all tests, the operators, the engine."""
    digest = hashlib.sha256(json.dumps([engine_version(), sample, shard, target.module, target.tests]).encode())
    files = [*sorted((root / "src" / "eija_studio").rglob("*")), *sorted((root / "tests").glob("*.py")),
             *(root / "quality" / "mutation" / name for name in _TOOLING)]
    for path in files:
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _cache_path(root: Path, target: Target, shard: tuple[int, int]) -> Path:
    return root / ".tmp" / "mutation-cache" / f"{target.slug}-{shard[0]}of{shard[1]}.json"


def _load_cached(path: Path, key: str) -> list[Mutant] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if data.get("fingerprint") != key:
        return None
    return [Mutant(**{**m, "start": tuple(m["start"]), "end": tuple(m["end"])}) for m in data["mutants"]]


def _job(root: Path, target: Target, sample: int | None, shard: tuple[int, int], resume: bool) -> tuple[list[Mutant], bool]:
    key = fingerprint(root, target, sample, shard)
    cache = _cache_path(root, target, shard)
    if resume and (cached := _load_cached(cache, key)) is not None:
        return cached, True
    mutants = run_target(root, target, sample=sample, shard=shard)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(json.dumps({"fingerprint": key, "mutants": [asdict(m) for m in mutants]}, sort_keys=True).encode("utf-8"))
    return mutants, False


def run_all(root: Path, targets: tuple[Target, ...], *, workers: int, sample: int | None, resume: bool = False) -> list[Mutant]:
    """Run every target, split into `workers` shards each, on `workers` threads (each drives one subprocess).

    A `MutationError` from any job propagates and cancels jobs not yet started: a partial measurement is
    never reported as a result.
    """
    if not 1 <= workers <= MAX_WORKERS:
        raise SystemExit(f"--workers must be between 1 and {MAX_WORKERS} (shared 16 GB PC)")
    jobs = [(target, (index, workers)) for target in targets for index in range(workers)]
    mutants: list[Mutant] = []
    started = time.monotonic()
    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        futures = {pool.submit(_job, root, target, sample, shard, resume): (target, shard) for target, shard in jobs}
        for future in as_completed(futures):
            target, shard = futures[future]
            try:
                result, cached = future.result()
            except Exception as error:
                print(f"[mutation] {target.module} shard {shard[0] + 1}/{shard[1]} FAILED: {error}", file=sys.stderr, flush=True)
                raise
            mutants.extend(result)
            print(f"[mutation] {target.module} shard {shard[0] + 1}/{shard[1]}{' (cached)' if cached else ''}: {tally(result)} "
                  f"({time.monotonic() - started:.0f}s elapsed)", file=sys.stderr, flush=True)
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
    return sorted(mutants, key=lambda m: m.sort_key)
