---
type: Verification Technique
title: Bounded runtime matrix (integration_test)
description: 'Implemented: Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched a hand-written oracle that is partly derived from the model under test.'
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
  hash_method: ast-v2
  sha256: 541a56ce7ed40c5a24b78449b9ec97e2f5206a88810cac4227f9c6703eb045d3
- resource: repo://src/eija_studio/domain/evidence.py#assess_receipt
  title: domain/evidence.assess_receipt
  hash_method: ast-v2
  sha256: bb6f442458c3a35dfda81ac33ed4835ef6b26e20674ad78771e33ebd3225af47
- resource: repo://src/eija_studio/domain/evidence.py#aggregate_status
  title: domain/evidence.aggregate_status
  hash_method: ast-v2
  sha256: 7ad71b12b551b1bcdf5e1f9ac639ebd499188cfd53a29a332adbd50033cfce06
notes_baseline: 55d322b42a241bacd87634f5b798e2181b00997a7f8632b76ada1eecda97b702
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 5d21e613989ef49d69d9fecaa45b6ce4586bf651ae92865c6062a5fd79da4db3
  sources_sha256: 55d322b42a241bacd87634f5b798e2181b00997a7f8632b76ada1eecda97b702
---

# Bounded runtime matrix (integration_test)

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Evidence kind | `integration_test` |
| Claim | `runtime_matrix` |
| Status | implemented in the kernel |

## What it can establish

Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched a hand-written oracle that is partly derived from the model under test. The receipt is recomputed from raw observations.

## What it does not establish

Not a proof over arbitrary histories, not an independent oracle (same author), not crash durability of the owner workspace, and never evidence of human comprehension (that stays UNKNOWN).

## Implemented by

* [`application/verifier.verify_runtime`](/symbols/application/verifier/verify_runtime.md)
* [`domain/evidence.assess_receipt`](/symbols/domain/evidence/assess_receipt.md)
* [`domain/evidence.aggregate_status`](/symbols/domain/evidence/aggregate_status.md)
<!-- okf:generated:end facts -->

## Notes

The first evidence kind the kernel could establish; ADR-0145 adds per-kind admissibility for the formal kinds (`bend_proof`, `smt_proof`, `bounded_model_check`), which report `NOT_RUN` when their prerequisite is missing. `ORACLE` and the runtime share an author, and the expected outcome is not fully separate from the model under test (the `Reject` source state and the candidate shape are read from the model, see [verify_runtime](/symbols/application/verifier/verify_runtime.md)), so read a `PASS` as consistency with the written policy under bounded one-step experiments. Human comprehension remains `UNKNOWN`, and `field-use` remains blocked.

<!-- okf:generated:begin links -->
## Implemented by

* [application.verifier.verify_runtime](/symbols/application/verifier/verify_runtime.md) - `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory) -> dict[str, Any]` in `application/verifier`.
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
* [domain.evidence.assess_receipt](/symbols/domain/evidence/assess_receipt.md) - `def assess_receipt(receipt: dict[str, Any], subject: dict[str, Any], claim: str, kind: str, context: Context…` in `domain/evidence`.
<!-- okf:generated:end links -->
