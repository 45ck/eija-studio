---
type: Function
title: domain.screens.check_screens
description: Design problems, each with a stable code and the use case it is about.
resource: repo://src/eija_studio/domain/screens.py#check_screens
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#check_screens
  title: domain/screens.py
  hash_method: ast-v2
  sha256: 63c764875cd0eaa5776dc5416855350e6309108c4e5839c7fd887738a885f1c4
notes_baseline: 56e8ddfbcad0c11a1963a580caca8cadb22e51aabe1a6ba79150d40f5bda8e5a
---

# domain.screens.check_screens

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `def check_screens(screens: Screens, model: Workflow, data: DataModel \| None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/domain/screens.py#check_screens` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Design problems, each with a stable code and the use case it is about. Empty means the screens can be built.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.use_cases](/symbols/domain/screens/use_cases.md) - Creating a record (None), then each distinct action in transition-id order: the ellipses of the use case diagram.

## Referenced by

* [domain.screens.require_buildable](/symbols/domain/screens/require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.
<!-- okf:generated:end links -->
