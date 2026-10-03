# ADR-0028: Model-to-code conformance by exhaustive graph comparison and TLC trace validation

* Status: accepted
* Date: 2026-09-29
* Lane: tla (formal V&V, evidence kind `tlc_model_check`)

## Context and problem statement

A TLA+ proof about `Excursion.tla` is a proof about the model. [ADR-0018](0018-formal-vv-portfolio.md) already states that conformance between model and Python runtime is a separate claim. The model's decision procedure (`Decide`) is a transcription; the risk is a runtime change (for example moving the replay lookup above authority) that leaves the model green and the code wrong, or the reverse.

## Decision drivers

* The evidence must come from the **real** `application.runtime.execute`, not a reimplementation.
* Disagreement must be reported precisely (state, command, both outcomes), and the check must be shown to be sensitive to a seeded defect.
* Must run on the reference PC in minutes, with data kept in the checkout.

## Considered options

* Two complementary measurements (chosen): exhaustive state-graph comparison within a bound, plus TLC trace validation of observed executions.
* Trace validation only: samples histories; cannot show that an outcome code is right in every reachable state.
* Graph comparison only: exhaustive but bounded to the small op-id set; does not reach longer or randomised histories.
* Generate the Python runtime from the TLA+ spec, or the spec from the runtime: rejected, it would create a second interpreter (AGENTS.md) or hide the transcription risk instead of measuring it.

## Decision outcome

Chosen option: both measurements, sharing one abstraction.

* **Abstraction.** `verification/tla/abstraction.py` maps a `UnitOfWork` to the nested tuple that `Key(...)` in the spec prints (workflow state, version, audit count, per-operation binding and result, outbox rows per operation, actor directory). It uses only the application port, except environment steps, which follow the existing kernel tests and update the fixture `actors` table with SQL because the kernel has no revocation API.
* **State-graph comparison.** TLC prints, for every reachable state, the outcome code of every command in the bound and the successor of every committing command and environment step. Python explores the same bounded space by driving the real `execute` on an ephemeral SQLite sandbox (`sandbox_factory`), one scratch transaction per state, each command inside a savepoint. The two tables are compared cell by cell, along with the reachable state sets.
* **Trace validation.** Scripted scenarios (replay, replay after revocation and assignment loss, cross-actor replay, binding conflict, stale version, unknown actor), shortest paths to reachable states with replay and cross-actor probes, and seeded random walks with directory changes are executed on the real runtime with real commits. Each step's observed outcome and post-state feed a trace-validation spec (`ExcursionTrace.tla`) that TLC checks against the model, at a larger op-id bound than the graph comparison.
* **Sensitivity.** The same comparison and traces are run against the spec with a seeded defect (replay before authority). Both must report disagreement, otherwise the run fails.

### Consequences

* Good: a disagreement names the state, the command and the two outcome codes; agreement counts are reported (states, cells, traces, steps).
* Good: no new engine; TLC is the only checker, Python only observes the real runtime.
* Bad: agreement holds only within the bound and the abstraction. Audit bodies, outbox payloads, result JSON beyond state/version, timestamps, concurrency and crashes are outside it.
* Bad: the concretisation used to load a scratch store from a state key is an assumption, mitigated by checking `abstract(concretise(k)) = k` for every explored state and by the un-injected trace validation.
* Bad: the binding hash is decoded by recomputing the runtime's binding formula; if that formula changes, decoding fails loudly and the harness must be updated.
* Revisit when: the runtime gains new guards or outcome codes (extend `Decide` and the command space), or a second lane needs the same abstraction (extract it).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| TLC trace validation idiom (Cirstea et al., "Validating Traces of Distributed Programs Against TLA+ Specifications", 2024) | The idiom is adopted; it still needs a per-system trace encoder | `conformance.py` is the encoder for this kernel |
| Hypothesis stateful testing | Owned by the property-test lane (ADR-0031/0032); compares against a Python reference model, not the TLA+ spec | Both can run; they are distinct evidence kinds |
