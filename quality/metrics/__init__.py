"""Quantitative metrics and models for EIJA Studio (capability lane: metrics).

Every collector in this package measures the checked-out source tree and the currently
installed environment. A collector result states what it measured and what it did NOT
measure (a static proxy is never presented as a runtime guarantee, and a missing
prerequisite reports NOT_RUN, never PASS). See docs/metrics/README.md for the formulas,
their sources, and the honesty conventions this package follows.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "eija_studio"
SCHEMA_VERSION = "eija.metrics.v1"
