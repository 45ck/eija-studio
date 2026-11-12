---
type: Function
title: application.runtime.check_due
description: Refuse a transition with a time event, ``after(14 days)``, before the record has been in its source state that long (ADR-0237).
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
  sha256: 8d6df2acfa9eb5610bab20641fd1b4a618379aedaad9fb3ff9ab1d8cedc1c6a6
notes_baseline: 04ce28cf006231d04ae27dc880702743710000a9d5ccf1c70a2c724fdede1b8b
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
long (ADR-0237). An unknown entry time is never due (fail closed).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
