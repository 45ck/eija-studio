---
type: Module
title: interfaces.play_interop
description: 'PlayIDE routes for UML interchange (ADR-0190): export the model on screen, and read a UML file as a report.'
resource: repo://src/eija_studio/interfaces/play_interop.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/play_interop.py
  title: interfaces/play_interop.py
  hash_method: ast-api-v1
  sha256: d2ee80435aa4da47b0b4a49fac3fbb7529f344b74b0c5f800b17cf022f34296e
notes_baseline: 50d5f9862a703815c4636ef41a3aaf0b5f4ca6f81fc5555ea9c8267911cabeea
---

# interfaces.play_interop

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/play_interop.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
PlayIDE routes for UML interchange (ADR-0190): export the model on screen, and read a UML file as a report.

`/api/play/export` writes the model the page shows (the model in force, or with the previewed plan) in one of the four
formats. `/api/play/import` reads an uploaded file against the model in force and returns the import report: its
typed edits are offered to the person as a plan, the same as drawn edits, so nothing is applied or saved from here.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/plan`](/modules/application/plan.md)
* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
<!-- okf:generated:end links -->
