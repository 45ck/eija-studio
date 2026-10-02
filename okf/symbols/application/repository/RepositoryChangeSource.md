---
type: Class
title: application.repository.RepositoryChangeSource
description: Immutable, read-only facts for an explicit pair in one configured repository.
resource: repo://src/eija_studio/application/repository.py#RepositoryChangeSource
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/repository.py#RepositoryChangeSource
  title: application/repository.py
  hash_method: ast-sig-v1
  sha256: 99045201f2cf7c029b2066e3a274d41db9affccd9761ac42cbb43c051f694ce7
notes_baseline: 3c9069db4283c5cf669f9e3656b3d2e9751c70675c8e9fc98a168243bd33e659
---

# application.repository.RepositoryChangeSource

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/repository`](/modules/application/repository.md) |
| Signature | `class RepositoryChangeSource(Protocol)` |
| Code | `repo://src/eija_studio/application/repository.py#RepositoryChangeSource` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Immutable, read-only facts for an explicit pair in one configured repository.
~~~

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def compare_commits(self, base: str, head: str) -> dict[str, Any]`
* `def read_change_file(self, base: str, head: str, path: str, reference: str \| None=None) -> dict[str, Any]`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.repository.compare_repository_changes](/symbols/application/repository/compare_repository_changes.md) - Validate an immutable comparison request before dispatch to its read-only port.
* [application.repository.read_repository_change_file](/symbols/application/repository/read_repository_change_file.md) - Bound the historical selection before dispatch; absence never bypasses validation.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
<!-- okf:generated:end links -->
