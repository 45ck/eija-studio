---
type: Constant
title: domain.models.BASE_GUARDS
description: '`BASE_GUARDS: tuple[Guard, ...] = (''actor_active'', ''role_current'', ''state_equals'', ''expected_version'', ''operation_binding'')` in `domain/models` (the source has no docstring).'
resource: repo://src/eija_studio/domain/models.py#BASE_GUARDS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#BASE_GUARDS
  title: domain/models.py
  hash_method: ast-v1
  sha256: ae153132e4d12b3aae30f9b3ae92ea25da9a9972340ffbdc7ee457822db6a247
---

# domain.models.BASE_GUARDS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `BASE_GUARDS: tuple[Guard, ...] = ('actor_active', 'role_current', 'state_equals', 'expected_version', 'operation_binding')` |
| Code | `repo://src/eija_studio/domain/models.py#BASE_GUARDS` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Guard](/symbols/domain/models/Guard.md) - `Guard = Literal['actor_active', 'role_current', 'actor_assigned', 'state_equals', 'expected_version', 'operation_binding']` in `domain/models` (the source has…

## Referenced by

* [domain.models.Transition.guarded](/symbols/domain/models/Transition.guarded.md) - `def guarded(self) -> Transition` in `domain/models` (the source has no docstring).
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy` (the source has no docstring).
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
