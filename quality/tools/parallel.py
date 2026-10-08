"""One switch for running pytest across cores in nox sessions (pytest-xdist).

Only the pytest-driven sessions that are CPU-bound and share nothing use it. The heavy formal sessions (Z3, TLC,
Bend, Chrome) stay serial: they are RAM-bound, and the reference PC has 16 GB shared with other sessions.

    EIJA_SERIAL=1          force a serial run (debugging a failure, or comparing against the parallel result)
    EIJA_XDIST_WORKERS=N   worker count, default 4 (the machine has 12 logical cores but shares RAM)

``--dist loadfile`` keeps every test of a file on one worker, so module-scoped fixtures and file-level state
(the stateful Hypothesis test and its post-run assertion) behave as they do serially. A missing xdist gives the
serial command, never an error: speed is an optimisation, not a prerequisite.
"""
from __future__ import annotations

import importlib.util
import os

DEFAULT_WORKERS = 4


def xdist_available() -> bool:
    return importlib.util.find_spec("xdist") is not None


def xdist_args() -> list[str]:
    """Extra pytest arguments for a parallel run, or [] when serial is requested or xdist is missing."""
    if os.environ.get("EIJA_SERIAL") == "1" or not xdist_available():
        return []
    workers = os.environ.get("EIJA_XDIST_WORKERS", str(DEFAULT_WORKERS))
    if not workers.isdigit() or int(workers) < 2:
        return []
    return ["-n", workers, "--dist", "loadfile"]
