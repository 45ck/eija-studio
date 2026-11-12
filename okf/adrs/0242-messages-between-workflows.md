---
type: Architecture Decision Record
title: 'ADR-0242: Messages between workflows'
description: 'Issue #93, item 5.'
resource: repo://docs/adr/0242-messages-between-workflows.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0242-messages-between-workflows.md
  title: 0242-messages-between-workflows.md
  hash_method: lf-sha256-v1
  sha256: b6c080cee7a082635fbf03787d7deddf3297d3454c994933fe8524fa9f728438
notes_baseline: 917f6c2dd2b7c9f6ae56c805b587aebe573df8ac8caa09a08037e412f5b6caaa
---

# ADR-0242: Messages between workflows

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | kernel / executable UML |
| Source | `repo://docs/adr/0242-messages-between-workflows.md` |

## Decision outcome (verbatim)

> **The pack.** An effect may be of kind `signal`, named `Signal:Name`, with `recipient` naming another workflow (pack id) of the system. A transition requires it like any other effect. The policy and its law checks treat it as an effect, and only a signal may be named `Signal:`.
>
> **The workflow.** `Workflow.receives` lists `{signal, sender}` pairs, each meaning that this signal from that workflow starts a record. The list is a set in the semantic hash, at most 16 pairs long, and left out of the dump when empty.
>
> **The kernel.** The sender's step writes the signal to the outbox through `UnitOfWork.enqueue`, in its own unit of work. `runtime.receive(session, case, model, signal, sender, operation_id)` refuses a pair the model does not receive with `SIGNAL_NOT_ACCEPTED`. Otherwise it starts a record in the initial state and records the operation. The delivery binds the signal, the sender and the new record's values. A second delivery under the same id with the same binding returns the first record, and anything else under that id is `OPERATION_CONFLICT`. Starting a record this way does not check the model's `initiators`, because a signal is the system starting it, not a person.
>
> **The checkers.**
> * **System landscape:** each workflow lists `sends` and `receives`. A signal also joins two workflows into one system. `signals` lists each pair that both ends declare. `SIGNAL_UNHEARD` flags a signal sent to a workflow that does not receive it from the sender, and `SIGNAL_NEVER_SENT` flags a received signal that the sender never sends. PlayIDE's System lens draws a `«signal»` arrow.
> * **Runtime matrix and Simulate:** a signal is an outbox write, counted with notifications.
> * **Generated app:** the receiving app has `POST /api/signals {signal, sender, operation_id, fields}`. The operation id is required and is never defaulted or cut short, because it is the delivery's identity. Its data model checks the new record's values, as it checks a record a person creates. The oracle gains `signal_cases`: each received signal starts a record, and an unknown signal and an unknown sender are refused. The conformance template checks them, including that a redelivery starts nothing new (12 generated tests). The sending app's outbox holds the signal, and the existing effect test checks it.
> * **SCXML:** a signal is in the transition's effect list, which the differential already compares.
> * **UML files:** an export cannot say which workflow a signal goes to or which signals a workflow receives, and the export lists both as not carried. A new system read from a file keeps the signal with recipient `unaddressed`, so the landscape reports it until someone names the receiver.
>
> **The example.** Returning a loan late (`ReturnLate`) sends `Signal:LateReturn` to `library-fines`, which starts a fine in `Issued`.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0203: A system landscape of the workflows that share classes](/adrs/0203-system-landscape-of-workflows-that-share-classes.md) - PlayIDE edits one workflow at a time: one state machine moving one record class, with its class diagram, use cases, screens and laws.
* [ADR-0241: Actions on linked objects](/adrs/0241-actions-on-linked-objects.md) - Issue #93, item 4.
<!-- okf:generated:end links -->
