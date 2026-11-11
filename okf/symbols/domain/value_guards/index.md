# Symbols of domain.value_guards

# Constants

* [domain.value_guards.MAX_VALUATIONS](MAX_VALUATIONS.md) - Constant `MAX_VALUATIONS` in `domain/value_guards`.

# Functions

* [domain.value_guards.combinations](combinations.md) - `valuations` over these guards, grouped by attribute.
* [domain.value_guards.guard_problems](guard_problems.md) - Codes for value guards that do not fit the data model's record class: no data model, an attribute the record does not have, or a constant of another type (or an ordering on text).
* [domain.value_guards.guards_by_attribute](guards_by_attribute.md) - Every value guard of the model, grouped by the attribute it reads, attributes in name order.
* [domain.value_guards.points](points.md) - Values of one attribute that stand for every value its guards can tell apart; None means no value.
* [domain.value_guards.valuations](valuations.md) - One record's values for each combination of `points` over the guarded attributes, in a fixed order; a value of None is left out.
