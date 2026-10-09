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
  sha256: b244773b6deef4eac0d431aa74081cd15aa882748734c81f4b397b454b10673b
notes_baseline: e76738453082c9dc3450e7927f890249be8bcbc8a952dc2c7117b039c68a3eb8
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
