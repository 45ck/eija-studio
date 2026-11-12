"""Guards over a record's values (issue #93, ADR-0234): which values can decide them, and whether they fit the data model.

A guard such as ``[amount > 500]`` compares one attribute of the record class with a constant. Whether it holds
depends only on which side of each constant a value falls, so a finite set of values stands for every value: for
numbers and dates, each constant, a point below the lowest, above the highest and between each neighbouring pair;
for text and choices, each constant and one other; for true/false, both; and, for every attribute, no value at all.
`valuations` takes one such value per guarded attribute, so the law proof and Simulate can try every case the kernel
can tell apart. `guard_problems` checks guards against the record class of the data model.

Pure: no IO, no clock, no randomness.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import date
from itertools import pairwise, product
import math
from typing import Any

from .data import DataModel, Entity
from .models import ValueGuard, Workflow, iso_date

MAX_VALUATIONS = 256


def guards_by_attribute(model: Workflow) -> dict[str, list[ValueGuard]]:
    """Every value guard of the model, grouped by the attribute it reads, attributes in name order."""
    found: dict[str, list[ValueGuard]] = {}
    for t in model.transitions:
        for guard in t.conditions:
            found.setdefault(guard.attribute, []).append(guard)
    return dict(sorted(found.items()))


def _first_fitting(candidates: tuple[Callable[[], Any], ...], fits: Callable[[Any], bool]) -> list[Any]:
    """The first candidate value that is a finite number and fits, as a one-item list; empty when none does. A
    candidate that overflows a float is skipped."""
    for candidate in candidates:
        try:
            value = candidate()
        except OverflowError:
            continue
        if (not isinstance(value, float) or math.isfinite(value)) and fits(value):
            return [value]
    return []


def _between(low: Any, high: Any, whole: bool) -> list[Any]:
    """A value strictly between two neighbouring constants, if there is one. Record numbers may be fractional, so
    between 5 and 6 lies 5.5; days are whole, so between two consecutive days lies none. Near 2**53 and beyond the
    plain midpoint can round onto a constant (or overflow), so the next float above ``low`` and the next whole number
    are tried too; two constants with no int or float between them have no point between them."""
    if whole:
        return [(low + high) // 2] if high - low >= 2 else []
    return _first_fitting((lambda: (low + high) / 2, lambda: low / 2 + high / 2,
                           lambda: math.nextafter(float(low), math.inf), lambda: math.floor(low) + 1),
                          lambda x: low < x < high)


def _beyond(constant: Any, step: int) -> Any:
    """A number strictly below (step -1) or above (step 1) ``constant``: one away when that is a different number,
    else the next float, else a whole number (beyond the largest float)."""
    rounding = math.floor if step < 0 else math.ceil
    return _first_fitting((lambda: constant + step, lambda: math.nextafter(float(constant), step * math.inf),
                           lambda: rounding(constant) + step),
                          lambda x: x < constant if step < 0 else x > constant)[0]


def _numbers(constants: list[Any], whole: bool = False) -> list[Any]:
    ordered = sorted(set(constants))
    inner = [x for a, b in pairwise(ordered) for x in _between(a, b, whole)]
    if whole:
        return sorted({ordered[0] - 1, *ordered, *inner, ordered[-1] + 1})
    return sorted({_beyond(ordered[0], -1), *ordered, *inner, _beyond(ordered[-1], 1)})


def _dates(constants: list[date]) -> list[str]:
    """Days standing for every date; a day before 0001-01-01 or after 9999-12-31 does not exist and is left out."""
    days = _numbers([d.toordinal() for d in constants], whole=True)
    return [date.fromordinal(int(n)).isoformat() for n in days if 1 <= n <= date.max.toordinal()]


def _other(constants: set[str]) -> str:
    other = "other"
    while other in constants:
        other += "*"
    return other


def _number_points(guards: list[ValueGuard]) -> list[Any]:
    numbers = [g.value for g in guards if isinstance(g.value, int | float) and not isinstance(g.value, bool)]
    return _numbers(numbers) if numbers else []


def _text_points(guards: list[ValueGuard]) -> list[Any]:
    texts = {g.value for g in guards if isinstance(g.value, str)}
    if not texts:
        return []
    dates = [d for d in (iso_date(t) for t in texts) if d is not None]
    return [*sorted(set(_dates(dates) if dates else []) | texts), _other(texts)]


def points(guards: list[ValueGuard]) -> list[Any]:
    """Values of one attribute that stand for every value its guards can tell apart; None means no value."""
    truths = [True, False] if any(isinstance(g.value, bool) for g in guards) else []
    return list(dict.fromkeys([None, *truths, *_number_points(guards), *_text_points(guards)]))


def valuations(model: Workflow) -> list[dict[str, Any]] | None:
    """One record's values for each combination of `points` over the guarded attributes, in a fixed order; a value of
    None is left out. [{}] for a model without value guards; None when there are more than `MAX_VALUATIONS`."""
    return combinations(guards_by_attribute(model))


def combinations(grouped: dict[str, list[ValueGuard]]) -> list[dict[str, Any]] | None:
    """`valuations` over these guards, grouped by attribute."""
    choices = [points(guards) for guards in grouped.values()]
    total = 1
    for values in choices:
        total *= len(values)
    if total > MAX_VALUATIONS:
        return None
    return [{name: v for name, v in zip(grouped, combo, strict=True) if v is not None} for combo in product(*choices)]


def _fits(guard: ValueGuard, kind: str, choices: tuple[str, ...]) -> bool:
    value = guard.value
    if kind == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "date":
        return isinstance(value, str) and iso_date(value) is not None
    if kind == "choice":
        return isinstance(value, str) and value in choices and guard.op in ("eq", "ne")
    return isinstance(value, str) and guard.op in ("eq", "ne")  # text: only equality


def guard_problems(model: Workflow, data: DataModel | None) -> list[str]:
    """Codes for value guards that do not fit the data model's record class: no data model, an attribute the record
    does not have, or a constant of another type (or an ordering on text). Empty when every guard fits."""
    grouped = guards_by_attribute(model)
    if not grouped:
        return []
    if data is None:
        return ["VALUE_GUARD_NO_DATA"]
    record: Entity = data.entity(data.record)
    attributes = {a.name: a for a in record.attributes}
    problems = [f"VALUE_GUARD_UNKNOWN:{name}" for name in grouped if name not in attributes]
    problems += [f"VALUE_GUARD_TYPE:{name}" for name, guards in grouped.items() if name in attributes
                 and not all(_fits(g, attributes[name].type, attributes[name].choices) for g in guards)]
    return problems

