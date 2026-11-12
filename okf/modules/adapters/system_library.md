---
type: Module
title: adapters.system_library
description: 'Where a person''s own systems live on disk (ADR-0185): one folder per system under a systems home, the recent list, and the saved draft of the work in progress.'
resource: repo://src/eija_studio/adapters/system_library.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/system_library.py
  title: adapters/system_library.py
  hash_method: ast-api-v1
  sha256: 6ce7a78e13b0ae2715f039d1867fb6de2e2447cbbb877d84c3768e8c7fe903cc
notes_baseline: 4fd67477bed04e3038c1bec393983ff4e66b6e1b5dabef1144af43dade649b06
---

# adapters.system_library

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/system_library.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Where a person's own systems live on disk (ADR-0185): one folder per system under a systems home, the recent list,
and the saved draft of the work in progress.

A system folder is an ordinary pack folder (`pack.json`, `data.json`, `screens.json`) with its own workspace,
`.eija/`, beside them, so its change cases, history and draft stay with it. Every write is whole-file and atomic
(written beside, then renamed), with LF line endings. Nothing here decides what a system means: the caller checks
the documents with the kernel before they are written.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

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

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
