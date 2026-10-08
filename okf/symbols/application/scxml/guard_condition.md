---
type: Function
title: application.scxml.guard_condition
description: 'The transition''s `cond`: the actor checks of `runtime.check_actor` and the version check, over the event data.'
resource: repo://src/eija_studio/application/scxml.py#guard_condition
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scxml.py#guard_condition
  title: application/scxml.py
  hash_method: ast-v2
  sha256: 6a8da9fb9f6fb36136e221e2ddf3a6b27d1d0f1facb57ab7adf2c5dbbb2b508f
notes_baseline: 827a5c5f6d670e3db8479dc8488029c2847e16a28ddd3e7ae11e0929638daa9a
---

# application.scxml.guard_condition

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scxml`](/modules/application/scxml.md) |
| Signature | `def guard_condition(transition: Transition) -> str` |
| Code | `repo://src/eija_studio/application/scxml.py#guard_condition` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The transition's `cond`: the actor checks of `runtime.check_actor` and the version check, over the event data.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
