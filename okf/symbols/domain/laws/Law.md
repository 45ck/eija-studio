---
type: Type Alias
title: domain.laws.Law
description: Type alias `Law` in `domain/laws`.
resource: repo://src/eija_studio/domain/laws.py#Law
tags:
- symbol
- domain
- type-alias
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#Law
  title: domain/laws.py
  hash_method: ast-v2
  sha256: ee40ba71d4d33819e4ab50d8f40bd9da99d832b02f31a3c9e5913188a3b5e4b1
notes_baseline: 3be0a33dbffe075adf6cecabbe3f1d4e41ef44c6a506ad18012f754f20ccf5fa
---

# domain.laws.Law

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | type-alias |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `Law = Annotated[Union[ClosedShape, OnlyRoleHolds, RoleNeverHolds, RoleNeverEnters, StateOnlyVia, ActionTarget, ActionSourceIn, ActionRequiresGuard, ForbiddenEf…` |
| Code | `repo://src/eija_studio/domain/laws.py#Law` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.ActionRequiresGuard](/symbols/domain/laws/ActionRequiresGuard.md) - Every transition performing ``action`` carries at least ``guards``.
* [domain.laws.ActionSourceIn](/symbols/domain/laws/ActionSourceIn.md) - Every transition performing ``action`` starts in one of ``states``.
* [domain.laws.ActionTarget](/symbols/domain/laws/ActionTarget.md) - Every transition performing ``action`` ends in ``state``.
* [domain.laws.ClosedShape](/symbols/domain/laws/ClosedShape.md) - The workflow has exactly these states and actions and this initial state.
* [domain.laws.ForbiddenEffects](/symbols/domain/laws/ForbiddenEffects.md) - No transition requires any of ``effects`` and every transition declares them forbidden.
* [domain.laws.OnlyRoleHolds](/symbols/domain/laws/OnlyRoleHolds.md) - Every transition performing ``action`` is held by ``role``.
* [domain.laws.PathRequires](/symbols/domain/laws/PathRequires.md) - Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
* [domain.laws.RequiresEvidence](/symbols/domain/laws/RequiresEvidence.md) - A review needs evidence of this kind; judged by the evidence matrix, never by the table.
* [domain.laws.RoleNeverEnters](/symbols/domain/laws/RoleNeverEnters.md) - No transition held by ``role`` enters ``state``.
* [domain.laws.RoleNeverHolds](/symbols/domain/laws/RoleNeverHolds.md) - No transition performing ``action`` is held by ``role``.
* [domain.laws.StateFinal](/symbols/domain/laws/StateFinal.md) - No transition leaves ``state``.
* [domain.laws.StateOnlyVia](/symbols/domain/laws/StateOnlyVia.md) - Every transition entering ``state`` performs one of ``actions``.

## Referenced by

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
