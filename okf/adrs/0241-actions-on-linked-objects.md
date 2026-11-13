---
type: Architecture Decision Record
title: 'ADR-0241: Actions on linked objects'
description: 'Issue #93, item 4.'
resource: repo://docs/adr/0241-actions-on-linked-objects.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0241-actions-on-linked-objects.md
  title: 0241-actions-on-linked-objects.md
  hash_method: lf-sha256-v1
  sha256: 2b845fbba1843aa801e6b50154885f9379c526c0103c3912d9bf2314df5cc628
notes_baseline: 50efc28bacf32e026797f3046d162cd8be5bc60d6c696c7ce9d6eb4996965c15
---

# ADR-0241: Actions on linked objects

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | kernel / executable UML |
| Source | `repo://docs/adr/0241-actions-on-linked-objects.md` |

## Decision outcome (verbatim)

> **The workflow.** `Workflow.objects` lists at most 8 linked objects, each `{link, entity, states, initial, moves: [{event, from_state, to_state}]}` with at most 8 states and 32 moves; a lifecycle's moves are closed over its states and deterministic. A transition may carry `then`, at most two `{link, event}` steps on different links, and every step names a declared lifecycle that has that event. One transition moves at most one object of each class, because two links could name the same object. Every transition one action labels carries the same `then` (ADR-0232). `link` must be a built to-one reference field of the record whose class is `entity` (ADR-0235), checked when the app is built (`LINK_NOT_BUILT`). Both keys are omitted from the dump when empty, so every existing model keeps its bytes and its semantic hash.
>
> **The kernel.** After all of today's checks pass, `runtime.execute` reads each linked object's state through `UnitOfWork.object_state(instance_id, link)`. If the object is unknown, its state is unknown, or the lifecycle has no move for the event from that state, it refuses with `LINKED_OBJECT_REFUSED`, naming the transition and the link. Otherwise it writes each new state with `UnitOfWork.move_object` in the same unit of work as the record's step, and the committed result lists `moved`. A step without `then` never calls either port. The preview SQLite store holds no objects, so it refuses such a step rather than guessing.
>
> **The checkers.**
> * **Law proof:** a configuration also holds each linked object's state, starting in its lifecycle's initial state, and each step carries its moves forward. Other records may share the object, so between steps an object may take any move of its lifecycle (`linked.drift`). `can_reach_end` is judged on these configurations, so a record whose object can never come back to the state it needs is stuck.
> * **Simulate:** `MemorySession` keeps object states. Each record links to one of a small pool of shared objects, starting in their initial state, so two records can contend for one object.
> * **Scenarios:** a scenario's record starts with its objects where a run of that record alone leaves them (`linked.along`).
> * **Generated app:** the `objects` table gains a `state` column (migrated in place). The oracle gains `linked_cases`: every transition with `then` tried with its objects in each combination of states. The conformance template checks them, and checks the objects' states after every ordinary commit (11 generated tests).
> * **SCXML:** each link becomes event data `object_<link>`. A transition with `then` becomes one SCXML transition per admissible combination, with a `cond` term per object and an `<assign>` that appends `link:state` to `moved`. The differential runs the linked cases and compares `moved`.
> * **Formal encodings:** TLA+, SMT and BMC refuse a model with `objects` (`OutsideFormalScope`). UML interchange files do not carry lifecycles and say so.
> * **Diagrams:** the state diagram writes `/ target.lock` after the action, in PlayIDE and in the exported diagrams.
>
> **The example.** The `ai-ops` pack links each deploy request to its `target` service. Opening a window moves the service from `Idle` to `RollingOut`, and confirming or rolling back moves it back. Opening a second window on a service that is already rolling out is refused.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* Amendment, 13 November 2026: links to one class share one lifecycle

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://docs/quality/inspection-2026-11-13-merged-prs.md`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.
* [ADR-0235: Built associations as checked reference fields](/adrs/0235-built-associations.md) - Issue #145, step 2.

## Referenced by

* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.
* [ADR-0242: Messages between workflows](/adrs/0242-messages-between-workflows.md) - Issue #93, item 5.
* [ADR-0243: Conformance that catches a divergent app by behaviour](/adrs/0243-conformance-that-catches-divergence.md) - The pitch for `eija build` (ADR-0150) is that the generated app's conformance tests prove the app matches its model.
<!-- okf:generated:end links -->
