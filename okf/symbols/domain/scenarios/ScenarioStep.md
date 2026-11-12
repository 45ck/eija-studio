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
  sha256: 262e55e4f4b8eabd04a190b2b4a4460663bfff149b815af106ffcd2b4dd0a749
notes_baseline: 3ec364bde06156a64d49d07e5749e45eb4ab5513fb9eec56d039450242780350
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
| `wait` | `Delay \| None` | `None` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.Delay](/symbols/domain/models/Delay.md) - A UML time event, ``after(14 days)`` (issue #93, ADR-0237): the transition may be taken only once the record has been in its source state this long.
* [domain.scenarios.NAME](/symbols/domain/scenarios/NAME.md) - Constant `NAME` in `domain/scenarios`.
* [domain.scenarios.Then](/symbols/domain/scenarios/Then.md) - What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).

## Referenced by

* [application.scenario_run.record_steps](/symbols/application/scenario_run/record_steps.md) - What the kernel does for each (actor, action) in turn, written as scenario steps that expect exactly that.
* [domain.scenarios.Scenario](/symbols/domain/scenarios/Scenario.md) - `class Scenario(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
