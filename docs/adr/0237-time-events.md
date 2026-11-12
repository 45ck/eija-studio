# ADR-0237: Time events on transitions

* Status: accepted
* Date: 2026-11-12
* Lane: kernel / executable UML

## Context and problem statement

Issue #93, item 2. UML state machines write time events on transitions: `after(14 days)`. Real workflows need them for overdue loans, expiring approvals and escalation when nobody acts. Until now the refund desk's `EscalateStale` was taken by an SLA timer role whenever that role chose to, so the "stale" in its name was only a word. ADR-0210 added «timer» actors and said elapsed-time triggers were not modelled yet.

## Decision drivers

* The kernel decides. The time check runs at commit time in `runtime.execute`, in the same unit of work, like every other guard.
* The kernel has no clock. Time comes in through a port, so the kernel stays deterministic and every checker can supply its own time.
* Fail closed. A record whose entry time is unknown is never due.
* Every existing model, digest, hash, oracle and recording keeps its exact bytes.
* Every checker that runs the model sees the same rule: the law proof, Simulate, the generated app's conformance oracle and the SCXML differential.

## Considered options

* A time event as a guard on a transition that an actor still takes: `after: {amount, unit}` makes the step allowed once the record has been in its source state that long (chosen).
* A transition that fires by itself when the time comes (a delayed SCXML `<send>`): it needs a scheduler inside the kernel and a step with no actor, which would bypass the authority checks every step passes today. A «timer» role run by a scheduled job gives the same behaviour with the existing checks.
* Absolute deadlines (`at(2026-12-01)`) and upper bounds (`within(3 days)`): useful, but the second makes waiting remove steps, which changes the law proof's argument below. Revisit when a pack needs them.

## Decision outcome

**The model.** A transition may carry `after`, `{"amount": n, "unit": "minutes" | "hours" | "days"}`, with `n` from 1 to 10,000. Diagrams write it as UML's `after(2 days)`. When there is no time event the field is left out of every dump, so the bytes and the semantic hash of every existing model stay the same. Every transition one action labels must carry the same time event (ADR-0232).

**What "in the state" means.** Time is measured from when the record entered its current state. Every committed step enters its target state afresh, a step back into the same state included, as an external self-transition does in UML.

**The runtime.** After the state check, a transition with a time event reads how long the record has been in its state through a new `UnitOfWork.elapsed` port. Before the time is up it refuses with `TIMER_NOT_DUE`, naming the transition and the state. A transition without a time event never calls the port.

**The clocks.**
* The Studio's preview store keeps no clock, so a time event is never due there, as value guards never hold there (ADR-0234).
* Simulate's `MemorySession` has a simulated clock. Each step lets one twelfth of the model's longest time event pass, so a time event falls due a few steps after a record enters its state. A model without time events lets no time pass, so its seeded runs are unchanged. The report gains `time` only for a timed model.
* The generated app stores `entered_at` on each record and reads the wall clock. Records from an older build have no entry time and are never due.

**The checkers.**
* **Law proof.** Time can always pass, so each step is tried after waiting the model's longest time event, when every time event is due. Waiting only adds steps, never removes them, so this covers every run the kernel allows. That argument holds because the only time construct is `after`; an upper bound such as `within` would break it.
* **Generated app.** Ordinary oracle cases are for records that have waited the longest time event (`waited` in the oracle, present only for a timed model). The oracle gains `timer_cases`: for each timed transition, an actor who may take it tries it after half the time and after the whole time. The conformance template checks them, so it now runs ten tests, and the app's action options use the same check.
* **SCXML.** A time event becomes a `cond` term over the event data, `has_elapsed and elapsed >= <seconds>`. The sender reads the time as the kernel's port does, as it already reads the actor and the record's values. The differential runs the timer cases, and a chart with the term removed disagrees with the kernel.
* **Scenarios.** A scenario step may say how long to `wait` before it (`{"amount": 1, "unit": "days"}`), on a simulated clock that moves only then. The refund desk's `timer-escalates` scenario shows the escalation refused after one day and taken after two. Steps without a wait keep their bytes and digests.
* **Formal encodings.** TLA+, SMT and BMC refuse a workflow with time events (`OutsideFormalScope`) instead of encoding it as if it had none.

**The example.** The refund desk's `EscalateStale` now waits `after(2 days)` in `AwaitingApproval`.

### Consequences

* Good: "escalate a refund nobody has approved for two days" is a rule the kernel enforces, and a reviewer reads it on the state diagram.
* Good: nothing changes for a model without time events.
* Bad: a time event makes a step allowed; it does not take it. Something must run the «timer» role's job. The built app does not schedule one.
* Bad: only "at least this long in the state". No deadlines, no calendar time and no business days.
* Bad: the TLA+, SMT and BMC encodings do not model time. The law proof, the oracle and the SCXML differential carry the evidence for timed models.
* Revisit when: a pack needs a deadline or an upper bound, the built app should run its timer jobs itself, or a formal encoding should cover time.
