---
type: Class
title: domain.change_case.OwnerPlanStep
description: Reported proposal provenance, never a capability or an owner decision.
resource: repo://src/eija_studio/domain/change_case.py#OwnerPlanStep
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/change_case.py#OwnerPlanStep
  title: domain/change_case.py
  hash_method: ast-sig-v1
  sha256: 1caef0c31a87f87e6d45adfd7fc3ec3b78bfb04bf8d1c2b5538a9f1fcbabeafc
notes_baseline: 65311399665ac1d1b40efe52fec406c5902e35f4f5ba9c77da97a09eb3b1bc50
---

# domain.change_case.OwnerPlanStep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/change_case`](/modules/domain/change_case.md) |
| Signature | `class OwnerPlanStep(Contract)` |
| Code | `repo://src/eija_studio/domain/change_case.py#OwnerPlanStep` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Reported proposal provenance, never a capability or an owner decision.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `transaction` | `Transaction` |  |
| `author` | `Literal['you', 'ai']` |  |
| `round` | `JsonInt` | `Field(ge=1)` |
| `request` | `str` | `Field(max_length=6000)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.JsonInt](/symbols/domain/models/JsonInt.md) - Type alias `JsonInt` in `domain/models`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [domain.change_case.OwnerPlanRequest](/symbols/domain/change_case/OwnerPlanRequest.md) - Exact accepted workflow commands and the identities of their reviewed preview.
* [domain.change_case.OwnerPlanSelection](/symbols/domain/change_case/OwnerPlanSelection.md) - `class OwnerPlanSelection(Contract)` in `domain/change_case`.
<!-- okf:generated:end links -->
