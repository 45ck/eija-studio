"""The finite vocabulary the symbolic grammar ranges over.

Everything that `check_policy` reads through *equality* is enumerated; every other string collapses to
one `OTHER` value. That abstraction is sound for a policy that only tests equality, membership and
set-equality against the known constants (the differential test in `differential.py` checks exactly
that, using arbitrary out-of-vocabulary strings).

Constants are imported from the kernel where the kernel exposes them, so a change to `EFFECTS`,
`FORBIDDEN` or `BASE_GUARDS` is followed automatically by the ENCODED POLICY and the grammar. Logic is not
imported: it is re-encoded in `encoding.py` and compared against the real function by the differential test.

The REQUIREMENT is the opposite: the literals in the "Requirement literals" block below are typed in from
the documentation and deliberately NOT imported, so weakening `FORBIDDEN` or `BASE_GUARDS` in the kernel makes
an invariant fail instead of silently weakening the requirement with it. `tests/test_formal_smt.py` pins both
directions. Changing a requirement literal is a reviewed decision, not a regeneration.
"""
from __future__ import annotations

from typing import get_args

from eija_studio.domain.models import BASE_GUARDS, Guard
from verification.excursion_pack import EFFECTS, FORBIDDEN

OTHER = "<other>"

ACTIONS: tuple[str, ...] = tuple(EFFECTS)  # Submit, Recommend, Approve, Reject, Revise
MANDATORY_ACTIONS: tuple[str, ...] = ("Submit", "Approve", "Reject", "Revise")
STATES: tuple[str, ...] = ("Draft", "Submitted", "Recommended", "Approved", "Rejected")
ROLES: tuple[str, ...] = ("Teacher", "Registrar", "Viewer")
# Requirement literals (docs/SECURITY_AND_TRUST.md, domain.policy.CANONICAL_OPTIONS): independent of the kernel constants.
REQUIRED_FORBIDDEN_EFFECTS: tuple[str, ...] = ("ParentDataExported", "PaymentCaptured")
REQUIRED_BASE_GUARDS: tuple[str, ...] = ("actor_active", "expected_version", "operation_binding", "role_current", "state_equals")
DECISION_AUDIT: tuple[str, ...] = ("Audit:ExcursionApproved", "Audit:ExcursionRejected")

GUARDS: tuple[str, ...] = tuple(dict.fromkeys([*get_args(Guard), *REQUIRED_BASE_GUARDS]))
BASE_GUARD_SET: frozenset[str] = frozenset(BASE_GUARDS)
BASE_GUARDS_TUPLE = tuple(BASE_GUARDS)
FORBIDDEN_EFFECTS: tuple[str, ...] = tuple(sorted(FORBIDDEN))
EFFECT_ATOMS: tuple[str, ...] = tuple(sorted({e for effects in EFFECTS.values() for e in effects} | set(FORBIDDEN)
                                             | set(REQUIRED_FORBIDDEN_EFFECTS) | set(DECISION_AUDIT)))
DECISION_STATES: tuple[str, ...] = ("Approved", "Rejected")


def abstract(value: str, universe: tuple[str, ...]) -> str:
    """Map a concrete string into the symbolic universe (unknown strings become `OTHER`)."""
    return value if value in universe else OTHER
