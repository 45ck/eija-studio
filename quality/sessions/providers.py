"""Providers lane: contract suite over every proposal provider with a mocked runner, plus real-process tests.

Live calls are never a session. Run them by hand, one provider at a time, with explicit consent:
    python scripts/live_provider_smoke.py --provider claude --consent
"""
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
TESTS = ("tests/test_provider_contract.py", "tests/test_provider_process.py", "tests/test_providers.py")
DOCTOR = (
    "import json;from eija_studio.adapters.providers import create_provider\n"
    "LABEL={'READY':'READY','READY_LOGIN_UNVERIFIED':'READY (login unverified)'}\n"
    "for n in ('codex','claude','opencode','gemini'):\n"
    "    r=create_provider(n).doctor()\n"
    "    print(n,LABEL.get(r.get('status'),'NOT_RUN'),json.dumps({k:r[k] for k in r if k in ('cli_version','login','login_verified','reason','missing_flags')}))\n"
)


@nox.session(python=False, tags=["fast", "full"])
def providers_contract(session: nox.Session) -> None:
    """Shared contract for codex/claude/opencode/gemini (mocked runner), tree-kill on real processes, HTTP providers (mock transport).

    Needs the ``providers`` extra. Without psutil the reparented-descendant kill tests would SKIP and the gate would
    report green without exercising the psutil path, so a missing psutil fails the session instead of passing it.
    """
    session.run(PYTHON, "-c", "import psutil", silent=True)  # a non-zero exit fails the session; install with: pip install -e '.[providers]'
    session.run(PYTHON, "-m", "pytest", "-q", *TESTS, *session.posargs)


@nox.session(python=False, tags=["release"])
def providers_doctor(session: nox.Session) -> None:
    """Local, offline diagnostic of every CLI provider (version, flags, official login status). A missing CLI or login is NOT_RUN, never PASS.

    ``READY (login unverified)`` (Gemini) means a call may be attempted; the CLI has no login-status command to confirm it.
    """
    session.run(PYTHON, "-c", DOCTOR)
