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
  sha256: 821029d1f7e3057b4e51323b8d32473c549f214b7145bc83df7798b4af46f075
description_override: The trusted four-state excursion workflow (Draft, Submitted, Approved, Rejected) that every Change Case starts from.
notes_baseline: ea1d82f16aa0c1f225a9035b1d218d49e5e5391dc089c9d7056655a668e3f735
---

# domain.policy.baseline

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def baseline(pack: Pack \| None=None) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#baseline` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's baseline workflow.
~~~
<!-- okf:generated:end facts -->

## Notes

Submit and Revise belong to the Teacher, Approve and Reject to the Registrar. It passes [check_policy](/symbols/domain/policy/check_policy.md) by construction; the tests assert that rather than assume it.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.diagram_catalog.demo_pair](/symbols/application/diagram_catalog/demo_pair.md) - Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended).
<!-- okf:generated:end links -->
