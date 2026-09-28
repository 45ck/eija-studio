# Symbols of domain.evidence

# Constants

* [domain.evidence.TECHNICAL_DIMENSIONS](TECHNICAL_DIMENSIONS.md) - The five subject dimensions an evidence receipt must match: semantic, implementation, policy, environment, harness.

# Functions

* [domain.evidence.aggregate_status](aggregate_status.md) - Combines authenticated receipts into one status; an authentic pass and an authentic fail give CONFLICT, not an average.
* [domain.evidence.assess_receipt](assess_receipt.md) - Recomputes a receipt's applicability from its raw observations; a supplied green status is never trusted.
