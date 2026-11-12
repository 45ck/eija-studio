---
type: Function
title: domain.linked.drift
description: 'The states the objects can be in after one move another record makes: any one object takes any move of its lifecycle from its state (ADR-0241).'
resource: repo://src/eija_studio/domain/linked.py#drift
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/linked.py#drift
  title: domain/linked.py
  hash_method: ast-v2
  sha256: 2d1de5e025ee27827fc9f238481bf9b78d94481352d31702f5d86c6647639bbd
notes_baseline: acb586df30e6d8712eeb2173dc0a17243fb183b946a50e5edfb40f0b5450fc5c
---

# domain.linked.drift

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/linked`](/modules/domain/linked.md) |
| Signature | `def drift(model: Workflow, objects: dict[str, str]) -> list[dict[str, str]]` |
| Code | `repo://src/eija_studio/domain/linked.py#drift` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The states the objects can be in after one move another record makes: any one object takes any move of its
lifecycle from its state (ADR-0241).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
