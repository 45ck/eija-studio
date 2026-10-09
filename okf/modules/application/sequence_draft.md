---
type: Module
title: application.sequence_draft
description: Scenarios drafted from the model, for a system that has none yet (ADR-0195).
resource: repo://src/eija_studio/application/sequence_draft.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequence_draft.py
  title: application/sequence_draft.py
  hash_method: ast-api-v1
  sha256: 2df82bd10b6c9475e37a42507efb91e5f980f0ce07bccd63afa2d28de3b92769
notes_baseline: 135eeacb034efd84c973ff18047fcc6338b29da106c1f9fe68064f51af1c18bd
---

# application.sequence_draft

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/sequence_draft.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Scenarios drafted from the model, for a system that has none yet (ADR-0195).

A system started from a sketch has a state machine and fixture actors but no `scenarios.json`, so its Sequences and
Tests tabs would be empty. `draft_scenarios` proposes some: the shortest path to each final state, each step taken
by a fixture actor in the transition's role, and one step someone in another role must be refused. What each step
must do is not written here: `scenario_run.record_steps` asks the kernel, so a draft states what the model does now.
It is a draft, never saved: the person keeps it by editing or downloading `scenarios.json`.
~~~

## Public symbols

* [`MAX_DRAFTS`](/symbols/application/sequence_draft/MAX_DRAFTS.md) (constant) - no docstring
* [`draft_scenarios`](/symbols/application/sequence_draft/draft_scenarios.md) (function) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
* [`scenarios_or_draft`](/symbols/application/sequence_draft/scenarios_or_draft.md) (function) - The pack's scenarios ("pack"), or a draft from the model in force when it has none ("drafted").

## Internal imports

* [`application/scenario_run`](/modules/application/scenario_run.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/scenarios`](/modules/domain/scenarios.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.scenario_run](/modules/application/scenario_run.md) - Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.scenarios](/modules/domain/scenarios.md) - Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).

## Referenced by

* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [application.sequence_draft.MAX_DRAFTS](/symbols/application/sequence_draft/MAX_DRAFTS.md) - Constant `MAX_DRAFTS` in `application/sequence_draft`.
* [application.sequence_draft.draft_scenarios](/symbols/application/sequence_draft/draft_scenarios.md) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
* [application.sequence_draft.scenarios_or_draft](/symbols/application/sequence_draft/scenarios_or_draft.md) - The pack's scenarios ("pack"), or a draft from the model in force when it has none ("drafted").
<!-- okf:generated:end links -->
