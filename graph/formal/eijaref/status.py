"""Status algebras of the weave, two of them, never mixed (design document section 6).

Values (evidence sort): PASS FAIL STALE UNKNOWN CONFLICT NOT_RUN. The kernel emits the first five;
NOT_RUN is the weave's addition ("a prerequisite was absent; nothing was observed").

Operator J (join, "several observations about ONE claim by ONE check"): the least upper bound in the
information order

        CONFLICT
        /      \\
     PASS      FAIL
        \\      /
         STALE
           |
        UNKNOWN
           |
        NOT_RUN

Its restriction to the five kernel values is the kernel's ``aggregate_status`` on flat inputs
(checked against the kernel in the tests, where the kernel is available).

Operator M (meet on a chain, "ALL of several required checks"): minimum in a chain with PASS at the top.
The chain is a parameter, because where NOT_RUN and UNKNOWN sit is an owner decision. The gate
predicate "is PASS" does not depend on that choice (checked over all 120 chains): only the label
attached to a non-PASS result does.

Claim status = M over required checks of (J over the evidence of that check).
An empty J is NOT_RUN (bottom). An empty M is NOT_RUN: a gate that requires nothing has proved nothing.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from functools import reduce
from itertools import permutations, product

VALUES = ("PASS", "FAIL", "STALE", "UNKNOWN", "CONFLICT", "NOT_RUN")
NON_PASS = tuple(v for v in VALUES if v != "PASS")

# Hasse diagram of the information order, child < parent.
_COVERS = (("NOT_RUN", "UNKNOWN"), ("UNKNOWN", "STALE"), ("STALE", "PASS"), ("STALE", "FAIL"),
           ("PASS", "CONFLICT"), ("FAIL", "CONFLICT"))


def _leq_table() -> frozenset[tuple[str, str]]:
    le = {(a, a) for a in VALUES} | set(_COVERS)
    changed = True
    while changed:
        changed = False
        for (a, b), (c, d) in product(sorted(le), sorted(le)):
            if b == c and (a, d) not in le:
                le.add((a, d))
                changed = True
    return frozenset(le)


LEQ = _leq_table()


def join2(a: str, b: str) -> str:
    """Least upper bound in the information order (defined by search, not by a hand table)."""
    upper = [x for x in VALUES if (a, x) in LEQ and (b, x) in LEQ]
    least = [x for x in upper if all((x, y) in LEQ for y in upper)]
    if len(least) != 1:  # would mean the order is not a lattice: a bug in this file, never in the data
        raise AssertionError(f"no unique least upper bound for {a}, {b}")
    return least[0]


def join(values: Iterable[str]) -> str:
    """J over a possibly empty collection. Empty is NOT_RUN: no observation."""
    return reduce(join2, values, "NOT_RUN")


DEFAULT_CHAIN = ("FAIL", "CONFLICT", "STALE", "NOT_RUN", "UNKNOWN", "PASS")  # low to high; proposal of ADR-0101


def meet2(a: str, b: str, chain: Sequence[str] = DEFAULT_CHAIN) -> str:
    return a if chain.index(a) <= chain.index(b) else b


def meet(values: Iterable[str], chain: Sequence[str] = DEFAULT_CHAIN) -> str:
    """M over a possibly empty collection. Empty is NOT_RUN (never PASS): non-vacuity."""
    vals = list(values)
    if not vals:
        return "NOT_RUN"
    return reduce(lambda a, b: meet2(a, b, chain), vals)


def claim_status(required_checks: Sequence[Sequence[str]], chain: Sequence[str] = DEFAULT_CHAIN) -> str:
    """required_checks[i] is the list of observed statuses of check i. Empty list means the check has no evidence."""
    return meet((join(evidence) for evidence in required_checks), chain)


def all_chains() -> list[tuple[str, ...]]:
    """Every total order of the six values with PASS at the top: 5! = 120 chains, low to high."""
    return [(*tuple(p), "PASS") for p in permutations(NON_PASS)]


# Link status (per link) and its fixed lift to the evidence sort (DESIGN, ADR-0093 / ADR-0101).
LINK_STATUSES = ("COVERED", "SUSPECT", "ORPHANED", "AMBIGUOUS", "UNRESOLVED")
LIFT: dict[str, str] = {"COVERED": "PASS", "SUSPECT": "STALE", "ORPHANED": "FAIL",
                        "AMBIGUOUS": "CONFLICT", "UNRESOLVED": "NOT_RUN"}


def lifted_gate(link_statuses: Iterable[str], chain: Sequence[str] = DEFAULT_CHAIN) -> str:
    return meet((LIFT[s] for s in link_statuses), chain)


# The deliberately wrong implementations used as negative controls for the law suite.
def vacuous_meet(values: Iterable[str], chain: Sequence[str] = DEFAULT_CHAIN) -> str:
    """Wrong: the empty gate passes (reduce with PASS as the identity)."""
    return reduce(lambda a, b: meet2(a, b, chain), values, "PASS")


def leaky_meet(values: Iterable[str], chain: Sequence[str] = DEFAULT_CHAIN) -> str:
    """Wrong: NOT_RUN is skipped like a missing value, so a skipped check cannot lower the result."""
    return meet((v for v in values if v != "NOT_RUN"), chain)


def check_laws(j: Callable[[str, str], str] = join2) -> dict[str, bool]:
    """Exhaustive over 6 values (pairs) and 216 triples: the finite reduction that closes the claim for
    every list length (a commutative, associative, idempotent operation folds to a function of the set)."""
    v = VALUES
    return {
        "commutative": all(j(a, b) == j(b, a) for a, b in product(v, repeat=2)),
        "associative": all(j(j(a, b), c) == j(a, j(b, c)) for a, b, c in product(v, repeat=3)),
        "idempotent": all(j(a, a) == a for a in v),
        "identity_not_run": all(j("NOT_RUN", a) == a for a in v),
    }
