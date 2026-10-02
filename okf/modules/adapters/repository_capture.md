---
type: Module
title: adapters.repository_capture
description: Bounded repository reads adapted to the existing deterministic Weave engine.
resource: repo://src/eija_studio/adapters/repository_capture.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/repository_capture.py
  title: adapters/repository_capture.py
  hash_method: ast-api-v1
  sha256: 100e7bb0b6140b9d519f6f0855f358c456e1dd37038288f1391a51ced2f30671
notes_baseline: ba277e39bfbd0e6de44b9fcbbc5f171cc892e55b3b956480b1bfa06af1610fd2
---

# adapters.repository_capture

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/repository_capture.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Bounded repository reads adapted to the existing deterministic Weave engine.

Only tracked, non-ignored, permitted text files enter a temporary mirror. Weave never
receives the original checkout, so a declared binding cannot bypass those exclusions.
Git metadata commands do not run project code, hooks, filters, or external diff tools.
The trusted-local-user assumption still applies: this is not an OS security sandbox.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [adapters.repository](/modules/adapters/repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
* [adapters.repository_analysis](/modules/adapters/repository_analysis.md) - Captured-byte syntax and partial impact adapted to existing Weave primitives.
* [adapters.repository_change_snapshot](/modules/adapters/repository_change_snapshot.md) - Captured immutable comparison snapshots shared by capture, analysis and retention.
* [adapters.repository_changes](/modules/adapters/repository_changes.md) - Read-only, bounded comparison of two local Git commits.
<!-- okf:generated:end links -->
