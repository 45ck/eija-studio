"""Formal lane `smt-bmc`: Z3 policy-soundness proof and bounded model checking of the real runtime.

Reports land in reports/formal/ (gitignored). A missing prerequisite is NOT_RUN (the session is
reported as skipped), never a pass. Extra needed: `pip install -e ".[smt]"` (z3-solver, pinned).
"""
import importlib.util
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["full"])
def formal_smt(session: nox.Session) -> None:
    """Z3 proof that check_policy admits only authority-preserving candidates (+ faithfulness + negative controls)."""
    if importlib.util.find_spec("z3") is None:
        session.run(PYTHON, "-m", "verification.smt", success_codes=[3])  # writes a NOT_RUN report
        session.skip("NOT_RUN: z3-solver is not installed (pip install -e .[smt])")
    session.run(PYTHON, "-m", "verification.smt", *session.posargs)


@nox.session(python=False, tags=["full"])
def bmc(session: nox.Session) -> None:
    """Bounded model check of the real runtime to depth 6 (baseline + recommendation candidate), with seeded-fault self-test."""
    session.run(PYTHON, "-m", "verification.bmc", "--depth", "6", "--tier", "full", *session.posargs)


@nox.session(python=False, tags=["release"])
def bmc_deep(session: nox.Session) -> None:
    """Release-tier bounded model check: depth 8 over all three workflow variants (several minutes)."""
    session.run(PYTHON, "-m", "verification.bmc", "--depth", "8", "--tier", "release", *session.posargs)
