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
  sha256: 4cb2ff64efab7ed6f8e3ec33df9af699ceeb528a4369883bdc2de291fa73f268
notes_baseline: bc00a2e0df2d28d4433591371cfaa1602f8395f77369d38c123e1acdb8ced7e3
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
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
* [application.review.review_change](/symbols/application/review/review_change.md) - Everything a reviewer needs to check a change: what changed, how risky, and what the kernel does differently.
<!-- okf:generated:end links -->
