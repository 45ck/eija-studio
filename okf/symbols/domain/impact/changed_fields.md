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
  sha256: d0e640dbd14d42e780e26a2fbf64a0a387a7e682bfe96acee9b5b690b49e6de9
notes_baseline: ffb19947bba88f446c2e256f21ad2436a40569e9f44bf834303c754294be5e0f
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
* [domain.models.guard_keys](/symbols/domain/models/guard_keys.md) - Value guards as a set compared by their JSON, as the semantic hash compares them.

## Referenced by

* [application.diagrams.diff_summary](/symbols/application/diagrams/diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]` in `domain/impact`.
<!-- okf:generated:end links -->
