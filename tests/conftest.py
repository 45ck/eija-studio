import tempfile
from pathlib import Path

import pytest
from eija_studio.domain.models import OWNER
from kernel_support import HARNESS_MARK, approve, harness_identity, harness_studio  # noqa: F401 - re-exported for old imports

try:
    from hypothesis import settings
except ImportError:
    settings = None

ROOT = Path(__file__).resolve().parents[1]


def pytest_configure(config):
    # The system temp directory may sit on a slow disk (the reference PC: an HDD, ~1.2 s per durable
    # SQLite commit). Keep pytest's numbered, concurrency-safe temp dirs inside the checkout instead.
    if not config.option.basetemp:
        (ROOT / ".tmp").mkdir(exist_ok=True)
        tempfile.tempdir = str(ROOT / ".tmp")
    _derandomize_hypothesis(config)


def _derandomize_hypothesis(config):
    """Every Hypothesis test that does not pick its own profile runs the same examples in every process, so a
    parallel (pytest-xdist) run, a serial run and another machine agree. tests/property chooses its own profile
    (ci: derandomized, deep: random) when it is collected, after this hook; an explicit --hypothesis-profile wins."""
    if settings is None:  # the testing extra is optional; its absence is reported where it matters
        return
    if not config.getoption("hypothesis_profile", None):
        settings.register_profile("eija-default", derandomize=True, database=None, deadline=None)
        settings.load_profile("eija-default")


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
