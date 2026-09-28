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
  hash_method: ast-v1
  sha256: 7648030c417e0858962511004fd9c3db260adad1e3bb3459f6c8e993d1760376
description_override: Recomputes a receipt's applicability from its raw observations; a supplied green status is never trusted.
---

# domain.evidence.assess_receipt

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def assess_receipt(receipt: dict, subject: dict, claim: str, kind: str) -> str` |
| Code | `repo://src/eija_studio/domain/evidence.py#assess_receipt` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Only the claim `runtime_matrix` with kind `integration_test` can be established here; any other claim or kind is `UNKNOWN`. The function returns:

* `STALE` when any technical dimension of the receipt subject differs from the current subject ([TECHNICAL_DIMENSIONS](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md)),
* `FAIL` when the artifact hash, matrix shape, duplicate or missing cells, or observation types are wrong,
* `PASS` only when every declared actor x state x action cell exists exactly once and expected equals actual.

See [Evidence Receipt](/language/evidence-receipt.md) and the technique page [Bounded runtime matrix](/verification/integration-test.md). It cannot establish other claims by relabelling (acceptance [AC19](/requirements/ac19.md)).

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence.TECHNICAL_DIMENSIONS](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md) - `TECHNICAL_DIMENSIONS = ('semantic', 'implementation', 'policy', 'environment', 'harness')` in `domain/evidence` (the source has no docstring).
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models` (the source has no docstring).

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict], subject: dict, authenticator) -> str` in `domain/evidence` (the source has no docstring).
* [Bounded runtime matrix (integration_test)](/verification/integration-test.md) - Every cell of a declared actor x state x action matrix, run against the real runtime in a disposable sandbox, matched a separately written expected outcome; th…
<!-- okf:generated:end links -->
