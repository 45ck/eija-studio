"""The HTTP status a generated app answers each refusal code with (ADR-0250).

One table, read by the generated server (app/server.py) when it answers a refusal and by the API contract
(application/api_contract.py) when it documents one, so the two cannot drift apart. Every code the kernel, the data
model's checks or the generated app can refuse with is listed; a code that is not would be answered 409 by default and
documented nowhere, which the tests refuse.

Pure: no I/O.
"""
from __future__ import annotations

# Status -> (what it means, the codes answered with it). The order of the codes is the order they are documented in.
REFUSALS: dict[str, tuple[str, tuple[str, ...]]] = {
    "400": ("The request is malformed, or a field breaks the record class",
            ("BAD_REQUEST", "INVALID_TITLE", "FIELD_REQUIRED", "FIELD_TYPE", "FIELD_TOO_LONG", "FIELD_CHOICE", "UNKNOWN_FIELD",
             "REFERENCE_UNKNOWN")),
    "403": ("The request is not from this app's own address, or the actor may not do this",
            ("HOST_DENIED", "UNKNOWN_ACTOR", "ACTOR_REVOKED", "ROLE_DENIED", "ASSIGNMENT_DENIED", "ROLE_CANNOT_START",
             "SEPARATION_DENIED")),
    "404": ("No such record, page or endpoint, or no stored class of that name", ("NOT_FOUND",)),
    "408": ("The request's body did not arrive within the app's 30 second timeout", ("REQUEST_TIMEOUT",)),
    "409": ("The kernel refused the step: the record is not in a state the action leaves, a guard, timer, linked object or "
            "signal does not allow it, its version moved on, the operation id was used for another request, or it was made "
            "under another model or data model",
            ("STATE_DENIED", "ACTION_DENIED", "VALUE_GUARD_DENIED", "TIMER_NOT_DUE", "LINKED_OBJECT_REFUSED", "SIGNAL_NOT_ACCEPTED",
             "EFFECT_DENIED", "INVALID_STATE", "OPERATION_CONFLICT", "STALE_VERSION", "STALE_INSTANCE", "STALE_DATA")),
    "500": ("The app could not answer this request", ("INTERNAL_ERROR",)),
}
STATUS: dict[str, int] = {code: int(status) for status, (_, codes) in REFUSALS.items() for code in codes}


def status_of(code: str) -> int:
    """The status a refusal with this code is answered with; a code missing from the table is a conflict."""
    return STATUS.get(code, 409)
