---
type: Verification Technique
title: Bounded runtime matrix (integration_test)
description: Every cell of a declared actor x state x action matrix, run against the real runtime in a disposable sandbox, matched a separately written expected outcome; the receipt is recomputed from raw observations.
resource: repo://src/eija_studio/application/verifier.py#verify_runtime
tags:
- verification
- implemented
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/verifier.py#verify_runtime
  title: application/verifier.verify_runtime
  hash_method: ast-v1
  sha256: 965a4eb4528fcf9567dc290edea1908cb359c250790f614edbf74089cd33e34a
- resource: repo://src/eija_studio/domain/evidence.py#assess_receipt
  title: domain/evidence.assess_receipt
  hash_method: ast-v1
  sha256: 7648030c417e0858962511004fd9c3db260adad1e3bb3459f6c8e993d1760376
- resource: repo://src/eija_studio/domain/evidence.py#aggregate_status
  title: domain/evidence.aggregate_status
  hash_method: ast-v1
  sha256: 1f004a921b3f43b115a3b93f7717de794c73dd76438d14c542b87e7b0cfdb78c
---

# Bounded runtime matrix (integration_test)

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Evidence kind | `integration_test` |
| Claim | `runtime_matrix` |
| Status | implemented in the kernel |

## What it can establish

Every cell of a declared actor x state x action matrix, run against the real runtime in a disposable sandbox, matched a separately written expected outcome; the receipt is recomputed from raw observations.

## What it does not establish

Not a proof over arbitrary histories, not an independent oracle (same author), not crash durability of the owner workspace, and never evidence of human comprehension (that stays UNKNOWN).

## Implemented by

* [`application/verifier.verify_runtime`](/symbols/application/verifier/verify_runtime.md)
* [`domain/evidence.assess_receipt`](/symbols/domain/evidence/assess_receipt.md)
* [`domain/evidence.aggregate_status`](/symbols/domain/evidence/aggregate_status.md)
<!-- okf:generated:end facts -->

## Notes

The only evidence kind the kernel can currently establish. `ORACLE` and the runtime share an author, so read a `PASS` as consistency with the written policy under bounded one-step experiments. Human comprehension remains `UNKNOWN`, and `field-use` remains blocked.

<!-- okf:generated:begin links -->
## Implemented by

* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` in `application/verifier` (the source has no docstring).
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict], subject: dict, authenticator) -> str` in `domain/evidence` (the source has no docstring).
* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict, subject: dict, claim: str, kind: str) -> str` in `domain/evidence` (the source has no docstring).
<!-- okf:generated:end links -->
