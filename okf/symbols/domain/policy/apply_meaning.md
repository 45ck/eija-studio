---
type: Function
title: domain.policy.apply_meaning
description: The candidate a supported pack meaning produces from ``model`` (policy-checked).
resource: repo://src/eija_studio/domain/policy.py#apply_meaning
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#apply_meaning
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 03786549a8888bb20c7b6f07162fcb00acf4725de6636608ee0bc402d83fc9f0
notes_baseline: 466c31818f6434713ca32b847645de8b23f1c41e03d01f76eda3722e09126c35
---

# domain.policy.apply_meaning

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def apply_meaning(model: Workflow, meaning_id: str, pack: Pack \| None=None) -> Workflow` |
| Code | `repo://src/eija_studio/domain/policy.py#apply_meaning` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The candidate a supported pack meaning produces from ``model`` (policy-checked).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.apply_transactions](/symbols/domain/policy/apply_transactions.md) - Apply an edit sequence as one change: the start must conform, the result must conform (intermediate steps need only be coherent workflows).

## Referenced by

* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
* [domain.policy.demo_candidate](/symbols/domain/policy/demo_candidate.md) - The pack's baseline with its first supported meaning applied.
<!-- okf:generated:end links -->
