---
type: Method
title: application.service.Studio.reset_preview
description: '`def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict` in `application/service`.'
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
  sha256: 7ca0e9c503e42d41d6792f6ff7444a5b28c8d1d7dffca122b54cd51695dacea3
notes_baseline: 7619f1f933ab068cbb3787e75ea29161b2e1dc97b009fe6ddbd6f32b62dadb1c
---

# application.service.Studio.reset_preview

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def reset_preview(self, case_id: str, expected: int, state: str \| None=None) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.reset_preview` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict` in `application/runtime`.
<!-- okf:generated:end links -->
