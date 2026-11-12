---
type: Function
title: application.runtime.check_due
description: Refuse a transition with a time event, ``after(14 days)``, before the record has been in its source state that long (ADR-0236).
resource: repo://src/eija_studio/application/runtime.py#check_due
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#check_due
  title: application/runtime.py
  hash_method: ast-v2
  sha256: ef9da7e61524eb0cbabfab3a80ad2f075c7de41ef776eb057925a1fc831b14c3
notes_baseline: 780ab66b074106a450ebcf1d0bdda5d0fe6a1279a2dc88ce9a4f271a40cbc362
---

# application.runtime.check_due

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def check_due(transition: Transition, elapsed: float \| None) -> None` |
| Code | `repo://src/eija_studio/application/runtime.py#check_due` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Refuse a transition with a time event, ``after(14 days)``, before the record has been in its source state that
long (ADR-0236). An unknown entry time is never due (fail closed).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
