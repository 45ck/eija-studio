---
type: Function
title: domain.policy.baseline
description: The trusted four-state excursion workflow (Draft, Submitted, Approved, Rejected) that every Change Case starts from.
resource: repo://src/eija_studio/domain/policy.py#baseline
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#baseline
  title: domain/policy.py
  hash_method: ast-v1
  sha256: 2e26c1f07f3fecf9eb09e594cffa3bd06de9be0eecfda455cce39155c29a3edc
description_override: The trusted four-state excursion workflow (Draft, Submitted, Approved, Rejected) that every Change Case starts from.
---

# domain.policy.baseline

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def baseline() -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#baseline` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Submit and Revise belong to the Teacher, Approve and Reject to the Registrar. It passes [check_policy](/symbols/domain/policy/check_policy.md) by construction; the tests assert that rather than assume it.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
