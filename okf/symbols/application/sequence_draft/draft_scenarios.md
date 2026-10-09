---
type: Function
title: application.sequence_draft.draft_scenarios
description: 'Scenarios for a system with none: each step''s expectation is what the kernel does on `model`.'
resource: repo://src/eija_studio/application/sequence_draft.py#draft_scenarios
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_draft.py#draft_scenarios
  title: application/sequence_draft.py
  hash_method: ast-v2
  sha256: 73f1c718223195e5be4915afb162f187e2da95e7b7a5860241e40e27f531c409
notes_baseline: 542710f09d181994f421603636cc9d1942a263095a272d0b3806c9987b7c481b
---

# application.sequence_draft.draft_scenarios

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequence_draft`](/modules/application/sequence_draft.md) |
| Signature | `def draft_scenarios(pack: Pack, model: Workflow) -> Scenarios` |
| Code | `repo://src/eija_studio/application/sequence_draft.py#draft_scenarios` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.scenario_run.record_steps](/symbols/application/scenario_run/record_steps.md) - What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
* [application.sequence_draft.MAX_DRAFTS](/symbols/application/sequence_draft/MAX_DRAFTS.md) - Constant `MAX_DRAFTS` in `application/sequence_draft`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
* [domain.scenarios.parse_scenarios](/symbols/domain/scenarios/parse_scenarios.md) - `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.

## Referenced by

* [application.sequence_draft.scenarios_or_draft](/symbols/application/sequence_draft/scenarios_or_draft.md) - The pack's scenarios ("pack"), or a draft from the model in force when it has none ("drafted").
<!-- okf:generated:end links -->
