---
type: Class
title: domain.screens.Screen
description: '`class Screen(Contract)` in `domain/screens`.'
resource: repo://src/eija_studio/domain/screens.py#Screen
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#Screen
  title: domain/screens.py
  hash_method: ast-sig-v1
  sha256: ed5466dc2c7774e08ecd86be9e65de4fddf2eed6965db5550f679d69170ec856
notes_baseline: f425c000fa980ee12faccf5138b2fa98df600748d5df7b63504af2fc8af3796c
---

# domain.screens.Screen

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `class Screen(Contract)` |
| Code | `repo://src/eija_studio/domain/screens.py#Screen` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `use_case` | `str \| None` | `Field(default=CREATE, min_length=1, max_length=60)` |
| `title` | `str` | `Field(min_length=1, max_length=60)` |
| `fields` | `tuple[ScreenField, ...]` | `Field(default=(), max_length=40)` |
| `button` | `str` | `Field(default='', max_length=40)` |

## Methods

* [`unique`](/symbols/domain/screens/Screen.unique.md) - `def unique(self) -> Screen`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.screens.CREATE](/symbols/domain/screens/CREATE.md) - Constant `CREATE` in `domain/screens`.
* [domain.screens.ScreenField](/symbols/domain/screens/ScreenField.md) - `class ScreenField(Contract)` in `domain/screens`.

## Referenced by

* [domain.screens.Screen.unique](/symbols/domain/screens/Screen.unique.md) - `def unique(self) -> Screen` in `domain/screens`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.Screens.screen](/symbols/domain/screens/Screens.screen.md) - `def screen(self, use_case: str | None) -> Screen | None` in `domain/screens`.
* [domain.screens.default_screen](/symbols/domain/screens/default_screen.md) - The screen a use case gets when nobody designed one: `create` asks for every record attribute; an action shows the required ones.
<!-- okf:generated:end links -->
