---
type: Function
title: domain.data.data_for
description: The data model beside this pack's `pack.json`, if it has one.
resource: repo://src/eija_studio/domain/data.py#data_for
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#data_for
  title: domain/data.py
  hash_method: ast-v2
  sha256: 9a48908e90cde435eb9d22500f5732b7a1b58a534aab4214a6cfb28f92f883ac
notes_baseline: 0be42ac8bf6faf4a6591653d20dc6d198244a99cd2d28ad9568d2397e6d9f92e
---

# domain.data.data_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `def data_for(pack: Pack) -> DataModel \| None` |
| Code | `repo://src/eija_studio/domain/data.py#data_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The data model beside this pack's `pack.json`, if it has one.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…

## Referenced by

* [application.sequences.record_name](/symbols/application/sequences/record_name.md) - The record lifeline's name and its class: `loan : Loan` when the pack has a data model.
<!-- okf:generated:end links -->
