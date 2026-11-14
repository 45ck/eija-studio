---
type: Function
title: application.scxml.guard_condition
description: 'The transition''s `cond`: the actor checks of `runtime.check_actor`, its guards over record values and the version check, over the event data.'
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
  sha256: c768db24f42070f7e562607b35548aef935c18f007e9663b67af2fce0cdc735d
notes_baseline: ad92bed2b9c485587eccb9b5c2fe2ea32e0bf858b162656663cd60e6729290a6
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
The transition's `cond`: the actor checks of `runtime.check_actor`, its guards over record values and the
version check, over the event data.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
<!-- okf:generated:end links -->
