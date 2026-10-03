---
type: Module
title: adapters.repository_analysis
description: Captured-byte syntax and partial impact adapted to existing Weave primitives.
resource: repo://src/eija_studio/adapters/repository_analysis.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/repository_analysis.py
  title: adapters/repository_analysis.py
  hash_method: ast-api-v1
  sha256: dae51d9a55744590fe85fc9320c6d4476f62cee3771a27d909c7ea64ab615991
notes_baseline: 0219b6e49818f7bb4ef3fd9789d82924a1d150a551f799f6c66cf2dc692bb6ca
---

# adapters.repository_analysis

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/repository_analysis.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Captured-byte syntax and partial impact adapted to existing Weave primitives.

Python uses codelink's existing parser, symbol resolver and closure digests over
the supplied bytes. JavaScript runs the existing pinned parser in its bounded
worker. Neither path executes target code or supplies a behavioral proof.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/repository`](/modules/adapters/repository.md)
* [`adapters/repository_capture`](/modules/adapters/repository_capture.md)
* [`adapters/repository_change_snapshot`](/modules/adapters/repository_change_snapshot.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.repository](/modules/adapters/repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
* [adapters.repository_capture](/modules/adapters/repository_capture.md) - Bounded repository reads adapted to the existing deterministic Weave engine.
* [adapters.repository_change_snapshot](/modules/adapters/repository_change_snapshot.md) - Captured immutable comparison snapshots shared by capture, analysis and retention.
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [adapters.repository_changes](/modules/adapters/repository_changes.md) - Read-only, bounded comparison of two local Git commits.
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
