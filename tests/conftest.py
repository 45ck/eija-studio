import tempfile
from pathlib import Path

import pytest
from eija_studio.adapters.identity import identity as measured_identity
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import OWNER

ROOT = Path(__file__).resolve().parents[1]
HARNESS_MARK = "pytest-harness"


def pytest_configure(config):
    # The system temp directory may sit on a slow disk (the reference PC: an HDD, ~1.2 s per durable
    # SQLite commit). Keep pytest's numbered, concurrency-safe temp dirs inside the checkout instead.
    if not config.option.basetemp:
        (ROOT / ".tmp").mkdir(exist_ok=True)
        tempfile.tempdir = str(ROOT / ".tmp")


def harness_identity() -> dict:
    """Kernel tests exercise the behaviour of the source under test. Whether those bytes are the
    owner-stamped release is a separate release gate (scripts/verify_release.py), never assumed here.
    The `identity_source` mark distinguishes this from a measured production identity."""
    return measured_identity() | {"trusted_fixture": True, "identity_source": HARNESS_MARK}


def harness_studio(workspace: Path):
    s = build_studio(workspace)
    s.identity_provider = harness_identity
    return s


@pytest.fixture
def open_studio():
    """Open (or reopen) a workspace with the harness identity."""
    return harness_studio


@pytest.fixture
def studio(tmp_path):
    return harness_studio(tmp_path / "workspace")

@pytest.fixture
def selected(studio):
    c = studio.create("Let teachers sign off excursions.")
    c = studio.propose(c["id"], c["version"])
    return studio.select(c["id"], c["version"], "recommend_only", OWNER)

@pytest.fixture
def verified(studio, selected):
    return studio.verify(selected["id"], selected["version"])


def approve(studio, case):
    packet = studio.view(case["id"])["packet"]
    return studio.approve(case["id"], case["version"], packet["subject_hash"],
        {q["id"]: q["expected"] for q in packet["questions"]}, True, OWNER)
