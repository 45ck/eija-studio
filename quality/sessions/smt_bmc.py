"""Formal lane `smt-bmc`: Z3 policy-soundness proof and bounded model checking of the real runtime.

Reports land in reports/formal/ (gitignored). A missing prerequisite is NOT_RUN, never a pass: in the `full`
tier the session is reported as skipped (so a machine without the extra can still run the tier, visibly); in
the `release` tier a missing z3-solver FAILS the session. Extra needed: `pip install -e ".[dev,smt]"`.

Each gate also runs the `formal`-marked pytest tests of its lane (`pytest -m formal`): those are the slow
negative controls, deselected from the default pytest run so the fast tier and the coverage run stay quick.
"""
import importlib.util
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
Z3_MISSING = "NOT_RUN: z3-solver is not installed (pip install -e .[smt])"


@nox.session(python=False, tags=["full"])
def formal_smt(session: nox.Session) -> None:
    """Z3 proof that check_policy admits only authority-preserving candidates (+ sampled faithfulness + negative controls)."""
    if importlib.util.find_spec("z3") is None:
        session.run(PYTHON, "-m", "verification.smt", success_codes=[3])  # writes a NOT_RUN report
        session.skip(Z3_MISSING)
    session.run(PYTHON, "-m", "verification.smt", *session.posargs)
    session.run(PYTHON, "-m", "verification.smt.laws")  # WBS 1.4: generated laws, every pack; hand <=> generated where hand-encoded
    session.run(PYTHON, "-m", "pytest", "-q", "-m", "formal", "tests/test_formal_smt.py", "tests/test_smt_laws_gen.py")


@nox.session(python=False, tags=["release"])
def formal_smt_release(session: nox.Session) -> None:
    """Release tier: the same proof with a 4x larger differential sample; a missing z3-solver fails instead of skipping."""
    session.run(PYTHON, "-m", "verification.smt", "--differential-mutants", "6000", "--differential-fresh", "2000",
                *session.posargs)  # exit status 3 (NOT_RUN) fails the session


@nox.session(python=False, tags=["full"])
def bmc(session: nox.Session) -> None:
    """Bounded model check of the real runtime to depth 6 (baseline + recommendation candidate), with seeded-fault self-test."""
    session.run(PYTHON, "-m", "verification.bmc", "--depth", "6", "--tier", "full", *session.posargs)
    session.run(PYTHON, "-m", "pytest", "-q", "-m", "formal", "tests/test_formal_bmc.py")


@nox.session(python=False, tags=["release"])
def bmc_deep(session: nox.Session) -> None:
    """Release-tier bounded model check: depth 8 over all three workflow variants (several minutes)."""
    session.run(PYTHON, "-m", "verification.bmc", "--depth", "8", "--tier", "release", *session.posargs)
