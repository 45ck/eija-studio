---
type: Function
title: application.runtime.receive
description: 'Start a record because another workflow of the system sent `signal` (issue #93 item 5, ADR-0242).'
resource: repo://src/eija_studio/application/runtime.py#receive
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/runtime.py#receive
  title: application/runtime.py
  hash_method: ast-v2
  sha256: d7cbb86e6fdcf33a5ae1b640dde1a792097fbc85b16204844b8f1422c8318d06
notes_baseline: 1df5ff164ee3d6f61e8a51b7255e7c3531115912e4c506284c0a53cde9fc0204
---

# application.runtime.receive

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/runtime`](/modules/application/runtime.md) |
| Signature | `def receive(session: UnitOfWork, case_id: str, model: Workflow, signal: str, sender: str, operation_id: str, *, pack: Pack \| None=None, values: dict[str, Any] \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/runtime.py#receive` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Start a record because another workflow of the system sent `signal` (issue #93 item 5, ADR-0242).

The sender's step put the signal in its outbox in its own unit of work; delivering it here is a separate unit of
work, so the sender is never refused by the receiver. A signal the model does not say it receives from `sender` is
refused with SIGNAL_NOT_ACCEPTED. The operation id makes a redelivery start nothing new: the same signal, sender and
record `values` return the original record, and anything else under that id is OPERATION_CONFLICT.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.memo.model_hash](/symbols/application/memo/model_hash.md) - `model.semantic_hash`, computed once per model object.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - Start a record.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
<!-- okf:generated:end links -->
