---
type: Type Alias
title: domain.models.Guard
description: Type alias `Guard` in `domain/models`.
resource: repo://src/eija_studio/domain/models.py#Guard
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Guard
  title: domain/models.py
  hash_method: ast-v2
  sha256: 5cecf48d3c03830f8dccc9ce62739d394c68e139b58600292aa0d8c8f278ad21
notes_baseline: 037f5244f0800cf5486c9e8caa208df38916cc3d79393e4b596cda388f147e65
---

# domain.models.Guard

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `Guard = Literal['actor_active', 'role_current', 'actor_assigned', 'state_equals', 'expected_version', 'operation_binding']` |
| Code | `repo://src/eija_studio/domain/models.py#Guard` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.laws.ActionRequiresGuard](/symbols/domain/laws/ActionRequiresGuard.md) - Every transition performing ``action`` carries at least ``guards``.
* [domain.models.BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) - Constant `BASE_GUARDS` in `domain/models`.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.pack.ActionSpec](/symbols/domain/pack/ActionSpec.md) - The declared guards and required effects of one action; the policy holds every transition to them.
* [domain.transactions.SetGuards](/symbols/domain/transactions/SetGuards.md) - `class SetGuards(Contract)` in `domain/transactions`.
<!-- okf:generated:end links -->
