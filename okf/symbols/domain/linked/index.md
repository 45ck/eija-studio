# Symbols of domain.linked

# Functions

* [domain.linked.admitting](admitting.md) - The first combination of states (as `combinations` orders them) from which `transition` can move every object it names; `{}` when it moves none, None when no combination can.
* [domain.linked.advance](advance.md) - The objects' states after `transition` (unchanged when it moves none), or None when one of its moves is not possible from their states.
* [domain.linked.along](along.md) - For each state a record can reach, the states its linked objects are in when only this record moves them, from every object in its initial state: the first such combination found breadth-first.
* [domain.linked.combinations](combinations.md) - Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.
* [domain.linked.drift](drift.md) - The states the objects can be in after one move another record makes: any one object takes any move of its lifecycle from its state (ADR-0241).
