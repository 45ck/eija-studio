---
type: Architecture Decision Record
title: 'ADR-0237: Time events on transitions'
description: 'Issue #93, item 2.'
resource: repo://docs/adr/0237-time-events.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0237-time-events.md
  title: 0237-time-events.md
  hash_method: lf-sha256-v1
  sha256: ce813a262947dbac6cd1fb824a0dcae9ba865fa4aabcc2bd2b12be5b27516296
notes_baseline: cc8358b2f5feea9c5caf89688488f9982c5c1dada6282bc2f9c55b61c1bfffc8
---

# ADR-0237: Time events on transitions

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | kernel / executable UML |
| Source | `repo://docs/adr/0237-time-events.md` |

## Decision outcome (verbatim)

> **The model.** A transition may carry `after`, `{"amount": n, "unit": "minutes" | "hours" | "days"}`, with `n` from 1 to 10,000. Diagrams write it as UML's `after(2 days)`. When there is no time event the field is left out of every dump, so the bytes and the semantic hash of every existing model stay the same. Every transition one action labels must carry the same time event (ADR-0232).
>
> **What "in the state" means.** Time is measured from when the record entered its current state. Every committed step enters its target state afresh, a step back into the same state included, as an external self-transition does in UML.
>
> **The runtime.** After the state check, a transition with a time event reads how long the record has been in its state through a new `UnitOfWork.elapsed` port. Before the time is up it refuses with `TIMER_NOT_DUE`, naming the transition and the state. A transition without a time event never calls the port.
>
> **The clocks.**
> * The Studio's preview store keeps no clock, so a time event is never due there, as value guards never hold there (ADR-0234).
> * Simulate's `MemorySession` has a simulated clock. Each step lets one twelfth of the model's longest time event pass, so a time event falls due a few steps after a record enters its state. A model without time events lets no time pass, so its seeded runs are unchanged. The report gains `time` only for a timed model.
> * The generated app stores `entered_at` on each record and reads the wall clock. Records from an older build have no entry time and are never due.
>
> **The checkers.**
> * **Law proof.** Time can always pass, so each step is tried after waiting the model's longest time event, when every time event is due. Waiting only adds steps, never removes them, so this covers every run the kernel allows. That argument holds because the only time construct is `after`; an upper bound such as `within` would break it.
> * **Generated app.** Ordinary oracle cases are for records that have waited the longest time event (`waited` in the oracle, present only for a timed model). The oracle gains `timer_cases`: for each timed transition, an actor who may take it tries it after half the time and after the whole time. The conformance template checks them, so it now runs ten tests, and the app's action options use the same check.
> * **SCXML.** A time event becomes a `cond` term over the event data, `has_elapsed and elapsed >= <seconds>`. The sender reads the time as the kernel's port does, as it already reads the actor and the record's values. The differential runs the timer cases, and a chart with the term removed disagrees with the kernel.
> * **Scenarios.** A scenario step may say how long to `wait` before it (`{"amount": 1, "unit": "days"}`), on a simulated clock that moves only then. The refund desk's `timer-escalates` scenario shows the escalation refused after one day and taken after two. Steps without a wait keep their bytes and digests.
> * **Formal encodings.** TLA+, SMT and BMC refuse a workflow with time events (`OutsideFormalScope`) instead of encoding it as if it had none.
>
> **The example.** The refund desk's `EscalateStale` now waits `after(2 days)` in `AwaitingApproval`.

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

* [ADR-0210: Actors that are not people: AI agents, timers and external systems in the model](/adrs/0210-actors-that-are-not-people.md) - Systems people design now have AI agents in them: a support bot that triages tickets and proposes refunds, a scheduled job that escalates what nobody handled,…
* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.
* [ADR-0234: Guards over record values](/adrs/0234-guards-over-record-values.md) - Issue #93, item 1.

## Referenced by

* [ADR-0242: Conformance that catches a divergent app by behaviour](/adrs/0242-conformance-that-catches-divergence.md) - The pitch for `eija build` (ADR-0150) is that the generated app's conformance tests prove the app matches its model.
<!-- okf:generated:end links -->
