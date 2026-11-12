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
  sha256: 2a46bd3e84bc2c6905cfcbc47a974a6555a0813a64616bd33b63d8861a071c76
notes_baseline: 833028d6524968fe587b7691d747b507756abe44c3e76eb54e7f8e6a943a253e
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

> **The workflow.** `Workflow.objects` lists at most 8 linked objects, each `{link, entity, states, initial, moves: [{event, from_state, to_state}]}` with at most 8 states and 32 moves; a lifecycle's moves are closed over its states and deterministic. A transition may carry `then`, at most two `{link, event}` steps on different links, and every step names a declared lifecycle that has that event. Every transition one action labels carries the same `then` (ADR-0232). `link` must be a built to-one reference field of the record whose class is `entity` (ADR-0235), checked when the app is built (`LINK_NOT_BUILT`). Both keys are omitted from the dump when empty, so every existing model keeps its bytes and its semantic hash.
>
> **The kernel.** After all of today's checks pass, `runtime.execute` reads each linked object's state through `UnitOfWork.object_state(instance_id, link)`. If the object is unknown, its state is unknown, or the lifecycle has no move for the event from that state, it refuses with `LINKED_OBJECT_REFUSED`, naming the transition and the link. Otherwise it writes each new state with `UnitOfWork.move_object` in the same unit of work as the record's step, and the committed result lists `moved`. A step without `then` never calls either port. The preview SQLite store holds no objects, so it refuses such a step rather than guessing.
>
> **The checkers.**
> * **Law proof:** a step is tried with its objects in every combination of their states (`linked.combinations`, at most 64), so a refusal shows up wherever it can happen.
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
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.
* [ADR-0235: Built associations as checked reference fields](/adrs/0235-built-associations.md) - Issue #145, step 2.
<!-- okf:generated:end links -->
