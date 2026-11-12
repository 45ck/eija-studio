# ADR-0242: Messages between workflows

* Status: accepted
* Date: 2026-11-12
* Lane: kernel / executable UML

## Context and problem statement

Issue #93, item 5. A system is several workflows (ADR-0203). Until now they were linked only by the classes their class diagrams share, which is a design dependency the kernel never runs. The library shows the gap: a loan returned late should lead to a fine, but nothing in the loan workflow could say so. The fines workflow only had records that a person started by hand. A UML component diagram whose components send each other signals could not be run.

## Decision drivers

* The kernel decides each end, and it stays one interpreter.
* A sender is never refused because of the receiver. They are separate units of work, as two services are.
* Delivery is at most once per delivery id, so a retry cannot start a second record.
* Every existing model, digest, hash, oracle and recording keeps its exact bytes.
* The system check sees both ends. A signal that only one end declares is reported.
* Bounded: the slice includes no relay between built apps, no signal that moves an existing record, and no values mapped from the sender's record.

## Considered options

* **A signal is a typed effect, and a receiving workflow says which signals start a record (chosen).** The sender's step writes it to its outbox, exactly as it writes a notification. The receiver's kernel starts a record when it is delivered.
* **A synchronous call into the other workflow in the same unit of work.** It is simpler to test. But it couples two apps' storage and lets the receiver refuse the sender, which no real component boundary does.
* **A signal that moves an existing record of the receiver.** It needs a correlation between the two records, which item 4's links (ADR-0241) only give one level deep. Revisit with the multi-entity runtime (#65).

## Decision outcome

**The pack.** An effect may be of kind `signal`, named `Signal:Name`, with `recipient` naming another workflow (pack id) of the system. A transition requires it like any other effect. The policy and its law checks treat it as an effect, and only a signal may be named `Signal:`.

**The workflow.** `Workflow.receives` lists `{signal, sender}` pairs, each meaning that this signal from that workflow starts a record. The list is a set in the semantic hash, at most 16 pairs long, and left out of the dump when empty.

**The kernel.** The sender's step writes the signal to the outbox through `UnitOfWork.enqueue`, in its own unit of work. `runtime.receive(session, case, model, signal, sender, operation_id)` refuses a pair the model does not receive with `SIGNAL_NOT_ACCEPTED`. Otherwise it starts a record in the initial state and records the operation. A second delivery under the same id returns the first record, and a different request under that id is `OPERATION_CONFLICT`. Starting a record this way does not check the model's `initiators`, because a signal is the system starting it, not a person.

**The checkers.**
* **System landscape:** each workflow lists `sends` and `receives`. A signal also joins two workflows into one system. `signals` lists each pair that both ends declare. `SIGNAL_UNHEARD` flags a signal sent to a workflow that does not receive it from the sender, and `SIGNAL_NEVER_SENT` flags a received signal that the sender never sends. PlayIDE's System lens draws a `«signal»` arrow.
* **Runtime matrix and Simulate:** a signal is an outbox write, counted with notifications.
* **Generated app:** the receiving app has `POST /api/signals {signal, sender, operation_id, fields}`. Its data model checks the new record's values, as it checks a record a person creates. The oracle gains `signal_cases`: each received signal starts a record, and an unknown signal and an unknown sender are refused. The conformance template checks them, including that a redelivery starts nothing new (12 generated tests). The sending app's outbox holds the signal, and the existing effect test checks it.
* **SCXML:** a signal is in the transition's effect list, which the differential already compares.
* **UML files:** an export cannot say which workflow a signal goes to or which signals a workflow receives, and the export lists both as not carried. A new system read from a file keeps the signal with recipient `unaddressed`, so the landscape reports it until someone names the receiver.

**The example.** Returning a loan late (`ReturnLate`) sends `Signal:LateReturn` to `library-fines`, which starts a fine in `Issued`.

### Consequences

* Good: a component diagram's dependency can be a message the kernel runs, checked at both ends and drawn on the System lens.
* Good: delivery is idempotent by construction, so a relay can retry safely.
* Bad: nothing carries a signal from one built app to another yet. A relay that reads one outbox and posts to the other's `/api/signals` is the next step.
* Bad: the signal does not say how the sender's record maps to the new record's values. The deliverer supplies them, and the receiver's data model checks them.
