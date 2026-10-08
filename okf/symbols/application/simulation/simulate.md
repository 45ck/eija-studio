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
  sha256: 8f8ff1fdf6a35d7010987c4cfc31d6f806f08977227ac7174ac22fd603e92e0a
notes_baseline: d8e5374f3fd85400a3367e496e2d754dadfdac5d00c9483b1f37672b0e7ccb3b
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

* [application.simulation.MAX_STEPS](/symbols/application/simulation/MAX_STEPS.md) - Constant `MAX_STEPS` in `application/simulation`.
* [application.simulation.MemorySession](/symbols/application/simulation/MemorySession.md) - The kernel's unit-of-work port over plain dictionaries, keeping every record, operation and effect.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
