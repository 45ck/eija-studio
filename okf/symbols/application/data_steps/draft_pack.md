---
type: Function
title: application.data_steps.draft_pack
description: '`pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and the data model holds their data-model steps (ADR-0202).'
resource: repo://src/eija_studio/application/data_steps.py#draft_pack
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/data_steps.py#draft_pack
  title: application/data_steps.py
  hash_method: ast-v2
  sha256: 167d24dd9b9ca6d1bf3abdab686962d7cacd6d6a7fa83f1f959b9b07c514769c
notes_baseline: 2eee3e6729838aaa63ad9725bc72b949c2019de9ae90924ef379b87d0815faec
---

# application.data_steps.draft_pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/data_steps`](/modules/application/data_steps.md) |
| Signature | `def draft_pack(pack: Pack, steps: Sequence[Step], grows: bool) -> Pack` |
| Code | `repo://src/eija_studio/application/data_steps.py#draft_pack` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions
and roles they name are declared (ADR-0201) and the data model holds their data-model steps (ADR-0202). A shipped
pack is itself, and a data-model step on it is refused.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.data_steps.FIXED](/symbols/application/data_steps/FIXED.md) - Constant `FIXED` in `application/data_steps`.
* [application.data_steps.Step](/symbols/application/data_steps/Step.md) - Type alias `Step` in `application/data_steps`.
* [application.data_steps.apply_data](/symbols/application/data_steps/apply_data.md) - `data` with the data-model steps applied in turn, checked by the data model's own contract; `data` when none.
* [application.data_steps.split](/symbols/application/data_steps/split.md) - The kernel transactions and the data-model steps, each in plan order.
* [application.new_system.declare](/symbols/application/new_system/declare.md) - `pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declares them (ADR-0201): an action gets the ba…
* [domain.data.DATA_FILE](/symbols/domain/data/DATA_FILE.md) - Constant `DATA_FILE` in `domain/data`.
* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.hold](/symbols/domain/pack/hold.md) - A draft of `pack` that holds `content` in memory as its file `name` beside `pack.json` (such as a draft data model for `data.json`, ADR-0202).

## Referenced by

* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
<!-- okf:generated:end links -->
