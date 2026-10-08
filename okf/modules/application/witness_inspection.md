---
type: Module
title: application.witness_inspection
description: Immutable display projections of the deciding formal record, never new evidence or verdicts.
resource: repo://src/eija_studio/application/witness_inspection.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py
  title: application/witness_inspection.py
  hash_method: ast-api-v1
  sha256: 1ba5d45cea825f8433356f99076a006870ce91ee1dc5785407972955976282f7
notes_baseline: 1de5599964d274023297f66857ec90783ff9393262923d5867b62292daf6e147
verified:
- by: process:codex-formal-inspection
  at: '2026-10-03T01:36:00Z'
  notes_sha256: 04b8e67bb530ebac9eff32435d1ea5334d1f564fe16526f2d653528d6865d1fa
  sources_sha256: 1de5599964d274023297f66857ec90783ff9393262923d5867b62292daf6e147
---

# application.witness_inspection

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/witness_inspection.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Immutable display projections of the deciding formal record, never new evidence or verdicts.

Raw JSON is retained as canonical text so inspecting a specimen cannot mutate a sealed artifact.
The adapters below read known artifact locations only; action labels never become navigation refs.
~~~

## Public symbols

* [`InspectionContext`](/symbols/application/witness_inspection/InspectionContext.md) (class) - The case revision and review scope captured by the compiler, not inferred by a browser.
* [`InspectionModel`](/symbols/application/witness_inspection/InspectionModel.md) (class) - A supplied specimen, a validated projection of it, or an explicit absence of model data.
* [`InspectionNavigation`](/symbols/application/witness_inspection/InspectionNavigation.md) (class) - Current artifacts have no complete witness-reference contract, so no link is emitted.
* [`InspectionReceipt`](/symbols/application/witness_inspection/InspectionReceipt.md) (class) - Identity of the exact deciding intact receipt; its seal is deliberately not projected.
* [`InspectionRecord`](/symbols/application/witness_inspection/InspectionRecord.md) (class) - One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
* [`InspectionReview`](/symbols/application/witness_inspection/InspectionReview.md) (class) - Full review identity; subject_json retains every subject field, including presentation.
* [`InspectionStep`](/symbols/application/witness_inspection/InspectionStep.md) (class) - An ordered literal recorded step.
* [`WitnessInspection`](/symbols/application/witness_inspection/WitnessInspection.md) (class) - Supplemental record inspection; availability never changes the existing evidence status.
* [`inspect_verdict`](/symbols/application/witness_inspection/inspect_verdict.md) (function) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.

## Internal imports

* [`domain/evidence`](/modules/domain/evidence.md)
* [`domain/formal`](/modules/domain/formal.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

This adapter reuses the existing receipt integrity check and Workflow validators to present recorded BMC, SMT and Bend data. Counterexamples, seeded negative controls and diagnostics have separate origins and exact artifact paths. Raw canonical JSON preserves malformed data; specimen validation never repairs it or establishes policy acceptance. The module does not run a solver, change a review result or write state.

The current record formats lack complete witness-to-model/source bindings, so both navigation targets are null. Literal action names and the current candidate cannot fill that gap. Case-bound inspection also needs the compiler's captured review context; bare-workflow views can report that context unavailable.

<!-- okf:generated:begin links -->
## Imports

* [domain.evidence](/modules/domain/evidence.md) - Compatibility is computed.
* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.witness_inspection.InspectionContext](/symbols/application/witness_inspection/InspectionContext.md) - The case revision and review scope captured by the compiler, not inferred by a browser.
* [application.witness_inspection.InspectionModel](/symbols/application/witness_inspection/InspectionModel.md) - A supplied specimen, a validated projection of it, or an explicit absence of model data.
* [application.witness_inspection.InspectionNavigation](/symbols/application/witness_inspection/InspectionNavigation.md) - Current artifacts have no complete witness-reference contract, so no link is emitted.
* [application.witness_inspection.InspectionReceipt](/symbols/application/witness_inspection/InspectionReceipt.md) - Identity of the exact deciding intact receipt; its seal is deliberately not projected.
* [application.witness_inspection.InspectionRecord](/symbols/application/witness_inspection/InspectionRecord.md) - One exact JSON-pointer location within the deciding artifact, labelled by its known origin.
* [application.witness_inspection.InspectionReview](/symbols/application/witness_inspection/InspectionReview.md) - Full review identity; subject_json retains every subject field, including presentation.
* [application.witness_inspection.InspectionStep](/symbols/application/witness_inspection/InspectionStep.md) - An ordered literal recorded step.
* [application.witness_inspection.WitnessInspection](/symbols/application/witness_inspection/WitnessInspection.md) - Supplemental record inspection; availability never changes the existing evidence status.
* [application.witness_inspection.inspect_verdict](/symbols/application/witness_inspection/inspect_verdict.md) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
<!-- okf:generated:end links -->
