"""Hypothesis profiles, example-count evidence and the ``reports/testing/property.json`` writer.

Loaded by ``conftest.py`` only when the ``testing`` extra is installed.

Profiles (select with ``EIJA_HYPOTHESIS_PROFILE``):

* ``ci`` (default): ``derandomize=True``. The same examples run on every machine and every run, so a
  red gate is reproducible and a green gate is not luck. Small ``max_examples`` (see
  ``property_support.SCALE``); the database is not consulted because a derandomized run is a fixed set.
* ``deep``: random seeds, 10x the examples, failures saved to ``.hypothesis/`` and replayed by later
  runs. Used by the release tier (``nox -s property_deep``). It looks for bugs; it is not reproducible.

The report is written only when ``EIJA_PROPERTY_REPORT`` names a file, so that an ad-hoc ``pytest -k``
run never overwrites the evidence of a full run.
"""
from __future__ import annotations

import json
import os
import platform
import sys
from collections import Counter
from importlib import metadata
from pathlib import Path

import pytest

from hypothesis import HealthCheck, settings  # noqa: E402
from hypothesis.database import DirectoryBasedExampleDatabase  # noqa: E402
from hypothesis.statistics import collector  # noqa: E402

from . import property_support as support  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PROFILE = os.environ.get("EIJA_HYPOTHESIS_PROFILE", "ci")
_COMMON = dict(deadline=None, print_blob=True,
               suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.filter_too_much])

settings.register_profile("ci", settings(derandomize=True, database=None, **_COMMON))
settings.register_profile("deep", settings(derandomize=False, database=DirectoryBasedExampleDatabase(ROOT / ".hypothesis" / "examples"),
                                           **_COMMON))
if PROFILE not in support.SCALE:
    raise pytest.UsageError(f"EIJA_HYPOTHESIS_PROFILE must be one of {sorted(support.SCALE)}, got {PROFILE!r}")
settings.load_profile(PROFILE)

_RESULTS: dict[str, dict] = {}


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "property: Hypothesis property-based or stateful test (docs/testing/property-based.md)")


def _requested(config: pytest.Config) -> bool:
    """The property suite takes minutes, so a bare ``pytest`` (the fast kernel suite) reports it as
    skipped rather than running it. It runs when asked for: ``pytest tests/property``, ``-m property``,
    a chosen profile, or ``nox -s property`` / ``nox -s property_deep``."""
    if os.environ.get("EIJA_HYPOTHESIS_PROFILE") or os.environ.get("EIJA_PROPERTY_REPORT"):
        return True
    if any("property" in str(arg).replace("\\", "/") for arg in config.args):
        return True
    return "property" in (config.getoption("markexpr") or "")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    here = Path(__file__).parent
    skip = pytest.mark.skip(reason="property suite not requested (minutes): run `nox -s property` or `pytest tests/property`")
    for item in items:
        if Path(str(item.path)).is_relative_to(here):
            item.add_marker(pytest.mark.property)
            if not _requested(config):
                item.add_marker(skip)


def _count_cases(stats: dict) -> dict:
    """Count the test cases Hypothesis executed, by phase and status (valid / invalid / overrun / interesting)."""
    by_status: Counter[str] = Counter()
    for phase in ("reuse-phase", "generate-phase", "shrink-phase"):
        for case in stats.get(phase, {}).get("test-cases", []):
            by_status[f"{phase.split('-')[0]}:{case['status']}"] += 1
    generated = sum(v for k, v in by_status.items() if k.startswith("generate:"))
    return {"generated": generated, "valid_generated": by_status.get("generate:valid", 0),
            "by_phase_status": dict(sorted(by_status.items())), "stopped_because": stats.get("stopped-because", "")}


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_call(item: pytest.Item):
    """Record Hypothesis statistics for every test in this directory, chaining to any existing collector
    (the pytest plugin's ``--hypothesis-show-statistics`` keeps working)."""
    previous = collector.value

    def note(stats: dict) -> None:
        _RESULTS[item.nodeid] = _count_cases(stats)
        if previous is not None:
            previous(stats)

    with collector.with_value(note):
        yield


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when == "call" and report.nodeid in _RESULTS:
        _RESULTS[report.nodeid]["outcome"] = report.outcome


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    target = os.environ.get("EIJA_PROPERTY_REPORT")
    if not target or not _RESULTS:
        return
    tests = dict(sorted(_RESULTS.items()))
    report = {
        "schema": "eija.testing.property.v1",
        "profile": PROFILE,
        "derandomized": settings.get_profile(PROFILE).derandomize,
        "scale": support.SCALE[PROFILE],
        "platform": {"python": platform.python_version(), "system": platform.platform(), "executable": Path(sys.executable).name},
        "versions": {name: metadata.version(name) for name in ("hypothesis", "hypothesis-jsonschema", "jsonschema", "pydantic", "pytest")},
        "status": "PASS" if int(exitstatus) == 0 else "FAIL",
        "exit_status": int(exitstatus),
        "totals": {"tests": len(tests), "generated_examples": sum(t["generated"] for t in tests.values()),
                   "valid_examples": sum(t["valid_generated"] for t in tests.values())},
        "stateful_outcomes": dict(sorted(support.MAIN_OUTCOMES.items())),
        "tests": tests,
        "limits": ["Example counts are cases Hypothesis executed, not proof of absence of defects.",
                   "The reference model shares authorship and vocabulary with the kernel; it is a differential oracle, not a blinded holdout."],
    }
    path = Path(target)
    path = path if path.is_absolute() else ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
