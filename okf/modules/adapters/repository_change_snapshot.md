---
type: Module
title: adapters.repository_change_snapshot
description: Captured immutable comparison snapshots shared by capture, analysis and retention.
resource: repo://src/eija_studio/adapters/repository_change_snapshot.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/repository_change_snapshot.py
  title: adapters/repository_change_snapshot.py
  hash_method: ast-api-v1
  sha256: 8a9af506e0942fea2c81b28e2a230ec2246e5e461071d011daee2c9ef5081f20
notes_baseline: 857f3fb5b4bf0f2834661b320a2c8fa7fb771b049bfe407fc1ade371fd40829a
---

# adapters.repository_change_snapshot

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/repository_change_snapshot.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Captured immutable comparison snapshots shared by capture, analysis and retention.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/repository`](/modules/adapters/repository.md)
* [`adapters/repository_capture`](/modules/adapters/repository_capture.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.repository](/modules/adapters/repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
* [adapters.repository_capture](/modules/adapters/repository_capture.md) - Bounded repository reads adapted to the existing deterministic Weave engine.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [adapters.repository_analysis](/modules/adapters/repository_analysis.md) - Captured-byte syntax and partial impact adapted to existing Weave primitives.
* [adapters.repository_change_cache](/modules/adapters/repository_change_cache.md) - Bounded retention eligibility and installed extractor prerequisite identity.
* [adapters.repository_changes](/modules/adapters/repository_changes.md) - Read-only, bounded comparison of two local Git commits.
<!-- okf:generated:end links -->
