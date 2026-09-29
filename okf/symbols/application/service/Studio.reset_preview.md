---
type: Method
title: application.service.Studio.reset_preview
description: '`def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.'
resource: repo://src/eija_studio/application/service.py#Studio.reset_preview
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.reset_preview
  title: application/service.py
  hash_method: ast-v2
  sha256: 7cff8fd800e033486375ac6a199e991e16ce2aba7de3ff364aa46241697e7780
notes_baseline: 39664dc6c32fb89e7581d5313fc8948f6b2de325d226566d5bd6ca9a4de7dfea
---

# application.service.Studio.reset_preview

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def reset_preview(self, case_id: str, expected: int, state: str \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.reset_preview` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None, pack: Pack | No…` in `application/runtime`.
<!-- okf:generated:end links -->
