---
type: Function
title: application.simulation.simulate
description: Run `steps` seeded attempts by the pack's fixture actors through the kernel and report where they went.
resource: repo://src/eija_studio/application/simulation.py#simulate
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/simulation.py#simulate
  title: application/simulation.py
  hash_method: ast-v2
  sha256: a9e71e0c3d5cda41e1af699bfc57e5d7ae3a6191465aea557729b1f9e7327f5d
notes_baseline: 4d2fedb639c83744c5c0b07a1e932ceaaa6663de9898b421e16f98e18b53f3ea
---

# application.simulation.simulate

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/simulation`](/modules/application/simulation.md) |
| Signature | `def simulate(pack: Pack, model: Workflow, *, seed: int=1, steps: int=500) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/simulation.py#simulate` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Run `steps` seeded attempts by the pack's fixture actors through the kernel and report where they went.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
