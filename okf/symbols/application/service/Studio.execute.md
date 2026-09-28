---
type: Method
title: application.service.Studio.execute
description: '`def execute(self, case_id: str, command: ExecuteCommand, fault=None) -> dict` in `application/service` (the source has no docstring).'
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
  hash_method: ast-v1
  sha256: 4d9e12b0c4522f67ddf00dc0d19683478d31f5ea3c1a227dbc2ce72eb0158d14
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
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> dict` in `application/runtime` (the source has no d…
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models` (the source has no docstring).
<!-- okf:generated:end links -->
