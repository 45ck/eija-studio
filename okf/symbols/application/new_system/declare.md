---
type: Function
title: application.new_system.declare
description: '`pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declares them (ADR-0201): an action gets the base guards and one audit entry, a role one active, assigned f…'
resource: repo://src/eija_studio/application/new_system.py#declare
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#declare
  title: application/new_system.py
  hash_method: ast-v2
  sha256: 9ac9af576adfaac701377ea6187304794a723d1c2bd88515f770160a94c05007
notes_baseline: 93d68f440d9ebf27c65ee49b96174ca57c067b9e497d0b4a69be166dede4da32
---

# application.new_system.declare

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def declare(pack: Pack, transactions: list[Transaction]) -> Pack` |
| Code | `repo://src/eija_studio/application/new_system.py#declare` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
`pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch
declares them (ADR-0201): an action gets the base guards and one audit entry, a role one active, assigned fixture
actor. The result is a draft held in memory, checked by the kernel's pack check; nothing is written, and the laws,
meanings and tests are the pack's own. `pack` itself when nothing is new.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.new_system.new_names](/symbols/application/new_system/new_names.md) - The actions and roles `transactions` name that `pack` does not declare, in order of first use.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.
* [domain.pack.derive](/symbols/domain/pack/derive.md) - A draft of `pack` held in memory (`document`, checked as `parse_pack` checks any pack), whose files beside `pack.json` (`data.json`, `screens.json`, `scenarios…
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.plan.preview_plan](/symbols/application/plan/preview_plan.md) - What the accepted steps would make of `model`.
<!-- okf:generated:end links -->
