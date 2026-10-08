---
type: Function
title: domain.screens.use_cases
description: '`create`, then each distinct action in transition-id order: the ellipses of the use case diagram.'
resource: repo://src/eija_studio/domain/screens.py#use_cases
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#use_cases
  title: domain/screens.py
  hash_method: ast-v2
  sha256: e0fbd0fcc2078752d007dbb93664d844b2c0ec63de6c059b2be307a2cf1f6e69
notes_baseline: f1c942fb0c9998e9c112c5b16fb5d36a5102aa8f2783a205d443610250ff7c5f
---

# domain.screens.use_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `def use_cases(model: Workflow) -> list[str]` |
| Code | `repo://src/eija_studio/domain/screens.py#use_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`create`, then each distinct action in transition-id order: the ellipses of the use case diagram.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.screens.CREATE](/symbols/domain/screens/CREATE.md) - Constant `CREATE` in `domain/screens`.

## Referenced by

* [domain.screens.check_screens](/symbols/domain/screens/check_screens.md) - Design problems, each with a stable code and the use case it is about.
* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One screen per use case: `create` asks for every record attribute; an action shows the required ones.
<!-- okf:generated:end links -->
