---
type: Function
title: domain.screens.default_screens
description: 'One screen per use case: `create` asks for every record attribute; an action shows the required ones.'
resource: repo://src/eija_studio/domain/screens.py#default_screens
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#default_screens
  title: domain/screens.py
  hash_method: ast-v2
  sha256: 1f7f073bee4c512c3514a8b7d8e4ea2705676e2876e2988d8da2e616827d400d
notes_baseline: 9efc60cf0df532024f4d60c6cac255fd179da90aa7c1f7c2cdadd23de6e162fc
---

# domain.screens.default_screens

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `def default_screens(pack: Pack, model: Workflow, data: DataModel \| None) -> Screens` |
| Code | `repo://src/eija_studio/domain/screens.py#default_screens` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
One screen per use case: `create` asks for every record attribute; an action shows the required ones.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.use_cases](/symbols/domain/screens/use_cases.md) - Creating a record (None), then each distinct action in transition-id order: the ellipses of the use case diagram.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
<!-- okf:generated:end links -->
