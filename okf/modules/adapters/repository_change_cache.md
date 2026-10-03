---
type: Module
title: adapters.repository_change_cache
description: Bounded retention eligibility and installed extractor prerequisite identity.
resource: repo://src/eija_studio/adapters/repository_change_cache.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/repository_change_cache.py
  title: adapters/repository_change_cache.py
  hash_method: ast-api-v1
  sha256: b653ff74870a1470117d8816e11b61e948d5af40787d4de5559fc74b91c095fd
notes_baseline: b40a536d4b0810bc114edaaffdbe3cbb299933233d36e8a953a860f5d36f5297
---

# adapters.repository_change_cache

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/repository_change_cache.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Bounded retention eligibility and installed extractor prerequisite identity.

Retention is optional. Revalidation and request ordering remain with the Git
comparison adapter; these helpers neither read target source nor return it.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`adapters/repository_change_snapshot`](/modules/adapters/repository_change_snapshot.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [adapters.repository_change_snapshot](/modules/adapters/repository_change_snapshot.md) - Captured immutable comparison snapshots shared by capture, analysis and retention.

## Referenced by

* [adapters.repository_changes](/modules/adapters/repository_changes.md) - Read-only, bounded comparison of two local Git commits.
<!-- okf:generated:end links -->
