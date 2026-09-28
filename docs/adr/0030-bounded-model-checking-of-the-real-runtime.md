# ADR-0030: Bounded model checking by explicit-state search over the real runtime

* Status: accepted
* Date: 2026-09-28
* Lane: smt-bmc (formal: bounded model checking)

## Context and problem statement

The runtime matrix in `application/verifier.py` is one-step: five actors times five states times five actions, each cell from a fresh instance. The kernel's hardest guarantees are about **sequences**: authority is rechecked before an earlier success is replayed, a stale `expected_version` never commits, a rejected or replayed command leaves no trace, and a revoked or unassigned actor loses the ability to act. A one-step matrix cannot see a fault that needs "commit, revoke, replay". ADR-0018 reserves a `bounded_model_check` evidence kind.

## Decision drivers

* Check the code that runs (`application.runtime.execute` over the SQLite unit of work), not a model of it; a model of the runtime is the TLA+ lane's job (ADR-0027) and the two should later be linked by trace conformance.
* Shortest counterexample traces, state-space statistics and honest bounds.
* Fast enough for the full tier (depth 6 measured at 85 s including the self-test on the shared reference PC, 2026-09-29); a deeper release tier.
* The checker must be shown to find bugs: seeded faults must be caught.

## Considered options

* **Custom breadth-first explicit-state search that drives the real runtime** (chosen).
* TLA+ / TLC over a model of the protocol: a different artefact and a different claim (ADR-0027); TLC cannot execute Python or SQLite.
* Hypothesis stateful testing: randomised, no completeness statement at a depth, weaker counterexample minimality. Complementary (ADR-0031).
* CrossHair / CBMC-style bounded symbolic execution of `execute`: the runtime is dominated by SQLite I/O, which such tools do not model.
* Pure random fuzzing: no bound statement at all.

## Decision outcome

Chosen option: "explicit-state BFS in `verification/bmc/`", because no mature model checker executes an arbitrary Python callable against a database, and the search itself is a few hundred lines around the real `execute`.

* **State** is the full observable sandbox database (instance, actors, operations, audit, outbox), taken from an ephemeral store built by `adapters.sqlite_store.sandbox_factory`; it is restored between moves by writing the observed rows back.
* **Moves** are every (actor, action, expected version, operation id) command over the five fixture actors plus an unknown actor and an unmodelled action, with the current or a stale version, replay of every recorded operation id (identical, other actor, other action), and environment moves that revoke/restore and assign/unassign actors by updating the actors table.
* **Checks** run on every transition and every new state: authority on commit, authority **before replay**, compare-and-swap, state guard, exactly-once operations and binding, exact commit effects, no trace from rejection or replay, no spurious denial, denial reason, the audit trail being a valid run of the model that ends at the instance state, decisions only by Registrar, approval only after a recommendation, no forbidden effect, outbox rows only for committed Recommends.
* **Search** is breadth-first with state de-duplication, so the first counterexample per invariant is a shortest one. Reports carry states, transitions, per-depth new states, outcome-class counts (a coverage check fails if the alphabet never provokes a denial code, a replay or a revocation), whether the reachable set closed, and wall-clock time under `measurements` only.
* **Self-test.** Six seeded runtime faults (revocation ignored, assignment ignored, role ignored, replay before authority, stale version accepted, replay reapplies effects) must each be found within three moves. The real runtime must not be flagged.
* **Tiers.** Full: depth 6, baseline and recommendation candidate. Release: depth 8, all three workflow variants. Deterministic statistics for depth 6 are committed and drift-checked.

### Consequences

* Good: multi-step authority, replay and revocation behaviour of the shipped code is checked with shortest counterexamples and a fault-detection demonstration.
* Bad: bounded. No violation to depth k is not a proof for k+1; the reachable set did not close at the depths run, and the report says so.
* Bad: the reference model is a same-author oracle; concurrency, crash points and unknown actors beyond one are out of scope; SQLite itself is trusted.
* Bad: between 1.7 ms (author's machine) and 3.6 ms (measured 2026-09-29 on the loaded reference PC) per transition (each `store.transaction()` opens a connection); the alphabet, not the engine, is the cost driver.
* Revisit when: the actors table, the guard set or the effect kinds change (the statistics drift check fails), or when TLC trace conformance can consume these traces.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| TLC (TLA+), Hypothesis stateful, CrossHair, Stateright, pytest | None executes an arbitrary Python callable against SQLite with completeness at a stated depth and shortest traces | Feed the same alphabet to Hypothesis `RuleBasedStateMachine` for depth beyond k; replay found traces against the TLA+ model |
