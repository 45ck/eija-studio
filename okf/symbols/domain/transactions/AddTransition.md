---
type: Class
title: domain.transactions.AddTransition
description: A transition performing a declared action; its guards and effects are the action's declared ones.
resource: repo://src/eija_studio/domain/transactions.py#AddTransition
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#AddTransition
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: fb581bea73bd25bd1133eea50f8bbd44380c1657ac49495de7db225fec7affe9
notes_baseline: 3801f66c8a651afbbfb3f24c3588dcbb737b5737eeb56cfde08d059fe91d5597
---

# domain.transactions.AddTransition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class AddTransition(Contract)` |
| Code | `repo://src/eija_studio/domain/transactions.py#AddTransition` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A transition performing a declared action; its guards and effects are the action's declared ones.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['add_transition']` |  |
| `id` | `TransitionId` |  |
| `action` | `Name` |  |
| `from_state` | `Name` |  |
| `to_state` | `Name` |  |
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

* [application.new_system.new_names](/symbols/application/new_system/new_names.md) - The actions and roles `transactions` name that `pack` does not declare, in order of first use.
* [application.plan.describe](/symbols/application/plan/describe.md) - One line a person can check against the diagram.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
