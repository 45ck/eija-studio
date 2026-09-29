---
type: Function
title: domain.evidence.assess_receipt
description: Recomputes a receipt's applicability from its raw observations; a supplied green status is never trusted.
resource: repo://src/eija_studio/domain/evidence.py#assess_receipt
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#assess_receipt
  title: domain/evidence.py
  hash_method: ast-v2
  sha256: bb6f442458c3a35dfda81ac33ed4835ef6b26e20674ad78771e33ebd3225af47
description_override: Recomputes a receipt's applicability from its raw observations; a supplied green status is never trusted.
notes_baseline: 53de9f8d1cf80a2eb58d826d924d74e54ecd54718a0205e1a67ef10b2cbfb9d5
---

# domain.evidence.assess_receipt

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context \| None=None) -> str` |
| Code | `repo://src/eija_studio/domain/evidence.py#assess_receipt` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Only the claim `runtime_matrix` with kind `integration_test` can be established here; any other claim or kind is `UNKNOWN`. The function returns:

* `STALE` when any technical dimension of the receipt subject differs from the current subject ([TECHNICAL_DIMENSIONS](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md)),
* `FAIL` when the artifact hash, matrix shape, duplicate or missing cells, or observation types are wrong,
* `UNKNOWN` when the receipt's `producer`, `method` or artifact `protocol` is not the one this function knows (`eija-local-verifier`, `bounded-runtime-matrix-v1`): an unrecognised producer is never rounded to `PASS` or `FAIL`,
* `PASS` only when every declared actor x state x action cell exists exactly once and expected equals actual.

See [Evidence Receipt](/language/evidence-receipt.md) and the technique page [Bounded runtime matrix](/verification/integration-test.md). It cannot establish other claims by relabelling (acceptance [AC19](/requirements/ac19.md)).

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence.RUNTIME_MATRIX](/symbols/domain/evidence/RUNTIME_MATRIX.md) - Constant `RUNTIME_MATRIX` in `domain/evidence`.
* [domain.evidence.TECHNICAL_DIMENSIONS](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md) - Constant `TECHNICAL_DIMENSIONS` in `domain/evidence`.
* [domain.evidence.assess_formal_receipt](/symbols/domain/evidence/assess_formal_receipt.md) - Per-kind admissibility (ADR-0145): envelope checks in the runtime matrix's order, then the kind's own check.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.

## Referenced by

* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
* [domain.evidence.receipt_status](/symbols/domain/evidence/receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [Bounded runtime matrix (integration_test)](/verification/integration-test.md) - Implemented: Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched a hand-written oracle that is partly de…
<!-- okf:generated:end links -->
