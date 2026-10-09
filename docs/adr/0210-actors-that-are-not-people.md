# ADR-0210: Actors that are not people: AI agents, timers and external systems in the model

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE (owner ask, 9 October 2026: many tasks across sectors to refine "how humans and computers and agents and software etc is all designed"; this record covers non-human actors inside the system being designed, not PlayIDE's own chat AI)

## Context and problem statement

Systems people design now have AI agents in them: a support bot that triages tickets and proposes refunds, a scheduled job that escalates what nobody handled, a payment provider that calls back. A UML engineer draws each of them as an actor. PlayIDE could only say "role": every role was a person as far as anything could tell. So the rule that matters most once an agent is in the loop could not be written: "only a person approves a refund, whichever agent we add later". A law naming one role (`role_never_holds SupportAgent`) is silent the day someone adds a second agent role, and silent again when a candidate model uses a role the pack never declared.

A session on the library loan pack showed the gap: the Clerk who "flags overdue loans" is really a nightly job, and nothing in the model, the diagrams or the laws could say so.

## Decision drivers

* The kernel decides, and it decides the same way for every actor. An agent's request goes through `runtime.check_actor` like a person's; nothing about the kernel or its trusted files changes.
* Proper UML. UML 2.5.1 (§18.1) says an actor may be a person, an external system or a device, and may be drawn as a stick figure or as a classifier with the «actor» keyword and its own icon. Use-case practice adds the time actor (Cockburn, *Writing Effective Use Cases*), so timers are actors too.
* Laws about the kind of actor, not a named role, so they keep biting as roles are added; and fail closed: a role nobody declared is never treated as a person.
* No change to any pack's identity. A pack that names no kinds keeps its digest, so every receipt and evidence file that binds one still matches.
* Every new law kind gets executable semantics, a missing-resolver rejection, a negative oracle and an evidence policy (AGENTS.md).

## What existing tools do

| Tool | How non-human actors and human-in-the-loop are modelled | What PlayIDE takes |
|---|---|---|
| UML 2.5.1 (OMG standard) | `Actor` covers people, systems and devices; keyword/icon notation is allowed | The four kinds and their notation: stick figure for a person, «agent», «timer» or «system» classifier for the rest |
| BPMN 2.0 (OMG standard; bpmn-js avoided earlier) | User tasks vs service tasks; timer events; pools for external participants | A timer is a scheduled actor; an external system is a participant that calls in |
| Camunda / Flowable (Apache-2.0) | Human approval as a user task assigned to a group; service tasks for systems | "Only a person decides" as a law, with the assignment guard for "on shift" |
| AWS Step Functions, Temporal (Apache-2.0 for Temporal) | `waitForTaskToken` / signals pause a workflow for a human | The person-in-the-loop path law: no run reaches the end state without a person's step |
| LangGraph (MIT) | `interrupt()` stops an agent graph for human approval | The same idea stated over the whole model, checked before anything runs, not inside an agent's code |
| Stately / XState (MIT) | No actor kinds; guards are code | Nothing to adopt: the kinds are a typed field read by laws |

None is a library PlayIDE can call for this: the change is one typed field on a pack role and three law kinds over the existing kernel, so no dependency is added.

## Considered options

* **A `kind` on each role (`human` default, `agent`, `timer`, `system`) and three laws about kinds: `only_kind_holds`, `only_kind_enters`, `path_requires_kind`** (chosen).
* Name each non-human role in ordinary role laws (`role_never_holds`). Rejected: silent for any role added later or left undeclared.
* A kind on each fixture actor instead of on the role. Rejected: the kernel authorises by role, the diagrams draw roles, and a law has to be about what the model allows, not about today's fixtures.
* New kernel guards for agents (for example an amount threshold an agent may approve under). Deferred: value guards and timers are kernel operators waiting on the owner's restamp (issue #93, #80).

## Decision outcome

Chosen option: a role kind and three kind laws, because they say the thing engineers need to say about agents in the vocabulary they already use, in data the kernel already checks.

* **Role kind.** `Role.kind` in `domain/pack.py`. A person is the default and is not written out when the pack is serialised, so existing packs keep their digests.
* **`only_kind_holds`** (action, role kinds): every transition performing the action is held by a role of those kinds. "Only a person approves a refund."
* **`only_kind_enters`** (state, role kinds): every transition entering the state is held by a role of those kinds, whatever the action.
* **`path_requires_kind`** (state, role kinds): every path from the initial state to the state includes a step by a role of those kinds, the entering step included. "A person acted on every refund that is paid."
* **Binding.** When a pack loads, each kind law is bound to the pack's roles of its kinds. A role the pack does not declare has no kind, so it never counts: an AI proposing a step for an invented "AutoApprover" role breaks the law. A kind law whose kinds match no declared role is refused when the pack loads (`no declared role is of kind …`).
* **Where each is judged.** The protected policy judges all three on the table on every edit, so a chat plan or a drawn edit that gives the approval to the agent is refused and names the laws. The law proof (ADR-0166) judges them on every run; for `path_requires_kind` its configurations also record whether a step of the law's kinds has happened yet. The generated SMT encoding covers the two per-transition laws; the path law is listed NOT_RUN with the reason, like `path_requires`.
* **Diagrams and Simulate.** The use case diagram draws a person as a stick figure and the other kinds as an actor classifier with «agent», «timer» or «system». Simulate reports what each kind of actor tried and what the kernel answered, and the run log names an actor's kind when it is not a person. `/api/play/roles` serves the kinds to the page.
* **Example.** `packs/refund-desk`: an AI agent triages and proposes, a timer escalates, the payment system confirms or fails a payout, and only a supervisor on shift approves. Its test cases include the agent being refused when it tries to approve, a paused agent (its kill switch: an inactive actor) refused at once, and a supervisor unable to mark a refund paid by hand.

### Consequences

* Good: "keep a person in the loop" is a checked law, proved over every run, that survives new agent roles and invented ones.
* Good: no kernel or trusted file changes; existing packs, receipts and evidence are untouched.
* Bad: a timer is an actor that acts when the simulation picks it, not after elapsed time; real `after(…)` timers are issue #93.
* Bad: "an agent may approve refunds under 50" needs value guards (issue #93); today a law can only keep the whole decision with a person.
* Revisit when: value guards or timers land in the kernel, or a sketch, UML import or chat needs to declare a role's kind.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Camunda / Flowable user tasks | A process engine with its own runtime; PlayIDE's kernel is the only interpreter (ADR-0165) | None needed: the kinds are pack data |
| LangGraph `interrupt()` | Pauses an agent at run time inside agent code; it cannot prove that no run skips the person | None needed |
| Stately / XState | No notion of actor kinds | None needed |
