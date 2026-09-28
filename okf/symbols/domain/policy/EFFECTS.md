---
type: Constant
title: domain.policy.EFFECTS
description: The exact audit and notification effects each action must produce at commit time.
resource: repo://src/eija_studio/domain/policy.py#EFFECTS
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#EFFECTS
  title: domain/policy.py
  hash_method: ast-v1
  sha256: ad8634c2c7d1f2d3faf5dae9d6db857ca494735762b2d158920100e014a81a43
description_override: The exact audit and notification effects each action must produce at commit time.
---

# domain.policy.EFFECTS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `EFFECTS = {'Submit': ('Audit:ExcursionSubmitted',), 'Recommend': ('Audit:ExcursionRecommended', 'Notification:RegistrarQueued'), 'Approve': ('Audit:ExcursionAp…` |
| Code | `repo://src/eija_studio/domain/policy.py#EFFECTS` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

`Recommend` alone enqueues `Notification:RegistrarQueued`. [runtime.execute](/symbols/application/runtime/execute.md) turns these names into audit rows and outbox intents inside the same transaction; an effect with no adapter is refused (`EFFECT_DENIED`). Enqueue is not external delivery ([Effect Intent](/language/effect-intent.md)).

<!-- okf:generated:begin links -->
## Referenced by

* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy` (the source has no docstring).
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
