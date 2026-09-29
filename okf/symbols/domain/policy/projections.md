---
type: Function
title: domain.policy.projections
description: Derives rules, state views and journey sentences from the executable transitions, so no view is a second source of truth.
resource: repo://src/eija_studio/domain/policy.py#projections
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#projections
  title: domain/policy.py
  hash_method: ast-v2
  sha256: b6d80e8f3057e0060aadd5e541949b02c21b46c3af4bc058a8d1b3c4662c9a3e
description_override: Derives rules, state views and journey sentences from the executable transitions, so no view is a second source of truth.
notes_baseline: 7202169821e390365e71cc835a35e68ee46944b297bafb9db0508ac4f4e562c4
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: b9653ce09416d0dbaafd0b8269494a5d791cbb023eb9f6052d69ba815b4df895
  sources_sha256: 7202169821e390365e71cc835a35e68ee46944b297bafb9db0508ac4f4e562c4
---

# domain.policy.projections

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def projections(model: Workflow) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/domain/policy.py#projections` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Journey wording and rules derive from executable transitions, not AI copy.
~~~
<!-- okf:generated:end facts -->

## Notes

Rules, state views and journey sentences are all computed here from the same [Workflow](/symbols/domain/models/Workflow.md), so they agree by construction (see acceptance [AC02](/requirements/ac02.md)). Journey wording is never AI copy.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
<!-- okf:generated:end links -->
