---
type: Function
title: domain.policy.law_violations
description: '`def law_violations(model: Workflow, pack: Pack | None=None) -> list[Violation]` in `domain/policy`.'
resource: repo://src/eija_studio/domain/policy.py#law_violations
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#law_violations
  title: domain/policy.py
  hash_method: ast-v2
  sha256: 43998f571106b3898fd9b1f190e3bba124adf6d9675f5cf4f005836d94b51ca0
notes_baseline: d6843ad139bd87569f8749ba3ed25a6c0401e20b12d5c6285369898f1323eac8
---

# domain.policy.law_violations

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def law_violations(model: Workflow, pack: Pack \| None=None) -> list[Violation]` |
| Code | `repo://src/eija_studio/domain/policy.py#law_violations` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Violation](/symbols/domain/laws/Violation.md) - One broken law: its id, the code the policy reports, and the model elements involved.
* [domain.laws.evaluate_table](/symbols/domain/laws/evaluate_table.md) - Every violation of the applicable laws by the workflow's transition table, in law order.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
* [domain.policy.policy_refs](/symbols/domain/policy/policy_refs.md) - The laws and model elements a refusal points at (``law:<id>``, ``transition:<id>``, ``state:<id>``), sorted.
<!-- okf:generated:end links -->
