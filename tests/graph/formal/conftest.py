"""Path setup for the formal-verification tests of the weave lane.

``eijaref`` (graph/formal) is independent of eijagraph and of the kernel. The benchmark module
(graph/bench/formal_checks.py) is loaded by path because ``graph`` is not a package.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FORMAL = ROOT / "graph" / "formal"
if str(FORMAL) not in sys.path:
    sys.path.insert(0, str(FORMAL))


def load_bench():
    """graph/bench/formal_checks.py as a module (cached)."""
    name = "weave_formal_checks"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "graph" / "bench" / "formal_checks.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
