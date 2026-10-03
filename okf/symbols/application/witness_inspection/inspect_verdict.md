---
type: Function
title: application.witness_inspection.inspect_verdict
description: Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
resource: repo://src/eija_studio/application/witness_inspection.py#inspect_verdict
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#inspect_verdict
  title: application/witness_inspection.py
  hash_method: ast-v2
  sha256: 3e4bf59960e59e9e83229c3b5fd386c2cc7fede6636e286167c76f2725465ef8
notes_baseline: 721e9bceba22d29a5f0fe9bcd9a3d83868217ed3f8ea79e94ceedd9214d85518
verified:
- by: process:codex-formal-inspection
  at: '2026-10-03T01:36:00Z'
  notes_sha256: 5d921a9d657ccd39aed4a0a40aecd51a8c16a64f99cc1261a5641304691e7309
  sources_sha256: 721e9bceba22d29a5f0fe9bcd9a3d83868217ed3f8ea79e94ceedd9214d85518
---

# application.witness_inspection.inspect_verdict

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `def inspect_verdict(verdict: FormalVerdict, subject: dict[str, Any], context: Context, authenticator: Callable[[dict[str, Any]], bool], pack: Pack \| None, review_context: InspectionContext \| None=None) -> WitnessInspection` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#inspect_verdict` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
~~~
<!-- okf:generated:end facts -->

## Notes

Inspect only the `FormalVerdict.receipt` already chosen by aggregation, after `intact_artifact` admits its integrity and protocol. Missing context or a missing/unadmitted artifact produces an unavailable display projection while preserving the existing status and reasons. An intact record's original subject can differ from the current review; both are retained explicitly.

Nested schema problems remain raw diagnostics or recorded projection limits. A purported SMT refutation needs a valid invariant identity and a supplied specimen before it is labelled a counterexample; Workflow validation controls specimen display, not the verdict. This function supplies no current-model or source navigation and performs no execution or mutation.

<!-- okf:generated:begin links -->
## Depends on

* [application.witness_inspection.InspectionContext](/symbols/application/witness_inspection/InspectionContext.md) - The case revision and review scope captured by the compiler, not inferred by a browser.
* [application.witness_inspection.InspectionReceipt](/symbols/application/witness_inspection/InspectionReceipt.md) - Identity of the exact deciding intact receipt; its seal is deliberately not projected.
* [application.witness_inspection.WitnessInspection](/symbols/application/witness_inspection/WitnessInspection.md) - Supplemental record inspection; availability never changes the existing evidence status.
* [domain.evidence.FormalVerdict](/symbols/domain/evidence/FormalVerdict.md) - The status of one evidence kind for the current subject, with the receipt that decided it.
* [domain.evidence.intact_artifact](/symbols/domain/evidence/intact_artifact.md) - The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
