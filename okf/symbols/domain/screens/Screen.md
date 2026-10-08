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
  sha256: 54f7c83509193f4251906988f337fcccdb9a176fed724152b4186047dfb8d61b
notes_baseline: 88683641e82167260a28fc862cf796af31463d97f9ceb2eadf15bb5a96e07109
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
| `use_case` | `str` | `Field(min_length=1, max_length=60)` |
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
* [domain.screens.ScreenField](/symbols/domain/screens/ScreenField.md) - `class ScreenField(Contract)` in `domain/screens`.

## Referenced by

* [domain.screens.Screen.unique](/symbols/domain/screens/Screen.unique.md) - `def unique(self) -> Screen` in `domain/screens`.
* [domain.screens.Screens](/symbols/domain/screens/Screens.md) - `class Screens(Contract)` in `domain/screens`.
* [domain.screens.Screens.screen](/symbols/domain/screens/Screens.screen.md) - `def screen(self, use_case: str) -> Screen | None` in `domain/screens`.
<!-- okf:generated:end links -->
