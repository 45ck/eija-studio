"""Mutation analysis: does the kernel suite detect injected faults? (ADR-0033, ADR-0034)

Engine: cosmic-ray (OSS, native Windows). `mutation_quick` mutates only the protected policy
(`domain/policy.py`), the code that decides who may do what; `mutation` mutates every target module. Both
fail when a module's mutation score drops below the committed ratchet floor
(`quality/mutation/baseline.json`). Reports: `reports/mutation/summary.json` and `survivors.md`.

A missing engine reports NOT_RUN (nox "skipped"), never a pass.
"""
import importlib.util
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


def _require_engine(session: nox.Session) -> None:
    if importlib.util.find_spec("cosmic_ray") is None:
        session.skip("NOT_RUN: cosmic-ray is not installed (pip install -e '.[mutation]')")


@nox.session(python=False, tags=["full"])
def mutation_quick(session: nox.Session) -> None:
    """Authority-core mutation run (policy.py, two workers, a few minutes) gated by the ratchet floor."""
    _require_engine(session)
    session.run(PYTHON, "-m", "quality.mutation", "run", "--quick", "--check", *session.posargs)


@nox.session(python=False, tags=["release"])
def mutation(session: nox.Session) -> None:
    """Full mutation run over the domain and application authority/evidence modules, gated by the ratchet floor."""
    _require_engine(session)
    session.run(PYTHON, "-m", "quality.mutation", "run", "--check", *session.posargs)
