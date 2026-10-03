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
  sha256: 4f201f10eafdb41526bff8428c693cc58d1f76e130fa80af34abb233927b69c5
notes_baseline: 845f8a234a2105524a4156d02c50a05d1b01e4969d4d70b46eaa29dcd4b7e4ad
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

* [`changed_fields`](/symbols/domain/impact/changed_fields.md) (function) - Semantic differences of one action's transition.
* [`closure`](/symbols/domain/impact/closure.md) (function) - Edges mean source affects target.
* [`model_impact`](/symbols/domain/impact/model_impact.md) (function) - no docstring

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
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [domain.impact.changed_fields](/symbols/domain/impact/changed_fields.md) - Semantic differences of one action's transition.
* [domain.impact.closure](/symbols/domain/impact/closure.md) - Edges mean source affects target.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict[str, Any]` in `domain/impact`.
<!-- okf:generated:end links -->
