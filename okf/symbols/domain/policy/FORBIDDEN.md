---
type: Constant
title: domain.policy.FORBIDDEN
description: 'Effects no transition may ever perform: PaymentCaptured and ParentDataExported.'
resource: repo://src/eija_studio/domain/policy.py#FORBIDDEN
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#FORBIDDEN
  title: domain/policy.py
  hash_method: ast-v1
  sha256: 59bdc3b84d9af928c5a77c2f75ee07a55fd4bac877243a2e3fd604a0f87dac2f
description_override: 'Effects no transition may ever perform: PaymentCaptured and ParentDataExported.'
---

# domain.policy.FORBIDDEN

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `FORBIDDEN = ('PaymentCaptured', 'ParentDataExported')` |
| Code | `repo://src/eija_studio/domain/policy.py#FORBIDDEN` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Every transition must list both as forbidden; [check_policy](/symbols/domain/policy/check_policy.md) reports `EFFECT_POLICY:<action>` otherwise. Weakening this tuple to make something pass is a policy change and needs an ADR.

<!-- okf:generated:begin links -->
## Referenced by

* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - `def check_policy(model: Workflow) -> list[str]` in `domain/policy` (the source has no docstring).
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
