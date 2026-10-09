---
type: Class
title: domain.scenarios.Scenarios
description: '`class Scenarios(Contract)` in `domain/scenarios`.'
resource: repo://src/eija_studio/domain/scenarios.py#Scenarios
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py#Scenarios
  title: domain/scenarios.py
  hash_method: ast-sig-v1
  sha256: 55a9519070b7717b3396473911474458feb9438823427fe53ce53d83770af629
notes_baseline: 4efe32b8304c67ffaafcffe01126aeaa34cd3490224d554b51eacda3d9e6d45f
---

# domain.scenarios.Scenarios

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/scenarios`](/modules/domain/scenarios.md) |
| Signature | `class Scenarios(Contract)` |
| Code | `repo://src/eija_studio/domain/scenarios.py#Scenarios` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `schema_version` | `Literal['eija.scenarios.v1']` | `'eija.scenarios.v1'` |
| `id` | `str` | `Field(pattern='^[a-z][a-z0-9-]{0,39}$')` |
| `scenarios` | `tuple[Scenario, ...]` | `Field(default=(), max_length=200)` |

## Methods

* [`digest`](/symbols/domain/scenarios/Scenarios.digest.md) - `def digest(self) -> str`
* [`unique`](/symbols/domain/scenarios/Scenarios.unique.md) - `def unique(self) -> Scenarios`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.scenarios.Scenario](/symbols/domain/scenarios/Scenario.md) - `class Scenario(Contract)` in `domain/scenarios`.

## Referenced by

* [application.describe_system.update_tests](/symbols/application/describe_system/update_tests.md) - The tests brought up to date with `model`, for the person to keep or not (What's missing's "Update the tests", ADR-0216).
* [application.readiness.missing](/symbols/application/readiness/missing.md) - Every view's row: what it is missing or what is wrong with it, or nothing when it is ready.
* [application.scenario_run.run_scenarios](/symbols/application/scenario_run/run_scenarios.md) - Every scenario run on `model`; a model the policy refuses runs none of them.
* [application.sequence_draft.draft_scenarios](/symbols/application/sequence_draft/draft_scenarios.md) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
* [application.sequence_draft.scenarios_or_draft](/symbols/application/sequence_draft/scenarios_or_draft.md) - The pack's scenarios ("pack"), or a draft from the model in force when it has none ("drafted").
* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
* [domain.scenarios.Scenarios.digest](/symbols/domain/scenarios/Scenarios.digest.md) - `def digest(self) -> str` in `domain/scenarios`.
* [domain.scenarios.Scenarios.unique](/symbols/domain/scenarios/Scenarios.unique.md) - `def unique(self) -> Scenarios` in `domain/scenarios`.
* [domain.scenarios.load_scenarios](/symbols/domain/scenarios/load_scenarios.md) - The scenarios in `directory`, or None when it has no `scenarios.json`.
* [domain.scenarios.parse_scenarios](/symbols/domain/scenarios/parse_scenarios.md) - `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.
* [domain.scenarios.scenarios_for](/symbols/domain/scenarios/scenarios_for.md) - The scenarios beside this pack's `pack.json`, or none.
<!-- okf:generated:end links -->
