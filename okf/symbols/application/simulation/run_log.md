---
type: Function
title: application.simulation.run_log
description: Every step of the seeded run in order, and where a run with these breakpoints stops (ADR-0160).
resource: repo://src/eija_studio/application/simulation.py#run_log
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/simulation.py#run_log
  title: application/simulation.py
  hash_method: ast-v2
  sha256: 488c1a97abb0b26fc76dafdc782941710f6a75d3744076c3eaf48c6a40b3ed9c
notes_baseline: 2a8ca72345fbbe44a8eb9341b237d1c85f1f95eb7ad5a2a1643fc18f3d8be973
---

# application.simulation.run_log

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/simulation`](/modules/application/simulation.md) |
| Signature | `def run_log(pack: Pack, model: Workflow, *, seed: int=1, steps: int=500, breakpoints: list[str] \| None=None, break_on_refusal: bool=False) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/simulation.py#run_log` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every step of the seeded run in order, and where a run with these breakpoints stops (ADR-0160).

The run bar's play, pause, step and restart move through this log; nothing runs in the page. A breakpoint is a
diagram element: `state:<name>` stops when a record enters that state, `transition:<id>` when someone tries that
transition, whatever the kernel answers. `break_on_refusal` also stops at every attempt the kernel refuses. A stop
comes after the kernel has decided the step, so the person sees its answer. The same seed and model always give
the same log and the same stops, which is what makes pausing and stepping a faithful replay of one live run.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
