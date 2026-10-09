---
type: Module
title: application.landscape
description: 'The system landscape (ADR-0203): the workflows that make up one system, drawn as a UML component diagram, and the places where their class diagrams disagree.'
resource: repo://src/eija_studio/application/landscape.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/landscape.py
  title: application/landscape.py
  hash_method: ast-api-v1
  sha256: f4a4d4f22a21aea43a9e114c508f467c66833d73377d3a541f34ddfa3a62c1ab
notes_baseline: c95dcbcd6a593ce8baf8c798f4f93a0aa4ad7eacb93a62dc4e967674f7a4903f
---

# application.landscape

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/landscape.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
The system landscape (ADR-0203): the workflows that make up one system, drawn as a UML component diagram, and the
places where their class diagrams disagree.

A workflow is a pack: one state machine moving one record class (`data.json`'s `record`). Nothing here is written by
hand for the landscape. Two workflows belong to one system when their class diagrams name the same class, the way two
UML packages that import one class are related. The workflow whose record a class is owns it; any other workflow that
names it uses that workflow. Each workflow provides its actions, each held by the roles its transitions name, and
publishes its notification effects (the outbox the built app writes). Roles with the same name in two workflows are one
actor.

The checks are the questions an architect asks first when two teams model the same thing: who owns this class, do the
copies agree, and do two workflows both claim to move the same record. Each finding names the classes, attributes and
workflows it is about. They are design checks over the documents; the built apps do not call each other, which the
result says.

Pure: takes parsed packs and data models, reads no files.
~~~

## Public symbols

* [`FORMAT`](/symbols/application/landscape/FORMAT.md) (constant) - no docstring
* [`LIMITS`](/symbols/application/landscape/LIMITS.md) (constant) - no docstring
* [`landscape`](/symbols/application/landscape/landscape.md) (function) - The system the workflow `focus` is part of: its workflows, actors, links and findings (ADR-0203).

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.landscape.FORMAT](/symbols/application/landscape/FORMAT.md) - Constant `FORMAT` in `application/landscape`.
* [application.landscape.LIMITS](/symbols/application/landscape/LIMITS.md) - Constant `LIMITS` in `application/landscape`.
* [application.landscape.landscape](/symbols/application/landscape/landscape.md) - The system the workflow `focus` is part of: its workflows, actors, links and findings (ADR-0203).
<!-- okf:generated:end links -->
