"""Defects found by the principal engineering review of the inspection pull requests merged on 2026-11-13 and 14 (#250
to #261). Log: docs/quality/inspection-2026-11-14-todays-prs.md. Each test failed on main before its fix.

* N1: #258 (K3) made an ordering against a date fail for text that is not a date, in the kernel only. The SCXML export
  still compared such text as a string, so the chart committed `[due > "2026-01-15"]` for `due = "other"`.
* N2: the SCXML export compared a record value with a guard of another kind. The kernel never lets a guard hold across
  kinds, but Python takes True for 1 and finds 6 != "a", so the chart committed where the kernel refused.
* N3: two inspection test modules named log files that do not exist.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from eija_studio.application.scxml import event_data, guard_condition
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import load_pack

ROOT = Path(__file__).resolve().parents[1]
LOAN = load_pack(ROOT / "packs" / "library-loan")
ACTOR = {"active": True, "role": "", "assigned": True}


def _guarded(conditions: list[dict]) -> Workflow:
    raw = LOAN.model.model_dump(mode="json")
    next(t for t in raw["transitions"] if t["action"] == "CheckOut")["conditions"] = conditions
    return Workflow.model_validate(raw)


def _chart_commits(model: Workflow, values: dict) -> bool:
    """The exported `cond` of CheckOut, evaluated as the chart's Python datamodel would, with no engine needed."""
    t = model.transition_for("CheckOut")
    assert t is not None
    attributes = tuple(sorted({g.attribute for g in t.conditions}))
    data = event_data(ACTOR | {"role": t.role}, 0, values, attributes)
    return bool(eval(guard_condition(t), {"__builtins__": {}}, {"_event": SimpleNamespace(data=SimpleNamespace(**data)), "version": 0}))  # noqa: S307 - our own export


def _kernel_commits(model: Workflow, values: dict) -> bool:
    t = model.transition_for("CheckOut")
    assert t is not None
    return all(g.holds(values) for g in t.conditions)


# ---- N1 ------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("due", ["other", "2026-02-30", "2026-01-16", "2026-01-15", "2026-01-14"])
def test_n1_an_ordering_against_a_date_holds_in_the_chart_only_for_a_date(due):
    model = _guarded([{"attribute": "due", "op": "gt", "value": "2026-01-15"}])
    assert _chart_commits(model, {"due": due}) == _kernel_commits(model, {"due": due})


# ---- N2 ------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize(("conditions", "value"), [
    ([{"attribute": "x", "op": "eq", "value": 1}], True),
    ([{"attribute": "x", "op": "ne", "value": False}], 1),
    ([{"attribute": "x", "op": "ne", "value": "a"}], 6),
    ([{"attribute": "x", "op": "gt", "value": 5}], "6"),
    ([{"attribute": "x", "op": "eq", "value": 1}], 1.0),
    ([{"attribute": "x", "op": "eq", "value": True}], True),
])
def test_n2_a_guard_never_holds_in_the_chart_across_kinds(conditions, value):
    model = _guarded(conditions)
    assert _chart_commits(model, {"x": value}) == _kernel_commits(model, {"x": value})


def test_n2_the_differential_agrees_on_guards_of_two_kinds_over_one_attribute():
    differential = pytest.importorskip("verification.scxml.differential")
    pytest.importorskip("statemachine.io")
    for conditions in ([{"attribute": "x", "op": "eq", "value": 1}, {"attribute": "x", "op": "ne", "value": False}],
                       [{"attribute": "x", "op": "gt", "value": 5}, {"attribute": "x", "op": "ne", "value": "a"}],
                       [{"attribute": "due", "op": "gt", "value": "2026-01-15"}]):
        report = differential.compare(LOAN, _guarded(conditions))
        assert report["status"] == "PASS", report["disagreements"][:2]


# ---- N3 ------------------------------------------------------------------------------------------------------

def test_n3_every_inspection_test_module_names_a_log_that_exists():
    named = {}
    for module in (ROOT / "tests").glob("test_*inspection*.py"):
        doc = ast.get_docstring(ast.parse(module.read_text(encoding="utf-8"))) or ""
        named |= {f"{module.name}: {path}": path for path in re.findall(r"docs/quality/[\w./-]+\.md", doc)}
    assert named and all((ROOT / path).is_file() for path in named.values()), named
