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
  sha256: b95e3e22c25b081710481fe3934ac350f80e0dc4314146310a9370d1d0b7da15
notes_baseline: 9a947b15aa6e7f324849392a9d65f43b592fbb6237a26dc4a574dcb69541c6c0
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
* [`data_for`](/symbols/domain/data/data_for.md) (function) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
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

* [application.api_contract](/modules/application/api_contract.md) - The API contract of an app built from a workflow (ADR-0207): an OpenAPI 3.1 document of what the generated server serves, written from the model, the pack and…
* [application.appgen](/modules/application/appgen.md) - App generation: a reviewed workflow model becomes a runnable app and its conformance oracle (ADR-0150).
* [application.class_build](/modules/application/class_build.md) - What the built app does with each part of the class diagram (#145, ADR-0205): the record class is built and checked; the other classes and the associations are…
* [application.data_steps](/modules/application/data_steps.md) - Data-model steps in a chat plan (ADR-0202): add an attribute to a class, remove one, or make one required or optional; and the step that changes the kind of ac…
* [application.landscape](/modules/application/landscape.md) - The system landscape (ADR-0203): the workflows that make up one system, drawn as a UML component diagram, and the places where their class diagrams disagree.
* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.ripple](/modules/application/ripple.md) - Ripple (ADR-0158): what one change to the state machine does to every other diagram of the same system, and the follow-on edits that would keep them in agreeme…
* [application.sequences](/modules/application/sequences.md) - The pack's scenarios drawn as UML sequence diagrams the kernel checks (ADR-0195).
* [domain.screens](/modules/domain/screens.md) - Screens: the user interface of a pack's app, designed against its use cases and data model (ADR-0154).
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [interfaces.play_interop](/modules/interfaces/play_interop.md) - PlayIDE routes for UML interchange (ADR-0190): export the model on screen, and read a UML file as a report.
* [interfaces.uml_interop](/modules/interfaces/uml_interop.md) - `eija uml export` and `eija uml import`: UML interchange from the command line (ADR-0190).
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
* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.data.load_data](/symbols/domain/data/load_data.md) - The pack's data model, or None when the pack has no `data.json`.
* [domain.data.parse_data](/symbols/domain/data/parse_data.md) - `def parse_data(document: Any, pack_id: str) -> DataModel` in `domain/data`.
<!-- okf:generated:end links -->
