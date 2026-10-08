---
type: Class
title: domain.screens.Screens
description: '`class Screens(Contract)` in `domain/screens`.'
resource: repo://src/eija_studio/domain/screens.py#Screens
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/screens.py#Screens
  title: domain/screens.py
  hash_method: ast-sig-v1
  sha256: e28926e945957bff0ad8f29a761dc03d3d7a3e697f37899f042b892834f4d74b
notes_baseline: 372e620500f12e107b3ef38629daba6f9ca9afc56db98a0cd11da9dcd466b363
---

# domain.screens.Screens

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/screens`](/modules/domain/screens.md) |
| Signature | `class Screens(Contract)` |
| Code | `repo://src/eija_studio/domain/screens.py#Screens` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.screens.v1']` | `'eija.screens.v1'` |
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
| `screens` | `tuple[Screen, ...]` | `Field(min_length=1, max_length=80)` |

## Methods

* [`digest`](/symbols/domain/screens/Screens.digest.md) - `def digest(self) -> str`
* [`screen`](/symbols/domain/screens/Screens.screen.md) - `def screen(self, use_case: str) -> Screen \| None`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.screens.Screen](/symbols/domain/screens/Screen.md) - `class Screen(Contract)` in `domain/screens`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [domain.screens.Screens.digest](/symbols/domain/screens/Screens.digest.md) - `def digest(self) -> str` in `domain/screens`.
* [domain.screens.Screens.screen](/symbols/domain/screens/Screens.screen.md) - `def screen(self, use_case: str) -> Screen | None` in `domain/screens`.
* [domain.screens.check_screens](/symbols/domain/screens/check_screens.md) - Design problems, each with a stable code and the use case it is about.
* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One screen per use case: `create` asks for every record attribute; an action shows the required ones.
* [domain.screens.load_screens](/symbols/domain/screens/load_screens.md) - The pack's screens, or None when the pack has no `screens.json`.
* [domain.screens.parse_screens](/symbols/domain/screens/parse_screens.md) - `def parse_screens(document: Any, pack_id: str) -> Screens` in `domain/screens`.
* [domain.screens.require_buildable](/symbols/domain/screens/require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.
* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, or the default ones.
<!-- okf:generated:end links -->
