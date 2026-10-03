"""Agent integration lane: MCP server surface and agent static checks (ADR-0041)."""
import subprocess
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["full"])
def agents(session: nox.Session) -> None:
    """MCP tools/resources via the SDK's in-memory session and stdio start-up, plus the SDK-free static checks.

    The SDK-free checks (owner-operation lint, config snippets, docs and skills drift) always run. The SDK tests
    need the `agents` extra; without it the session runs the static checks and then SKIPS with a NOT_RUN reason:
    nox reports a plain success as a pass, so a session whose MCP behaviour tests did not run must not end in one.
    """
    tests = ["tests/test_agent_static.py"]
    sdk = subprocess.run([PYTHON, "-c", "import mcp"], capture_output=True, check=False).returncode == 0
    if sdk:
        tests.append("tests/test_mcp_server.py")
    session.run(PYTHON, "-m", "pytest", "-q", *tests, *session.posargs)
    if not sdk:
        session.skip('NOT_RUN: the MCP SDK is not installed, so tests/test_mcp_server.py did not run (the static checks passed); '
                     'pip install -e ".[agents]"')
