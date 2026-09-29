---
type: Constant
title: domain.policy.EFFECTS
description: The exact audit and notification effects each action must produce at commit time.
resource: repo://src/eija_studio/domain/policy.py#EFFECTS
tags:
- symbol
- domain
- constant
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#EFFECTS
  title: domain/policy.py
  hash_method: ast-v2
  sha256: c50b644c94d30c992f8795a22928009d50179d7ae419a6a8410aa53a4cef2cf8
description_override: The exact audit and notification effects each action must produce at commit time.
notes_baseline: c157773027d10311a6edf826ac64c1ba9c268a2f5fff1ae41e7afb8934dd031c
---

# domain.policy.EFFECTS

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `EFFECTS = {'Submit': ('Audit:ExcursionSubmitted',), 'Recommend': ('Audit:ExcursionRecommended', 'Notification:RegistrarQueued'), 'Approve': ('Audit:ExcursionAp…` |
| Code | `repo://src/eija_studio/domain/policy.py#EFFECTS` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

`Recommend` alone enqueues `Notification:RegistrarQueued`. [runtime.execute](/symbols/application/runtime/execute.md) turns these names into audit rows and outbox intents inside the same transaction; an effect with no adapter is refused (`EFFECT_DENIED`). Enqueue is not external delivery ([Effect Intent](/language/effect-intent.md)).

<!-- okf:generated:begin links -->
## Referenced by

* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy`.
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy`.
<!-- okf:generated:end links -->
