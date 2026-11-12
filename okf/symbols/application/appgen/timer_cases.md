---
type: Function
title: application.appgen.timer_cases
description: For each transition with a time event, an actor who may take it tries it on a record that has been in the source state half the time and the whole time, and the kernel's answer (ADR-0236).
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
  sha256: aa4c68c0e950a55a3d090f85b43ff44eee1f560fd64f6d10d8792647f9323f66
notes_baseline: 172876fc22aab28d8c6e72446172df6ca1d9455adc8328652c3f2cef3f99eb22
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
state half the time and the whole time, and the kernel's answer (ADR-0236). Empty for a model without time events,
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
