---
type: Function
title: domain.scenarios.load_scenarios
description: The scenarios in `directory`, or None when it has no `scenarios.json`.
resource: repo://src/eija_studio/domain/scenarios.py#load_scenarios
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py#load_scenarios
  title: domain/scenarios.py
  hash_method: ast-v2
  sha256: 914e637edfa3f8be180dacd897ec9c845e16e8618be1f37b46a4b0bb5b3e3824
notes_baseline: 7d166aa61d29ff1e2cff129bcc2a63f7f60626f2717945314787f3e42285c877
---

# domain.scenarios.load_scenarios

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/scenarios`](/modules/domain/scenarios.md) |
| Signature | `def load_scenarios(directory: str \| Path, pack_id: str) -> Scenarios \| None` |
| Code | `repo://src/eija_studio/domain/scenarios.py#load_scenarios` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The scenarios in `directory`, or None when it has no `scenarios.json`.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.scenarios.SCENARIOS_FILE](/symbols/domain/scenarios/SCENARIOS_FILE.md) - Constant `SCENARIOS_FILE` in `domain/scenarios`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
* [domain.scenarios.parse_scenarios](/symbols/domain/scenarios/parse_scenarios.md) - `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.

## Referenced by

* [domain.scenarios.scenarios_for](/symbols/domain/scenarios/scenarios_for.md) - The scenarios beside this pack's `pack.json`, or none.
<!-- okf:generated:end links -->
