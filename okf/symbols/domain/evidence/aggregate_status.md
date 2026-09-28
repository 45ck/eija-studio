---
type: Function
title: domain.evidence.aggregate_status
description: Combines authenticated receipts into one status; an authentic pass and an authentic fail give CONFLICT, not an average.
resource: repo://src/eija_studio/domain/evidence.py#aggregate_status
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#aggregate_status
  title: domain/evidence.py
  hash_method: ast-v1
  sha256: 1f004a921b3f43b115a3b93f7717de794c73dd76438d14c542b87e7b0cfdb78c
description_override: Combines authenticated receipts into one status; an authentic pass and an authentic fail give CONFLICT, not an average.
---

# domain.evidence.aggregate_status

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def aggregate_status(receipts: list[dict], subject: dict, authenticator) -> str` |
| Code | `repo://src/eija_studio/domain/evidence.py#aggregate_status` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Unauthenticated receipts count as `FAIL`. `STALE` is reported only when nothing current passed or failed. Human understanding is never derived here: it stays `UNKNOWN`.

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict, subject: dict, claim: str, kind: str) -> str` in `domain/evidence` (the source has no docstring).

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
* [Bounded runtime matrix (integration_test)](/verification/integration-test.md) - Every cell of a declared actor x state x action matrix, run against the real runtime in a disposable sandbox, matched a separately written expected outcome; th…
<!-- okf:generated:end links -->
