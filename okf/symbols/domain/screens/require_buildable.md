---
type: Function
title: domain.screens.require_buildable
description: '`def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.'
resource: repo://src/eija_studio/domain/screens.py#require_buildable
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#require_buildable
  title: domain/screens.py
  hash_method: ast-v2
  sha256: 9e15c205fa79f951a34b35d3a365d961f4183d349eb7ec72b98036a377a227e7
notes_baseline: c7140e54d4058e141c9771df7bf4081c4577ea391df739a12622b3669820956c
---

# domain.screens.require_buildable

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `def require_buildable(screens: Screens, model: Workflow, data: DataModel \| None) -> None` |
| Code | `repo://src/eija_studio/domain/screens.py#require_buildable` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.check_screens](/symbols/domain/screens/check_screens.md) - Design problems, each with a stable code and the use case it is about.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
