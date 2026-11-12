"""Value guards, initiators, one action from several states and separation of duties (ADR-0231 to ADR-0234).

The law proof, Simulate and the generated app's conformance oracle all rest on one claim in
``domain/value_guards.py``: "a finite set of values stands for every value". If a record value exists whose
pattern of true/false answers over an attribute's guards matches no representative point, the proof never tries
that record and can report HOLDS for a law the kernel breaks. These properties state the claim directly and check
it against arbitrary values, including the edges of float precision.

What this establishes: over generated guards and values, every truth pattern a value can produce is produced by
some representative; guards fail closed on missing, mistyped and non-finite values; the model contract compares
guards by their literal (``true`` is not ``1``); ``separation_breach`` agrees with a naive reading of ADR-0233.
What it does NOT establish: that the law proof searches every path (``test_law_proof*`` cover that), or anything
about values the data model refuses (``check_values`` is tested for the non-finite case only).
"""
from __future__ import annotations

from datetime import date
import math

import pytest
from hypothesis import assume, given, settings, strategies as st
from pydantic import ValidationError

from eija_studio.domain.data import Attribute, Entity, check_values
from eija_studio.domain.impact import changed_fields
from eija_studio.domain.laws import DistinctActors, separation_breach
from eija_studio.domain.models import BASE_GUARDS, DomainError, Transition, ValueGuard, Workflow
from eija_studio.domain.value_guards import MAX_VALUATIONS, combinations, points
from .property_strategies import guard_identity, value_guards
from .property_support import examples

ORDERED = ("eq", "ne", "lt", "le", "gt", "ge")
EDGES = (0, -0.0, 2**53, 2**53 + 1, 2**53 + 2, 2**63, 10**309, -(10**309), 1.7976931348623157e308,
         -1.7976931348623157e308, 5e-324, -5e-324, 0.1, 0.2, 0.30000000000000004)
NUMBERS = st.one_of(st.integers(), st.integers(-(10**400), 10**400), st.floats(allow_nan=False, allow_infinity=False),
                    st.sampled_from(EDGES))
DATES = st.dates().map(date.isoformat)
TEXTS = st.text(max_size=4)


def pattern(guards: list[ValueGuard], value: object) -> tuple[bool, ...]:
    """The true/false answer of each guard for a record holding ``value`` (None: the record has no value)."""
    values = {} if value is None else {guards[0].attribute: value}
    return tuple(g.holds(values) for g in guards)


def assert_represented(guards: list[ValueGuard], value: object) -> None:
    reps = points(guards)
    assert reps[0] is None, "no value at all is always a representative"
    assert len(reps) == len({(type(r), repr(r)) for r in reps}), f"duplicate representatives: {reps}"
    wanted = pattern(guards, value)
    assert any(pattern(guards, r) == wanted for r in reps), (
        f"value {value!r} answers {wanted} over {[str(g) for g in guards]}; no representative in {reps} does")


@settings(max_examples=examples(400))
@given(st.lists(st.tuples(st.sampled_from(ORDERED), NUMBERS), min_size=1, max_size=4), st.one_of(st.none(), NUMBERS))
def test_number_representatives_cover_every_number(constants, value):
    """Found two defects: below/above/between collapsed onto a constant at and beyond 2**53 (``x ≠ 2**53`` had no
    representative that differs from it), and integer constants beyond the float range raised OverflowError."""
    assert_represented([ValueGuard(attribute="amount", op=op, value=c) for op, c in constants], value)


@settings(max_examples=examples(300))
@given(st.lists(st.tuples(st.sampled_from(ORDERED), DATES), min_size=1, max_size=4), st.one_of(st.none(), DATES))
def test_date_representatives_cover_every_date(constants, value):
    """Dates are whole days: the representatives include the day before, after and between, where one exists."""
    assert_represented([ValueGuard(attribute="due", op=op, value=c) for op, c in constants], value)


@settings(max_examples=examples(200))
@given(st.lists(st.tuples(st.sampled_from(("eq", "ne")), TEXTS), min_size=1, max_size=4), st.one_of(st.none(), TEXTS))
def test_text_representatives_cover_every_text(constants, value):
    assert_represented([ValueGuard(attribute="kind", op=op, value=c) for op, c in constants], value)


@settings(max_examples=examples(60))
@given(st.lists(st.tuples(st.sampled_from(("eq", "ne")), st.booleans()), min_size=1, max_size=4),
       st.one_of(st.none(), st.booleans()))
def test_boolean_representatives_cover_both_truths(constants, value):
    assert_represented([ValueGuard(attribute="urgent", op=op, value=c) for op, c in constants], value)


@settings(max_examples=examples(200))
@given(value_guards(), st.one_of(st.none(), st.booleans(), NUMBERS, TEXTS, DATES, st.just(math.nan),
                                 st.just(math.inf), st.just(-math.inf)))
def test_guards_fail_closed_on_missing_mistyped_and_non_finite_values(guard, value):
    """A guard holds only for a finite value of its own kind. Found: NaN satisfied every ``≠`` guard, while no
    representative is NaN, so the proof never tried the record the kernel admitted."""
    guard = ValueGuard.model_validate(guard)

    def kind(v: object) -> str:
        return "boolean" if isinstance(v, bool) else "number" if isinstance(v, int | float) else "text"
    non_finite = isinstance(value, float) and not math.isfinite(value)
    if value is None or non_finite or kind(value) != kind(guard.value):
        assert not guard.holds({} if value is None else {guard.attribute: value})


@settings(max_examples=examples(60))
@given(st.sampled_from([math.nan, math.inf, -math.inf]))
def test_records_refuse_non_finite_numbers(value):
    """``json.loads`` accepts NaN and Infinity, so the generated app's record check must refuse them."""
    record = Entity(name="Claim", attributes=(Attribute(name="amount", type="number"),))
    with pytest.raises(DomainError) as refused:
        check_values(record, {"amount": value})
    assert refused.value.code == "FIELD_TYPE"


@settings(max_examples=examples(150))
@given(st.dictionaries(st.sampled_from(("amount", "due", "urgent", "kind")),
                       st.lists(value_guards(), min_size=1, max_size=3), max_size=4))
def test_valuations_are_the_product_of_representatives_or_refused(grouped):
    """Every combination is tried, each at most once, or the check says it cannot (None), never a silent subset."""
    grouped = {name: [g.model_copy(update={"attribute": name}) for g in map(ValueGuard.model_validate, guards)]
               for name, guards in grouped.items()}
    total = math.prod(len(points(g)) for g in grouped.values())
    tried = combinations(grouped)
    if total > MAX_VALUATIONS:
        assert tried is None
        return
    assert tried is not None and len(tried) == total
    assert len({tuple(sorted((k, type(v).__name__, repr(v)) for k, v in row.items())) for row in tried}) == total


def _transition(tid: str, action: str, source: str, conditions: list[dict], target: str = "Done") -> dict:
    return {"id": tid, "action": action, "from_state": source, "to_state": target, "role": "Clerk",
            "guards": list(BASE_GUARDS), "required_effects": [], "forbidden_effects": [], "conditions": conditions}


@settings(max_examples=examples(150))
@given(st.lists(value_guards(), min_size=1, max_size=3, unique_by=guard_identity), st.data())
def test_siblings_of_one_action_must_share_their_guards_by_literal(conditions, data):
    """ADR-0232: transitions one action labels differ only in id and source. Found: ``[x = true]`` and ``[x = 1]``
    compared equal (``True == 1``), so siblings with different meanings were accepted and a guard was refused as a
    duplicate of a different one."""
    other = data.draw(st.lists(value_guards(), min_size=1, max_size=3, unique_by=guard_identity))
    same = {guard_identity(g) for g in conditions} == {guard_identity(g) for g in other}
    document = {"id": "claims", "states": ["New", "Held", "Done"], "initial_state": "New",
                "transitions": [_transition("T1", "Settle", "New", conditions), _transition("T2", "Settle", "Held", other)]}
    try:
        model = Workflow.model_validate(document)
    except ValidationError:
        assert not same
        return
    assert same
    assert model.transition_for("Settle", "Held").id == "T2"
    assert model.transition_for("Settle", "New").id == "T1"
    assert model.sources("Settle") == ("New", "Held")


def test_true_and_one_are_two_guards_not_a_duplicate():
    Transition.model_validate(_transition("T1", "Go", "New", [{"attribute": "x", "op": "eq", "value": True},
                                                              {"attribute": "x", "op": "eq", "value": 1}]))


@settings(max_examples=examples(150))
@given(st.lists(value_guards(), max_size=3, unique_by=guard_identity),
       st.lists(value_guards(), max_size=3, unique_by=guard_identity))
def test_ripple_reports_a_guard_change_exactly_when_the_guards_differ(before, after):
    old = Transition.model_validate(_transition("T1", "Go", "New", before))
    new = Transition.model_validate(_transition("T1", "Go", "New", list(reversed(after))))
    differ = {guard_identity(g) for g in before} != {guard_identity(g) for g in after}
    assert ("conditions" in changed_fields(old, new)) == differ


ACTIONS = ("Raise", "Approve", "Pay", "Close")
ACTORS = ("ann", "bob", "cy")


def naive_breach(law: DistinctActors, action: str, actor: str, history: list[tuple[str, str]]) -> bool:
    """ADR-0233 read literally: refuse when this actor already took a *different* action the law names."""
    return bool(actor) and action in law.actions and any(
        who == actor and done != action and done in law.actions for done, who in history)


@settings(max_examples=examples(300))
@given(st.lists(st.sampled_from(ACTIONS), min_size=2, max_size=4, unique=True),
       st.lists(st.tuples(st.sampled_from(ACTIONS), st.sampled_from(ACTORS)), max_size=8),
       st.sampled_from(ACTIONS), st.sampled_from((*ACTORS, "")))
def test_separation_breach_matches_a_naive_reading(named, history, action, actor):
    law = DistinctActors(id="sod", kind="distinct_actors", actions=tuple(named), code="SEPARATION_DENIED")
    found = separation_breach(law, action, actor, history)
    assert (found is not None) == naive_breach(law, action, actor, history)
    if found is not None:
        assert found != action and found in named and (found, actor) in history


@settings(max_examples=examples(100))
@given(st.lists(st.text(min_size=1, max_size=6), max_size=4))
def test_initiators_are_a_set(roles):
    """Who may start a record is a set: listing a role twice is refused, and order never changes the hash."""
    document = {"id": "claims", "states": ["New", "Done"], "initial_state": "New",
                "transitions": [_transition("T1", "Go", "New", [])], "initiators": roles}
    if len(set(roles)) != len(roles):
        with pytest.raises(ValidationError):
            Workflow.model_validate(document)
        return
    assume(roles)
    model = Workflow.model_validate(document)
    assert Workflow.model_validate(document | {"initiators": roles[::-1]}).semantic_hash == model.semantic_hash

