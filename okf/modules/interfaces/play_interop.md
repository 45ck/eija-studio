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
  sha256: 021b99caf41fe1a79129db1ba1605793c62079416426a96f7c86041fb3071534
notes_baseline: 363e8d09d37621c6a0e6979cf6d50f60be1f57e1e669cca543c33444bc6f053a
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

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
<!-- okf:generated:end links -->
