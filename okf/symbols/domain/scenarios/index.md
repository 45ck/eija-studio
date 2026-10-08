# Symbols of domain.scenarios

# Classes

* [domain.scenarios.Scenario](Scenario.md) - `class Scenario(Contract)` in `domain/scenarios`.
* [domain.scenarios.ScenarioStep](ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.
* [domain.scenarios.Scenarios](Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
* [domain.scenarios.Then](Then.md) - What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).

# Constants

* [domain.scenarios.NAME](NAME.md) - Constant `NAME` in `domain/scenarios`.
* [domain.scenarios.SCENARIOS_FILE](SCENARIOS_FILE.md) - Constant `SCENARIOS_FILE` in `domain/scenarios`.

# Functions

* [domain.scenarios.load_scenarios](load_scenarios.md) - The scenarios in `directory`, or None when it has no `scenarios.json`.
* [domain.scenarios.parse_scenarios](parse_scenarios.md) - `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.
* [domain.scenarios.scenarios_for](scenarios_for.md) - The scenarios beside this pack's `pack.json`, or none.

# Methods

* [domain.scenarios.Scenarios.digest](Scenarios.digest.md) - `def digest(self) -> str` in `domain/scenarios`.
* [domain.scenarios.Scenarios.unique](Scenarios.unique.md) - `def unique(self) -> Scenarios` in `domain/scenarios`.
* [domain.scenarios.Then.one](Then.one.md) - `def one(self) -> Then` in `domain/scenarios`.
