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
  sha256: 7c184b9e3d90629b393a013df319efc32a553d905d93fac3c08b74855c1d9ae9
description_override: Recomputes a receipt's applicability from its raw observations; a supplied green status is never trusted.
notes_baseline: 53de9f8d1cf80a2eb58d826d924d74e54ecd54718a0205e1a67ef10b2cbfb9d5
---

# domain.evidence.assess_receipt

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def assess_receipt(receipt: dict, subject: dict, claim: str, kind: str) -> str` |
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

* [domain.evidence.TECHNICAL_DIMENSIONS](/symbols/domain/evidence/TECHNICAL_DIMENSIONS.md) - Constant `TECHNICAL_DIMENSIONS` in `domain/evidence`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo…` in `application/compiler`.
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict], subject: dict, authenticator) -> str` in `domain/evidence`.
* [Bounded runtime matrix (integration_test)](/verification/integration-test.md) - Implemented: Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched a hand-written oracle that is partly de…
<!-- okf:generated:end links -->
