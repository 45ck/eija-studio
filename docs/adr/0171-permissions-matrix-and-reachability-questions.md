# ADR-0171: Who can do what, as a matrix the kernel checks, and reachability questions with a proof or a path

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026: "UI, HCI, AHCI"; input from the "Who PlayIDE is for" research)

## Context and problem statement

Access rules are what AI-written apps most often get wrong, and they are what reviewers and auditors ask about first: who can do what, from which state, and can anything happen without the right person. In PlayIDE the answer was spread over the state machine's transition labels, the use case diagram and the inspector. Nothing let an engineer ask the question directly, and nothing showed how a previewed AI plan changed permissions.

## Decision drivers

* Answers come from the kernel and the model, never from a reading of the page.
* A "no" must be a proof, and a "yes" must be something the kernel actually did. Anything in between says so.
* One source per fact: the matrix is a projection of the model's transitions, not a second permissions file.
* The same question works on a previewed plan, so a reviewer can see what an AI change does to access.

## Considered options

* A server-side projection and search in the application layer, with each cell and each path replayed through `runtime.execute` (chosen).
* A policy engine such as Casbin (Apache-2.0) or OPA. Rejected: a second source of permissions beside the model, with a second interpreter.
* The existing TLA+ specification (`verification/tla`) for reachability. Not chosen for the interactive path: it needs Java and runs seconds to minutes, while the question is answered in milliseconds by a breadth-first search over at most a few dozen transitions. TLC stays the deeper check.
* NetworkX for the search. Not needed: a breadth-first search over the transitions is a dozen lines of the standard library, and NetworkX is only in the `graph` extra.

## Decision outcome

Chosen option.

* `application/access.py`:
  * `matrix(pack, model)` lists, for every state and every role in the pack, the actions that role may take from that state. It tries each one in the kernel with every fixture actor in that role, on a fresh record in that state, and records who was let through and the refusal code for the rest (`ASSIGNMENT_DENIED`, `ACTOR_REVOKED`, …).
  * `access(pack, model, base)` adds the permissions a model adds and removes compared with `base`.
  * `reach(pack, model, target, without)` asks whether a record can reach `target` with no step taken by role `without` (or at all). It answers with one of three outcomes:
    * **UNREACHABLE.** No sequence of the model's transitions avoiding the role gets there. Guards can only refuse more, so this holds for every actor.
    * **REACHABLE.** It searches the transitions some fixture actor can take in the kernel, then replays the shortest path on one record, step by step. The answer carries that path and the actors.
    * **NOT_SHOWN.** The model has a path, but the fixture actors could not take it in the kernel. Other actors might.
* `POST /api/play/access` and `POST /api/play/reach` take the same request as Build & run and Simulate. With accepted plan steps, they answer for the previewed candidate, recomputed on the server. `access` then flags the changes against the base model.
* The **Permissions** tab (`play-access.js`, `play-access.css`) shows the question as a sentence ("Can a record reach [Overdue] without [a Clerk]? Ask the kernel"), the answer with its path (each step selects its transition on the state machine), the plan's permission changes, and the matrix. Added permissions are marked new; removed ones are struck through. A question once asked is asked again whenever a plan is previewed or left. The command palette (ADR-0170) has "Show who can do what".

### Consequences

* Good: a reviewer can ask the access question an auditor would ask and get a proof or a replayed path, on the model or on an AI's plan.
* Good: the matrix shows the guards' effect per actor (assigned only, revoked), from the kernel's own refusals.
* Bad: REACHABLE and the matrix's per-actor marks use the pack's fixture actors. They say what those actors can do, not what every real actor can do. The UNREACHABLE proof does not have this limit.
* Bad: the question form covers "reach a state without a role". Questions over effects, or "only after a role acted", are not yet expressible.
* Revisit when: the review workbench shows a change case, since the same question belongs beside its diagram diff, or when packs gain guards that depend on record data rather than the actor and state.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Casbin, Open Policy Agent (Apache-2.0) | Policy engines: a second permissions source and interpreter beside the model | — |
| TLA+/TLC (existing, `verification/tla`) | Seconds to minutes and a JVM for a question answered in milliseconds; stays the deeper check | Generate a TLC property from a question if deeper checks are wanted |
| NetworkX (BSD-3, `graph` extra) | Not a core dependency; the search is a few lines of `collections.deque` | — |
| Existing `runtime.execute` and the simulation's `MemorySession` | Adopted: every cell and every path step is the kernel's own answer | — |
