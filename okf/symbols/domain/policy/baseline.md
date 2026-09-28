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
  hash_method: ast-v2
  sha256: 581f794861efc3065b93676316370ff94668fbe45a048098cffa7c83d8421ce3
description_override: The trusted four-state excursion workflow (Draft, Submitted, Approved, Rejected) that every Change Case starts from.
notes_baseline: ea1d82f16aa0c1f225a9035b1d218d49e5e5391dc089c9d7056655a668e3f735
---

# domain.policy.baseline

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def baseline() -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#baseline` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Submit and Revise belong to the Teacher, Approve and Reject to the Registrar. It passes [check_policy](/symbols/domain/policy/check_policy.md) by construction; the tests assert that rather than assume it.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.policy.transition](/symbols/domain/policy/transition.md) - `def transition(action: str, source: str, target: str, role: str) -> Transition` in `domain/policy`.
<!-- okf:generated:end links -->
