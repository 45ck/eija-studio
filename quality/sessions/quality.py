"""Static-analysis, architecture, complexity, coverage and dependency-hygiene gates (ADR-0035).

Thresholds live in `pyproject.toml` (`[tool.ruff]`, `[tool.mypy]`, `[tool.importlinter]`,
`[tool.coverage.report]`, `[tool.deptry]`) and `quality/gates/complexity_baseline.json`, never in this file,
so a threshold change is one reviewable diff. Ratchet rule: thresholds tighten, never loosen. See
docs/quality/gates.md.
"""

import socket
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
ROOT = Path(__file__).resolve().parents[2]
# Files this lane owns and holds to `ruff format`. The kernel (src/, tests/, scripts/) is deliberately NOT
# reformatted because other lanes edit it in parallel, and other lanes' session modules are theirs to format.
FORMATTED = ["quality/gates", "quality/sessions/quality.py", "tests/test_quality_gates.py"]
LINT_IMPORTS = "from importlinter.cli import lint_imports_command; lint_imports_command()"


def _env() -> dict[str, str]:
    """Keep every tool's scratch space inside the checkout: the system TEMP may be a slow HDD."""
    scratch = ROOT / ".tmp"
    scratch.mkdir(exist_ok=True)
    return {"TMP": str(scratch), "TEMP": str(scratch)}


def _run(session: nox.Session, *args: str) -> None:
    session.run(PYTHON, "-m", *args, env=_env())


@nox.session(python=False, tags=["fast", "full"])
def lint(session: nox.Session) -> None:
    """Ruff lint (bugbear, bandit subset, simplify, pyupgrade, pylint subset); format check of lane files."""
    _run(session, "ruff", "check", ".", *session.posargs)
    _run(session, "ruff", "format", "--check", *FORMATTED)


@nox.session(python=False, tags=["fast", "full"])
def typecheck(session: nox.Session) -> None:
    """mypy: strict on eija_studio.domain and .application, default profile with a ratchet plan elsewhere."""
    _run(session, "mypy", *session.posargs)


# Tagged release until the providers package lands: the legacy adapters/providers.py calls os.killpg/SIGKILL
# behind a runtime os.name check that mypy cannot see. Promote to ["full"] afterwards.
@nox.session(python=False, tags=["release"])
def typecheck_win32(session: nox.Session) -> None:
    """mypy again as win32: Windows-only branches (subprocess creation flags, msvcrt) are invisible to the linux run."""
    _run(session, "mypy", "--platform", "win32", *session.posargs)


@nox.session(python=False, tags=["fast", "full"])
def architecture(session: nox.Session) -> None:
    """import-linter: layer order, vendor-free domain and application, adapters wired only by bootstrap."""
    # import-linter ships a console script but no `python -m` entry point; call its click command directly.
    session.run(PYTHON, "-c", LINT_IMPORTS, *session.posargs, env=_env())


@nox.session(python=False, tags=["fast", "full"])
def complexity(session: nox.Session) -> None:
    """xenon module/average rank ceilings plus the per-function ratchet."""
    _run(session, "xenon", "--max-average", "A", "--max-modules", "D", "src", "quality")
    _run(session, "quality.gates.complexity_ratchet", *session.posargs)


@nox.session(python=False, tags=["fast", "full"])
def dependencies(session: nox.Session) -> None:
    """deptry: every import is declared, every declared runtime dependency is used."""
    _run(session, "deptry", ".", *session.posargs)


@nox.session(python=False, tags=["full"])
def coverage(session: nox.Session) -> None:
    """Branch coverage of src/eija_studio with a ratcheted floor; reports go to reports/coverage/."""
    (ROOT / "reports" / "coverage").mkdir(parents=True, exist_ok=True)
    _run(
        session,
        "pytest",
        "-q",
        "--cov",
        "--cov-report=term:skip-covered",
        "--cov-report=xml",
        "--cov-report=html",
        *session.posargs,
    )  # fail_under comes from [tool.coverage.report]


def _pypi_reachable() -> bool:
    try:
        with socket.create_connection(("pypi.org", 443), timeout=5):
            return True
    except OSError:
        return False


@nox.session(python=False, tags=["release"])
def audit(session: nox.Session) -> None:
    """pip-audit of the measured runtime pins (requirements-tested.txt) against the PyPI advisory database.

    Needs network. Without it the session reports NOT_RUN, never PASS: an unchecked tree is not a clean one.
    """
    if not _pypi_reachable():
        print("NOT_RUN: pypi.org unreachable, so no advisory lookup happened. This is not a PASS.")
        session.skip("NOT_RUN: network unavailable for pip-audit")
    _run(
        session, "pip_audit", "-r", "requirements-tested.txt", "--no-deps", "--disable-pip", *session.posargs
    )
