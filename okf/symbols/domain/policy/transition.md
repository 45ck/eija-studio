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
  hash_method: ast-v2
  sha256: e4abc97bf36ffd9435e5dc08fe17baa09e44fbd8283e60bbd582577929979341
description_override: Builds a Transition whose guards and effects come from the protected tables, never from caller input.
notes_baseline: 131f5b3ffb1c32f6fdfbae407b359fda148e5335ad64b4d62500a7929308ff58
---

# domain.policy.transition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def transition(action: str, source: str, target: str, role: str) -> Transition` |
| Code | `repo://src/eija_studio/domain/policy.py#transition` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

`TR-<ACTION>` id; guards are [BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) plus `actor_assigned` for `Recommend`; required effects come from [EFFECTS](/symbols/domain/policy/EFFECTS.md) and forbidden effects from [FORBIDDEN](/symbols/domain/policy/FORBIDDEN.md).

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) - Constant `BASE_GUARDS` in `domain/models`.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.policy.EFFECTS](/symbols/domain/policy/EFFECTS.md) - Constant `EFFECTS` in `domain/policy`.
* [domain.policy.FORBIDDEN](/symbols/domain/policy/FORBIDDEN.md) - Constant `FORBIDDEN` in `domain/policy`.

## Referenced by

* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - `def apply_transaction(model: Workflow, tx: SemanticTransaction) -> Workflow` in `domain/policy`.
* [domain.policy.baseline](/symbols/domain/policy/baseline.md) - `def baseline() -> Workflow` in `domain/policy`.
<!-- okf:generated:end links -->
