---
type: Type Alias
title: domain.transactions.Name
description: Type alias `Name` in `domain/transactions`.
resource: repo://src/eija_studio/domain/transactions.py#Name
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#Name
  title: domain/transactions.py
  hash_method: ast-v2
  sha256: 3cc0e6c7f034669814c3baf950524b491f69b4bff63c9a8efde6a01b50548ab9
notes_baseline: 1cd43426f035ca8fb2d98e683a8dd45f7e6d5509d4428083a635a243b927cb55
---

# domain.transactions.Name

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `Name = Annotated[str, Field(min_length=1, max_length=60)]` |
| Code | `repo://src/eija_studio/domain/transactions.py#Name` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.transactions.AddState](/symbols/domain/transactions/AddState.md) - `class AddState(Contract)` in `domain/transactions`.
* [domain.transactions.AddTransition](/symbols/domain/transactions/AddTransition.md) - A transition performing a declared action; its guards and effects are the action's declared ones.
* [domain.transactions.RemoveState](/symbols/domain/transactions/RemoveState.md) - `class RemoveState(Contract)` in `domain/transactions`.
* [domain.transactions.RenameState](/symbols/domain/transactions/RenameState.md) - `class RenameState(Contract)` in `domain/transactions`.
* [domain.transactions.RetargetTransition](/symbols/domain/transactions/RetargetTransition.md) - Move one end of a transition to another state (the drag-and-drop edit).
* [domain.transactions.SetEffects](/symbols/domain/transactions/SetEffects.md) - `class SetEffects(Contract)` in `domain/transactions`.
* [domain.transactions.SetInitial](/symbols/domain/transactions/SetInitial.md) - `class SetInitial(Contract)` in `domain/transactions`.
* [domain.transactions.SetRole](/symbols/domain/transactions/SetRole.md) - `class SetRole(Contract)` in `domain/transactions`.
<!-- okf:generated:end links -->
