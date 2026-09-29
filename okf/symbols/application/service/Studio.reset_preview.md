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
  sha256: 4681f04c8892cf651eb4807b86eb59b022fd5a9a954b7cf84c46e6895fb8d249
notes_baseline: f442f3904b0beb267b5865c142f820519255b0d92200ca6ae5f2346f9fe06b7d
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

* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict[str, An…` in `application/runtime`.
<!-- okf:generated:end links -->
