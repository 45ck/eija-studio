---
type: Architecture Decision Record
title: 'ADR-0028: Model-to-code conformance by exhaustive graph comparison and TLC trace validation'
description: A TLA+ proof about `Excursion.tla` is a proof about the model.
resource: repo://docs/adr/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md
  title: 0028-runtime-conformance-by-graph-comparison-and-trace-validation.md
  hash_method: lf-sha256-v1
  sha256: 9acb6e4779bb7bdaf91ca4c5e9e41c5d12119c974385654857702b7a90317dc4
notes_baseline: a8ac68c52516bdc11561775fecce3ccf6769183d76e6b0344218a7c3efbfbbe7
---

# ADR-0028: Model-to-code conformance by exhaustive graph comparison and TLC trace validation

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-29 |
| Lane | tla (formal V&V, evidence kind `tlc_model_check`) |
| Source | `repo://docs/adr/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md` |

## Decision outcome (verbatim)

> Chosen option: both measurements, sharing one abstraction.
>
> * **Abstraction.** `verification/tla/abstraction.py` maps a `UnitOfWork` to the nested tuple that `Key(...)` in the spec prints (workflow state, version, audit count, per-operation binding and result, outbox rows per operation, actor directory). It uses only the application port, except environment steps, which follow the existing kernel tests and update the fixture `actors` table with SQL because the kernel has no revocation API.
> * **State-graph comparison.** TLC prints, for every reachable state, the outcome code of every command in the bound and the successor of every committing command and environment step. Python explores the same bounded space by driving the real `execute` on an ephemeral SQLite sandbox (`sandbox_factory`), one scratch transaction per state, each command inside a savepoint. The two tables are compared cell by cell, along with the reachable state sets.
> * **Trace validation.** Scripted scenarios (replay, replay after revocation and assignment loss, cross-actor replay, binding conflict, stale version, unknown actor), shortest paths to reachable states with replay and cross-actor probes, and seeded random walks with directory changes are executed on the real runtime with real commits. Each step's observed outcome and post-state feed a trace-validation spec (`ExcursionTrace.tla`) that TLC checks against the model, at a larger op-id bound than the graph comparison.
> * **Sensitivity.** The same comparison and traces are run against the spec with a seeded defect (replay before authority). Both must report disagreement, otherwise the run fails.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://verification/tla/abstraction.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
* [ADR-0031: Property-based testing with Hypothesis, in two profiles](/adrs/0031-property-based-testing-with-hypothesis.md) - The kernel's guarantees are universally quantified: "every actor x state x action", "any order of definitions hashes the same", "any dependency graph closes to…

## Referenced by

* [ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC](/adrs/0027-tla-plus-specification-and-model-checking.md) - The v0.2 runtime matrix checks one step from each state.
* [Formal: TLA+/TLC specification and trace conformance](/lanes/0027-formal-tla-tlc-specification-and-trace.md) - Capability lane with ADR numbers 0027–0028 reserved.
<!-- okf:generated:end links -->
