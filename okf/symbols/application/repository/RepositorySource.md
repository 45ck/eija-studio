---
type: Class
title: application.repository.RepositorySource
description: Evidence about one explicitly configured checkout and its declared domain bindings.
resource: repo://src/eija_studio/application/repository.py#RepositorySource
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/repository.py#RepositorySource
  title: application/repository.py
  hash_method: ast-sig-v1
  sha256: 9badecc35a35811008e7be3bf51a9292b82cd23475eb3ded1d3575eb47ada9cf
notes_baseline: c45caaf2a087df8faf4ea2d06dae95b9399c59330f44a9073beeecdb1297caa8
---

# application.repository.RepositorySource

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/repository`](/modules/application/repository.md) |
| Signature | `class RepositorySource(Protocol)` |
| Code | `repo://src/eija_studio/application/repository.py#RepositorySource` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Evidence about one explicitly configured checkout and its declared domain bindings.
~~~

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def snapshot(self) -> dict[str, Any]`
* `def context(self) -> dict[str, Any]`
* `def impact(self, subject: str) -> dict[str, Any]`
* `def read_source(self, reference: str) -> dict[str, Any]`
* `def freshness(self, file_hashes: Mapping[str, str]) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
