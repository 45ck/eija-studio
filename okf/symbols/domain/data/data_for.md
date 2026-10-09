---
type: Function
title: domain.data.data_for
description: 'The data model beside this pack''s `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.'
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
  sha256: d48e5cb4d04567c91290eace2bcefa7568103ef39281abcd686c96ad100c7a97
notes_baseline: ea0a6ea87838c59994760ccf082903d4782abbaacc3445a6b21eba75e9928d71
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
The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DATA_FILE](/symbols/domain/data/DATA_FILE.md) - Constant `DATA_FILE` in `domain/data`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.held](/symbols/domain/pack/held.md) - What a draft holds as its file `name` (see `hold`), or None to read the file from the pack's folder.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
* [application.new_system.classes](/symbols/application/new_system/classes.md) - A system's record class and each class's attribute names, for naming data-model steps (ADR-0202); None when the system has no class diagram.
* [application.sequences.record_name](/symbols/application/sequences/record_name.md) - The record lifeline's name and its class: `loan : Loan` when the pack has a data model.
<!-- okf:generated:end links -->
