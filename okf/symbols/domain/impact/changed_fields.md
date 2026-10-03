---
type: Function
title: domain.impact.changed_fields
description: Semantic differences of one action's transition.
resource: repo://src/eija_studio/domain/impact.py#changed_fields
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/impact.py#changed_fields
  title: domain/impact.py
  hash_method: ast-v2
  sha256: a342dd99aa9aa2a5aec5bb649f068a96258543aa184a6644115cd01407e6da4e
notes_baseline: cb5c872fc8c050e072618623dc7e8e3bd3664d068341c148dbce0dc4c8c527b7
---

# domain.impact.changed_fields

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def changed_fields(old: Transition, new: Transition) -> list[str]` |
| Code | `repo://src/eija_studio/domain/impact.py#changed_fields` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Semantic differences of one action's transition. Guards and effects are sets (their order is non-semantic,
as in `Workflow.semantic_hash`), so shuffling them is not a change. The single definition of "changed"
shared by the ripple and the diagram diff.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.

## Referenced by

* [application.diagrams.diff_summary](/symbols/application/diagrams/diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]` in `domain/impact`.
<!-- okf:generated:end links -->
