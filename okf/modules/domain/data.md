---
type: Module
title: domain.data
description: 'The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.'
resource: repo://src/eija_studio/domain/data.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/data.py
  title: domain/data.py
  hash_method: ast-api-v1
  sha256: 909e8067e61a1d93934143c7751a723a67d67545007d5502abd67640cf9a00f0
notes_baseline: 5947c6b707e41160b0f1339dccdb4e2a6e4724c8601539dc658849979aaffb6c
---

# domain.data

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/data.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.

It lives in an optional `data.json` beside a pack's `pack.json`, with its own digest, so packs without one, their
digests and every receipt over them are unchanged. One entity is the workflow's record: the thing that moves through
the state machine. `check_values` is the only place record values are checked; the generated app calls it, so there
is no second reading of the rules.
~~~

## Public symbols

* [`ATTRIBUTE_NAME`](/symbols/domain/data/ATTRIBUTE_NAME.md) (constant) - no docstring
* [`Association`](/symbols/domain/data/Association.md) (class) - no docstring
* [`Attribute`](/symbols/domain/data/Attribute.md) (class) - no docstring
* [`DATA_FILE`](/symbols/domain/data/DATA_FILE.md) (constant) - no docstring
* [`DataModel`](/symbols/domain/data/DataModel.md) (class) - no docstring
* [`Entity`](/symbols/domain/data/Entity.md) (class) - no docstring
* [`FieldType`](/symbols/domain/data/FieldType.md) (type-alias) - no docstring
* [`Multiplicity`](/symbols/domain/data/Multiplicity.md) (type-alias) - no docstring
* [`NAME`](/symbols/domain/data/NAME.md) (constant) - no docstring
* [`check_values`](/symbols/domain/data/check_values.md) (function) - Validate a record's values against its entity.
* [`data_for`](/symbols/domain/data/data_for.md) (function) - The data model beside this pack's `pack.json`, if it has one.
* [`load_data`](/symbols/domain/data/load_data.md) (function) - The pack's data model, or None when the pack has no `data.json`.
* [`parse_data`](/symbols/domain/data/parse_data.md) (function) - no docstring

## Internal imports

* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [domain.data.ATTRIBUTE_NAME](/symbols/domain/data/ATTRIBUTE_NAME.md) - Constant `ATTRIBUTE_NAME` in `domain/data`.
* [domain.data.Association](/symbols/domain/data/Association.md) - `class Association(Contract)` in `domain/data`.
* [domain.data.Attribute.coherent](/symbols/domain/data/Attribute.coherent.md) - `def coherent(self) -> Attribute` in `domain/data`.
* [domain.data.Attribute](/symbols/domain/data/Attribute.md) - `class Attribute(Contract)` in `domain/data`.
* [domain.data.DATA_FILE](/symbols/domain/data/DATA_FILE.md) - Constant `DATA_FILE` in `domain/data`.
* [domain.data.DataModel.coherent](/symbols/domain/data/DataModel.coherent.md) - `def coherent(self) -> DataModel` in `domain/data`.
* [domain.data.DataModel.digest](/symbols/domain/data/DataModel.digest.md) - `def digest(self) -> str` in `domain/data`.
* [domain.data.DataModel.entity](/symbols/domain/data/DataModel.entity.md) - `def entity(self, name: str) -> Entity` in `domain/data`.
* [domain.data.DataModel](/symbols/domain/data/DataModel.md) - `class DataModel(Contract)` in `domain/data`.
* [domain.data.Entity](/symbols/domain/data/Entity.md) - `class Entity(Contract)` in `domain/data`.
* [domain.data.Entity.unique](/symbols/domain/data/Entity.unique.md) - `def unique(self) -> Entity` in `domain/data`.
* [domain.data.FieldType](/symbols/domain/data/FieldType.md) - Type alias `FieldType` in `domain/data`.
* [domain.data.Multiplicity](/symbols/domain/data/Multiplicity.md) - Type alias `Multiplicity` in `domain/data`.
* [domain.data.NAME](/symbols/domain/data/NAME.md) - Constant `NAME` in `domain/data`.
* [domain.data.check_values](/symbols/domain/data/check_values.md) - Validate a record's values against its entity.
* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
* [domain.data.parse_data](/symbols/domain/data/parse_data.md) - `def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.
<!-- okf:generated:end links -->
