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
  sha256: 917f2dcc7dc94115064327d5a8309729b09bfff506d482a95cbed2b1edb5c1f2
notes_baseline: fc74e6d3d2eaf7cdca6ba4a0866928cc7b7dcf217d94732435dbe4d525302cb5
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

* [application.memo.ensure_conforms](/symbols/application/memo/ensure_conforms.md) - `ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again, so the error is always the check's own.
* [application.memo.model_hash](/symbols/application/memo/model_hash.md) - `model.semantic_hash`, computed once per model object.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - Start a record.
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.

## Referenced by

* [application.appgen.signal_cases](/symbols/application/appgen/signal_cases.md) - Each signal the model receives, delivered with valid record values, and the kernel's answer (a record started in the initial state), then the first one under a…
<!-- okf:generated:end links -->
