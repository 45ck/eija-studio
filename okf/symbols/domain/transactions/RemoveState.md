---
type: Class
title: domain.transactions.RemoveState
description: '`class RemoveState(Contract)` in `domain/transactions`.'
resource: repo://src/eija_studio/domain/transactions.py#RemoveState
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#RemoveState
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: b9b942016043b5dc41cbb392205437bc022d1f5ac01ed88641f4e2eff7bf72b5
notes_baseline: fc53338c448e82af2e6a336c2cb67d3475152d9ea81b7ad843eb768182a22c52
---

# domain.transactions.RemoveState

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class RemoveState(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#RemoveState` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['remove_state']` |  |
| `state` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.transactions.Name](/symbols/domain/transactions/Name.md) - Type alias `Name` in `domain/transactions`.

## Referenced by

* [domain.pack.state_sets](/symbols/domain/pack/state_sets.md) - The state sets a workflow of this pack can have: the baseline's, and the baseline's after each supported meaning (states its transactions add or remove).
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
