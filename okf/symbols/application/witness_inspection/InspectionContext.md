---
type: Class
title: application.witness_inspection.InspectionContext
description: The case revision and review scope captured by the compiler, not inferred by a browser.
resource: repo://src/eija_studio/application/witness_inspection.py#InspectionContext
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/witness_inspection.py#InspectionContext
  title: application/witness_inspection.py
  hash_method: ast-sig-v1
  sha256: fb96e32d177bac99689a040a1ccc0ab2c5bbea289d626b36c08a2997c8e924f7
notes_baseline: 8e24218cc26fa8ec32dac41879d8a31ecb9247127524e50fbd826dc3ca7740fe
---

# application.witness_inspection.InspectionContext

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/witness_inspection`](/modules/application/witness_inspection.md) |
| Signature | `class InspectionContext(Contract)` |
| Code | `repo://src/eija_studio/application/witness_inspection.py#InspectionContext` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
The case revision and review scope captured by the compiler, not inferred by a browser.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `case_id` | `str` |  |
| `case_version` | `int` |  |
| `scope` | `str` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack) the pack's declared verifiers, so a ki…
* [application.witness_inspection.inspect_verdict](/symbols/application/witness_inspection/inspect_verdict.md) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
<!-- okf:generated:end links -->
