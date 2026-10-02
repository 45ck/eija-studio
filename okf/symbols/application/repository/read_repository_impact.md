---
type: Function
title: application.repository.read_repository_impact
description: Known repository links only.
resource: repo://src/eija_studio/application/repository.py#read_repository_impact
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/repository.py#read_repository_impact
  title: application/repository.py
  hash_method: ast-v2
  sha256: e04e1152b3ebdbf9cc37b18084405f82cccb86297f04642da8b92593803ea9a4
notes_baseline: 0042aa46421b18f30de9cfe68f8fc3e902fa125f74af378617a3c84c83574f47
---

# application.repository.read_repository_impact

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/repository`](/modules/application/repository.md) |
| Signature | `def read_repository_impact(source: RepositorySource \| None, term: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/repository.py#read_repository_impact` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Known repository links only. This neither edits the repository nor grants evidence or authority.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.repository.RepositorySource](/symbols/application/repository/RepositorySource.md) - Evidence about one explicitly configured checkout and its declared domain bindings.

## Referenced by

* [application.service.Studio.repository_impact](/symbols/application/service/Studio.repository_impact.md) - Known repository links only.
<!-- okf:generated:end links -->
