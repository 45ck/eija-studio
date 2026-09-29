import ast
import copy
import sys

import pytest

from quality.metrics import budgets, structure
from quality.metrics.common import FAIL, PASS


def parse_class(src: str) -> ast.ClassDef:
    return next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.ClassDef))


@pytest.mark.parametrize("src,expected", [
    ("class P(Protocol):\n    def f(self): ...", True),
    ("class P(typing.Protocol[T]):\n    pass", True),
    ("class A(ABC):\n    pass", True),
    ("class A(metaclass=ABCMeta):\n    pass", True),
    ("class A:\n    @abstractmethod\n    def f(self): ...", True),
    ("class A:\n    @abc.abstractmethod\n    def f(self): ...", True),
    ("class C:\n    def f(self): ...", False),
    ("class M(BaseModel):\n    x: int", False),
])
def test_is_abstract_classification(src, expected):
    assert structure.is_abstract(parse_class(src)) is expected


def test_martin_formulas_on_known_values():
    assert structure.instability(3, 1) == 0.25 and structure.instability(0, 5) == 1.0
    assert structure.instability(0, 0) is None  # isolated: undefined, never silently 0
    assert structure.abstractness(4, 1) == 0.25 and structure.abstractness(0, 0) == 0.0
    assert structure.distance(0.0, 1.0) == 0.0  # on the main sequence
    assert structure.distance(0.0, 0.0) == 1.0  # stable and concrete: maximum distance
    assert structure.distance(None, 0.5) is None


def test_zones_name_the_regions():
    assert structure.zone(0.0, 0.0).startswith("zone of pain")
    assert structure.zone(1.0, 1.0).startswith("zone of uselessness")
    assert structure.zone(0.5, 0.5) == "main sequence"
    assert structure.zone(None, 0.0) == "undefined"


def test_cycle_detection_finds_a_cycle_and_accepts_a_dag():
    assert structure.cycles({"a": {"b"}, "b": {"c"}, "c": {"a"}, "d": {"a"}}) == [["a", "b", "c"]]
    assert structure.cycles({"a": {"b"}, "b": {"c"}, "c": set()}) == []


def test_sdp_violation_is_reported_only_against_the_stability_gradient():
    inst = {"stable": 0.1, "flaky": 0.9}
    down = [{"from": "flaky", "to": "stable", "imports": 1}]
    up = [{"from": "stable", "to": "flaky", "imports": 1}]
    assert structure.sdp_violations(down, inst) == []
    assert structure.sdp_violations(up, inst)[0]["to"] == "flaky"


TOY = {
    "__init__.py": "",
    "a/__init__.py": "",
    "a/m.py": "from typing import Protocol

class P(Protocol):
    def f(self) -> int: ...

class C:
    pass
",
    "b/__init__.py": "",
    "b/m.py": "from toy.a import m

class X:
    pass
",
    "c/__init__.py": "",
    "c/m.py": "from toy.a import m
from toy.b import m as bm
",
}


def test_martin_metrics_of_a_hand_worked_toy_package(tmp_path, monkeypatch):
    """Package `toy`: c imports a and b, b imports a, a imports nothing.  Derived by hand from the definitions:

      a: Ca = {b.m, c.m} = 2, Ce = 0 -> I = 0/2 = 0;    classes 2 (one Protocol) -> A = 1/2;  D = |0.5 + 0 - 1| = 0.5
      b: Ca = {c.m} = 1,      Ce = {a.m} = 1 -> I = 1/2; classes 1, none abstract  -> A = 0;    D = |0 + 0.5 - 1| = 0.5
      c: Ca = 0,              Ce = {a.m, b.m} = 2 -> I = 1; no classes             -> A = 0;    D = |0 + 1 - 1| = 0
    """
    for name, body in TOY.items():
        path = tmp_path / "toy" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    sys.modules.pop("toy", None)
    result = structure.collect("toy", tmp_path / "toy")
    rows = {r["name"]: r for r in result["layers"]}
    got = {n: (r["ca"], r["ce"], r["instability"], r["abstractness"], r["distance"]) for n, r in rows.items()}
    assert got == {"a": (2, 0, 0.0, 0.5, 0.5), "b": (1, 1, 0.5, 0.0, 0.5), "c": (0, 2, 1.0, 0.0, 0.0)}
    assert result["summary"]["layer_cycles"] == [] and result["summary"]["sdp_violations"] == []
    assert result["summary"]["mean_layer_distance"] == pytest.approx(1 / 3, abs=1e-3)


@pytest.fixture(scope="module")
def martin():
    return structure.collect()


def test_real_tree_layers_and_direction(martin):
    layers = {r["name"]: r for r in martin["layers"]}
    assert {"domain", "application", "adapters", "interfaces", "bootstrap"} <= set(layers)
    assert layers["domain"]["ce"] == 0 and layers["domain"]["instability"] == 0.0
    assert layers["application"]["abstract_classes"] >= 1  # the ports
    assert martin["summary"]["layer_cycles"] == [] and martin["summary"]["module_cycles"] == []


def test_structural_collection_is_deterministic(martin):
    assert structure.collect() == martin


def test_architecture_budgets_pass_on_the_real_tree(martin):
    doc = {"sections": {"martin": martin}}
    results = {r["id"]: r for r in budgets.evaluate(doc) if r["section"] == "martin"}
    assert all(r["status"] == PASS for r in results.values()), results


def test_budget_negative_controls_fail_when_the_property_is_broken(martin):
    """Corrupt a copy of the measurement: the budgets must notice (they are not tautologies)."""
    bad = copy.deepcopy(martin)
    next(r for r in bad["layers"] if r["name"] == "domain").update(ce=2, instability=0.5)
    bad["summary"]["layer_cycles"] = [["domain", "adapters"]]
    bad["summary"]["sdp_violations"] = [{"from": "domain", "to": "adapters"}]
    results = {r["id"]: r["status"] for r in budgets.evaluate({"sections": {"martin": bad}})}
    assert results["ARCH-01"] == FAIL and results["ARCH-03"] == FAIL
    assert results["ARCH-04"] == FAIL and results["ARCH-05"] == FAIL
