---
type: Constant
title: domain.laws.PROTECTING
description: Constant `PROTECTING` in `domain/laws`.
resource: repo://src/eija_studio/domain/laws.py#PROTECTING
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#PROTECTING
  title: domain/laws.py
  hash_method: ast-v2
  sha256: a8d599ca9b7f9d5f083742ad30945ed26dfcda8b98cf46dc081dd53215e9683b
notes_baseline: 8d2e7961a04e92f5b9637def0f57db563b7ba0ab4fee3181a97291d4580aac36
---

# domain.laws.PROTECTING

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `PROTECTING = (StateFinal, RoleNeverEnters, StateOnlyVia, OnlyKindEnters, PathRequires, PathRequiresKind)` |
| Code | `repo://src/eija_studio/domain/laws.py#PROTECTING` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.OnlyKindEnters](/symbols/domain/laws/OnlyKindEnters.md) - Every transition entering ``state`` is held by a role of one of ``role_kinds``.
* [domain.laws.PathRequires](/symbols/domain/laws/PathRequires.md) - Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
* [domain.laws.PathRequiresKind](/symbols/domain/laws/PathRequiresKind.md) - Every path from the initial state to ``state`` includes a step by a role of one of ``role_kinds``, the step entering ``state`` included: a human in the loop be…
* [domain.laws.RoleNeverEnters](/symbols/domain/laws/RoleNeverEnters.md) - No transition held by ``role`` enters ``state``.
* [domain.laws.StateFinal](/symbols/domain/laws/StateFinal.md) - No transition leaves ``state``.
* [domain.laws.StateOnlyVia](/symbols/domain/laws/StateOnlyVia.md) - Every transition entering ``state`` performs one of ``actions``.

## Referenced by

* [domain.laws.protects_absent](/symbols/domain/laws/protects_absent.md) - Whether ``law`` protects a state the model does not have: the law is broken, never vacuously kept.
<!-- okf:generated:end links -->
