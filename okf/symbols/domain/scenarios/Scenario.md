---
type: Class
title: domain.scenarios.Scenario
description: '`class Scenario(Contract)` in `domain/scenarios`.'
resource: repo://src/eija_studio/domain/scenarios.py#Scenario
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py#Scenario
  title: domain/scenarios.py
  hash_method: ast-sig-v1
  sha256: 294a55484fde61fc714af458616493023e2a6bda5a0bb1129bcb393d547baf0a
notes_baseline: 693de5fca4328940cc852ba2a02308ca3177277a407cbb3f5f71eb13a9e06457
---

# domain.scenarios.Scenario

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/scenarios`](/modules/domain/scenarios.md) |
| Signature | `class Scenario(Contract)` |
| Code | `repo://src/eija_studio/domain/scenarios.py#Scenario` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,59}$')` |
| `title` | `str` | `Field(min_length=1, max_length=120)` |
| `start` | `str \| None` | `Field(default=None, pattern=NAME)` |
| `steps` | `tuple[ScenarioStep, ...]` | `Field(min_length=1, max_length=40)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.scenarios.NAME](/symbols/domain/scenarios/NAME.md) - Constant `NAME` in `domain/scenarios`.
* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.

## Referenced by

* [application.scenario_run.run_scenario](/symbols/application/scenario_run/run_scenario.md) - Run one scenario; it stops at the first step whose outcome differs from what it expects.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
