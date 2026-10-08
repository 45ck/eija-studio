---
type: Class
title: domain.scenarios.ScenarioStep
description: '`class ScenarioStep(Contract)` in `domain/scenarios`.'
resource: repo://src/eija_studio/domain/scenarios.py#ScenarioStep
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py#ScenarioStep
  title: domain/scenarios.py
  hash_method: ast-sig-v1
  sha256: 97ca4062e3e6ae0b42ae3ed1bf80e9c0d898201c87c52e9d6ab9da2ea2ba02df
notes_baseline: 544f569f73c59d4509246dc0866a29bd1288a7c2abccff79eaf2f996fce0f525
---

# domain.scenarios.ScenarioStep

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/scenarios`](/modules/domain/scenarios.md) |
| Signature | `class ScenarioStep(Contract)` |
| Code | `repo://src/eija_studio/domain/scenarios.py#ScenarioStep` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `actor` | `str` | `Field(min_length=1, max_length=60)` |
| `action` | `str` | `Field(pattern=NAME)` |
| `then` | `Then` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.scenarios.NAME](/symbols/domain/scenarios/NAME.md) - Constant `NAME` in `domain/scenarios`.
* [domain.scenarios.Then](/symbols/domain/scenarios/Then.md) - What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).

## Referenced by

* [application.scenario_run.record_steps](/symbols/application/scenario_run/record_steps.md) - What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
* [domain.scenarios.Scenario](/symbols/domain/scenarios/Scenario.md) - `class Scenario(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
