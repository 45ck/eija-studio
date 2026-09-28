"""The finite vocabulary the symbolic grammar ranges over.

Everything that `check_policy` reads through *equality* is enumerated; every other string collapses to
one `OTHER` value. That abstraction is sound for a policy that only tests equality, membership and
set-equality against the known constants (the differential test in `differential.py` checks exactly
that, using arbitrary out-of-vocabulary strings).

Constants are imported from the kernel where the kernel exposes them, so a change to `EFFECTS`,
`FORBIDDEN` or `BASE_GUARDS` is followed automatically. Logic is not imported: it is re-encoded in
`encoding.py` and compared against the real function by the differential test.
"""
from __future__ import annotations

from typing import get_args

from eija_studio.domain.models import BASE_GUARDS, Guard
from eija_studio.domain.policy import EFFECTS, FORBIDDEN

OTHER = "<other>"

ACTIONS: tuple[str, ...] = tuple(EFFECTS)  # Submit, Recommend, Approve, Reject, Revise
MANDATORY_ACTIONS: tuple[str, ...] = ("Submit", "Approve", "Reject", "Revise")
STATES: tuple[str, ...] = ("Draft", "Submitted", "Recommended", "Approved", "Rejected")
ROLES: tuple[str, ...] = ("Teacher", "Registrar", "Viewer")
GUARDS: tuple[str, ...] = tuple(get_args(Guard))
BASE_GUARD_SET: frozenset[str] = frozenset(BASE_GUARDS)
BASE_GUARDS_TUPLE = tuple(BASE_GUARDS)
FORBIDDEN_EFFECTS: tuple[str, ...] = tuple(sorted(FORBIDDEN))
EFFECT_ATOMS: tuple[str, ...] = tuple(sorted({e for effects in EFFECTS.values() for e in effects} | set(FORBIDDEN)))
DECISION_STATES: tuple[str, ...] = ("Approved", "Rejected")
DECISION_AUDIT: tuple[str, ...] = ("Audit:ExcursionApproved", "Audit:ExcursionRejected")


def abstract(value: str, universe: tuple[str, ...]) -> str:
    """Map a concrete string into the symbolic universe (unknown strings become `OTHER`)."""
    return value if value in universe else OTHER
