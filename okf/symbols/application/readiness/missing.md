---
type: Function
title: application.readiness.missing
description: 'Every view''s row: what it is missing or what is wrong with it, or nothing when it is ready.'
resource: repo://src/eija_studio/application/readiness.py#missing
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/readiness.py#missing
  title: application/readiness.py
  hash_method: ast-v2
  sha256: 6897474fed0c79c8c0e9c1d8893849f9e0029aa517a026ea2c6eb59134201d40
notes_baseline: 1df2d7e12d448341e0343e3e4872f6c818db11e7874c3c8216891e0307e36aaa
---

# application.readiness.missing

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/readiness`](/modules/application/readiness.md) |
| Signature | `def missing(pack: Pack, model: Workflow, data: DataModel \| None, screens: Screens, scenarios: Scenarios) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/readiness.py#missing` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every view's row: what it is missing or what is wrong with it, or nothing when it is ready.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.readiness.VIEWS](/symbols/application/readiness/VIEWS.md) - Constant `VIEWS` in `application/readiness`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
<!-- okf:generated:end links -->
