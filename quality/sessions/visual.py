"""Visual lane: diagrams generated from the executable model must not drift, and must render."""
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["fast", "full"])
def diagrams_drift(session: nox.Session) -> None:
    """docs/diagrams/*.md equal a fresh render of the executable model (no browser, no network)."""
    session.run(PYTHON, "scripts/generate_diagrams.py", "--check")


@nox.session(python=False, tags=["release"])
def diagrams_syntax(session: nox.Session) -> None:
    """Every emitted diagram is accepted by the real renderers. A missing Chrome/Java/jar prints NOT_RUN, never PASS.
    Set EIJA_PLANTUML_JAR to a PlantUML jar to include PlantUML; pass `-- --require` to make NOT_RUN fail (exit 3)."""
    session.run(PYTHON, "scripts/validate_diagram_syntax.py", *session.posargs)


@nox.session(python=False, tags=["release"])
def visual_screenshots(session: nox.Session) -> None:
    """Drive the real Studio in Chrome to the Visual view, assert no CSP violation, refresh docs/assets/*.png.
    Exit code 3 means NOT_RUN (Chrome or Playwright missing) and is reported, not hidden."""
    session.run(PYTHON, "scripts/capture_visual_screenshots.py", success_codes=[0, 3])
