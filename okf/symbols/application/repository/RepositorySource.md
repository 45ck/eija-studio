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
  sha256: 8bea782918a78b280fe59c3611ae53a4f0822410add7086c9d8a07fa17726646
notes_baseline: 6ebfac9dbdce4d3bad7189352ef2eb4ff1a8a1c369cb32a5dd285552121a546f
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
* `def impact(self, subject: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]`
* `def read_source(self, reference: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]`
* `def freshness(self, file_hashes: Mapping[str, str] \| None=None, *, expected_source_hash: str \| None=None) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.repository.read_repository_freshness](/symbols/application/repository/read_repository_freshness.md) - Observe captured byte identity; this grants no source conformance, evidence or owner authority.
* [application.repository.read_repository_impact](/symbols/application/repository/read_repository_impact.md) - Known repository links only.
* [application.repository.read_repository_source](/symbols/application/repository/read_repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
