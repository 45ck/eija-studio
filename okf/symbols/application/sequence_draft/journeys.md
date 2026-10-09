---
type: Function
title: application.sequence_draft.journeys
description: Each end state the model can reach with the pack's fixture actors, and the (actor, action) steps that reach it.
resource: repo://src/eija_studio/application/sequence_draft.py#journeys
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_draft.py#journeys
  title: application/sequence_draft.py
  hash_method: ast-v2
  sha256: addf2fb87452b61e1592b850cd4ac57028fae91078b6dc0d17c7ec166e5777d6
notes_baseline: c6e9a5c12da99b95228559a6325221f386232c5d077408da0e6a9141c720e204
---

# application.sequence_draft.journeys

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequence_draft`](/modules/application/sequence_draft.md) |
| Signature | `def journeys(pack: Pack, model: Workflow) -> list[tuple[str, list[tuple[str, str]]]]` |
| Code | `repo://src/eija_studio/application/sequence_draft.py#journeys` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Each end state the model can reach with the pack's fixture actors, and the (actor, action) steps that reach it.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.sequence_draft.draft_scenarios](/symbols/application/sequence_draft/draft_scenarios.md) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
<!-- okf:generated:end links -->
