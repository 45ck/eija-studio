---
type: Function
title: application.sequences.check_sequences
description: Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
resource: repo://src/eija_studio/application/sequences.py#check_sequences
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequences.py#check_sequences
  title: application/sequences.py
  hash_method: ast-v2
  sha256: 98dbb3b62c8978120b4667e5c7b9b2a1c24ad5f8ff6a9056eef0b20bf7979738
notes_baseline: ce951a576a1ebd1d071787cf01cfbd3a414954a43f1b84482ebdb5ee3ad71962
---

# application.sequences.check_sequences

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequences`](/modules/application/sequences.md) |
| Signature | `def check_sequences(pack: Pack, model: Workflow, scenarios: Scenarios, base: Workflow \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/sequences.py#check_sequences` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also
on it, for the change.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.ghost_diff.ghost_diff](/symbols/application/ghost_diff/ghost_diff.md) - The union of two state machines, each element with its status, and the ordered list of changes.
* [application.sequences.FORMAT](/symbols/application/sequences/FORMAT.md) - Constant `FORMAT` in `application/sequences`.
* [application.sequences.LIMITS](/symbols/application/sequences/LIMITS.md) - Constant `LIMITS` in `application/sequences`.
* [application.sequences.record_name](/symbols/application/sequences/record_name.md) - The record lifeline's name and its class: `loan : Loan` when the pack has a data model.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.scenarios.Scenarios](/symbols/domain/scenarios/Scenarios.md) - `class Scenarios(Contract)` in `domain/scenarios`.
<!-- okf:generated:end links -->
