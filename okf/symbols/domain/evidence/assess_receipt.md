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
  sha256: 336c57b0d35ce2729d8cc95b98d7590a53aa956a509ed5abe705009ad816c760
description_override: Recomputes a receipt's applicability from its raw observations; a supplied green status is never trusted.
notes_baseline: 6944a894ceb09193d5c5ac25db0a005bc37cdc7a542aa4fda8653f3a21dc984f
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 4813aef1ec692d5ab82451d4249853fe1ff452e43126c16c8131e23223290019
  sources_sha256: 9d21dc847e586dc822b77c20074aaefc587246dcef1ac109f6fd40c1fd79298c
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 4813aef1ec692d5ab82451d4249853fe1ff452e43126c16c8131e23223290019
  sources_sha256: 6944a894ceb09193d5c5ac25db0a005bc37cdc7a542aa4fda8653f3a21dc984f
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

The claim `runtime_matrix` with kind `integration_test` is assessed by the rules below. Any other claim and kind is delegated to `assess_formal_receipt`, which has an admissibility rule only for the kinds registered in `evidence_kinds` (ADR-0145: `bend_proof`, `smt_proof`, `bounded_model_check`); an unregistered claim or kind is `UNKNOWN`. For the runtime matrix the function returns:

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
* [domain.evidence.runtime_shape](/symbols/domain/evidence/runtime_shape.md) - `def runtime_shape(context: Context | None) -> RuntimeShape` in `domain/evidence`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.

## Referenced by

* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
* [domain.evidence.receipt_status](/symbols/domain/evidence/receipt_status.md) - One receipt's applicability by its OWN declared claim and kind; an unauthentic receipt is FAIL.
* [Bounded runtime matrix (integration_test)](/verification/integration-test.md) - Implemented: Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched a hand-written oracle that is partly de…
<!-- okf:generated:end links -->
