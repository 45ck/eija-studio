---
type: Class
title: domain.data.DataModel
description: '`class DataModel(Contract)` in `domain/data`.'
resource: repo://src/eija_studio/domain/data.py#DataModel
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py#DataModel
  title: domain/data.py
  hash_method: ast-sig-v1
  sha256: dd8466670fb323c5a0fb1f0977de5c8908698503d3f525a49cd074cc651afa41
notes_baseline: fd8a3f09769c739cf0f8895648ca9cd7e1aba4469768fa45d21a776ccb6e746b
---

# domain.data.DataModel

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/data`](/modules/domain/data.md) |
| Signature | `class DataModel(Contract)` |
| Code | `repo://src/eija_studio/domain/data.py#DataModel` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.data.v1']` | `'eija.data.v1'` |
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
| `record` | `str` | `Field(pattern=NAME)` |
| `entities` | `tuple[Entity, ...]` | `Field(min_length=1, max_length=40)` |
| `associations` | `tuple[Association, ...]` | `Field(default=(), max_length=80)` |

## Methods

* [`coherent`](/symbols/domain/data/DataModel.coherent.md) - `def coherent(self) -> DataModel`
* [`digest`](/symbols/domain/data/DataModel.digest.md) - `def digest(self) -> str`
* [`entity`](/symbols/domain/data/DataModel.entity.md) - `def entity(self, name: str) -> Entity`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.Association](/symbols/domain/data/Association.md) - `class Association(Contract)` in `domain/data`.
* [domain.data.Entity](/symbols/domain/data/Entity.md) - `class Entity(Contract)` in `domain/data`.
* [domain.data.NAME](/symbols/domain/data/NAME.md) - Constant `NAME` in `domain/data`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [application.appgen.app_limits](/symbols/application/appgen/app_limits.md) - `def app_limits(data: DataModel | None) -> list[str]` in `application/appgen`.
* [application.appgen.data_cases](/symbols/application/appgen/data_cases.md) - Record values to create with, and `check_values`' answer for each: a valid record, then each required value missing, each value of the wrong type, each text on…
* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.appgen.readme](/symbols/application/appgen/readme.md) - `def readme(pack: Pack, model: Workflow, cases: int, data: DataModel | None=None) -> str` in `application/appgen`.
* [domain.data.DataModel.coherent](/symbols/domain/data/DataModel.coherent.md) - `def coherent(self) -> DataModel` in `domain/data`.
* [domain.data.DataModel.digest](/symbols/domain/data/DataModel.digest.md) - `def digest(self) -> str` in `domain/data`.
* [domain.data.DataModel.entity](/symbols/domain/data/DataModel.entity.md) - `def entity(self, name: str) -> Entity` in `domain/data`.
* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
* [domain.data.parse_data](/symbols/domain/data/parse_data.md) - `def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.
* [domain.screens.check_screens](/symbols/domain/screens/check_screens.md) - Design problems, each with a stable code and the use case it is about.
* [domain.screens.default_screens](/symbols/domain/screens/default_screens.md) - One screen per use case: `create` asks for every record attribute; an action shows the required ones.
* [domain.screens.require_buildable](/symbols/domain/screens/require_buildable.md) - `def require_buildable(screens: Screens, model: Workflow, data: DataModel | None) -> None` in `domain/screens`.
* [domain.screens.screens_for](/symbols/domain/screens/screens_for.md) - The screens beside this pack's `pack.json`, each use case they leave out given its default screen; or the defaults.
<!-- okf:generated:end links -->
