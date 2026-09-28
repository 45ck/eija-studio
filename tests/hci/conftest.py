"""HCI test plumbing.

* `quality/` is engineering tooling outside the shipped package; pyproject's pytest `pythonpath` puts the repo root on sys.path.
* Browser tests carry the `hci` marker and are OPT-IN (`pytest -m hci`, `nox -s hci` or EIJA_HCI=1):
  the default `pytest -q` stays a fast kernel suite. Opted in but Chrome/Playwright unusable -> the
  tests are skipped with a reason starting `NOT_RUN`, which is never a pass.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from quality.hci import journey, report

ROOT = Path(__file__).resolve().parents[2]


def pytest_configure(config):
    config.addinivalue_line("markers", "hci: drives real Chrome through the Studio journey (opt-in; NOT_RUN if Chrome/Playwright is unavailable)")


def _selected(config) -> bool:
    expr = config.getoption("markexpr") or ""
    return os.environ.get("EIJA_HCI") == "1" or ("hci" in expr and "not hci" not in expr)


def pytest_collection_modifyitems(config, items):
    if _selected(config):
        return
    skip = pytest.mark.skip(reason="NOT_RUN: opt-in browser tests; run `pytest -m hci` or `nox -s hci`")
    for item in items:
        if item.get_closest_marker("hci"):
            item.add_marker(skip)


@pytest.fixture(scope="session")
def hci_report():
    """One full instrumented run (Chrome, real `eija serve`), shared by every browser test."""
    ok, detail = journey.prerequisites()
    if not ok:
        pytest.skip("NOT_RUN: " + detail)
    repeats = int(os.environ.get("EIJA_HCI_REPEATS", "3"))
    raw = journey.collect(repeats=repeats)
    rep = report.build_report(raw)
    out = Path(os.environ.get("EIJA_HCI_OUT", ROOT / "reports" / "hci"))
    report.write_text(out / "report.json", report.dumps(rep))
    report.write_text(out / "REPORT.md", report.render_markdown(rep))
    return {"raw": raw, "report": rep}
