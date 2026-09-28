"""Run the whole TLA+ verification lane and write reports/formal/tla.json.

    python -m verification.tla.run                 # what the `formal_tla` nox session runs
    python -m verification.tla.run --deep          # also model-check the candidate at a larger bound
    python -m verification.tla.run --no-fetch      # never download; NOT_RUN if the jar is absent

Verdicts are honest by construction: no Java or no verifiable jar => `NOT_RUN` (never `PASS`); a
negative control that does NOT produce its expected counterexample => `FAIL`; a single disagreement
between the spec and the real runtime => `FAIL`.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import sys
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eija_studio.adapters.sqlite_store import sandbox_factory

from . import conformance, generate, model, render, tlc

ROOT = tlc.ROOT
DEFAULT_OUT = ROOT / "reports" / "formal" / "tla.json"
TRACE_OPS = 6  # operation ids in trace validation: larger than the exhaustive bounds
PROBE_LIMIT = 100  # at most this many reachable states get a shortest-path + probe trace

LIMITATIONS = [
    "Bounded: N operation ids, one preview instance, a fixed 5-actor fixture directory; no claim beyond the bounds.",
    "The model is a hand-written TLA+ transcription of the runtime's check order; agreement with the code is measured "
    "(state-graph comparison and trace validation), not proved.",
    "Not modelled: several instances or cases, model-hash staleness, NOT_FOUND, concurrent connections, crash/power loss "
    "(covered by the kernel's process-termination tests), real identity, external delivery of the outbox.",
    "Negative controls use seeded defects and hostile workflows that protected policy rejects; they show the invariants "
    "are sensitive, not that the kernel contains those defects.",
    "The runtime side is compared through the abstraction in verification/tla/abstraction.py; fields outside it "
    "(audit bodies, payloads, timestamps) are not compared.",
    "Same-author model and code: agreement is not independent validation.",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _tlc_summary(run: tlc.TlcRun) -> dict[str, Any]:
    return {"result": run.result, "states_generated": run.generated, "distinct_states": run.distinct, "depth": run.depth,
            "seconds": run.seconds, "violated": run.violated or None, "violation_kind": run.violation_kind or None}


def model_check(config: model.TlaConfig, work: Path, *, ops: int | None = None, workers: int = 2) -> tuple[dict[str, Any], str]:
    """Model-check one configuration. Returns (report entry, counterexample markdown or "")."""
    ops = ops or config.check_ops
    if ops == config.check_ops:
        spec = generate.OUT / f"MC_{config.name}.tla"
        cfg = generate.OUT / f"MC_{config.name}.cfg"
    else:  # a deeper bound is generated at run time, not committed
        deep = replace(config, name=f"{config.name}_ops{ops}", check_ops=ops)
        for name, text in {f"MC_{deep.name}.tla": generate.module_text(deep, dump=False),
                           f"MC_{deep.name}.cfg": generate.cfg_text(deep, dump=False)}.items():
            (work / name).write_bytes(text.encode("utf-8"))
        spec, cfg = work / f"MC_{deep.name}.tla", work / f"MC_{deep.name}.cfg"
    run = tlc.run_tlc(spec, cfg, work, workers=1 if config.negative_control else workers)
    entry: dict[str, Any] = {
        "name": config.name, "description": config.description, "role": "negative_control" if config.negative_control else "safe",
        "bound": {"operation_ids": ops, "max_expected_version": ops, "actors": len(model.directory()),
                  "mutable_actors": list(model.MUTABLE_ACTORS)},
        "workflow_semantic_hash": config.workflow.semantic_hash, "policy_verdict": list(config.policy_errors) or "accepted",
        "mutation": config.mutation, "invariants": list(model.INVARIANTS), "properties": list(model.PROPERTIES),
        "tlc": _tlc_summary(run)}
    markdown = ""
    if config.negative_control:
        entry["expected_violation"] = config.expect
        entry["why"] = config.note
        entry["expected_violation_observed"] = run.result == "VIOLATION" and run.violated == config.expect
        rows = render.describe_steps(config, run.trace) if run.trace else []
        entry["counterexample"] = rows
        entry["passed"] = entry["expected_violation_observed"]
        if rows:
            markdown = render.markdown(config.name, run.violated, config.description, rows, config.note)
    else:
        entry["passed"] = run.result == "PASS"
    return entry, markdown


def _first_divergence(run: tlc.TlcRun) -> dict[str, Any]:
    text = run.output.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"(?m)^State \d+: ", text)
    last = blocks[-1] if len(blocks) > 1 else ""
    tr, pos = re.search(r"/\\ tr = (\d+)", last), re.search(r"/\\ pos = (\d+)", last)
    return {"trace_index_1based": int(tr.group(1)) if tr else None, "steps_validated_incl_divergent": int(pos.group(1)) if pos else None}


def _write(work: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        (work / name).write_bytes(text.encode("utf-8"))


def conformance_for(config: model.TlaConfig, work: Path, *, seed: str, random_count: int, sensitivity: bool) -> dict[str, Any]:
    """Exhaustive graph comparison + trace validation (+ seeded-defect sensitivity) for one safe config."""
    (work / "workspace").mkdir(parents=True, exist_ok=True)
    sandbox = sandbox_factory(work / "workspace")
    started = time.monotonic()
    graph = conformance.explore(config.workflow, config.dump_ops, sandbox)
    explore_seconds = round(time.monotonic() - started, 2)
    dump = tlc.run_tlc(generate.OUT / f"MCD_{config.name}.tla", generate.OUT / f"MCD_{config.name}.cfg", work, workers=1)
    if dump.result != "PASS":
        return {"agree": False, "reason": f"TLC dump run did not complete: {dump.result}", "tlc": _tlc_summary(dump)}
    comparison = conformance.compare(graph, conformance.parse_dump(dump.output))
    out: dict[str, Any] = {
        "state_graph": {"bound": {"operation_ids": config.dump_ops}, "runtime_explore_seconds": explore_seconds,
                        "tlc": _tlc_summary(dump), **comparison}}

    started = time.monotonic()
    traces, counts = conformance.build_traces(config.workflow, TRACE_OPS, sandbox, graph, seed=seed, random_count=random_count,
                                              probe_limit=PROBE_LIMIT)
    record_seconds = round(time.monotonic() - started, 2)
    _write(work, generate.trace_files(config, TRACE_OPS, traces))
    run = tlc.run_tlc(work / f"MCT_{config.name}.tla", work / f"MCT_{config.name}.cfg", work, workers=1)
    outcomes: dict[str, int] = {}
    for trace in traces:
        for step in trace["steps"]:
            outcomes[step[5]] = outcomes.get(step[5], 0) + 1
    out["trace_validation"] = {
        "bound": {"operation_ids": TRACE_OPS}, "seed": seed, "traces": len(traces), "by_kind": counts,
        "steps": conformance.trace_steps_total(traces), "outcome_histogram": dict(sorted(outcomes.items())),
        "runtime_record_seconds": record_seconds, "tlc": _tlc_summary(run), "agree": run.result == "PASS",
        **({"first_divergence": _first_divergence(run)} if run.result != "PASS" else {})}
    out["agree"] = bool(comparison.get("agree")) and run.result == "PASS"

    if sensitivity:
        out["sensitivity"] = _sensitivity(config, graph, traces, work)
    return out


def _sensitivity(config: model.TlaConfig, graph: conformance.Graph, traces: list[dict[str, Any]], work: Path) -> dict[str, Any]:
    """The comparison must NOT agree with a spec carrying a seeded defect (else it proves nothing)."""
    mutation = "replay_before_auth"
    label = f"{config.name}_seeded"
    _write(work, generate.dump_files(config, mutation=mutation, label=label))
    dump = tlc.run_tlc(work / f"MCD_{label}.tla", work / f"MCD_{label}.cfg", work, workers=1)
    graph_result = conformance.compare(graph, conformance.parse_dump(dump.output)) if dump.result == "PASS" else {"agree": True}
    _write(work, generate.trace_files(config, TRACE_OPS, traces, mutation=mutation, label=label))
    trace_run = tlc.run_tlc(work / f"MCT_{label}.tla", work / f"MCT_{label}.cfg", work, workers=1)
    return {"seeded_defect": mutation, "state_graph_detected": not graph_result["agree"],
            "state_graph_outcome_disagreements": graph_result.get("outcome_disagreements"),
            "trace_validation_detected": trace_run.result == "VIOLATION", "detected": (not graph_result["agree"]) and trace_run.result == "VIOLATION"}


def environment_report() -> dict[str, Any]:
    lock = tlc.load_lock()
    return {"platform": platform.platform(), "python": platform.python_version(), "java": tlc.java_banner(),
            "tlc": {"release": lock["release"], "sha256": lock["sha256"], "url": lock["url"]}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--work", type=Path, default=ROOT / ".tmp" / "tla")
    parser.add_argument("--no-fetch", action="store_true", help="never download the pinned jar")
    parser.add_argument("--deep", action="store_true", help="also model-check `candidate` with 5 operation ids (~2 min)")
    parser.add_argument("--configs", default="", help="comma-separated subset of configuration names")
    parser.add_argument("--random", type=int, default=200, dest="random_count", help="random traces per safe configuration")
    parser.add_argument("--seed", default="eija-tla-v1")
    parser.add_argument("--snapshot", type=Path, help="also copy the report here (a committed evidence snapshot)")
    args = parser.parse_args(argv)

    report: dict[str, Any] = {"kind": "tlc_model_check", "schema": "eija.formal.tla.v1", "lane": "tla", "created_at": _now(),
                              "claim": "Safety invariants of the excursion workflow and commit protocol hold in the TLC-explored "
                                       "state space of the declared bounds, and the runtime agrees with the model on the compared behaviours.",
                              "limitations": LIMITATIONS}
    problems = generate.drift()
    report["generated_files"] = {"count": len(generate.generated_files()), "drift": problems}
    try:
        tlc.ensure_jar(fetch=not args.no_fetch)
        report["environment"] = environment_report()
    except tlc.NotRun as exc:
        report.update(result="NOT_RUN", reason=str(exc), environment={"platform": platform.platform(), "python": platform.python_version()})
        return _finish(report, args, 0 if not problems else 1)
    except tlc.ToolError as exc:
        report.update(result="FAIL", reason=str(exc))
        return _finish(report, args, 1)

    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    wanted = {n for n in args.configs.split(",") if n}
    configs = [c for c in model.configs() if not wanted or c.name in wanted]
    entries: list[dict[str, Any]] = []
    counterexamples: list[str] = []
    started = time.monotonic()
    for config in configs:
        print(f"[tla] model-check {config.name}", flush=True)
        entry, markdown = model_check(config, work)
        entries.append(entry)
        counterexamples += [markdown] if markdown else []
        print(f"[tla]   {entry['tlc']['result']} states={entry['tlc']['distinct_states']} depth={entry['tlc']['depth']} passed={entry['passed']}", flush=True)
    if args.deep:
        candidate = next(c for c in model.configs() if c.name == "candidate")
        print("[tla] model-check candidate (deep, 5 operation ids)", flush=True)
        entry, _ = model_check(candidate, work, ops=5, workers=4)
        entry["name"] = "candidate_deep"
        entries.append(entry)
    report["model_checking"] = entries

    conformance_entries: dict[str, Any] = {}
    for config in configs:
        if config.negative_control:
            continue
        print(f"[tla] conformance {config.name}", flush=True)
        conformance_entries[config.name] = conformance_for(config, work, seed=args.seed, random_count=args.random_count,
                                                            sensitivity=config.name == "candidate")
        print(f"[tla]   agree={conformance_entries[config.name].get('agree')}", flush=True)
    report["conformance"] = conformance_entries
    report["total_seconds"] = round(time.monotonic() - started, 1)

    ok = (not problems and all(e["passed"] for e in entries) and all(c.get("agree") for c in conformance_entries.values())
          and all(c.get("sensitivity", {}).get("detected", True) for c in conformance_entries.values()))
    report["result"] = "PASS" if ok else "FAIL"
    if counterexamples:
        path = args.out.with_name("tla-counterexamples.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(("# TLC counterexamples (negative controls)\n\n" + "\n".join(counterexamples)).encode("utf-8"))
        report["counterexamples_file"] = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    return _finish(report, args, 0 if ok else 1)


def _finish(report: dict[str, Any], args: argparse.Namespace, code: int) -> int:
    text = json.dumps(report, indent=2, sort_keys=False, default=str) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(text.encode("utf-8"))
    if args.snapshot:
        args.snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.snapshot.write_bytes(text.encode("utf-8"))
    print(f"[tla] result={report['result']} report={args.out}")
    if report["result"] == "NOT_RUN":
        print(f"[tla] NOT_RUN: {report['reason']}")
    return code


if __name__ == "__main__":
    sys.exit(main())
