---
type: Type Alias
title: domain.laws.Name
description: Type alias `Name` in `domain/laws`.
resource: repo://src/eija_studio/domain/laws.py#Name
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#Name
  title: domain/laws.py
  hash_method: ast-v2
  sha256: 3cc0e6c7f034669814c3baf950524b491f69b4bff63c9a8efde6a01b50548ab9
notes_baseline: 0b908fea1181c403ae60ead51fc6408a0d442fe01000381e0bea188e7d8b1081
---

# domain.laws.Name

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `Name = Annotated[str, Field(min_length=1, max_length=60)]` |
| Code | `repo://src/eija_studio/domain/laws.py#Name` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.laws.ActionRequiresGuard](/symbols/domain/laws/ActionRequiresGuard.md) - Every transition performing ``action`` carries at least ``guards``.
* [domain.laws.ActionSourceIn](/symbols/domain/laws/ActionSourceIn.md) - Every transition performing ``action`` starts in one of ``states``.
* [domain.laws.ActionTarget](/symbols/domain/laws/ActionTarget.md) - Every transition performing ``action`` ends in ``state``.
* [domain.laws.ClosedShape](/symbols/domain/laws/ClosedShape.md) - The workflow has exactly these states and actions and this initial state.
* [domain.laws.ForbiddenEffects](/symbols/domain/laws/ForbiddenEffects.md) - No transition requires any of ``effects`` and every transition declares them forbidden.
* [domain.laws.OnlyKindEnters](/symbols/domain/laws/OnlyKindEnters.md) - Every transition entering ``state`` is held by a role of one of ``role_kinds``.
* [domain.laws.OnlyKindHolds](/symbols/domain/laws/OnlyKindHolds.md) - Every transition performing ``action`` is held by a role of one of ``role_kinds`` (e.g.
* [domain.laws.OnlyRoleHolds](/symbols/domain/laws/OnlyRoleHolds.md) - Every transition performing ``action`` is held by ``role``.
* [domain.laws.PathRequires](/symbols/domain/laws/PathRequires.md) - Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
* [domain.laws.PathRequiresKind](/symbols/domain/laws/PathRequiresKind.md) - Every path from the initial state to ``state`` includes a step by a role of one of ``role_kinds``, the step entering ``state`` included: a human in the loop be…
* [domain.laws.RoleNeverEnters](/symbols/domain/laws/RoleNeverEnters.md) - No transition held by ``role`` enters ``state``.
* [domain.laws.RoleNeverHolds](/symbols/domain/laws/RoleNeverHolds.md) - No transition performing ``action`` is held by ``role``.
* [domain.laws.StateFinal](/symbols/domain/laws/StateFinal.md) - No transition leaves ``state``.
* [domain.laws.StateOnlyVia](/symbols/domain/laws/StateOnlyVia.md) - Every transition entering ``state`` performs one of ``actions``.
* [domain.laws.When](/symbols/domain/laws/When.md) - Condition under which a law applies.
<!-- okf:generated:end links -->
