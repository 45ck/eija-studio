---
type: Function
title: application.runtime.check_starter
description: 'The role of the actor starting a record: an unknown actor is refused by the directory and a revoked one as it is refused an action (ADR-0250), so whoever starts a record is checked like whoever acts on one.'
resource: repo://src/eija_studio/application/runtime.py#check_starter
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#check_starter
  title: application/runtime.py
  hash_method: ast-v2
  sha256: 044fe71eff8cb211eb9a8e2f1c21517fbd552cb91fa2f5fa840d3578638bc5c1
notes_baseline: 454bf8d0ff7643bdf91a1839e90617f7b792afc229d7a73e2b28bd7ab136b35d
---

# application.runtime.check_starter

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def check_starter(session: UnitOfWork, actor_id: str) -> str` |
| Code | `repo://src/eija_studio/application/runtime.py#check_starter` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The role of the actor starting a record: an unknown actor is refused by the directory and a revoked one as it is
refused an action (ADR-0250), so whoever starts a record is checked like whoever acts on one.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.

## Referenced by

* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - Start a record.
<!-- okf:generated:end links -->
