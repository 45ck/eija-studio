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
  sha256: 6046a17a3072aee897dee6aa3a2f2f38159e416ab660e06e15d69b4f6e471ffd
notes_baseline: ca4be214d2a2b60cb395649f82645d631dd28bee8529e6bc66d937a73a0f6507
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
| `values` | `dict[str, _Value]` | `Field(default_factory=dict, max_length=40)` |
| `steps` | `tuple[ScenarioStep, ...]` | `Field(min_length=1, max_length=40)` |

## Methods

* [`named_values`](/symbols/domain/scenarios/Scenario.named_values.md) - `def named_values(self) -> Scenario`
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
* [application.sequence_layout.place](/symbols/application/sequence_layout/place.md) - `def place(pack: Pack, scenario: Scenario, start: str, steps: list[dict[str, Any]], record: tuple[str, str]) -…` in `application/sequence_layout`.
* [domain.scenarios.Scenario.named_values](/symbols/domain/scenarios/Scenario.named_values.md) - `def named_values(self) -> Scenario` in `domain/scenarios`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
