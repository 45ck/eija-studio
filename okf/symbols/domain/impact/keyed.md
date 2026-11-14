---
type: Function
title: domain.impact.keyed
description: Both models' transitions keyed for comparison.
resource: repo://src/eija_studio/domain/impact.py#keyed
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/impact.py#keyed
  title: domain/impact.py
  hash_method: ast-v2
  sha256: ed528b59161c2164114224a09bc12ab86b7411f0761336c4973a3b1670f470ba
notes_baseline: 3fe6fff77251c1a4d56269aa2b6fee8071d3d1cd21973f14c95f4114b4738abf
---

# domain.impact.keyed

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def keyed(before: Workflow, after: Workflow) -> tuple[dict[str, Transition], dict[str, Transition]]` |
| Code | `repo://src/eija_studio/domain/impact.py#keyed` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Both models' transitions keyed for comparison. By action while it labels at most one transition in each model,
so a moved source reads as a change of that transition; by action and source state ("Cancel from Paused") once it
labels several in either (ADR-0232).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.diagrams.diff_summary](/symbols/application/diagrams/diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [application.ghost_diff.ghost_diff](/symbols/application/ghost_diff/ghost_diff.md) - The union of two state machines, each element with its status, and the ordered list of changes.
<!-- okf:generated:end links -->
