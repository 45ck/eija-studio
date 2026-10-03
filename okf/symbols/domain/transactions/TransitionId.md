---
type: Type Alias
title: domain.transactions.TransitionId
description: Type alias `TransitionId` in `domain/transactions`.
resource: repo://src/eija_studio/domain/transactions.py#TransitionId
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#TransitionId
  title: domain/transactions.py
  hash_method: ast-v2
  sha256: 99eaa09c254096f6be3971fb15237a282d3f4f3dbbd86ba797bf3f2bdfa397f7
notes_baseline: fe43ec2e96696543406463518135e38b655bf078d80edff8d2713add14610818
---

# domain.transactions.TransitionId

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `TransitionId = Annotated[str, Field(pattern='^[A-Z][A-Z0-9_-]{0,63}$')]` |
| Code | `repo://src/eija_studio/domain/transactions.py#TransitionId` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.transactions.AddTransition](/symbols/domain/transactions/AddTransition.md) - A transition performing a declared action; its guards and effects are the action's declared ones.
* [domain.transactions.RemoveTransition](/symbols/domain/transactions/RemoveTransition.md) - `class RemoveTransition(Contract)` in `domain/transactions`.
* [domain.transactions.RetargetTransition](/symbols/domain/transactions/RetargetTransition.md) - Move one end of a transition to another state (the drag-and-drop edit).
* [domain.transactions.SetEffects](/symbols/domain/transactions/SetEffects.md) - `class SetEffects(Contract)` in `domain/transactions`.
* [domain.transactions.SetGuards](/symbols/domain/transactions/SetGuards.md) - `class SetGuards(Contract)` in `domain/transactions`.
* [domain.transactions.SetRole](/symbols/domain/transactions/SetRole.md) - `class SetRole(Contract)` in `domain/transactions`.
<!-- okf:generated:end links -->
