"""Shared helpers of the kernel tests (harness identity, studio factory, owner approval).

They live here and not in conftest.py because every directory without an __init__.py names its conftest
`conftest`, so `from conftest import ...` resolves to whichever conftest pytest imported last (collection order
decides). A uniquely named module cannot be shadowed. tests/conftest.py re-exports them for its fixtures.
"""
from pathlib import Path

from eija_studio.adapters.identity import identity as measured_identity
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import OWNER

HARNESS_MARK = "pytest-harness"


def harness_identity() -> dict:
    """Kernel tests exercise the behaviour of the source under test. Whether those bytes are the
    owner-stamped release is a separate release gate (scripts/verify_release.py), never assumed here.
    The `identity_source` mark distinguishes this from a measured production identity."""
    return measured_identity() | {"trusted_fixture": True, "identity_source": HARNESS_MARK}


def harness_studio(workspace: Path):
    s = build_studio(workspace)
    s.identity_provider = harness_identity
    return s


def approve(studio, case):
    packet = studio.view(case["id"])["packet"]
    return studio.approve(case["id"], case["version"], packet["subject_hash"],
        {q["id"]: q["expected"] for q in packet["questions"]}, True, OWNER)
