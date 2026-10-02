---
type: Module
title: adapters.repository
description: Repository analysis and bounded source navigation over captured checkout bytes.
resource: repo://src/eija_studio/adapters/repository.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/repository.py
  title: adapters/repository.py
  hash_method: ast-api-v1
  sha256: b92fbca836916427c96a9d5b49e94126763c6d8715733a97d3121bcf824331c4
notes_baseline: 9196d9dcd6f114d46c1224db10c5aa2e0fe157494bf94dd34a37849b495a3e35
---

# adapters.repository

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/repository.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Repository analysis and bounded source navigation over captured checkout bytes.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/repository_capture`](/modules/adapters/repository_capture.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.repository_capture](/modules/adapters/repository_capture.md) - Bounded repository reads adapted to the existing deterministic Weave engine.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [adapters.repository_analysis](/modules/adapters/repository_analysis.md) - Captured-byte syntax and partial impact adapted to existing Weave primitives.
* [adapters.repository_change_snapshot](/modules/adapters/repository_change_snapshot.md) - Captured immutable comparison snapshots shared by capture, analysis and retention.
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
