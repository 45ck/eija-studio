"""Read the Bend lane's report (``verification/bend``) into a ``bend_proof`` artifact (ADR-0146)."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

from eija_studio.domain.formal import FormalArtifact
from eija_studio.domain.formal_bend import MODEL_FILES, PROTOCOL, SPEC
from eija_studio.domain.models import Workflow

from .common import NotRun, Report, collect_from, lf_sha256

KIND = SPEC.kind
REPORTS = ("reports/formal/bend.json", "verification/bend/evidence/bend.json")
PREREQUISITE = "Docker with the pinned Bend image: python verification/bend/bend_runner.py"
ASSUMPTIONS = (
    "The Bend model is generated from the executable Workflow by verification/bend/bend_generate.py; the generator is "
    "trusted, and the kernel confirms only that regenerating from the current workflows gives the proved text.",
    "Bend's proof kernel (BendTT, run with --verdict) is trusted: no proof certificate leaves the container, so its "
    "answer is accepted under the sealed local producer.",
    "The laws in LAWS.bend are authored by the same team as the model; they are not an independently blinded specification.",
    "Actors are the fixture directory of the runtime matrix; roles and assignments are inputs the laws quantify over.",
)


def _regenerated_sha(root: Path, baseline: Workflow, candidate: Workflow) -> str | None:
    """SHA-256 of ``main.bend`` regenerated from the CURRENT workflows by the lane's own generator, or None."""
    path = root / "verification" / "bend" / "bend_generate.py"
    saved = list(sys.path)  # the generator prepends the checkout's src/ to sys.path on import; do not leak that
    try:
        spec = importlib.util.spec_from_file_location("eija_formal_bend_generate", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return hashlib.sha256(module.render_main({"Baseline": baseline, "Candidate": candidate}).encode("utf-8")).hexdigest()
    except (ImportError, OSError, ValueError, KeyError, AttributeError):
        return None  # the generator is missing or refuses these workflows: the binding is then UNKNOWN, not assumed
    finally:
        sys.path[:] = saved


def _control(c: dict[str, Any]) -> dict[str, Any]:
    out = {"name": c["name"], "model_well_formed": c["model_well_formed"], "full_run": {"result": c["full_run"]["result"]},
           "failing_laws": c["failing_laws"], "passing_laws": c["passing_laws"],
           "kernel_policy_findings": c.get("kernel_policy_findings") or []}
    out.update({k: c[k] for k in ("counterexample", "effect_probe") if k in c})
    return out


def _proof(proof: dict[str, Any]) -> dict[str, Any]:
    return {"command": proof["command"], "model_check": {"result": proof["model_check"]["result"]},
            "full_run": {"result": proof["full_run"]["result"]},
            "laws": [{"name": x["name"], "result": x["result"]} for x in proof["laws"]],
            "laws_without_proof": proof["laws_without_proof"]}


def _conformance(conf: dict[str, Any]) -> dict[str, Any]:
    return {"matrix": {k: conf["matrix"][k] for k in ("cells", "agree", "mismatches", "unmatched_cells")},
            "witnesses": [{k: w[k] for k in ("name", "bend_final_state", "python_final_state", "expected_final_state")}
                          for w in conf["witnesses"]]}


def extract(report: Report, root: Path, baseline: Workflow, candidate: Workflow) -> dict[str, Any]:
    """Copy the raw fields the kernel checks. No verdict is computed here."""
    body = report.body
    if body.get("status") == "NOT_RUN":
        raise NotRun(str(body.get("reason", "the Bend runner reported NOT_RUN")), PREREQUISITE)
    if body.get("kind") != KIND:
        raise NotRun(f"{report.origin} is not a bend_proof report", report.origin)
    base = root / "verification" / "bend"
    current = {name: digest for name in MODEL_FILES if (digest := lf_sha256(base / name)) is not None}
    return {
        "protocol": PROTOCOL,
        "tool": {k: body["tool"][k] for k in ("bend_version", "bend_commit", "image_id", "image_tag", "base_image", "lean_version")},
        "mode": body["mode"],
        "model": {"semantic_hash": body["model"]["semantic_hash"], "files": body["model"]["files"]},
        "binding": {"current_files_sha256": current, "regenerated_main_bend_sha256": _regenerated_sha(root, baseline, candidate)},
        "proof": _proof(body["proof"]),
        "negative_controls": [_control(c) for c in body["negative_controls"]],
        "conformance": _conformance(body["conformance"]),
        "assumptions": list(ASSUMPTIONS), "limitations": list(body["limits"]),
        "reported": {"verdict": body["status"], "checks": [{"id": k, "status": v} for k, v in sorted(body.get("summary", {}).items())]},
        "source": {"origin": report.origin},
    }


def collect(root: Path, baseline: Workflow, candidate: Workflow) -> list[FormalArtifact]:
    missing = NotRun("no Bend report found (neither a fresh run nor the committed snapshot)", PREREQUISITE)
    return collect_from(KIND, PROTOCOL, root, REPORTS, missing, lambda r: extract(r, root, baseline, candidate))
