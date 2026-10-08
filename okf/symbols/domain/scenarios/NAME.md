---
type: Constant
title: domain.scenarios.NAME
description: Constant `NAME` in `domain/scenarios`.
resource: repo://src/eija_studio/domain/scenarios.py#NAME
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py#NAME
  title: domain/scenarios.py
  hash_method: ast-v2
  sha256: a593985568c6772154869b0fab5adbb1913063abe74ddf92f30ede3a60dfb5cf
notes_baseline: ace7fa1b007cd0a64ddb95e43200a8be2caee9a610ff494e6a07deacb57c8237
---

# domain.scenarios.NAME

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/scenarios`](/modules/domain/scenarios.md) |
| Signature | `NAME = '^[A-Za-z][A-Za-z0-9_:-]{0,59}$'` |
| Code | `repo://src/eija_studio/domain/scenarios.py#NAME` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.scenarios.Scenario](/symbols/domain/scenarios/Scenario.md) - `class Scenario(Contract)` in `domain/scenarios`.
* [domain.scenarios.ScenarioStep](/symbols/domain/scenarios/ScenarioStep.md) - `class ScenarioStep(Contract)` in `domain/scenarios`.
* [domain.scenarios.Then](/symbols/domain/scenarios/Then.md) - What a step must do: move the record to `state`, or be refused with `refused` (a kernel refusal code).
<!-- okf:generated:end links -->
