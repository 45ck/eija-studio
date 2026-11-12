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
  sha256: ed025c38dd2008e535ce2fb22bf4a5a55bd250f24b1a5ab5494f3d151ed58689
notes_baseline: fa2ae60fdcaf7686f67c4763b4360d067dc015e7a9b008d481725ba9e1d0abe3
---

# application.scenario_run.record_steps

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scenario_run`](/modules/application/scenario_run.md) |
| Signature | `def record_steps(pack: Pack, model: Workflow, start: str \| None, steps: Sequence[tuple[str, str] \| tuple[str, str, Delay \| None]], values: dict[str, Any] \| None=None) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/scenario_run.py#record_steps` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
A step given as (actor, action, wait) lets that time pass first and keeps its wait (ADR-0237).

This is how a person adds a test: try the steps, read what happened, and keep it if it is what should happen.
`values` are the record's values, which guards over values read (ADR-0234).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Delay](/symbols/domain/models/Delay.md) - A UML time event, ``after(14 days)`` (issue #93, ADR-0237): the transition may be taken only once the record has been in its source state this long.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.

## Referenced by

* [application.sequence_draft.draft_scenarios](/symbols/application/sequence_draft/draft_scenarios.md) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
<!-- okf:generated:end links -->
