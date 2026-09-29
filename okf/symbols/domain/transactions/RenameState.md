---
type: Class
title: domain.transactions.RenameState
description: '`class RenameState(Contract)` in `domain/transactions`.'
resource: repo://src/eija_studio/domain/transactions.py#RenameState
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#RenameState
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: 458faaac0a1a9c98cdf5c15ffc5f581906104efb92122c18dfd1207187e722ae
notes_baseline: e009166bbf663b636b3702beb681ae118099fd3439b388ab87651e418494d6d4
---

# domain.transactions.RenameState

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class RenameState(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#RenameState` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['rename_state']` |  |
| `state` | `Name` |  |
| `to` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.transactions.Name](/symbols/domain/transactions/Name.md) - Type alias `Name` in `domain/transactions`.

## Referenced by

* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
