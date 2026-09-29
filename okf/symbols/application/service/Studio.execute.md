---
type: Method
title: application.service.Studio.execute
description: '`def execute(self, case_id: str, command: ExecuteCommand, fault=None) -> dict` in `application/service`.'
resource: repo://src/eija_studio/application/service.py#Studio.execute
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.execute
  title: application/service.py
  hash_method: ast-v2
  sha256: 12b66ae114b168dc0e8ad2b0b5e6329c5943994e865d167ae6abbec8a76730a1
notes_baseline: dadc7f29a93e73d7e16f64a6a84916fafc007a2f37ab55168aaae4d6dd612591
---

# application.service.Studio.execute

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def execute(self, case_id: str, command: ExecuteCommand, fault=None) -> dict` |
| Code | `repo://src/eija_studio/application/service.py#Studio.execute` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> di…` in `application/runtime`.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
