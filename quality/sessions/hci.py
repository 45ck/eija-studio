"""HCI-law instrumentation gates (lane: hci). See docs/hci/README.md and ADR-0039/0040."""
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["fast", "full"])
def hci_docs(session: nox.Session) -> None:
    """Drift check: docs/hci/REPORT.md must equal the rendering of docs/hci/report.snapshot.json (no browser)."""
    session.run(PYTHON, "-m", "quality.hci", "check")


@nox.session(python=False, tags=["full", "release"])
def hci(session: nox.Session) -> None:
    """Drive real Chrome through the owner journey against a real `eija serve`; enforce the HCI budgets.

    Writes reports/hci/{report.json,REPORT.md}. Chrome, Playwright or axe unavailable -> the session is
    SKIPPED with a NOT_RUN reason (nox lists it as skipped): a missing prerequisite is never a pass.
    """
    out = session.run(PYTHON, "-m", "quality.hci", "prereq", silent=True, success_codes=[0, 3])
    if out and out.strip().startswith("NOT_RUN"):
        session.skip(out.strip())
    session.log(out.strip() if out else "")
    session.run(PYTHON, "-m", "pytest", "-m", "hci", "-q", "tests/hci", *session.posargs)
