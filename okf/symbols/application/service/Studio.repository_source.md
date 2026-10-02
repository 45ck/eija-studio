---
type: Method
title: application.service.Studio.repository_source
description: Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
resource: repo://src/eija_studio/application/service.py#Studio.repository_source
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.repository_source
  title: application/service.py
  hash_method: ast-v2
  sha256: 9b8fcc69e509097d8716810d8434a41931c94af5e0bc87afbb3fc3be4266a978
notes_baseline: 5dbf841ad761b82cb04dc3c066766e3fc58c611affe8d4f61545a6d529e59bac
---

# application.service.Studio.repository_source

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def repository_source(self, reference: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.repository_source` |
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

* [application.repository.read_repository_source](/symbols/application/repository/read_repository_source.md) - Bounded source view from the configured repository's captured nodes; no arbitrary path or execution.
<!-- okf:generated:end links -->
