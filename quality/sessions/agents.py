"""Agent integration lane: MCP server surface, client config and docs drift (ADR-0041)."""
import subprocess
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["full"])
def agents(session: nox.Session) -> None:
    """MCP tools/resources via the SDK's in-memory session, owner-operation absence, stdio start-up, docs drift.

    Needs the `agents` extra. Without it the gate reports NOT_RUN (skipped), never a pass.
    """
    if subprocess.run([PYTHON, "-c", "import mcp"], capture_output=True).returncode != 0:
        session.skip('NOT_RUN: the MCP SDK is not installed; run: pip install -e ".[agents]"')
    session.run(PYTHON, "-m", "pytest", "-q", "tests/test_mcp_server.py", *session.posargs)
