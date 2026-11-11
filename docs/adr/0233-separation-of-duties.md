# ADR-0233: Separation of duties

* Status: accepted
* Date: 2026-11-11
* Lane: kernel / laws

## Context and problem statement

Issue #149. Many real workflows need "the person who raises a request is not the person who approves it". Every law kind so far is about roles, states, actions and effects in the transition table, or about one run's sequence of roles. None can say "not the same actor", because the kernel never remembered who took which step on a record. A role check alone is not enough: an actor whose role changes between steps (a support agent promoted to supervisor mid-record) holds the right role for each step.

## Decision drivers

* The refusal is made by the kernel at commit time, in the same unit of work as the step, never by the UI.
* Existing packs, models, digests, oracles and workspaces keep their exact bytes and behaviour.
* The law proof, Simulate and the generated app's conformance oracle all see the same refusal.

## Considered options

* A new law kind `distinct_actors` that the runtime enforces from a per-record log of who took which named action (chosen).
* A guard on transitions (`actor_distinct_from:<action>`): it puts a pack rule in the model, and every transition of the action would have to repeat it.
* Deriving the history from the audit log: the audit only holds effects the pack declares, so an action without an audit effect would leave no trace.

## Decision outcome

**The law.** `{"kind": "distinct_actors", "actions": [two to eight actions]}`: on one record, no single actor takes two different actions of the list. The same action repeated (a resubmission) is allowed. Its references are checked like every other law's. The table cannot break it, so `check_policy` never reports it.

**The runtime.** After the state check, `runtime.execute` looks up the separation laws in force that name the action. Only when there is one does it read the record's act log (`UnitOfWork.acts`) and refuse an actor who already took another listed action with `SEPARATION_DENIED`, naming the law's code and `law:<id>` in the details. On commit it appends `(action, actor)` to the log (`record_act`) in the same unit of work. Packs without the law never touch the log. A replay is still answered from the operation record. The SQLite store and the generated app each gain an additive `acts` table; no schema version changes.

**The proof.** The law proof's actor classes cannot tell two actors of a role apart, so `distinct_actors` is judged by asking the kernel: wherever one listed action directly follows another on a reachable record, one actor takes the first, is given the role of the second and tries it, and must be refused; a different actor must not be refused for separation. No such place is reported as VACUOUS. `evaluate_run` also judges runs whose steps record their actor. The SMT encoding lists it as not encoded.

**The generated app.** The oracle gains `separation_cases` (only when the pack has the law, so other oracles keep their bytes): a fixture actor takes one listed action, then the next, and the kernel's answer. The conformance template checks them, so it now runs eight tests. The app's action options use the same check, so a refused action shows as not allowed.

### Consequences

* Good: "the requester is not the approver" is now a law a pack can state and the kernel enforces, including across a change of role.
* Good: nothing changes for a pack without the law.
* Bad: the law proof checks adjacent pairs of listed actions only; two actions with other steps between them are enforced by the same runtime check but not explored by the proof.
* Bad: identity is the actor id. Two ids held by one person are two actors; the identity provider has to prevent that.
* Revisit when: a pack needs separation across records (for example per customer), or the proof needs non-adjacent pairs.
