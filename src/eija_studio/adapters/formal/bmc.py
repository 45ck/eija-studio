"""Read the smt-bmc lane's bounded-model-check report (``python -m verification.bmc``) into a
``bounded_model_check`` artifact (ADR-0146)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from eija_studio.domain.formal import FormalArtifact
from eija_studio.domain.formal_bmc import PROTOCOL, SOURCES, SPEC

from .common import NotRun, Report, collect_from, current_sources

KIND = SPEC.kind
# Deepest first; every readable report becomes its own receipt, and the kernel decides which count.
REPORTS = ("reports/formal/bmc_deep.json", "reports/formal/bmc.json", "verification/bmc/evidence/bmc.json")
PREREQUISITE = "python -m verification.bmc (no extra dependency)"
SCHEMA = "eija.formal-report/v1"
MODEL_FIELDS = ("semantic_hash", "states", "transitions", "max_depth", "exhausted", "truncated",
                "expected_outcomes_unreached", "invariant_checks")


def extract(report: Report, root: Path) -> dict[str, Any]:
    """Copy the raw fields the kernel checks. No verdict is computed here."""
    body = report.body
    if body.get("kind") != KIND or body.get("schema") != SCHEMA:
        raise NotRun(f"{report.origin} is not a bounded_model_check report of schema {SCHEMA}", report.origin)
    res = body["results"]
    return {
        "protocol": PROTOCOL,
        "tool": {"name": body["tool"]["name"], "system_under_test": body["tool"]["system_under_test"]},
        "tier": body["tier"], "claim": body["claim"], "subject_function": body["subject"]["function"],
        "bounds": body["bounds"], "invariants": body["invariants"],
        "models": {name: {k: m[k] for k in MODEL_FIELDS} for name, m in res["models"].items()},
        "counterexamples": res["counterexamples"],
        "mutation_self_test": [{"mutant": r["mutant"], "detected": r["detected"]} for r in res["mutation_self_test"]],
        "binding": {"reported_sources_sha256_lf": body["subject"]["sources_sha256_lf"],
                    "current_sources_sha256_lf": current_sources(root, SOURCES)},
        "assumptions": body["assumptions"], "limitations": body["limitations"],
        "reported": {"verdict": body["verdict"], "checks": [{"id": c["id"], "status": c["status"]} for c in body["checks"]]},
        "source": {"origin": report.origin},
    }


def collect(root: Path) -> list[FormalArtifact]:
    missing = NotRun("no bounded-model-check report found: python -m verification.bmc has not been run here", PREREQUISITE)
    return collect_from(KIND, PROTOCOL, root, REPORTS, missing, lambda r: extract(r, root))
