#!/usr/bin/env python3
"""Strict release-wheel proof in a fresh offline venv; source review must already match.

Uses explicit --wheel, --source, --wheelhouse, --scratch-root and --out arguments.
Changed candidates use candidate_wheel_smoke.py; this release probe still requires
a trusted fixture and an eligible verified demo.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.candidate_wheel_smoke import main


if __name__ == "__main__":
    raise SystemExit(main(mode="release"))
