---
type: Module
title: domain.scenarios
description: 'Scenarios: a pack''s test cases, written as stories a person can read and the kernel can run (ADR-0177).'
resource: repo://src/eija_studio/domain/scenarios.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py
  title: domain/scenarios.py
  hash_method: ast-api-v1
  sha256: b25884a9f7fb3c01de716a11b5ae41ca96ddf9a7544d66de12238dee8f0be84f
notes_baseline: 9c1fb951f09f1271715eeb59d370cd6cb57cee038612d41fcc6ca4e376a92ef0
---

# domain.scenarios

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/scenarios.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).

A scenario starts a new record (in the model's initial state unless it names another), then lists steps. Each step
is a fixture actor taking an action, and what must happen: the record moves to a state, or the kernel refuses with a
code. Scenarios decide nothing; they pin down what the kernel does, so a change to the model that alters it shows up
as a failing test. They live in an optional `scenarios.json` beside the pack's `pack.json` with their own digest.
~~~

## Public symbols

* [`NAME`](/symbols/domain/scenarios/NAME.md) (constant) - no docstring
* [`SCENARIOS_FILE`](/symbols/domain/scenarios/SCENARIOS_FILE.md) (constant) - no docstring
* [`Scenario`](/symbols/domain/scenarios/Scenario.md) (class) - no docstring
* [`ScenarioStep`](/symbols/domain/scenarios/ScenarioStep.md) (class) - no docstring
* [`Scenarios`](/symbols/domain/scenarios/Scenarios.md) (class) - no docstring
* [`Then`](/symbols/domain/scenarios/Then.md) (class) - What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).
* [`load_scenarios`](/symbols/domain/scenarios/load_scenarios.md) (function) - The scenarios in `directory`, or None when it has no `scenarios.json`.
* [`parse_scenarios`](/symbols/domain/scenarios/parse_scenarios.md) (function) - no docstring
* [`scenarios_for`](/symbols/domain/scenarios/scenarios_for.md) (function) - The scenarios beside this pack's `pack.json`, or none.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [application.new_system](/modules/application/new_system.md) - Start a new system (ADR-0185): the pack documents for a system started from a sketch or copied from a template.
* [application.scenario_run](/modules/application/scenario_run.md) - Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
* [application.sequence_draft](/modules/application/sequence_draft.md) - Scenarios drafted from the model, for a system that has none yet (ADR-0195).
* [application.sequence_layout](/modules/application/sequence_layout.md) - Where a scenario's sequence diagram is drawn, and its export (ADR-0195).
* [application.sequences](/modules/application/sequences.md) - The pack's scenarios drawn as UML sequence diagrams the kernel checks (ADR-0195).
* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
* [interfaces.play](/modules/interfaces/play.md) - PlayIDE routes: the visual UML canvas page, Build & run of the model as a live app beside it (ADR-0151), and Simulate, seeded simulated users whose every step…
* [domain.scenarios.NAME](/symbols/domain/scenarios/NAME.md) - Constant `NAME` in `domain/scenarios`.
* [domain.scenarios.SCENARIOS_FILE](/symbols/domain/scenarios/SCENARIOS_FILE.md) - Constant `SCENARIOS_FILE` in `domain/scenarios`.
* [domain.scenarios.Scenario](/symbols/domain/scenarios/Scenario.md) - `class Scenario(Contract)` in `domain/scenarios`.
* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.
* [domain.scenarios.Scenarios.digest](/symbols/domain/scenarios/Scenarios.digest.md) - `def digest(self) -> str` in `domain/scenarios`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
* [domain.scenarios.Scenarios.unique](/symbols/domain/scenarios/Scenarios.unique.md) - `def unique(self) -> Scenarios` in `domain/scenarios`.
* [domain.scenarios.Then](/symbols/domain/scenarios/Then.md) - What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).
* [domain.scenarios.Then.one](/symbols/domain/scenarios/Then.one.md) - `def one(self) -> Then` in `domain/scenarios`.
* [domain.scenarios.load_scenarios](/symbols/domain/scenarios/load_scenarios.md) - The scenarios in `directory`, or None when it has no `scenarios.json`.
* [domain.scenarios.parse_scenarios](/symbols/domain/scenarios/parse_scenarios.md) - `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.
* [domain.scenarios.scenarios_for](/symbols/domain/scenarios/scenarios_for.md) - The scenarios beside this pack's `pack.json`, or none.
<!-- okf:generated:end links -->
