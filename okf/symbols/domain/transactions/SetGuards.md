---
type: Class
title: domain.transactions.SetGuards
description: '`class SetGuards(Contract)` in `domain/transactions`.'
resource: repo://src/eija_studio/domain/transactions.py#SetGuards
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#SetGuards
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: ddc2ca3f88d495ba92132f59f4ee6249f70e600d71939a15766bb5ab8c8bd2e6
notes_baseline: db13fd509093d007fb976301ca040a33e3271229594dc3e453df3b5ebb00f350
---

# domain.transactions.SetGuards

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class SetGuards(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#SetGuards` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['set_guards']` |  |
| `transition` | `TransitionId` |  |
| `guards` | `tuple[Guard, ...]` | `Field(min_length=1, max_length=8)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Guard](/symbols/domain/models/Guard.md) - Type alias `Guard` in `domain/models`.
* [domain.transactions.TransitionId](/symbols/domain/transactions/TransitionId.md) - Type alias `TransitionId` in `domain/transactions`.

## Referenced by

* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
