"""Wires the property suite into pytest (see ``property_plugin.py`` for profiles and reporting).

Without the ``testing`` extra the suite is not collected at all and the header says NOT_RUN: a missing
prerequisite is never reported as a pass. (Its own directory is a package, so this ``conftest`` does not
collide with ``tests/conftest.py``.)
"""
from importlib.util import find_spec

MISSING = [m for m in ("hypothesis", "hypothesis_jsonschema", "jsonschema") if find_spec(m) is None]

if MISSING:
    collect_ignore_glob = ["test_*.py"]

    def pytest_report_header(config):
        return f"property suite NOT_RUN: missing {', '.join(MISSING)} (pip install -e '.[dev,testing]')"
else:
    from .property_plugin import *  # noqa: F401,F403  (pytest hooks)
