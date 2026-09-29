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
  hash_method: ast-v2
  sha256: 7ad71b12b551b1bcdf5e1f9ac639ebd499188cfd53a29a332adbd50033cfce06
description_override: Combines authenticated receipts into one status; an authentic pass and an authentic fail give CONFLICT, not an average.
notes_baseline: f30182e543f20cf506d782e72e776b11de16043b01250edb4896fdfc8ba9a3ae
---

# domain.evidence.aggregate_status

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool]) -> str` |
| Code | `repo://src/eija_studio/domain/evidence.py#aggregate_status` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Unauthenticated receipts count as `FAIL`. `STALE` is reported only when nothing current passed or failed. Human understanding is never derived here: it stays `UNKNOWN`.

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
* [domain.evidence.combine](/symbols/domain/evidence/combine.md) - The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states; STALE (a receipt for another subject), then NOT_RUN (a p…

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [Bounded runtime matrix (integration_test)](/verification/integration-test.md) - Implemented: Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched a hand-written oracle that is partly de…
<!-- okf:generated:end links -->
