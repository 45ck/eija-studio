"""Shared helpers: statuses, run metadata, deterministic JSON, small statistics.

Statistics use the standard library (`statistics.linear_regression`, `correlation`) rather than a
numerical dependency: the models here are one- and two-parameter least squares on tens of points.
"""
from __future__ import annotations

import json
import math
import os
import platform
import statistics
import subprocess
import sys
import sysconfig
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from . import ROOT, SCHEMA_VERSION

MEASURED = "MEASURED"
NOT_RUN = "NOT_RUN"
PASS, FAIL = "PASS", "FAIL"

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
    return out.stdout.rstrip("\n")  # not strip(): porcelain lines start with a significant space (" M path")


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
    return {"commit": commit, "branch": _git("rev-parse", "--abbrev-ref", "HEAD"), "dirty": bool(dirty),
            "dirty_paths": sorted(dirty)[:20]}


def platform_info() -> dict:
    """Platform label without `platform.system()/release()/machine()`: on some Windows CPython builds those
    go through a WMI query that dumps a scary (handled) fatal-exception traceback into test and CLI output."""
    if sys.platform == "win32":
        v = sys.getwindowsversion()  # type: ignore[attr-defined]
        system, release = "Windows", f"{v.major}.{v.minor}.{v.build}"
    else:
        system, release = sys.platform, os.uname().release
    return {"system": system, "release": release, "machine": sysconfig.get_platform(),
            "python": platform.python_version(), "implementation": platform.python_implementation(),
            "label": f"{system} {release} / CPython {platform.python_version()}"}


def meta(profile: str, generated_at: str | None) -> dict:
    body = {"schema": SCHEMA_VERSION, "profile": profile, "platform": platform_info(), "source": git_state(),
            "tools": {n: tool_version(n) for n in ("radon", "grimp", "coverage", "fastapi", "uvicorn", "httpx")},
            "timing_note": ("Sections `performance`, `scaling` and `verification_yield` contain wall-clock MEASUREMENTS "
                            "taken on this platform under this load; they vary run to run. All other sections are "
                            "deterministic functions of the source tree.")}
    if generated_at:
        body["generated_at"] = generated_at
    return body


# ---- statistics --------------------------------------------------------------------------------

def percentile(sorted_values: Sequence[float], q: float) -> float:
    """Linear-interpolation percentile (the 'inclusive' / R-7 definition). q in [0, 100]."""
    if not sorted_values:
        raise ValueError("empty sample")
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    pos = (len(sorted_values) - 1) * q / 100.0
    lo, hi = math.floor(pos), math.ceil(pos)
    return float(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo))


def latency_summary(samples_ms: Sequence[float]) -> dict:
    s = sorted(samples_ms)
    return {"n": len(s), "min_ms": r3(s[0]), "p50_ms": r3(percentile(s, 50)), "p95_ms": r3(percentile(s, 95)),
            "p99_ms": r3(percentile(s, 99)), "max_ms": r3(s[-1]), "mean_ms": r3(statistics.fmean(s))}


def r3(x: float) -> float:
    return round(float(x), 3)


def _r_squared(ys: Sequence[float], predicted: Sequence[float]) -> float:
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, predicted, strict=True))
    mean_y = statistics.fmean(ys)
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
    return {"c0": fit.intercept, "c1": fit.slope, "r2": _r_squared(ys, predicted), "predicted": predicted,
            "residuals": [y - p for y, p in zip(ys, predicted, strict=True)]}


def _solve(a: list[list[float]], k: int) -> list[float]:
    """Gauss-Jordan elimination with partial pivoting on the k x (k+1) augmented matrix `a`."""
    for col in range(k):
        pivot = max(range(col, k), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("features are collinear")
        a[col], a[pivot] = a[pivot], a[col]
        for r in (r for r in range(k) if r != col):
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
    augmented = [[sum(d[i] * d[j] for d in design) for j in range(k)] + [sum(d[i] * y for d, y in zip(design, ys, strict=True))]
                 for i in range(k)]
    beta = _solve(augmented, k)
    predicted = [sum(b * x for b, x in zip(beta, d, strict=True)) for d in design]
    return {"beta": beta, "r2": _r_squared(ys, predicted), "predicted": predicted,
            "residuals": [y - p for y, p in zip(ys, predicted, strict=True)]}


def main_python() -> str:
    return sys.executable
