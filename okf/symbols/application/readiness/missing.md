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
  sha256: 900e2d12a2e7b131a0bcfd3d7f911efb116aaf6e51def9440b375a6bce050b3d
notes_baseline: b3eccbf3fda6e43cc1969e1a1cf0f3d9cc86559ac42b6406107c63e208de1c89
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
