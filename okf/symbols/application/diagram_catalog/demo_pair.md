---
type: Function
title: application.diagram_catalog.demo_pair
description: Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended).
resource: repo://src/eija_studio/application/diagram_catalog.py#demo_pair
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/diagram_catalog.py#demo_pair
  title: application/diagram_catalog.py
  hash_method: ast-v2
  sha256: 55bfd1ceaea436780f8270c8c1894d027c10a6fc4dc6422f9475f198d28acb9c
notes_baseline: f8b0c3dbf09660594ab48c643d514849d83a22de531f7ad42b720a33a30341b7
---

# application.diagram_catalog.demo_pair

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/diagram_catalog`](/modules/application/diagram_catalog.md) |
| Signature | `def demo_pair() -> tuple[Workflow, Workflow]` |
| Code | `repo://src/eija_studio/application/diagram_catalog.py#demo_pair` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Baseline and the recommend_only candidate the excursion demo produces (rejection source Recommended).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.policy.baseline](/symbols/domain/policy/baseline.md) - The pack's baseline workflow.
* [domain.policy.demo_candidate](/symbols/domain/policy/demo_candidate.md) - The pack's baseline with its first supported meaning applied.

## Referenced by

* [application.diagram_catalog.docs_bundle](/symbols/application/diagram_catalog/docs_bundle.md) - Markdown pages for docs/diagrams/, keyed by file name.
<!-- okf:generated:end links -->
