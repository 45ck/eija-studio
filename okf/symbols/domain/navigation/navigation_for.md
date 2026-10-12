---
type: Function
title: domain.navigation.navigation_for
description: Project actual supported panels from one canonical workflow/data/screens snapshot.
resource: repo://src/eija_studio/domain/navigation.py#navigation_for
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/navigation.py#navigation_for
  title: domain/navigation.py
  hash_method: ast-v2
  sha256: 03f0a7a8cf1533e1589559f96692699f887bb3d12140b399c97eeb6f217f8b9a
notes_baseline: bec9cc180ad1683c9dd91aa4b783e4ae677ecf7ad61480fef7c65eace8e543eb
---

# domain.navigation.navigation_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/navigation`](/modules/domain/navigation.md) |
| Signature | `def navigation_for(pack: Pack, model: Workflow, data: DataModel \| None, screens: Screens) -> Navigation` |
| Code | `repo://src/eija_studio/domain/navigation.py#navigation_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Project actual supported panels from one canonical workflow/data/screens snapshot.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.navigation.Destination](/symbols/domain/navigation/Destination.md) - `class Destination(Contract)` in `domain/navigation`.
* [domain.navigation.Navigation](/symbols/domain/navigation/Navigation.md) - `class Navigation(Contract)` in `domain/navigation`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.require_buildable](/symbols/domain/screens/require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
<!-- okf:generated:end links -->
