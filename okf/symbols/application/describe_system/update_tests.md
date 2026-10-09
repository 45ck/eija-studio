---
type: Function
title: application.describe_system.update_tests
description: The tests brought up to date with `model`, for the person to keep or not (What's missing's "Update the tests", ADR-0216).
resource: repo://src/eija_studio/application/describe_system.py#update_tests
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/describe_system.py#update_tests
  title: application/describe_system.py
  hash_method: ast-v2
  sha256: 3b08289c682e6c8f7803374141079649e3b5dec796493b748fc40aba65d63e54
notes_baseline: 80ca98ab194afcbf03befc34c9b3d2da9d2b5f7055e017792db1460c2f6a7e83
---

# application.describe_system.update_tests

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/describe_system`](/modules/application/describe_system.md) |
| Signature | `def update_tests(pack: Pack, model: Workflow, scenarios: Scenarios, record: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/describe_system.py#update_tests` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The tests brought up to date with `model`, for the person to keep or not (What's missing's "Update the tests",
ADR-0216). A test that still passes stays as it is. A failing one is recorded again by the kernel when the model
still has its way (the same id from `tests_for`), and is dropped when it has none: its end state or step is gone.
The way to a new end state is added. Nothing is saved: the result is a draft of `scenarios.json`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.scenario_run.run_scenarios](/symbols/application/scenario_run/run_scenarios.md) - Every scenario run on `model`; a model the policy refuses runs none of them.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
* [domain.scenarios.parse_scenarios](/symbols/domain/scenarios/parse_scenarios.md) - `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.
<!-- okf:generated:end links -->
