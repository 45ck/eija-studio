---
type: Constant
title: domain.policy.FORBIDDEN
description: 'Effects no transition may ever perform: PaymentCaptured and ParentDataExported.'
resource: repo://src/eija_studio/domain/policy.py#FORBIDDEN
tags:
- symbol
- domain
- constant
status: deprecated
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#FORBIDDEN
  title: domain/policy.py
  hash_method: ast-v2
  sha256: f8209ff9f835a751bb55a66b18366b9cdbed1724e29da770bc92d1569a13d9fe
description_override: 'Effects no transition may ever perform: PaymentCaptured and ParentDataExported.'
notes_baseline: e835ca5963059a1a766b92659a7e66d04a15fb9d29b937ba1ec471c86b2823af
---

# domain.policy.FORBIDDEN

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `FORBIDDEN = ('PaymentCaptured', 'ParentDataExported')` |
| Code | `repo://src/eija_studio/domain/policy.py#FORBIDDEN` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Every transition must list both as forbidden; [check_policy](/symbols/domain/policy/check_policy.md) reports `EFFECT_POLICY:<action>` otherwise. Weakening this tuple to make something pass is a policy change and needs an ADR.

<!-- okf:generated:begin links -->
## Referenced by

* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy`.
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy`.
<!-- okf:generated:end links -->
