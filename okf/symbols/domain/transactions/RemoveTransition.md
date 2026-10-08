---
type: Class
title: domain.transactions.RemoveTransition
description: '`class RemoveTransition(Contract)` in `domain/transactions`.'
resource: repo://src/eija_studio/domain/transactions.py#RemoveTransition
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#RemoveTransition
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: f6f6249f3033d14f4ef41c966c1aa3a9bcc8c64e93ae1a32108059ae6874b94b
notes_baseline: 25373e210e86580c1ecb17f4effc8222487b9a2b7afcd336f86caddd25baf888
---

# domain.transactions.RemoveTransition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class RemoveTransition(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#RemoveTransition` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['remove_transition']` |  |
| `transition` | `TransitionId` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.transactions.TransitionId](/symbols/domain/transactions/TransitionId.md) - Type alias `TransitionId` in `domain/transactions`.

## Referenced by

* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
