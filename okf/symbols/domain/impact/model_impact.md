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
  hash_method: ast-v1
  sha256: 46f9bca100abff59cc6ad75e52835f2a16e8648d900c961087a9088afae7cd62
description_override: Maps the changed actions between two workflows onto the rule, runtime, state-view, journey, obligation, receipt, review-packet and decision chain and closes over it.
---

# domain.impact.model_impact

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def model_impact(before: Workflow, after: Workflow) -> dict` |
| Code | `repo://src/eija_studio/domain/impact.py#model_impact` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The envelope is explicit in the result: it covers dependencies encoded by this excursion projection mapping, not every real-world consequence. Built on [closure](/symbols/domain/impact/closure.md); it is why a rule edit invalidates the receipt and the local decision.

<!-- okf:generated:begin links -->
## Depends on

* [domain.impact.closure](/symbols/domain/impact/closure.md) - Edges mean source affects target.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
<!-- okf:generated:end links -->
