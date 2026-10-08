---
type: Function
title: application.scenario_run.run_scenarios
description: Every scenario run on `model`; a model the policy refuses runs none of them.
resource: repo://src/eija_studio/application/scenario_run.py#run_scenarios
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/scenario_run.py#run_scenarios
  title: application/scenario_run.py
  hash_method: ast-v2
  sha256: 4dccc244f76947311823ea1c0f9eb88d19cbaa5ae9be1324a1457becd373d75b
notes_baseline: bae23c9f6ba333027a48ab329082e61aa75fd2a7a4a243b0885ae13f3e053a55
---

# application.scenario_run.run_scenarios

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/scenario_run`](/modules/application/scenario_run.md) |
| Signature | `def run_scenarios(pack: Pack, model: Workflow, scenarios: Scenarios) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/scenario_run.py#run_scenarios` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every scenario run on `model`; a model the policy refuses runs none of them.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.scenario_run.FORMAT](/symbols/application/scenario_run/FORMAT.md) - Constant `FORMAT` in `application/scenario_run`.
* [application.scenario_run.run_scenario](/symbols/application/scenario_run/run_scenario.md) - Run one scenario; it stops at the first step whose outcome differs from what it expects.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.check_policy](/symbols/domain/policy/check_policy.md) - Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
