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
  sha256: 2b2a3ee9323e296bac7127644a42bcbdd192bfeee15fd092482f460085fd71fb
notes_baseline: 6e3ad83027c02c1d9da5d3a9e91c43dd15441d8c0f9e311035fd992a908d8d75
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

* [domain.models.SemanticTransaction](/symbols/domain/models/SemanticTransaction.md) - `class SemanticTransaction(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Legacy closed vocabulary (two kinds), kept until the open vocabulary of WBS 1.3 replaces it: the recommendation meaning of the default pack and a rejection-sou…
* [domain.policy.baseline](/symbols/domain/policy/baseline.md) - The pack's baseline workflow.

## Referenced by

* [application.diagram_catalog.docs_bundle](/symbols/application/diagram_catalog/docs_bundle.md) - Markdown pages for docs/diagrams/, keyed by file name.
<!-- okf:generated:end links -->
