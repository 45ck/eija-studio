---
type: Function
title: application.runtime.check_linked
description: The moves a transition makes on the objects the record links to, given each object's state (ADR-0241).
resource: repo://src/eija_studio/application/runtime.py#check_linked
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#check_linked
  title: application/runtime.py
  hash_method: ast-v2
  sha256: 2b562b1a22fc237559ecc45f0a786fde52f86b6f92a0f049c8d9c7575a63dd22
notes_baseline: 4e4bf5e9c4d411e58858d9a0ec97a9ac9184bca407731ad0571a1aafd0063160
---

# application.runtime.check_linked

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def check_linked(model: Workflow, transition: Transition, states: dict[str, str \| None]) -> list[dict[str, str]]` |
| Code | `repo://src/eija_studio/application/runtime.py#check_linked` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The moves a transition makes on the objects the record links to, given each object's state (ADR-0241). Refuses
the whole step when an object is unknown, its state is, or its lifecycle has no move for the event from there.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
