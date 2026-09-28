"""Visual lane: diagrams generated from the executable model must not drift, and must render."""
import os
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


def allow_not_run() -> bool:
    """Dev machines without Chrome, Java or a PlantUML jar can opt out with EIJA_ALLOW_NOT_RUN=1. Off by default:
    a release run that could not run a renderer must not look green."""
    return os.environ.get("EIJA_ALLOW_NOT_RUN") == "1"


@nox.session(python=False, tags=["fast", "full"])
def diagrams_drift(session: nox.Session) -> None:
    """docs/diagrams/*.md equal a fresh render of the executable model (no browser, no network)."""
    session.run(PYTHON, "scripts/generate_diagrams.py", "--check")


@nox.session(python=False, tags=["release"])
def diagrams_syntax(session: nox.Session) -> None:
    """Every emitted diagram is accepted by the real renderers, and the real-browser negative controls pass.
    A renderer that could not run (Chrome, Playwright, Java, the PlantUML jar via EIJA_PLANTUML_JAR) is NOT_RUN and
    FAILS this session (exit 3) unless EIJA_ALLOW_NOT_RUN=1 is set; the JSON on stdout still says NOT_RUN."""
    env = {"EIJA_BROWSER_TESTS": "1"} | ({"EIJA_ALLOW_NOT_RUN": "1"} if allow_not_run() else {})
    session.run(PYTHON, "-m", "pytest", "-q", "-m", "browser", "tests/test_syntax_validator.py", env=env)
    session.run(PYTHON, "scripts/validate_diagram_syntax.py", *(["--allow-not-run"] if allow_not_run() else []), *session.posargs)


@nox.session(python=False, tags=["release"])
def visual_screenshots(session: nox.Session) -> None:
    """Drive the real Studio in Chrome to the Visual view, assert no CSP violation, refresh docs/assets/*.png.
    Exit code 3 means NOT_RUN (Chrome or Playwright missing): the session fails unless EIJA_ALLOW_NOT_RUN=1."""
    session.run(PYTHON, "scripts/capture_visual_screenshots.py", success_codes=[0, 3] if allow_not_run() else [0])
