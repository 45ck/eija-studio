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
  sha256: b1388e3215fa9f6d5b6d3a469b68c80bd29e4cc8653238a6addb23661881f086
notes_baseline: 3fbe0e4700b56db9f68210208e92150060fd4b8823d4d21159c65a574ed8e9b6
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
