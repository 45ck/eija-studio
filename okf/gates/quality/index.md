# Gates defined in quality/sessions/quality.py

# Quality Gates

* [nox -s architecture](architecture.md) - import-linter: layer order, vendor-free domain and application, adapters wired only by bootstrap.
* [nox -s audit](audit.md) - pip-audit of the measured runtime pins (requirements-tested.txt) against the PyPI advisory database.
* [nox -s complexity](complexity.md) - xenon module/average rank ceilings plus the per-function ratchet.
* [nox -s coverage](coverage.md) - Branch coverage of src/eija_studio with a ratcheted floor; reports go to reports/coverage/.
* [nox -s dependencies](dependencies.md) - deptry: every import is declared, every declared runtime dependency is used.
* [nox -s lint](lint.md) - Ruff lint (bugbear, bandit subset, simplify, pyupgrade, pylint subset); format check of lane files.
* [nox -s typecheck_win32](typecheck-win32.md) - mypy again as win32: Windows-only branches (subprocess creation flags, msvcrt) are invisible to the linux run.
* [nox -s typecheck](typecheck.md) - mypy: strict on eija_studio.domain and .application, default profile with a ratchet plan elsewhere.
