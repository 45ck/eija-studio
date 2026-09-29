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
  sha256: 6398db84b410971e6d289014aa4c19852a43538460a6d9eb369d3098a167c454
description_override: Derives rules, state views and journey sentences from the executable transitions, so no view is a second source of truth.
notes_baseline: a187b983cb2c335437e0848d9a93bf936831085d5404cfa280e880199dcc555b
---

# domain.policy.projections

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def projections(model: Workflow) -> dict` |
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

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo…` in `application/compiler`.
<!-- okf:generated:end links -->
