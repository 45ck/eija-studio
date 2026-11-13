---
type: Module
title: domain.impact
description: Module `domain/impact` (no module docstring).
resource: repo://src/eija_studio/domain/impact.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/impact.py
  title: domain/impact.py
  hash_method: ast-api-v1
  sha256: bc1b3e3a87434f3d9110eab59cbfcd63c8abe01329eb86246bc5a6acadc19cc3
notes_baseline: e826354ad6feee92770b4f1d1282b3043595ca455b4e5763aabc2e5e5f1a6445
---

# domain.impact

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/impact.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

_The source carries no module docstring._

## Public symbols

* [`START`](/symbols/domain/impact/START.md) (constant) - no docstring
* [`changed_fields`](/symbols/domain/impact/changed_fields.md) (function) - Semantic differences of one action's transition.
* [`closure`](/symbols/domain/impact/closure.md) (function) - Edges mean source affects target.
* [`keyed`](/symbols/domain/impact/keyed.md) (function) - Both models' transitions keyed for comparison.
* [`model_changes`](/symbols/domain/impact/model_changes.md) (function) - What changed outside the transitions that changes what the kernel does: how a record starts, and the lifecycles of link…
* [`model_impact`](/symbols/domain/impact/model_impact.md) (function) - The ripple of a change.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.diagrams](/modules/application/diagrams.md) - Diagram models derived from the executable Workflow (ADR-0019, ADR-0023).
* [application.ghost_diff](/modules/application/ghost_diff.md) - How a change looks on the state machine: both models on one canvas, with nothing hidden (ADR-0176).
* [application.review](/modules/application/review.md) - Review a model change in PlayIDE instead of a pull request (ADR-0175).
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [domain.impact.START](/symbols/domain/impact/START.md) - Constant `START` in `domain/impact`.
* [domain.impact.changed_fields](/symbols/domain/impact/changed_fields.md) - Semantic differences of one action's transition.
* [domain.impact.closure](/symbols/domain/impact/closure.md) - Edges mean source affects target.
* [domain.impact.keyed](/symbols/domain/impact/keyed.md) - Both models' transitions keyed for comparison.
* [domain.impact.model_changes](/symbols/domain/impact/model_changes.md) - What changed outside the transitions that changes what the kernel does: how a record starts, and the lifecycles of linked objects.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - The ripple of a change.
<!-- okf:generated:end links -->
