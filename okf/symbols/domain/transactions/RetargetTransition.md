---
type: Class
title: domain.transactions.RetargetTransition
description: Move one end of a transition to another state (the drag-and-drop edit).
resource: repo://src/eija_studio/domain/transactions.py#RetargetTransition
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#RetargetTransition
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: 0ae8cf3157fe68cd334b4c9d4870366f295bb09a4934c0116cbc20daf012727b
notes_baseline: 3767798ef4b27f3a0009d31f189b00f0c6482946c36238efb46b560f5d8872ae
---

# domain.transactions.RetargetTransition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class RetargetTransition(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#RetargetTransition` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Move one end of a transition to another state (the drag-and-drop edit).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['retarget_transition']` |  |
| `transition` | `TransitionId` |  |
| `end` | `Literal['source', 'target']` |  |
| `state` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.transactions.Name](/symbols/domain/transactions/Name.md) - Type alias `Name` in `domain/transactions`.
* [domain.transactions.TransitionId](/symbols/domain/transactions/TransitionId.md) - Type alias `TransitionId` in `domain/transactions`.

## Referenced by

* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
