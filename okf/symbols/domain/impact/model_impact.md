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
  sha256: fa8f04caa6b426d3c8b48431ae30e64627699749f7cefc25d01a31cbd31747a0
description_override: Maps the changed actions between two workflows onto the rule, runtime, state-view, journey, obligation, receipt, review-packet and decision chain and closes over it.
notes_baseline: 34c855018bf0c06b608044ea7fb8ce6f336ce1f864768075326b079c7a27fd4e
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: 22a952a5eb7bdf0d09c283bd2d21b88a1eff164aff7e1a9bbc1f5d9d217991f8
  sources_sha256: 1fa7e60b0804d292ba91963007e02ae01a913013daf3257ce6829defb409fc0f
- by: process:wbs-1.5-agent
  at: '2026-09-29T12:00:00Z'
  notes_sha256: 7068aa48c7c5e00741afaa492ba2f57538338d3e24ab145fbccd6da11b472e1a
  sources_sha256: 8897e73296bc1446d9ccad15e96b8d676fa9e7c612396800115306d7fcf97e04
- by: process:claude-code
  at: '2026-11-11T13:00:00Z'
  notes_sha256: e3bf02b93698b6ff483b51c2fe8acf9cf2e26db135566d5329fb04f79052b6f0
  sources_sha256: 903f19f9643615e15a09284a86aa6ca1f0fea1053a69bfb9e7e2e6df10e7db42
- by: process:kernel-inspection
  at: '2026-11-14T00:30:00Z'
  notes_sha256: 893ddf4aa25268ed91ffe48c5cb4921b7908ba25194d5562ee39355bced87f95
  sources_sha256: 34c855018bf0c06b608044ea7fb8ce6f336ce1f864768075326b079c7a27fd4e
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

~~~text
The ripple of a change. Changed transitions root it; so does a change to how a record starts or to a linked
object's lifecycle (`model_changes`, present only when there is one, so other reports keep their bytes; ADR-0246).
~~~
<!-- okf:generated:end facts -->

## Notes

The envelope is explicit in the result: it covers dependencies encoded by this projection mapping, not every real-world consequence. Transitions are compared through `keyed`: by action, or by action and source once an action leaves several states (ADR-0232); the changed list is still by action. A change outside the transitions that changes what the kernel does (initial state, initiators, received signals, a linked object's lifecycle) is named in `model_changes`, present only when non-empty: a start change roots a `record-start` node rippling to the review packet, and a lifecycle change marks the actions that move that object (ADR-0246). Built on [closure](/symbols/domain/impact/closure.md); it is why a rule edit invalidates the receipt and the local decision.

<!-- okf:generated:begin links -->
## Depends on

* [domain.impact.START](/symbols/domain/impact/START.md) - Constant `START` in `domain/impact`.
* [domain.impact.closure](/symbols/domain/impact/closure.md) - Edges mean source affects target.
* [domain.impact.model_changes](/symbols/domain/impact/model_changes.md) - What changed outside the transitions that changes what the kernel does: how a record starts, and the lifecycles of linked objects.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.diagram_catalog.case_diagrams](/symbols/application/diagram_catalog/case_diagrams.md) - Every view for one change case as one JSON-friendly payload.
* [application.diagrams.impact_graph](/symbols/application/diagrams/impact_graph.md) - The ripple of a change through the modelled dependency chain, taken from `domain.impact.model_impact`: changed rules -> runtime -> state view -> journey -> obl…
<!-- okf:generated:end links -->
