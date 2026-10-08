"""Reads the formal lanes' tool reports for the kernel (ADR-0146). Implements ``FormalEvidenceSource``.

Docker (Bend), z3-solver (SMT) and a saved run (bounded model check) are prerequisites of the TOOLS. When
one is missing the source returns a NOT_RUN artifact for that kind instead of nothing, so the review packet
shows why a kind is not green. This package imports only from the domain (never from ``eija_studio.application``) and never computes a verdict.
"""
from __future__ import annotations

from pathlib import Path

from eija_studio.domain.formal import FormalArtifact
from eija_studio.domain.evidence_kinds import KINDS
from eija_studio.domain.models import Workflow

from . import bend, bmc, smt
from .common import NotRun, not_run

# src/eija_studio/adapters/formal/__init__.py -> the repository root, when this is a source checkout.
CHECKOUT_ROOT = Path(__file__).resolve().parents[4]


class FormalReports:
    """Formal evidence from the reports of a source checkout: ``reports/formal`` and committed snapshots."""

    def __init__(self, root: Path | None = None):
        self.root = CHECKOUT_ROOT if root is None else Path(root)

    def collect(self, baseline: Workflow, candidate: Workflow) -> list[FormalArtifact]:
        if not (self.root / "verification").is_dir():
            why = NotRun("this installation is not a source checkout: there is no verification/ directory to read formal reports from",
                         "a source checkout (git clone) with the formal lanes")
            return [not_run(kind, spec.protocol, why) for kind, spec in KINDS.items()]
        return [*bend.collect(self.root, baseline, candidate), *smt.collect(self.root), *bmc.collect(self.root)]
