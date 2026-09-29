"""Shared helpers: statuses, run metadata, deterministic JSON, small statistics.

Statistics use the standard library (`statistics.linear_regression`) rather than a numerical
dependency: the models here are one- and two-parameter least squares on tens of points. Percentiles
and the interquartile range are NOT re-implemented: they come from `quality.hci.laws` (nearest rank),
the one place this repository defines them, so an HCI report and a metrics report agree.
"""
# ruff: noqa: S603, S607 - `git` is run with a fixed argv list, no shell, to label a snapshot with its commit
from __future__ import annotations

import json
import math
import platform
import statistics
import subprocess
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from quality.hci import laws

from . import ROOT, SCHEMA_VERSION

MEASURED = "MEASURED"
NOT_RUN = "NOT_RUN"
PASS, FAIL = "PASS", "FAIL"
DOHERTY_MS = laws.DOHERTY_MS  # 400 ms: defined once, in the HCI lane

# Everything below `ROOT` that a run writes; ignored when deciding whether the tree is "dirty".
GENERATED_PREFIXES = ("reports/", "docs/metrics/", ".tmp/", ".pytest-tmp/", ".nox/")


def not_run(reason: str, **extra: Any) -> dict:
    """A section whose prerequisite is absent. Never rendered or budgeted as a pass."""
    return {"status": NOT_RUN, "reason": reason, **extra}


def measured(**body: Any) -> dict:
    return {"status": MEASURED, **body}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def dumps(value: Any) -> str:
    """Deterministic JSON: sorted keys, two-space indent, LF, trailing newline."""
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def tool_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip()


def git_state() -> dict:
    """Commit the tree was measured at, and whether tracked source differs from it.

    Generated outputs (reports/, docs/metrics/) are excluded from the dirty test so committing a
    snapshot does not make the snapshot's own commit field a lie.
    """
    commit = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain", "--untracked-files=all")
    if commit is None or status is None:
        return {"commit": None, "dirty": None, "note": "git unavailable"}
    changed = [line[3:].strip().strip('"') for line in status.splitlines() if line.strip()]
    dirty = [p for p in changed if not p.startswith(GENERATED_PREFIXES)]
    return {
        "commit": commit,
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(dirty),
        "dirty_paths": sorted(dirty)[:20],
    }


def platform_info() -> dict:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "label": f"{platform.system()} {platform.release()} / CPython {platform.python_version()}",
    }


TIMING_NOTE = (
    "Sections `performance`, `scaling` and `verification_yield` contain wall-clock MEASUREMENTS taken on this "
    "platform under this load; they vary run to run and are summarised by median and interquartile range, "
    "never by a single run. All other sections are deterministic functions of the source tree."
)


def meta(profile: str, generated_at: str | None) -> dict:
    body = {
        "schema": SCHEMA_VERSION,
        "profile": profile,
        "platform": platform_info(),
        "source": git_state(),
        "tools": {n: tool_version(n) for n in ("radon", "grimp", "coverage", "fastapi", "uvicorn", "httpx")},
        "timing_note": TIMING_NOTE,
    }
    if generated_at:
        body["generated_at"] = generated_at
    return body


# ---- statistics --------------------------------------------------------------------------------


def r3(x: float) -> float:
    return round(float(x), 3)


def spread(samples: Sequence[float]) -> dict:
    """Median and interquartile range (nearest rank, `laws.iqr`) of repeated timings, in the samples' unit.

    A noisy wall-clock measurement is described by these, not by one run: the IQR shows the spread a
    single number hides. With few samples the quartiles are order statistics, not estimates.
    """
    q = laws.iqr(samples)
    if q is None:
        raise ValueError("empty sample")
    return {"n": len(samples), "min": r3(min(samples)), "p25": r3(q[0]), "median": r3(q[1]), "p75": r3(q[2])}


def latency_summary(samples_ms: Sequence[float]) -> dict:
    """n, min, p25/p50/p75 (median and IQR), p95, p99, max, mean in milliseconds (nearest-rank percentiles)."""
    s = sorted(samples_ms)
    q25, q50, q75 = laws.iqr(s) or (math.nan,) * 3
    return {
        "n": len(s),
        "min_ms": r3(s[0]),
        "p25_ms": r3(q25),
        "p50_ms": r3(q50),
        "p75_ms": r3(q75),
        "p95_ms": r3(laws.percentile(s, 95) or math.nan),
        "p99_ms": r3(laws.percentile(s, 99) or math.nan),
        "max_ms": r3(s[-1]),
        "mean_ms": r3(statistics.fmean(s)),
    }


def _r2(ys: Sequence[float], predicted: Sequence[float]) -> float:
    """Coefficient of determination R^2 = 1 - SS_res / SS_tot (1.0 when y is constant and fitted exactly)."""
    mean_y = statistics.fmean(ys)
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, predicted, strict=True))
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0


def ols(xs: Sequence[float], ys: Sequence[float]) -> dict:
    """Ordinary least squares y = c0 + c1*x with R^2 and residuals.

    Establishes how well a straight line describes THESE points. It does not prove an asymptotic
    bound; that needs the residual structure and the log-log exponent read together (see scaling.py).
    """
    if len(xs) != len(ys) or len(xs) < 3:
        raise ValueError("need at least three paired points")
    fit = statistics.linear_regression(xs, ys)
    predicted = [fit.intercept + fit.slope * x for x in xs]
    return {
        "c0": fit.intercept,
        "c1": fit.slope,
        "r2": _r2(ys, predicted),
        "predicted": predicted,
        "residuals": [y - p for y, p in zip(ys, predicted, strict=True)],
    }


def _solve(a: list[list[float]], k: int) -> list[float]:
    """Solve the augmented k x (k+1) system in place by Gauss-Jordan elimination with partial pivoting."""
    for col in range(k):
        pivot = max(range(col, k), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("features are collinear")
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(k):
            if r != col:
                f = a[r][col] / a[col][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col], strict=True)]
    return [a[i][k] / a[i][i] for i in range(k)]


def ols_multi(rows: Sequence[Sequence[float]], ys: Sequence[float]) -> dict:
    """OLS y = b0 + b1*x1 + ... + bk*xk by the normal equations (Gaussian elimination, partial pivoting).

    Intended for k <= 3 well-scaled features. Returns coefficients (intercept first), R^2 and residuals.
    """
    n, k = len(rows), len(rows[0]) + 1
    if n < k + 1:
        raise ValueError("not enough points for this many parameters")
    design = [[1.0, *map(float, r)] for r in rows]
    normal = [
        [sum(d[i] * d[j] for d in design) for j in range(k)] + [sum(d[i] * y for d, y in zip(design, ys, strict=True))]
        for i in range(k)
    ]
    beta = _solve(normal, k)
    predicted = [sum(b * x for b, x in zip(beta, d, strict=True)) for d in design]
    return {
        "beta": beta,
        "r2": _r2(ys, predicted),
        "predicted": predicted,
        "residuals": [y - p for y, p in zip(ys, predicted, strict=True)],
    }
