import pytest
from eija_studio.adapters.identity import identity as measured_identity
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import OWNER


def harness_identity() -> dict:
    """Kernel tests exercise the behaviour of the source under test. Whether those bytes are the
    owner-stamped release is a separate release gate (scripts/verify_release.py), never assumed here."""
    return measured_identity() | {"trusted_fixture": True}


@pytest.fixture
def studio(tmp_path):
    s = build_studio(tmp_path / "workspace")
    s.identity_provider = harness_identity
    return s

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
