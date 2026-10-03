---
type: Class
title: domain.transactions.SetRole
description: '`class SetRole(Contract)` in `domain/transactions`.'
resource: repo://src/eija_studio/domain/transactions.py#SetRole
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#SetRole
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: 86898a550611bf370b2b8d2bff1734dd7205bde930e5b95468c70206b3dcf0c5
notes_baseline: 49384eb9f85196f71913eaba2046b7587d0ca5f86d327d4cac072c76234bbdf1
---

# domain.transactions.SetRole

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class SetRole(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#SetRole` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['set_role']` |  |
| `transition` | `TransitionId` |  |
| `role` | `Name` |  |
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
