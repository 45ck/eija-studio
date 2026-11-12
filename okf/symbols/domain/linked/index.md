# Symbols of domain.linked

# Functions

* [domain.linked.admitting](admitting.md) - The first combination of states (as `combinations` orders them) from which `transition` can move every object it names; `{}` when it moves none, None when no combination can.
* [domain.linked.along](along.md) - For each state a record can reach, the states its linked objects are in when only this record moves them, from every object in its initial state: the first such combination found breadth-first.
* [domain.linked.combinations](combinations.md) - Every combination of states of the objects `transition` moves, one dict per combination; `[{}]` when it moves none.
