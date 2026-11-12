---
type: Function
title: application.diagrams.diff_summary
description: 'Structured diff of two workflows: states, and transitions by action with each changed field''s before and after.'
resource: repo://src/eija_studio/application/diagrams.py#diff_summary
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagrams.py#diff_summary
  title: application/diagrams.py
  hash_method: ast-v2
  sha256: 27d0a86c47cb4030d075aa583fc3ca8c9efdb6db2ce29c1be55b0758998eb1d6
notes_baseline: 2a19847e68aabb021217821aa5925a92564284da695f69c0ece027493bc9a18b
---

# application.diagrams.diff_summary

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagrams`](/modules/application/diagrams.md) |
| Signature | `def diff_summary(before: Workflow, after: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/diagrams.py#diff_summary` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.impact.changed_fields](/symbols/domain/impact/changed_fields.md) - Semantic differences of one action's transition.
* [domain.impact.keyed](/symbols/domain/impact/keyed.md) - Both models' transitions keyed for comparison.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
* [application.review.review_change](/symbols/application/review/review_change.md) - Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
<!-- okf:generated:end links -->
