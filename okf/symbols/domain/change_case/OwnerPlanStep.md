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
  sha256: f73f0745e609031e69875d8cb96690e61d92928e643aaeecada2ee39da0f838a
notes_baseline: 1ed33e73f27bdf296e7c436cfa8d1f82bfc2d6bd4627c14023b6cc43b8fa5957
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
| `round` | `int` | `Field(ge=1, strict=True)` |
| `request` | `str` | `Field(max_length=6000)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [domain.change_case.OwnerPlanRequest](/symbols/domain/change_case/OwnerPlanRequest.md) - Exact accepted workflow commands and the identities of their reviewed preview.
* [domain.change_case.OwnerPlanSelection](/symbols/domain/change_case/OwnerPlanSelection.md) - `class OwnerPlanSelection(Contract)` in `domain/change_case`.
<!-- okf:generated:end links -->
