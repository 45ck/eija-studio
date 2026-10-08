---
type: Function
title: application.repository.read_repository_source
description: Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
resource: repo://src/eija_studio/application/repository.py#read_repository_source
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/repository.py#read_repository_source
  title: application/repository.py
  hash_method: ast-v2
  sha256: 35a113ac77e5effe31b0f4590aba35a69b8cf88e6c37447b5e8340739c057a51
notes_baseline: 0343db383fa734d1efda336d6d8b7f50c420f4b7bd8d19abe2666073a16dc354
---

# application.repository.read_repository_source

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/repository`](/modules/application/repository.md) |
| Signature | `def read_repository_source(source: RepositorySource \| None, reference: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/repository.py#read_repository_source` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.repository.RepositorySource](/symbols/application/repository/RepositorySource.md) - Evidence about one explicitly configured checkout and its declared domain bindings.

## Referenced by

* [application.service.Studio.repository_source](/symbols/application/service/Studio.repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
<!-- okf:generated:end links -->
