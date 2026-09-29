---
type: Class
title: domain.transactions.AddState
description: '`class AddState(Contract)` in `domain/transactions`.'
resource: repo://src/eija_studio/domain/transactions.py#AddState
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#AddState
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: ecc540344d326bfc50b6866f92e8d913818d6616ba0fc23abea37b48fea44bae
notes_baseline: fb0853bc502ab44ad9cc336cb579cdafe86806253bf526140253e4f023a5a638
---

# domain.transactions.AddState

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class AddState(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#AddState` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['add_state']` |  |
| `state` | `Name` |  |
| `after` | `Name \| None` | `None` |
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
