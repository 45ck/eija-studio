"""Name the tests that did not run because an optional extra is missing, and fail the run when that is not allowed.

A test that needs an extra (z3 for the SMT proofs, Playwright, mcp, ruff ...) skips without it, and pytest still exits
0. On 2026-11-13 two z3-only tests were red on `main` for hours because every local fast run, the merge evidence while
hosted CI cannot start, skipped them (docs/quality/inspections/2026-11-14-integration-review.md, I1). So:

* every run ends with a short "NOT_RUN for a missing extra" list, grouped by the missing module or extra, and
* with ``EIJA_REQUIRE_EXTRAS=1`` (hosted CI and the merge-evidence run in CONTRIBUTING.md) such a skip fails the run.

A skip counts when it came from ``pytest.importorskip`` (its reason starts "could not import") or when its reason names
an extra. Opt-in tests (``EIJA_BROWSER_TESTS``, Docker, Node) are chosen by the person running them and do not count.
"""
from __future__ import annotations

import os
import re
from collections import Counter

import pytest

_IMPORT = re.compile(r"could not import '([^']+)'(?:: No module named '([^']+)')?")
_EXTRA = re.compile(r"`?([a-z][a-z-]*)`? extra\b|extra `([a-z][a-z-]*)`")
REQUIRE = "EIJA_REQUIRE_EXTRAS"


def missing_extra(reason: str) -> str | None:
    """What a skip reason says is missing (a module or an extra), or None when the skip is not about an extra."""
    found = _IMPORT.search(reason)
    if found:
        return (found.group(2) or found.group(1)).split(".")[0]
    if "extra" not in reason:
        return None
    named = _EXTRA.search(reason)
    return next((g for g in named.groups() if g), "extra") if named else "extra"


def _skip_reason(report: pytest.TestReport) -> str:
    longrepr = report.longrepr
    return str(longrepr[2]) if isinstance(longrepr, tuple) and len(longrepr) == 3 else str(longrepr)


class ExtrasGuard:
    def __init__(self) -> None:
        self.missing: Counter[str] = Counter()

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.skipped and not hasattr(report, "wasxfail"):
            what = missing_extra(_skip_reason(report))
            if what is not None:
                self.missing[what] += 1

    @pytest.hookimpl
    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        if report.skipped:  # a module-level importorskip skips the whole file at collection
            what = missing_extra(_skip_reason(report))
            if what is not None:
                self.missing[what] += 1

    @pytest.hookimpl(trylast=True)
    def pytest_terminal_summary(self, terminalreporter, exitstatus, config) -> None:
        if not self.missing:
            return
        listed = ", ".join(f"{what} ({n})" for what, n in sorted(self.missing.items()))
        terminalreporter.write_sep("=", "NOT_RUN for a missing extra", yellow=True)
        terminalreporter.write_line(f"Skipped, not passed: {listed}. Install the extras in docs/quality/gates.md, "
                                    f"or set {REQUIRE}=1 to make this fail.")

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        if self.missing and os.environ.get(REQUIRE) == "1" and exitstatus == 0:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_configure(config: pytest.Config) -> None:
    if not hasattr(config, "workerinput"):  # the controller sees every report, also under xdist
        config.pluginmanager.register(ExtrasGuard(), "eija-extras-guard")
