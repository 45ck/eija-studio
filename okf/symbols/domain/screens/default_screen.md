---
type: Function
title: domain.screens.default_screen
description: 'The screen a use case gets when nobody designed one: `create` asks for every record attribute; an action shows the required ones.'
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
  sha256: 2b924ca45e6181ae4b133ef54e6d9b81f56344b58f4361cb989023b335c87efa
notes_baseline: 5f540621b87f971da822201315884c4cadad22943674140559e558ee1a181679
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
The screen a use case gets when nobody designed one: `create` asks for every record attribute; an action shows
the required ones.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.screens.Screen](/symbols/domain/screens/Screen.md) - `class Screen(Contract)` in `domain/screens`.

## Referenced by

* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One default screen per use case.
<!-- okf:generated:end links -->
