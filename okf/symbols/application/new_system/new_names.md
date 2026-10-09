---
type: Function
title: application.new_system.new_names
description: The actions and roles `transactions` name that `pack` does not declare, in order of first use.
resource: repo://src/eija_studio/application/new_system.py#new_names
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#new_names
  title: application/new_system.py
  hash_method: ast-v2
  sha256: f1adeec1324de5c3c2d00bf93cf00b35afafc4549f097bec422fea8141b8155a
notes_baseline: 2a85939c163c92edeefb073b396078bb6b4443b0b0325b592390c1774e9e4f5e
---

# application.new_system.new_names

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def new_names(pack: Pack, transactions: list[Transaction]) -> tuple[list[str], list[str]]` |
| Code | `repo://src/eija_studio/application/new_system.py#new_names` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The actions and roles `transactions` name that `pack` does not declare, in order of first use.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.transactions.AddTransition](/symbols/domain/transactions/AddTransition.md) - A transition performing a declared action; its guards and effects are the action's declared ones.
* [domain.transactions.SetRole](/symbols/domain/transactions/SetRole.md) - `class SetRole(Contract)` in `domain/transactions`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [application.new_system.declare](/symbols/application/new_system/declare.md) - `pack` with every action and role `transactions` name but it does not declare yet, declared exactly as a sketch declares them (ADR-0201): an action gets the ba…
<!-- okf:generated:end links -->
