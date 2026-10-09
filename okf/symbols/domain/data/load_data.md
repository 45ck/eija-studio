---
type: Function
title: domain.data.load_data
description: The pack's data model, or None when the pack has no `data.json`.
resource: repo://src/eija_studio/domain/data.py#load_data
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#load_data
  title: domain/data.py
  hash_method: ast-v2
  sha256: a4b91a211d35b6a66e21233ebdb624681044f6bac611e1efdcc35439f548470a
notes_baseline: ca488f2ed09e15eec6627753d693caaf00aae3c6fec2c606783e1527567d1da0
---

# domain.data.load_data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `def load_data(pack_directory: str \| Path, pack_id: str) -> DataModel \| None` |
| Code | `repo://src/eija_studio/domain/data.py#load_data` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's data model, or None when the pack has no `data.json`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DATA_FILE](/symbols/domain/data/DATA_FILE.md) - Constant `DATA_FILE` in `domain/data`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.parse_data](/symbols/domain/data/parse_data.md) - `def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.pack_directory](/symbols/domain/pack/pack_directory.md) - The directory this exact pack snapshot was read from, or its authored directory, so optional files beside `pack.json` (such as `data.json`) are read from the s…

## Referenced by

* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
<!-- okf:generated:end links -->
