"""Regression tests for the kernel defects the property suite found in value guards (ADR-0237).

Each case is the smallest example Hypothesis shrank to; ``tests/property/test_value_guards.py`` states the general
property. These run in the fast tier so the fixes cannot regress between full-tier runs.
"""
from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from eija_studio.domain.data import Attribute, Entity, check_values
from eija_studio.domain.impact import changed_fields
from eija_studio.domain.models import BASE_GUARDS, DomainError, Transition, ValueGuard, Workflow
from eija_studio.domain.value_guards import points


def guard(op: str, value: object, attribute: str = "amount") -> ValueGuard:
    return ValueGuard(attribute=attribute, op=op, value=value)


@pytest.mark.parametrize("constant", [2**53, 9007199254740996.0, 1e16, 1.7976931348623157e308, -1.7976931348623157e308,
                                      10**400, -(10**400)])
def test_points_lie_strictly_either_side_of_a_large_constant(constant):
    """``c - 1 == c`` for floats from 2**53 on, so the old point "below" was the constant itself and ``≠ c`` and
    ``< c`` were never true for any point tried."""
    found = [p for p in points([guard("ne", constant)]) if p is not None]
    assert min(found) < constant < max(found)
    assert all(not isinstance(p, float) or math.isfinite(p) for p in found)


def test_points_between_huge_integer_constants_do_not_overflow():
    """``(a + b) / 2`` of two ints beyond the float range raised OverflowError and crashed the law proof."""
    found = points([guard("lt", 10**400), guard("gt", 10**400 + 4)])
    assert any(10**400 < p < 10**400 + 4 for p in found if p is not None)


def test_no_point_is_invented_between_adjacent_floats():
    low = 1.0
    high = math.nextafter(low, math.inf)
    found = points([guard("ge", low), guard("le", high)])
    assert not any(low < p < high for p in found if p is not None)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_values_satisfy_no_guard(value):
    assert not any(guard(op, 500).holds({"amount": value}) for op in ("eq", "ne", "lt", "le", "gt", "ge"))


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_records_refuse_non_finite_numbers(value):
    with pytest.raises(DomainError) as refused:
        check_values(Entity(name="Claim", attributes=(Attribute(name="amount", type="number"),)), {"amount": value})
    assert refused.value.code == "FIELD_TYPE"


def transition(tid: str, source: str, value: object) -> dict:
    return {"id": tid, "action": "Settle", "from_state": source, "to_state": "Done", "role": "Clerk",
            "guards": list(BASE_GUARDS), "required_effects": [], "forbidden_effects": [],
            "conditions": [{"attribute": "paid", "op": "eq", "value": value}]}


def test_one_action_cannot_hide_a_true_guard_behind_a_one():
    """ADR-0232: siblings share their guards. ``True == 1`` in Python made ``[paid = true]`` equal ``[paid = 1]``."""
    with pytest.raises(ValidationError, match="Duplicate or ambiguous"):
        Workflow.model_validate({"id": "claims", "states": ["New", "Held", "Done"], "initial_state": "New",
                                 "transitions": [transition("T1", "New", True), transition("T2", "Held", 1)]})


def test_true_and_one_are_different_guards():
    Transition.model_validate(transition("T1", "New", True) | {"conditions": [
        {"attribute": "paid", "op": "eq", "value": True}, {"attribute": "paid", "op": "eq", "value": 1}]})


def test_ripple_sees_a_guard_retyped_from_true_to_one():
    before = Transition.model_validate(transition("T1", "New", True))
    after = Transition.model_validate(transition("T1", "New", 1))
    assert changed_fields(before, after) == ["conditions"]


def test_duplicate_forbidden_effect_is_refused():
    """Mirrors the duplicate required effect; was a strict xfail in the property suite (spuriously stale evidence)."""
    with pytest.raises(ValidationError, match="Duplicate forbidden effects"):
        Transition.model_validate(transition("T1", "New", True) | {"forbidden_effects": ["Audit:X", "Audit:X"]})
