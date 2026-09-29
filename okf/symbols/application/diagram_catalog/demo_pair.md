---
type: Function
title: application.diagram_catalog.demo_pair
description: 'Baseline and the demo candidate: the default pack''s baseline with its first supported meaning applied.'
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
  sha256: 2cbea45d4d05133818e61ae39b23f0ffa08c2d8582d9f8bf647ad612f46b61b2
notes_baseline: f5010957c72dc57090f479c811041d4a641ecc3799b46d8bc4c88cab606a18ee
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
Baseline and the demo candidate: the default pack's baseline with its first supported meaning applied.
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
