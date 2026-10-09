---
type: Function
title: domain.scenarios.parse_scenarios
description: '`def parse_scenarios(document: Any, pack_id: str) -> Scenarios` in `domain/scenarios`.'
resource: repo://src/eija_studio/domain/scenarios.py#parse_scenarios
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/scenarios.py#parse_scenarios
  title: domain/scenarios.py
  hash_method: ast-v2
  sha256: 2fb5a0bbc4175afd479d1f566b73c061d8d583ca18a36575234723397792725e
notes_baseline: 608ffdc422e05ad2c5038ed7244184e6d2833608d500e1548019e2abee62f100
---

# domain.scenarios.parse_scenarios

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/scenarios`](/modules/domain/scenarios.md) |
| Signature | `def parse_scenarios(document: Any, pack_id: str) -> Scenarios` |
| Code | `repo://src/eija_studio/domain/scenarios.py#parse_scenarios` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.

## Referenced by

* [application.describe_system.update_tests](/symbols/application/describe_system/update_tests.md) - The tests brought up to date with `model`, for the person to keep or not (What's missing's "Update the tests", ADR-0216).
* [application.new_system.checked_documents](/symbols/application/new_system/checked_documents.md) - The documents, if the kernel's checks accept them; `PackError` with every problem otherwise.
* [application.sequence_draft.draft_scenarios](/symbols/application/sequence_draft/draft_scenarios.md) - Scenarios for a system with none: each step's expectation is what the kernel does on `model`.
* [domain.scenarios.load_scenarios](/symbols/domain/scenarios/load_scenarios.md) - The scenarios in `directory`, or None when it has no `scenarios.json`.
<!-- okf:generated:end links -->
