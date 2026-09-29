import copy

import pytest

from quality.gates import complexity_ratchet
from quality.metrics import ROOT, budgets, complexity
from quality.metrics.common import FAIL, PASS


@pytest.fixture(scope="module")
def cx():
    return complexity.collect()


def test_per_function_cc_is_the_quality_lanes_collector_not_a_second_run_of_radon():
    """One collector per metric: the dashboard's function list is exactly what the complexity ratchet measures."""
    ratchet = complexity_ratchet.measure((complexity.SRC_ROOT,), ROOT)
    ours = {f"{module}::{name}": cc for module, funcs in complexity.function_complexities().items() for name, cc in funcs.items()}
    assert len(ours) == len(ratchet) > 0
    by_key = {k.split("::", 1)[1]: v for k, v in ratchet.items()}
    assert sorted(ours.values()) == sorted(ratchet.values())
    assert max(ours.values()) == max(by_key.values())


def test_collect_is_deterministic_and_covers_every_module(cx):
    assert complexity.collect() == cx
    assert cx["summary"]["files"] == len(complexity.source_files())
    assert sum(cx["overall"]["ranks"].values()) == cx["overall"]["functions"]
    assert cx["hotspots"] == sorted(cx["hotspots"], key=lambda h: (-h["cc"], h["function"]))


def test_stats_use_the_repositorys_nearest_rank_percentile():
    stats = complexity._stats([1, 2, 3, 4, 20])
    assert stats["median"] == 3 and stats["p90"] == 20 and stats["max"] == 20 and stats["ranks"]["C"] == 0 and stats["ranks"]["D"] == 1


def test_complexity_budgets_hold_and_fail_on_a_worse_tree(cx):
    assert all(r["status"] == PASS for r in budgets.evaluate({"sections": {"complexity": cx}}) if r["section"] == "complexity")
    worse = copy.deepcopy(cx)
    worse["overall"]["ranks"].update(A=1, B=1, C=50, D=50, E=10, F=10)
    worse["overall"]["functions"] = 122
    worse["summary"]["min_mi"] = 5
    status = {r["id"]: r["status"] for r in budgets.evaluate({"sections": {"complexity": worse}})}
    assert status["CX-02"] == FAIL and status["CX-03"] == FAIL
    assert "CX-01" not in status  # max CC is the quality lane's ratchet (xenon + complexity_ratchet), not duplicated here
