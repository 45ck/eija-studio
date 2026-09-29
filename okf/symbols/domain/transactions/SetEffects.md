---
type: Class
title: domain.transactions.SetEffects
description: '`class SetEffects(Contract)` in `domain/transactions`.'
resource: repo://src/eija_studio/domain/transactions.py#SetEffects
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#SetEffects
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: 1cc14ab122be8ff4176f8839187e3990ec402de23484d60a829ea325a3e97cd9
notes_baseline: 7cf20feda2f785eca3ff71556fbb77eb1f457b686a87165249ee181b61a04ef3
---

# domain.transactions.SetEffects

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class SetEffects(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#SetEffects` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['set_effects']` |  |
| `transition` | `TransitionId` |  |
| `required_effects` | `tuple[Name, ...]` | `Field(max_length=16)` |
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
