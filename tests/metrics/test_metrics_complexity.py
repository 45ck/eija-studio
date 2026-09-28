import copy

import pytest
from radon.complexity import cc_visit

from quality.metrics import budgets, complexity
from quality.metrics.common import FAIL, PASS


def test_flatten_counts_each_method_once_and_includes_closures():
    src = (
        "class C:\n"
        "    def a(self, x):\n"
        "        if x:\n            return 1\n        return 2\n"
        "    def b(self):\n        return 0\n"
        "def outer(x):\n"
        "    def inner(y):\n        return y or 1\n"
        "    return inner(x)\n"
    )
    flat = {name: cc for name, _, cc in complexity._flatten(cc_visit(src))}
    assert flat["C.a"] == 2 and flat["C.b"] == 1 and flat["outer"] == 1 and flat["outer.inner"] == 2
    assert len(flat) == 4  # the Class block itself is not counted a second time


@pytest.fixture(scope="module")
def cx():
    return complexity.collect()


def test_collect_is_deterministic_and_covers_every_module(cx):
    assert complexity.collect() == cx
    assert cx["summary"]["files"] == len(complexity.source_files())
    assert sum(cx["overall"]["ranks"].values()) == cx["overall"]["functions"]
    assert cx["hotspots"] == sorted(cx["hotspots"], key=lambda h: (-h["cc"], h["function"]))


def test_complexity_budgets_hold_and_fail_on_a_worse_tree(cx):
    assert all(r["status"] == PASS for r in budgets.evaluate({"sections": {"complexity": cx}}) if r["section"] == "complexity")
    worse = copy.deepcopy(cx)
    worse["overall"]["max"] = 90
    worse["overall"]["ranks"].update(A=1, B=1, C=50, D=50, E=10, F=10)
    worse["overall"]["functions"] = 122
    worse["summary"]["min_mi"] = 5
    status = {r["id"]: r["status"] for r in budgets.evaluate({"sections": {"complexity": worse}})}
    assert status["CX-01"] == FAIL and status["CX-02"] == FAIL and status["CX-03"] == FAIL
