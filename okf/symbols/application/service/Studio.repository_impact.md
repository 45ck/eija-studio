---
type: Method
title: application.service.Studio.repository_impact
description: Known repository links only.
resource: repo://src/eija_studio/application/service.py#Studio.repository_impact
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.repository_impact
  title: application/service.py
  hash_method: ast-v2
  sha256: 70515e49c3fe05a50d36740cbab2dd0d7db65a59492f80bd10028389fd2f2a1d
notes_baseline: 79e8ca3921fd83f1e9bda8a4c8aaa324ac57c5ac18776fc79f2c95bf400eb615
---

# application.service.Studio.repository_impact

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def repository_impact(self, term: str, *, expected_source_hash: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.repository_impact` |
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

* [application.repository.read_repository_impact](/symbols/application/repository/read_repository_impact.md) - Known repository links only.
<!-- okf:generated:end links -->
