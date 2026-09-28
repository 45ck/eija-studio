import pytest
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import OWNER

@pytest.fixture
def studio(tmp_path):
    return build_studio(tmp_path / "workspace")

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
