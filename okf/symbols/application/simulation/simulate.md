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
  sha256: 5656a91c4e8a3daa2c075d7a386616d381348088de523061690bd758b7f76524
notes_baseline: 081e58366ecec76b789fd82d4bc425a43498c06b833256ae85b8c39bdaf1251c
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
