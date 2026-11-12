# ADR-0241: Actions on linked objects

* Status: accepted
* Date: 2026-11-12
* Lane: kernel / executable UML

## Context and problem statement

Issue #93, item 4. In xtUML each class has its own state machine, and a step on one object can move another. Until now a pack had one workflow: the record's. ADR-0235 lets a record link to a stored object of another class (a built to-one association, such as a deploy request's `target` service), but that object had no state, so "opening a deploy window locks the service" could not be said, and "a service that is already rolling out cannot get a second window" could not be enforced. Item 5 (messages between workflows) needs the same thing at a larger scale, so this is the base for it.

## Decision drivers

* The kernel decides, in one unit of work: the record's step and the linked object's step commit together or not at all.
* One interpreter. A linked object's lifecycle is checked by the same kernel, not by a second engine.
* Fail closed. An object whose state is unknown, or that has no move for the event, refuses the record's step.
* Every existing model, digest, hash, oracle and recording keeps its exact bytes.
* Every checker that runs the model sees the same rule: the law proof, Simulate, scenarios, the generated app's oracle and the SCXML differential.
* Bounded: no object-to-object chains, no to-many fan-out and no objects acting on their own.

## Considered options

* **A small lifecycle per link, declared in the workflow and moved by a record step (chosen).**
* **A full workflow per class, with its own actors and laws.** It is the xtUML ideal, but it needs one policy and law proof per class and a runtime of many machines (#65). Revisit after this.
* **Effects that only notify.** Already possible. A notification cannot be refused, so the rule cannot be enforced.

## Decision outcome

**The workflow.** `Workflow.objects` lists at most 8 linked objects, each `{link, entity, states, initial, moves: [{event, from_state, to_state}]}` with at most 8 states and 32 moves; a lifecycle's moves are closed over its states and deterministic. A transition may carry `then`, at most two `{link, event}` steps on different links, and every step names a declared lifecycle that has that event. Every transition one action labels carries the same `then` (ADR-0232). `link` must be a built to-one reference field of the record whose class is `entity` (ADR-0235), checked when the app is built (`LINK_NOT_BUILT`). Both keys are omitted from the dump when empty, so every existing model keeps its bytes and its semantic hash.

**The kernel.** After all of today's checks pass, `runtime.execute` reads each linked object's state through `UnitOfWork.object_state(instance_id, link)`. If the object is unknown, its state is unknown, or the lifecycle has no move for the event from that state, it refuses with `LINKED_OBJECT_REFUSED`, naming the transition and the link. Otherwise it writes each new state with `UnitOfWork.move_object` in the same unit of work as the record's step, and the committed result lists `moved`. A step without `then` never calls either port. The preview SQLite store holds no objects, so it refuses such a step rather than guessing.

**The checkers.**
* **Law proof:** a step is tried with its objects in every combination of their states (`linked.combinations`, at most 64), so a refusal shows up wherever it can happen.
* **Simulate:** `MemorySession` keeps object states. Each record links to one of a small pool of shared objects, starting in their initial state, so two records can contend for one object.
* **Scenarios:** a scenario's record starts with its objects where a run of that record alone leaves them (`linked.along`).
* **Generated app:** the `objects` table gains a `state` column (migrated in place). The oracle gains `linked_cases`: every transition with `then` tried with its objects in each combination of states. The conformance template checks them, and checks the objects' states after every ordinary commit (11 generated tests).
* **SCXML:** each link becomes event data `object_<link>`. A transition with `then` becomes one SCXML transition per admissible combination, with a `cond` term per object and an `<assign>` that appends `link:state` to `moved`. The differential runs the linked cases and compares `moved`.
* **Formal encodings:** TLA+, SMT and BMC refuse a model with `objects` (`OutsideFormalScope`). UML interchange files do not carry lifecycles and say so.
* **Diagrams:** the state diagram writes `/ target.lock` after the action, in PlayIDE and in the exported diagrams.

**The example.** The `ai-ops` pack links each deploy request to its `target` service. Opening a window moves the service from `Idle` to `RollingOut`, and confirming or rolling back moves it back. Opening a second window on a service that is already rolling out is refused.

### Consequences

* Good: a rule about another object is enforced by the kernel, drawn on the diagram and checked by every checker, including an independent SCXML engine.
* Good: messages between workflows (#93 item 5) can reuse the ports and the linked-case oracle.
* Bad: to-one links only, one level deep. A move cannot trigger another move.
* Bad: objects have no actors or laws of their own. That needs the multi-entity runtime (#65).
