---
type: Method
title: application.service.Studio.redo
description: Reapply the next undone typed command through the same interpreter and policy checks.
resource: repo://src/eija_studio/application/service.py#Studio.redo
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.redo
  title: application/service.py
  hash_method: ast-v2
  sha256: 43105b083a3a10e86534d7dba44e98001926ef7b2a4a17d92ffc2528546eea0a
notes_baseline: fbefab2f5f09aa3c158f7aa05d15cc8f5cd0aebda7c51c9608243478f1356e2f
---

# application.service.Studio.redo

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def redo(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.redo` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Reapply the next undone typed command through the same interpreter and policy checks.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.history.replay](/symbols/application/history/replay.md) - Fail closed when stored commands no longer explain the candidate under the exact active pack.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
