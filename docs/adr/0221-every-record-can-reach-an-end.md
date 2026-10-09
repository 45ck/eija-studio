# ADR-0221: A law that every record can still reach an end

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE (owner ask, 9 October 2026: many tasks across sectors to refine the demo; issue #151, law kinds the sector packs could not state)

## Context and problem statement

Writing the five sector packs (docs/sector-packs.md) turned up laws a real team would want and the law DSL could not say. One of them matters in every sector: no record may get stuck. A permit application that can reach a state from which nobody can ever decide it, or a refund that goes round a loop with no way out, is a defect a reviewer looks for first, and it is easy to introduce: park something "on hold" and forget the step that takes it off hold, or remove the only decision out of a review loop.

The existing laws are safety laws: "never this". `state_final` says nothing leaves a state; nothing said that some end can always still be reached. UML state machines mark final states but do not require that they stay reachable.

## Decision drivers

* State it in the vocabulary engineers already use: named end states, judged over the state machine.
* The kernel decides. The proof must judge what the kernel actually commits, not a re-encoding of it.
* Every new law kind gets executable semantics, a missing-resolver rejection, a negative oracle and an evidence policy (AGENTS.md).
* No change to the trusted kernel (`domain/policy.py`, `application/runtime.py`) or to any existing pack's identity.

## What existing tools do

| Tool | How "can always finish" is stated | What PlayIDE takes |
|---|---|---|
| Workflow nets (van der Aalst soundness; WoPeD, ProM) | "Option to complete": from every reachable marking the final marking is reachable | The property itself, over one record's states |
| CTL model checkers (NuSMV, LGPL) | `AG EF end`: on all paths, globally, there exists a path to an end | The same property; NuSMV itself is not needed for a finite graph of a few states |
| TLA+ / SPIN | Liveness (`<>`, leads-to) and non-progress cycles under fairness | Not adopted: a liveness law under fairness says a record *will* finish; this law says it still *can* |
| bpmnlint (MIT) | `end-event-required`, `no-disconnected` lint rules on a diagram | A structural check, made a law the policy and the proof judge |
| Stately / XState (MIT) | Final states only; no check that they stay reachable | Nothing to adopt |

The property is a reachability question on a graph of at most a few dozen states, which `domain/laws.reachable` already answers. No dependency is added.

## Considered options

* **A law kind `can_reach_end` (the end states) judged on the transition table by the policy and on the kernel's committed steps by the law proof** (chosen).
* Treat every state with no way out as an end. Rejected: that is exactly the defect; a forgotten state looks the same as a deliberate end unless the ends are named.
* Encode it for the SMT generator. Deferred: a reachability law needs an inductive encoding, like `path_requires`; it is listed NOT_RUN with the reason.
* Bounded repetition ("at most three delivery attempts") and conditional paths ("customs only for international parcels"). Not here: the first needs a counter on the record and the second a value guard, both kernel operators waiting on the owner's review (issues #93, #80). Issue #151 keeps them open.

## Decision outcome

* **`can_reach_end`** (`states`: the ends) in `domain/laws.py`. From every state a record can get to from the initial state, some end is still reachable. A state no record can reach strands nobody, so it does not count: a new state can be drawn before its steps.
* **Missing resolver.** Every end must be a declared state (one in the model or one a meaning adds), or the pack is refused when it loads (`laws[...]: state ... is not declared`).
* **Policy.** `evaluate_table` reports one violation naming the law and every stuck state (`state:<id>` refs), so an edit or a chat plan that strands a state is refused and the refusal points at the states.
* **Law proof.** Method `reach`: the breadth-first search over the kernel's configurations now records every step the kernel committed, and the law is judged on those steps. BROKEN carries the stuck states and the shortest run to the first one. A single run is never judged (`evaluate_run` skips it): the law is about the runs a record could still take.
* **Evidence policy.** HOLDS from the proof is evidence about the model and the kernel's guards over the bounded actor classes; it says nothing about whether anyone will in fact finish a record.
* **Example.** `packs/building-permit` law `no-application-stuck` (ends Completed, PermitRefused, Withdrawn, Lapsed). Its supported change, lapsing an issued permit, adds `Lapsed`, an end the law names, and is allowed. Its new unsupported meaning, putting an application on hold with no way back, is refused with `APPLICATION_STUCK` and `state:OnHold`.
* **Negative oracle.** `tests/test_reach_end_law.py`: a kernel that never lets the permit manager act leaves review and information requests looping, and the proof must report `InReview`, `InfoRequested` and `Registered` stuck with the run `AcceptLodgement, StartReview`; removing both decisions from the table must be refused naming the same states.

### Consequences

* Good: "nothing gets stuck" is a checked law, refused on every edit and proved over every run the kernel allows.
* Good: no kernel or trusted file changes; existing packs keep their digests.
* Bad: on a pack with this law, drawing a step into a new state before the step out of it is refused. Draw the way out first, or add the new state to the law's ends.
* Bad: it says a record *can* finish, not that it *will*: a person who never acts still leaves it open. Deadlines are timers (issue #93).
* Revisit when: counters or value guards land in the kernel (bounded repetition, conditional paths), or the SMT generator gains reachability encodings.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| NuSMV (LGPL) | A model checker for a property that is one graph search on a few states; another runtime and file format | Export to SMV if models outgrow the search |
| WoPeD / ProM soundness checks | Petri-net tools for whole process models, not one record's state machine judged by this kernel | None needed |
| bpmnlint | Lints BPMN diagrams; PlayIDE's models are UML state machines judged by the kernel | None needed |
