"""Quality gates as nox sessions (https://nox.thea.codes).

Sessions run inside the already-activated project environment (`python=False`): no per-session
virtualenv rebuilds. Each capability lane contributes its own module under `quality/sessions/`, so
adding a gate never edits a shared file. Tags select a tier:

    nox -t fast      # seconds; pre-commit
    nox -t full      # the PR gate; pre-push
    nox -t release   # maintainer release evidence (slow, may need Docker/Java/Chromium)

Heavy sessions run serially by design (the reference PC has 16 GB RAM).
"""
from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path

import nox

sys.path.insert(0, str(Path(__file__).resolve().parent))  # nox does not put the project root on sys.path
import quality.sessions  # noqa: E402

nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_missing_interpreters = True

# nox runs the selected sessions in registration order. `metrics` aggregates the reports the other lanes write
# (LANE-01), so it registers last: otherwise it judges the reports a *previous* run left behind (#206).
AGGREGATORS = ("metrics",)
modules = sorted((m.name for m in pkgutil.iter_modules(quality.sessions.__path__)), key=lambda name: name in AGGREGATORS)
for name in modules:
    importlib.import_module(f"quality.sessions.{name}")
