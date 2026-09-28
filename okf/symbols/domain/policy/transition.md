---
type: Function
title: domain.policy.transition
description: Builds a Transition whose guards and effects come from the protected tables, never from caller input.
resource: repo://src/eija_studio/domain/policy.py#transition
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#transition
  title: domain/policy.py
  hash_method: ast-v1
  sha256: 274d2ccc54637286efaacac73f62d012f5f3aa1d1fbeb01f6705db920f89331c
description_override: Builds a Transition whose guards and effects come from the protected tables, never from caller input.
---

# domain.policy.transition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def transition(action: str, source: str, target: str, role: str) -> Transition` |
| Code | `repo://src/eija_studio/domain/policy.py#transition` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

`TR-<ACTION>` id; guards are [BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) plus `actor_assigned` for `Recommend`; required effects come from [EFFECTS](/symbols/domain/policy/EFFECTS.md) and forbidden effects from [FORBIDDEN](/symbols/domain/policy/FORBIDDEN.md).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) - `BASE_GUARDS: tuple[Guard, ...] = ('actor_active', 'role_current', 'state_equals', 'expected_version', 'operation_binding')` in `domain/models` (the source has…
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models` (the source has no docstring).
* [domain.policy.EFFECTS](/symbols/domain/policy/EFFECTS.md) - `EFFECTS = {'Submit': ('Audit:ExcursionSubmitted',), 'Recommend': ('Audit:ExcursionRecommended', 'Notification:RegistrarQueued'), 'Approve': ('Audit:E…` in `do…
* [domain.policy.FORBIDDEN](/symbols/domain/policy/FORBIDDEN.md) - `FORBIDDEN = ('PaymentCaptured', 'ParentDataExported')` in `domain/policy` (the source has no docstring).

## Referenced by

* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy` (the source has no docstring).
* [domain.policy.baseline](/symbols/domain/policy/baseline.md) - `def baseline() -> Workflow` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
