---
type: Function
title: application.runtime.check_guards
description: Refuse a transition whose guards over the record's values do not hold (ADR-0234).
resource: repo://src/eija_studio/application/runtime.py#check_guards
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#check_guards
  title: application/runtime.py
  hash_method: ast-v2
  sha256: 53b86068e6a104c0a0e4bec215e95602e8b5bf90a71c44ac8fcacf718af055bd
notes_baseline: c312af705b306686dc28f0055d2ee790bf65c8be6f7a452f459bd68cea308005
---

# application.runtime.check_guards

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def check_guards(transition: Transition, values: dict[str, Any]) -> None` |
| Code | `repo://src/eija_studio/application/runtime.py#check_guards` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Refuse a transition whose guards over the record's values do not hold (ADR-0234). Missing values fail closed.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
