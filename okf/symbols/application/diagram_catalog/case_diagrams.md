---
type: Function
title: application.diagram_catalog.case_diagrams
description: Every view for one change case as one JSON-friendly payload.
resource: repo://src/eija_studio/application/diagram_catalog.py#case_diagrams
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_catalog.py#case_diagrams
  title: application/diagram_catalog.py
  hash_method: ast-v2
  sha256: c8a9bf2a39a0dc8b38e86bbfc85850b882db649ae974d36ffa967be2d30a1963
notes_baseline: 11566ac59709cb005973edf00a6523f3ab7fd9a805ebc03bfd160ea8c9d7121c
---

# application.diagram_catalog.case_diagrams

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagram_catalog`](/modules/application/diagram_catalog.md) |
| Signature | `def case_diagrams(before: Workflow, after: Workflow \| None, fmt: str='mermaid') -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/diagram_catalog.py#case_diagrams` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every view for one change case as one JSON-friendly payload. `sources` carries the semantic hashes the
text was generated from, so a reader can compare them with the review packet's evidence subject.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.diagram_catalog.VIEW_FORMATS](/symbols/application/diagram_catalog/VIEW_FORMATS.md) - Constant `VIEW_FORMATS` in `application/diagram_catalog`.
* [application.diagram_catalog.render_view](/symbols/application/diagram_catalog/render_view.md) - Generated diagram text for one view.
* [application.diagrams.diff_summary](/symbols/application/diagrams/diff_summary.md) - Structured diff of two workflows: states, and transitions by action with each changed field's before and after.
* [application.diagrams.policy_violations](/symbols/application/diagrams/policy_violations.md) - Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - The ripple of a change.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
