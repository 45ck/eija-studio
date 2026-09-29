"""Latency model of the local HTTP interface and of the runtime verification matrix.

Two transports are measured against the same application factory:

  * `testclient`  Starlette TestClient: the ASGI app in-process, no socket. Measures application +
                  SQLite cost without network stack noise.
  * `uvicorn`     a real uvicorn server on an ephemeral 127.0.0.1 port, called by httpx over a
                  loopback socket with keep-alive. This is closest to what a browser experiences,
                  minus browser rendering.

Per endpoint the report gives n, min, p50, p95, p99, max, mean (milliseconds; linear-interpolation
percentiles) and compares p95 with two thresholds:

  * 100 ms  "instantaneous" (Miller 1968; Nielsen 1993, ch. 5: about 0.1 s feels immediate);
  * 400 ms  the Doherty threshold (Doherty & Thadani, IBM Systems Journal 1982: below ~400 ms
            computer and user stay in a productive, mutually paced loop).

Percentile caveat: with n < 100, p99 is essentially the maximum; treat it as an upper indication.

What this does NOT establish: browser-perceived latency (parsing, layout, paint), behaviour under
concurrent load, other machines or disks, or the latency of a networked provider (the offline
provider is used; a live model call is out of scope and reported NOT_RUN elsewhere). The identity
provider runs its real byte-hashing of the implementation but is forced `trusted_fixture=True`
(marked `identity_source: metrics-harness`) so a working tree that differs from the owner-stamped
release can still be measured; no kernel guard is changed.
"""
from __future__ import annotations

import math
import socket
import tempfile
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import httpx
import uvicorn
from fastapi.testclient import TestClient

from eija_studio.adapters.identity import identity as measured_identity
from eija_studio.application import verifier
from eija_studio.application.compiler import subject_for
from eija_studio.bootstrap import build_studio
from eija_studio.domain.impact import model_impact
from eija_studio.domain.models import SemanticTransaction
from eija_studio.domain.policy import apply_transaction, baseline
from eija_studio.interfaces.http import create_app

from . import ROOT
from .common import latency_summary, measured, not_run, ols, r3
from .scaling import time_call

INSTANT_MS, DOHERTY_MS = 100.0, 400.0
TOKEN = "metrics-harness-token"  # noqa: S105  (a fixed test credential for a loopback server started here)
PROFILES = {  # profile -> read samples per endpoint, flow iterations, verify-scaling repeats
    "smoke": {"reads": 6, "flows": 3, "matrix_repeats": 1},  # unit tests only: proves the pipeline, not a statistic
    "quick": {"reads": 40, "flows": 4, "matrix_repeats": 3},
    "full": {"reads": 120, "flows": 15, "matrix_repeats": 5},
}
READ_ENDPOINTS = ("GET /", "GET /assets/app.js", "GET /api/status", "GET /api/doctor", "GET /api/cases")
Call = Callable[..., tuple[int, float, object]]  # (method, path, json) -> (status, milliseconds, decoded body)


def harness_identity() -> dict:
    """Real identity computation (hashes the implementation), forced trusted for measurement only."""
    return measured_identity() | {"trusted_fixture": True, "identity_source": "metrics-harness"}


def build(workspace: Path):
    studio = build_studio(workspace)
    studio.identity_provider = harness_identity
    return studio


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextmanager
def workspace() -> Iterator[Path]:
    """A scratch workspace inside the checkout (the system temp dir may be a slow disk)."""
    base = ROOT / ".tmp"
    base.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="metrics-", dir=base, ignore_cleanup_errors=True) as d:
        yield Path(d)


def _headers(port: int) -> dict:
    return {"Authorization": "Bearer " + TOKEN, "Origin": f"http://127.0.0.1:{port}"}


@contextmanager
def testclient_call(work: Path) -> Iterator[Call]:
    port = free_port()
    app = create_app(build(work / "ws"), TOKEN, port)
    with TestClient(app, base_url=f"http://127.0.0.1:{port}") as client:
        yield _timed(client, _headers(port))


class ServerThread:
    """uvicorn on an ephemeral loopback port, in a thread of this process."""

    def __init__(self, app, port: int):
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def __enter__(self) -> ServerThread:
        self.thread.start()
        deadline = time.monotonic() + 20
        while not self.server.started:
            if not self.thread.is_alive() or time.monotonic() > deadline:
                raise RuntimeError("uvicorn did not start")
            time.sleep(0.02)
        return self

    def __exit__(self, *exc) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=15)


@contextmanager
def uvicorn_call(work: Path) -> Iterator[Call]:
    port = free_port()
    app = create_app(build(work / "ws"), TOKEN, port)
    with ServerThread(app, port), httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60) as client:
        yield _timed(client, _headers(port))


def _timed(client, headers: dict) -> Call:
    def call(method: str, path: str, body: dict | None = None):
        start = time.perf_counter()
        response = client.request(method, path, headers=headers, json=body) if body is not None \
            else client.request(method, path, headers=headers)
        elapsed = (time.perf_counter() - start) * 1000.0
        content = response.json() if response.headers.get("content-type", "").startswith("application/json") else None
        return response.status_code, elapsed, content
    return call


def run_flow(call: Call, n: int, record: dict[str, list[float]] | None) -> None:
    """One full owner journey through the write endpoints (create ... verify ... approve ... export).

    `apply` is deliberately excluded: it mutates the workspace baseline, which would change what the
    next iteration measures. Every call must return 200; anything else is an error, not a sample.
    """
    def step(label: str, method: str, path: str, body: dict | None = None):
        status, ms, content = call(method, path, body)
        if status != 200:
            raise RuntimeError(f"{label} returned HTTP {status}: {content}")
        if record is not None:
            record.setdefault(label, []).append(ms)
        return content

    case = step("POST /api/cases", "POST", "/api/cases", {"request": "Let teachers sign off excursions."})
    root = "/api/cases/" + case["id"]
    case = step("POST /api/cases/{id}/propose", "POST", root + "/propose", {"expected_version": case["version"]})
    case = step("POST /api/cases/{id}/select", "POST", root + "/select",
                {"expected_version": case["version"], "interpretation": "recommend_only"})
    instance = step("POST /api/cases/{id}/preview", "POST", root + "/preview",
                    {"expected_version": case["version"], "state": "Recommended"})
    step("POST /api/cases/{id}/execute", "POST", root + "/execute",
         {"operation_id": f"m-{n}-{instance['id'][:8]}", "instance_id": instance["id"], "actor_id": "registrar",
          "action": "Approve", "expected_version": 0})
    step("GET /api/cases/{id}", "GET", root)
    case = step("POST /api/cases/{id}/verify", "POST", root + "/verify", {"expected_version": case["version"]})
    packet = step("GET /api/cases/{id}", "GET", root)["packet"]
    step("POST /api/cases/{id}/approve", "POST", root + "/approve",
         {"expected_version": case["version"], "subject_hash": packet["subject_hash"],
          "answers": {q["id"]: q["expected"] for q in packet["questions"]}, "acknowledge_unknowns": True})
    step("GET /api/cases/{id}/export", "GET", root + "/export")


def measure_transport(opener, profile: str) -> dict:
    cfg = PROFILES[profile]
    record: dict[str, list[float]] = {}
    with workspace() as work, opener(work) as call:
        run_flow(call, -1, None)  # warm-up: imports, JIT-less caches, SQLite file creation; excluded
        for n in range(cfg["flows"]):
            run_flow(call, n, record)
        for endpoint in READ_ENDPOINTS:
            method, path = endpoint.split(" ")
            call(method, path)  # warm-up read
            for _ in range(cfg["reads"]):
                status, ms, _ = call(method, path)
                if status != 200:
                    raise RuntimeError(f"{endpoint} returned HTTP {status}")
                record.setdefault(endpoint, []).append(ms)
    return endpoints_report(record)


def endpoints_report(record: dict[str, list[float]]) -> dict:
    rows = []
    for endpoint in sorted(record):
        s = latency_summary(record[endpoint])
        kind = "read" if endpoint.startswith("GET") else "compute" if endpoint.endswith("/verify") else "write"
        rows.append({"endpoint": endpoint, "kind": kind, **s,
                     "p95_within_instant": s["p95_ms"] <= INSTANT_MS, "p95_within_doherty": s["p95_ms"] <= DOHERTY_MS})
    return {"status": "MEASURED", "endpoints": rows,
            "summary": {"endpoints": len(rows), "worst_p95_ms": max(r["p95_ms"] for r in rows),
                        "worst_p95_endpoint": max(rows, key=lambda r: r["p95_ms"])["endpoint"],
                        "all_p95_within_doherty": all(r["p95_within_doherty"] for r in rows),
                        "over_doherty": sorted(r["endpoint"] for r in rows if not r["p95_within_doherty"]),
                        "over_instant": sorted(r["endpoint"] for r in rows if not r["p95_within_instant"])}}


# ---- runtime verification matrix vs size ------------------------------------------------------------

def matrix_points(repeats: int) -> tuple[list[dict], dict]:
    """Time `verify_runtime` for matrices of 20..125 cells (models x actor-count prefixes).

    The kernel's actor list is a module constant; slicing it (unittest.mock.patch.object, measurement
    only) varies the matrix size through the REAL verification code path without editing the kernel.
    Returns the points and the yield statistics of the full 125-cell matrix.
    """
    base = baseline()
    candidate = apply_transaction(base, SemanticTransaction(kind="enable_recommendation"))
    full_actors = list(verifier.ACTORS)
    points: list[dict] = []
    yield_stats: dict = {}
    with workspace() as work:
        studio = build(work / "ws")
        identity = harness_identity()
        for label, model in (("baseline", base), ("candidate", candidate)):
            subject = subject_for(model, {}, identity)
            for k in range(1, len(full_actors) + 1):
                with mock.patch.object(verifier, "ACTORS", full_actors[:k]):
                    receipt = verifier.verify_runtime(model, subject, studio.sandbox)  # also warms up
                    seconds = time_call(lambda m=model, s=subject: verifier.verify_runtime(m, s, studio.sandbox), repeats)
                cells = receipt["artifact"]["expected_cells"]
                if len(receipt["artifact"]["cells"]) != cells:
                    raise RuntimeError("verifier did not evaluate every expected cell")
                points.append({"model": label, "actors": k, "states": len(model.states), "cells": cells,
                               "ms": r3(seconds * 1000)})
                if label == "candidate" and k == len(full_actors):
                    yield_stats = _matrix_yield(receipt["artifact"], seconds)
    return sorted(points, key=lambda p: (p["cells"], p["model"])), yield_stats


def _matrix_yield(artifact: dict, seconds: float) -> dict:
    cells = artifact["cells"]
    accepted = sum(c["actual"]["accepted"] for c in cells)
    mismatches = sum(c["expected"] != c["actual"] for c in cells)
    return {"cells": len(cells), "accepted": accepted, "denied": len(cells) - accepted, "oracle_mismatches": mismatches,
            "seconds": seconds}


def verify_scaling(profile: str) -> tuple[dict, dict]:
    """Fit verification time against matrix size (cells), with a quadratic alternative and a log-log exponent.

    Establishes how well a straight line describes 10 points from 20 to 125 cells. That range is narrow, so
    the test has LOW POWER: it cannot separate linear from mildly superlinear growth, and the fitted
    intercept can be negative (a fit artefact from pooling matrices of different shape, not negative time).
    """
    points, stats = matrix_points(PROFILES[profile]["matrix_repeats"])
    xs, ys = [float(p["cells"]) for p in points], [p["ms"] for p in points]
    fit = ols(xs, ys)
    quad = ols([x * x for x in xs], ys)
    loglog = ols([math.log(x) for x in xs], [math.log(y) for y in ys])
    for p, pred, res in zip(points, fit["predicted"], fit["residuals"], strict=True):
        p["predicted_ms"], p["residual_ms"] = r3(pred), r3(res)
    body = {"status": "MEASURED", "model": "T_ms = c0 + c1 * cells", "c0_ms": round(fit["c0"], 4),
            "c1_ms_per_cell": round(fit["c1"], 5), "r2": round(fit["r2"], 6),
            "alt_quadratic_r2": round(quad["r2"], 6), "loglog_exponent": round(loglog["c1"], 4),
            "intercept_caveat": ("a negative c0 is a fit artefact (baseline and candidate matrices are pooled and "
                                 "differ in state count), not a physical negative time; treat c1 as a slope estimate"),
            "power_caveat": "20 to 125 cells cannot separate linear from mildly superlinear growth; see alt_quadratic_r2",
            "points": points,
            "note": ("Matrix = actors x states x 5 actions. Each cell is one isolated ephemeral-SQLite "
                     "transaction pair; the same-author oracle means agreement is not independent evidence.")}
    return body, stats


def impact_yield() -> dict:
    """Nodes explored by the model-impact closure for the recommendation change (size of the change envelope)."""
    base = baseline()
    candidate = apply_transaction(base, SemanticTransaction(kind="enable_recommendation"))
    report = model_impact(base, candidate)
    seconds = time_call(lambda: model_impact(base, candidate), 15)
    return {"nodes": len(report["affected"]), "edges": sum(len(v) for v in report["graph"].values()),
            "changed_actions": report["changed_actions"], "seconds": seconds}


def collect(profile: str = "quick", *, real_server: bool = True) -> tuple[dict, dict]:
    """Return (performance section, verification-yield rows keyed by technique)."""
    transports = {}
    for name, opener in (("testclient", testclient_call), ("uvicorn", uvicorn_call)):
        if name == "uvicorn" and not real_server:
            transports[name] = not_run("real-server measurement disabled for this run")
            continue
        try:
            transports[name] = measure_transport(opener, profile)
        except (OSError, RuntimeError) as exc:
            transports[name] = not_run(f"{name} transport failed: {exc.__class__.__name__}: {exc}")
    scaling, stats = verify_scaling(profile)
    cfg = PROFILES[profile]
    performance = measured(
        kind="measurement", method="wall-clock latency per endpoint; offline provider; durable SQLite workspace",
        thresholds={"instant_ms": INSTANT_MS, "doherty_ms": DOHERTY_MS},
        sources=["Doherty & Thadani, IBM Systems Journal 21(4), 1982", "Miller 1968", "Nielsen, Usability Engineering, 1993"],
        not_measured=["browser rendering", "concurrent load", "live model provider", "other machines"],
        config={**cfg, "warmup": "one full flow and one read per endpoint, excluded", "apply_endpoint": "excluded (mutates baseline)"},
        transports=transports, verify_scaling=scaling)
    return performance, {"matrix": stats, "impact": impact_yield()}
