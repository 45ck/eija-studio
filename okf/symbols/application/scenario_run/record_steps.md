---
type: Function
title: application.scenario_run.record_steps
description: What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
resource: repo://src/eija_studio/application/scenario_run.py#record_steps
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scenario_run.py#record_steps
  title: application/scenario_run.py
  hash_method: ast-v2
  sha256: 101dd3b7dc20a65155f6da45c47ed8454f7dd3f4eddb6a04a476ca9b3e9f4e7d
notes_baseline: 9b372b5f5389c89eb011b58cee3d3ba1cbb904abd52496e2c1a4a34f45ded532
---

# application.scenario_run.record_steps

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scenario_run`](/modules/application/scenario_run.md) |
| Signature | `def record_steps(pack: Pack, model: Workflow, start: str \| None, steps: list[tuple[str, str]], values: dict[str, Any] \| None=None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/scenario_run.py#record_steps` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.

This is how a person adds a test: try the steps, read what happened, and keep it if it is what should happen.
`values` are the record's values, which guards over values read (ADR-0234).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.

## Referenced by

* [application.sequence_draft.draft_scenarios](/symbols/application/sequence_draft/draft_scenarios.md) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
<!-- okf:generated:end links -->
