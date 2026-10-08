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
  sha256: fb7bdbe0d3632913f786c61f52d8c970fd085099657283c7c80ed8f8e824432b
notes_baseline: 6c899954324effde59cf3f546f4609ed2f16baa22749f772a42dad1279ccfea8
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
