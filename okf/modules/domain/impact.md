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
  sha256: 0084f7ea44c5884a2ad07afa41cffac4a5059f2422cbf581c6898946c3eef7bb
notes_baseline: a16eb74b6059152f4193212103538ee4bbaa112524cf121cfd4e71f2e04f70a5
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
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [domain.impact.closure](/symbols/domain/impact/closure.md) - Edges mean source affects target.
* [domain.impact.model_impact](/symbols/domain/impact/model_impact.md) - `def model_impact(before: Workflow, after: Workflow) -> dict` in `domain/impact`.
<!-- okf:generated:end links -->
