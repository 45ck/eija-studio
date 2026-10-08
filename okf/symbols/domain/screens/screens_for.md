---
type: Function
title: domain.screens.screens_for
description: The screens beside this pack's `pack.json`, or the default ones.
resource: repo://src/eija_studio/domain/screens.py#screens_for
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#screens_for
  title: domain/screens.py
  hash_method: ast-v2
  sha256: 6964eaaa5662d2be390ef7d4550f1c19707851eedb58cb755a19364ff20da982
notes_baseline: 34c6f3f065fdc37a5449399d6d55faa9c771c60b1f8de5abd1f958155a0d56bb
---

# domain.screens.screens_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `def screens_for(pack: Pack, model: Workflow, data: DataModel \| None) -> Screens` |
| Code | `repo://src/eija_studio/domain/screens.py#screens_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The screens beside this pack's `pack.json`, or the default ones.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One screen per use case: `create` asks for every record attribute; an action shows the required ones.
* [domain.screens.load_screens](/symbols/domain/screens/load_screens.md) - The pack's screens, or None when the pack has no `screens.json`.
<!-- okf:generated:end links -->
