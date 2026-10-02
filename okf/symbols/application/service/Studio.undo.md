---
type: Method
title: application.service.Studio.undo
description: Undo the last owner semantic edit; the selected meaning remains an indivisible protected prefix.
resource: repo://src/eija_studio/application/service.py#Studio.undo
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#Studio.undo
  title: application/service.py
  hash_method: ast-v2
  sha256: 8338747a2a5019066b1fd14e7192876fe88cc39fa6740fd33b0cdb42401f51b2
notes_baseline: 0343a6b191cb70a69d457f074f5a73a45adeea09821e79fc40d484318e69f89f
---

# application.service.Studio.undo

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/service`](/modules/application/service.md) |
| Class | [`Studio`](/symbols/application/service/Studio.md) |
| Signature | `def undo(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/service.py#Studio.undo` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Undo the last owner semantic edit; the selected meaning remains an indivisible protected prefix.
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
