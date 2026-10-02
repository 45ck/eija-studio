---
type: Function
title: application.history.command_event
description: Append-only command provenance; decision and receipt payloads remain in their existing audit.
resource: repo://src/eija_studio/application/history.py#command_event
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/history.py#command_event
  title: application/history.py
  hash_method: ast-v2
  sha256: 43d1fd4dc30d9d9a0af49dbdfce731901a9b1d9f14195e09d4fa6ea616bd09ba
notes_baseline: a09b448eb17c60a3ee3ecd1c8aee9185b45470214aa2138a4a84c3a3636b14e6
---

# application.history.command_event

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/history`](/modules/application/history.md) |
| Signature | `def command_event(case: ChangeCase, model: Workflow, tx: Transaction, by: str, time: str, discarded_redo: Sequence[Transaction]=()) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/history.py#command_event` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Append-only command provenance; decision and receipt payloads remain in their existing audit.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.change_case.ChangeCase](/symbols/domain/change_case/ChangeCase.md) - Aggregate boundary: transitions are mediated by the application and CAS store.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.
<!-- okf:generated:end links -->
