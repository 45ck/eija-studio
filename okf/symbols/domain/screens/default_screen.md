---
type: Function
title: domain.screens.default_screen
description: 'The screen a use case gets when nobody designed one: `create` asks for every record field (attributes, then the references of built associations); an action shows the required ones.'
resource: repo://src/eija_studio/domain/screens.py#default_screen
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#default_screen
  title: domain/screens.py
  hash_method: ast-v2
  sha256: 4c77c484d2d9b61f1eb611e602dfd089a8e79ea10f8e18e4b96c3f83fd31a5ab
notes_baseline: 4dc904052203489cda0009c8ca7ec64c37de168aae66f8280d1744cd87611fcc
---

# domain.screens.default_screen

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `def default_screen(case: str \| None, data: DataModel \| None) -> Screen` |
| Code | `repo://src/eija_studio/domain/screens.py#default_screen` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The screen a use case gets when nobody designed one: `create` asks for every record field (attributes, then the
references of built associations); an action shows the required ones.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.record_fields](/symbols/domain/data/record_fields.md) - What a record holds: the record class's attributes, then each reference field as text holding an object's id.
* [domain.screens.Screen](/symbols/domain/screens/Screen.md) - `class Screen(Contract)` in `domain/screens`.

## Referenced by

* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One default screen per use case.
<!-- okf:generated:end links -->
