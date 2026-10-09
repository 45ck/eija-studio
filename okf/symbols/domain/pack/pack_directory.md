---
type: Function
title: domain.pack.pack_directory
description: The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the same place as the pack.
resource: repo://src/eija_studio/domain/pack.py#pack_directory
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#pack_directory
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 89069e839b1d9d28be4338ac539adbb4c276e6b201ded526a15de439cdfd7ea7
notes_baseline: fcf9aa8d0a413cc5a531f8194032c8601f0c0cb370044514fa4cbdc0afc2b868
---

# domain.pack.pack_directory

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def pack_directory(pack: Pack) -> Path \| None` |
| Code | `repo://src/eija_studio/domain/pack.py#pack_directory` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The directory this exact pack snapshot was read from, or its authored directory, so optional files beside
`pack.json` (such as `data.json`) are read from the same place as the pack.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.PACKS_ROOT](/symbols/domain/pack/PACKS_ROOT.md) - Constant `PACKS_ROOT` in `domain/pack`.
* [domain.pack.PACK_FILE](/symbols/domain/pack/PACK_FILE.md) - Constant `PACK_FILE` in `domain/pack`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
* [domain.pack.derive](/symbols/domain/pack/derive.md) - A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside `pack.json` (`data.json`, `screens.json`, `scenarios…
* [domain.scenarios.scenarios_for](/symbols/domain/scenarios/scenarios_for.md) - The scenarios beside this pack's `pack.json`, or none.
* [domain.screens.load_screens](/symbols/domain/screens/load_screens.md) - The pack's screens, or None when the pack has no `screens.json`.
* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
<!-- okf:generated:end links -->
