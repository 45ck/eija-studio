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
  sha256: 4c0f160e3bfd36fc9644988ce9c522daea8460aa9829c09e12497c10ef59a349
description_override: Maps the changed actions between two workflows onto the rule, runtime, state-view, journey, obligation, receipt, review-packet and decision chain and closes over it.
notes_baseline: 0aed33da6b73a9f7d9324d110608d99a2f99a5bbd9faec66aae354971bc40a4d
---

# domain.impact.model_impact

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/impact`](/modules/domain/impact.md) |
| Signature | `def model_impact(before: Workflow, after: Workflow) -> dict` |
| Code | `repo://src/eija_studio/domain/impact.py#model_impact` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The envelope is explicit in the result: it covers dependencies encoded by this excursion projection mapping, not every real-world consequence. Built on [closure](/symbols/domain/impact/closure.md); it is why a rule edit invalidates the receipt and the local decision.

<!-- okf:generated:begin links -->
## Depends on

* [domain.impact.closure](/symbols/domain/impact/closure.md) - Edges mean source affects target.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo…` in `application/compiler`.
<!-- okf:generated:end links -->
