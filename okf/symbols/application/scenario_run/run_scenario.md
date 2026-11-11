---
type: Function
title: application.scenario_run.run_scenario
description: Run one scenario; it stops at the first step whose outcome differs from what it expects.
resource: repo://src/eija_studio/application/scenario_run.py#run_scenario
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scenario_run.py#run_scenario
  title: application/scenario_run.py
  hash_method: ast-v2
  sha256: 2fe40b14fb3f4cd620021683c4cd556a376890415ff7ad2e8bc3cc753d7074ed
notes_baseline: da51e090c36f5ce5131c398d962355b1063adef6f7d3a70517912db7c84c6f4b
---

# application.scenario_run.run_scenario

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scenario_run`](/modules/application/scenario_run.md) |
| Signature | `def run_scenario(pack: Pack, model: Workflow, scenario: Scenario) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/scenario_run.py#run_scenario` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Run one scenario; it stops at the first step whose outcome differs from what it expects.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.scenarios.Scenario](/symbols/domain/scenarios/Scenario.md) - `class Scenario(Contract)` in `domain/scenarios`.

## Referenced by

* [application.scenario_run.run_scenarios](/symbols/application/scenario_run/run_scenarios.md) - Every scenario run on `model`; a model the policy refuses runs none of them.
<!-- okf:generated:end links -->
