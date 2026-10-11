---
type: Class
title: domain.change_case.OwnerPlanSelection
description: '`class OwnerPlanSelection(Contract)` in `domain/change_case`.'
resource: repo://src/eija_studio/domain/change_case.py#OwnerPlanSelection
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/change_case.py#OwnerPlanSelection
  title: domain/change_case.py
  hash_method: ast-sig-v1
  sha256: 096ec429dfc2dabeea781670432572cc0375a0656722cf74ae0805a2ffe35108
notes_baseline: 34d5278b0db99bb3eb2a76ac51b32c3108ba886a93e44ef0caa79b114d47db89
---

# domain.change_case.OwnerPlanSelection

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/change_case`](/modules/domain/change_case.md) |
| Signature | `class OwnerPlanSelection(Contract)` |
| Code | `repo://src/eija_studio/domain/change_case.py#OwnerPlanSelection` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['owner_plan']` |  |
| `pack_id` | `str` |  |
| `pack_digest` | `str` | `Field(pattern='^[a-f0-9]{64}$')` |
| `baseline_semantic_hash` | `str` | `Field(pattern='^[a-f0-9]{64}$')` |
| `candidate_semantic_hash` | `str` | `Field(pattern='^[a-f0-9]{64}$')` |
| `steps` | `tuple[OwnerPlanStep, ...]` | `Field(min_length=1, max_length=64)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.OwnerPlanStep](/symbols/domain/change_case/OwnerPlanStep.md) - Reported proposal provenance, never a capability or an owner decision.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [domain.change_case.Selection](/symbols/domain/change_case/Selection.md) - Type alias `Selection` in `domain/change_case`.
<!-- okf:generated:end links -->
