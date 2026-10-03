"""Read the smt-bmc lane's Z3 report (``python -m verification.smt``) into an ``smt_proof`` artifact (ADR-0146)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from eija_studio.domain.formal import FormalArtifact
from eija_studio.domain.evidence_kinds import SMT_PROOF as SPEC
from eija_studio.domain.evidence_kinds import SMT_SOURCES as SOURCES

from .common import NotRun, Report, collect_from, current_sources

KIND = SPEC.kind
PROTOCOL = SPEC.protocol
REPORTS = ("reports/formal/smt.json", "verification/smt/evidence/smt.json")
PREREQUISITE = "z3-solver (pip install -e .[smt]) and python -m verification.smt"
SCHEMA = "eija.formal-report/v1"


def _witness(row: dict[str, Any] | None) -> dict[str, Any] | None:
    """The counterexample workflow of a leave-one-out row, reduced to its transitions."""
    if row is None or type(row.get("witness")) is not dict:
        return None
    transitions = [{"action": t["action"], "role": t["role"], "from": t["from_state"], "to": t["to_state"]}
                   for t in row["witness"]["transitions"]]
    return {"violated_invariants": row.get("violated_invariants"), "transitions": transitions}


def _controls(loo: dict[str, Any]) -> dict[str, Any]:
    rows = {r["clause"]: r for r in loo["rows"]}
    named = [{"remove": c["remove"], "expect_violation_of": c["expect_violation_of"],
              "counterexample_found": c["counterexample_found"], "witness": _witness(rows.get(c["remove"]))}
             for c in loo["named_controls"]]
    return {"named": named, "unknown": loo["unknown"], "inconsistent_witnesses": loo["inconsistent_witnesses"]}


def _accepted(acc: dict[str, Any]) -> dict[str, Any]:
    return {"enumeration_complete": acc["enumeration_complete"], "count": acc["count"],
            "equals_kernel_reachable_set": acc["equals_kernel_reachable_set"], "inconsistent_models": acc["inconsistent_models"],
            "semantic_hashes": sorted(x["semantic_hash"] for x in acc["accepted"])}


def extract(report: Report, root: Path) -> dict[str, Any]:
    """Copy the raw fields the kernel checks. No verdict is computed here."""
    body = report.body
    if body.get("verdict") == "NOT_RUN":
        raise NotRun(str(body.get("reason", "the SMT run reported NOT_RUN")), PREREQUISITE)
    if body.get("kind") != KIND or body.get("schema") != SCHEMA:
        raise NotRun(f"{report.origin} is not an smt_proof report of schema {SCHEMA}", report.origin)
    res, diff, acc = body["results"], body["results"]["differential"], body["results"]["accepted_set"]
    return {
        "protocol": PROTOCOL,
        "tool": {k: body["tool"][k] for k in ("name", "package_version", "z3")},
        "claim": body["claim"], "subject_function": body["subject"]["function"], "bounds": body["bounds"],
        "assumptions": body["assumptions"], "limitations": body["limitations"],
        "invariants": [{k: x[k] for k in ("id", "status", "counterexample") if k in x} for x in res["invariants"]],
        "non_vacuity": res["non_vacuity"],
        "accepted_set": _accepted(acc),
        "differential": {k: diff[k] for k in ("seed", "candidates", "code_disagreements", "invariant_disagreements",
                                              "admitted_but_python_invariant_false", "clauses", "clauses_never_fired",
                                              "clauses_never_silent")},
        "negative_controls": _controls(res["leave_one_out"]),
        "binding": {"reported_sources_sha256_lf": body["subject"]["sources_sha256_lf"],
                    "current_sources_sha256_lf": current_sources(root, SOURCES)},
        "reported": {"verdict": body["verdict"], "checks": [{"id": c["id"], "status": c["status"]} for c in body["checks"]]},
        "source": {"origin": report.origin},
    }


def collect(root: Path) -> list[FormalArtifact]:
    missing = NotRun("no Z3 report found: python -m verification.smt has not been run here (or z3-solver is missing)", PREREQUISITE)
    return collect_from(KIND, PROTOCOL, root, REPORTS, missing, lambda r: extract(r, root))
