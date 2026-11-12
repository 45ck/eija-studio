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
  sha256: 054d0565b58fba200a2fe51b63dff7fd3c1e000fbe41dd50abfb2898e6c0a6d1
notes_baseline: 407ee4f2910e3c736d36e3345a125ccc49755117329742e7823ddd85116ba2d5
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
