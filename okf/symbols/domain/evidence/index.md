# Symbols of domain.evidence

# Classes

* [domain.evidence.FormalVerdict](FormalVerdict.md) - The status of one evidence kind for the current subject, with the receipt that decided it.

# Constants

* [domain.evidence.RUNTIME_MATRIX](RUNTIME_MATRIX.md) - Constant `RUNTIME_MATRIX` in `domain/evidence`.
* [domain.evidence.TECHNICAL_DIMENSIONS](TECHNICAL_DIMENSIONS.md) - The five subject dimensions an evidence receipt must match: semantic, implementation, policy, environment, harness.

# Functions

* [domain.evidence.aggregate_formal](aggregate_formal.md) - Combine every receipt of one kind.
* [domain.evidence.aggregate_status](aggregate_status.md) - Combines authenticated receipts into one status; an authentic pass and an authentic fail give CONFLICT, not an average.
* [domain.evidence.assess_formal_receipt](assess_formal_receipt.md) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [domain.evidence.assess_receipt](assess_receipt.md) - Recomputes a receipt's applicability from its raw observations; a supplied green status is never trusted.
* [domain.evidence.combine](combine.md) - The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states; STALE (a receipt for another subject), then NOT_RUN (a prerequisite was missing), then UNKNOWN.
* [domain.evidence.expected_shape](expected_shape.md) - The runtime matrix a receipt must cover under ``pack``: exactly ``model``'s states when it is known.
* [domain.evidence.intact_artifact](intact_artifact.md) - The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.
* [domain.evidence.receipt_status](receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [domain.evidence.runtime_shape](runtime_shape.md) - `def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.
