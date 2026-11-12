---
type: Function
title: application.appgen.timer_cases
description: For each transition with a time event, an actor who may take it tries it on a record that has been in the source state half the time and the whole time, and the kernel's answer (ADR-0237).
resource: repo://src/eija_studio/application/appgen.py#timer_cases
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/appgen.py#timer_cases
  title: application/appgen.py
  hash_method: ast-v2
  sha256: d6acbe6e08ef5380fa4d8803c9af2ae2fe6ea2fc7f54b4784eb0bb3d3a3ed1b9
notes_baseline: 8202dfa4a8c2666a215dbd6906e807cc553676a057061211f0a311a7eae9e9e4
---

# application.appgen.timer_cases

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/appgen`](/modules/application/appgen.md) |
| Signature | `def timer_cases(pack: Pack, model: Workflow) -> list[dict[str, object]]` |
| Code | `repo://src/eija_studio/application/appgen.py#timer_cases` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
For each transition with a time event, an actor who may take it tries it on a record that has been in the source
state half the time and the whole time, and the kernel's answer (ADR-0237). Empty for a model without time events,
so every other oracle keeps its exact bytes.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
