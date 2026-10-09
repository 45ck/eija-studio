---
type: Function
title: application.sequence_draft.scenarios_or_draft
description: The pack's scenarios ("pack"), or a draft from the model in force when it has none ("drafted").
resource: repo://src/eija_studio/application/sequence_draft.py#scenarios_or_draft
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_draft.py#scenarios_or_draft
  title: application/sequence_draft.py
  hash_method: ast-v2
  sha256: 5651eb10f7f5959251df4f8442f3edadc48e182698d1bd6cc3f2c9020a5195e7
notes_baseline: 12caee212df4f7905994b4d8c61577322195c04d67432e96673e35fe1583e6fc
---

# application.sequence_draft.scenarios_or_draft

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequence_draft`](/modules/application/sequence_draft.md) |
| Signature | `def scenarios_or_draft(pack: Pack, scenarios: Scenarios, base: Workflow) -> tuple[Scenarios, str]` |
| Code | `repo://src/eija_studio/application/sequence_draft.py#scenarios_or_draft` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The pack's scenarios ("pack"), or a draft from the model in force when it has none ("drafted").
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.sequence_draft.draft_scenarios](/symbols/application/sequence_draft/draft_scenarios.md) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
