---
type: Method
title: application.service.Studio.execute
description: '`def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.'
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
  sha256: f49e8ecc099db2df510cbb797088fa8716fb9942379a33e34d76206235a5cbc4
notes_baseline: 6a291d701a58d40dfb0dee9d8ad8707a2a9829cdc40e767df1e00a94526a8002
---

# application.service.Studio.execute

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.execute` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault: Callable[[…` in `application/runtime`.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
