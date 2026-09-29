---
type: Function
title: domain.impact.model_impact
description: Maps the changed actions between two workflows onto the rule, runtime, state-view, journey, obligation, receipt, review-packet and decision chain and closes over it.
resource: repo://src/eija_studio/domain/impact.py#model_impact
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/impact.py#model_impact
  title: domain/impact.py
  hash_method: ast-v2
  sha256: cd067b1d87ce123f442f5dbd1f003c2ad457448f41f67e7501fcee007e1c7000
description_override: Maps the changed actions between two workflows onto the rule, runtime, state-view, journey, obligation, receipt, review-packet and decision chain and closes over it.
notes_baseline: 8897e73296bc1446d9ccad15e96b8d676fa9e7c612396800115306d7fcf97e04
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 22a952a5eb7bdf0d09c283bd2d21b88a1eff164aff7e1a9bbc1f5d9d217991f8
  sources_sha256: 1fa7e60b0804d292ba91963007e02ae01a913013daf3257ce6829defb409fc0f
- by: process:wbs-1.5-agent
  at: '2026-09-29T12:00:00Z'
  notes_sha256: 7068aa48c7c5e00741afaa492ba2f57538338d3e24ab145fbccd6da11b472e1a
  sources_sha256: 8897e73296bc1446d9ccad15e96b8d676fa9e7c612396800115306d7fcf97e04
---

# domain.impact.model_impact

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/domain/impact.py#model_impact` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The envelope is explicit in the result: it covers dependencies encoded by this projection mapping, not every real-world consequence. Built on [closure](/symbols/domain/impact/closure.md); it is why a rule edit invalidates the receipt and the local decision.

<!-- okf:generated:begin links -->
## Depends on

* [domain.impact.changed_fields](/symbols/domain/impact/changed_fields.md) - Semantic differences of one action's transition.
* [domain.impact.closure](/symbols/domain/impact/closure.md) - Edges mean source affects target.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
* [application.diagrams.impact_graph](/symbols/application/diagrams/impact_graph.md) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obl…
<!-- okf:generated:end links -->
