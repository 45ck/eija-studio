---
type: Module
title: interfaces.play
description: 'PlayIDE routes: the visual UML canvas page, and Build & run of the model as a live app beside it (ADR-0151).'
resource: repo://src/eija_studio/interfaces/play.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/play.py
  title: interfaces/play.py
  hash_method: ast-api-v1
  sha256: 13814b50985df47a0415f84038f08506eee34d9b928052c7bd9974df76f4e4d1
notes_baseline: a4a4d7e46766423867a5ce97cdc7cc0e0b685c61dcbbca432db595ec16b73121
---

# interfaces.play

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/play.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
PlayIDE routes: the visual UML canvas page, and Build & run of the model as a live app beside it (ADR-0151).

Build & run reuses `eija build` (ADR-0150): the app is generated into the workspace, its kernel conformance tests run,
and only a PASSing app is started, as a separate local process on a free loopback port. One app runs at a time; a new
model's build replaces it and the IDE stops it on exit. The generated app has no access to the workspace database.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`interfaces/app_build`](/modules/interfaces/app_build.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).

## Referenced by

* [interfaces.http](/modules/interfaces/http.md) - Loopback-only local adapter.
<!-- okf:generated:end links -->
