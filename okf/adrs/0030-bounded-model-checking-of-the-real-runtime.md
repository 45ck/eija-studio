---
type: Architecture Decision Record
title: 'ADR-0030: Bounded model checking by explicit-state search over the real runtime'
description: 'The runtime matrix in `application/verifier.py` is one-step: five actors times five states times five actions, each cell from a fresh instance.'
resource: repo://docs/adr/0030-bounded-model-checking-of-the-real-runtime.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0030-bounded-model-checking-of-the-real-runtime.md
  title: 0030-bounded-model-checking-of-the-real-runtime.md
  hash_method: lf-sha256-v1
  sha256: dc80ff62ac390867955297e95e94d74a18d5f9fd6ec04fff68a910bf54488c7a
notes_baseline: 65abd70e8ed8059ac876c7006ad0116ef98a68f65a808e77a040ee0f771736f9
---

# ADR-0030: Bounded model checking by explicit-state search over the real runtime

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-09-28 |
| Lane | smt-bmc (formal: bounded model checking) |
| Source | `repo://docs/adr/0030-bounded-model-checking-of-the-real-runtime.md` |

## Decision outcome (verbatim)

> Chosen option: "explicit-state BFS in `verification/bmc/`", because no mature model checker executes an arbitrary Python callable against a database, and the search itself is a few hundred lines around the real `execute`.
>
> * **State** is the full observable sandbox database (instance, actors, operations, audit, outbox), taken from an ephemeral store built by `adapters.sqlite_store.sandbox_factory`; it is restored between moves by writing the observed rows back.
> * **Moves** are every (actor, action, expected version, operation id) command over the five fixture actors plus an unknown actor and an unmodelled action, with the current or a stale version, replay of every recorded operation id (identical, other actor, other action), and environment moves that revoke/restore and assign/unassign actors by updating the actors table.
> * **Checks** run on every transition and every new state: authority on commit, authority **before replay**, compare-and-swap, state guard, exactly-once operations and binding, exact commit effects, no trace from rejection or replay, no spurious denial, denial reason, the audit trail being a valid run of the model that ends at the instance state, decisions only by Registrar, approval only after a recommendation, no forbidden effect, outbox rows only for committed Recommends.
> * **Search** is breadth-first with state de-duplication, so the first counterexample per invariant is a shortest one. Reports carry states, transitions, per-depth new states, outcome-class counts (a coverage check fails if the alphabet never provokes a denial code, a replay or a revocation), whether the reachable set closed, and wall-clock time under `measurements` only.
> * **Self-test.** Six seeded runtime faults (revocation ignored, assignment ignored, role ignored, replay before authority, stale version accepted, replay reapplies effects) must each be found within three moves. The real runtime must not be flagged.
> * **Tiers.** Full: depth 6, baseline and the recommendation candidate with rejection from Recommended (two of the three accepted workflows). Release: depth 8, all three workflow variants (the third, rejection from Submitted, is only checked here). Deterministic statistics for depth 6 and depth 8 are committed and drift-checked. A run that cannot compare with committed statistics (different depth or alphabet) or skipped the self-test is `PARTIAL`, never `PASS`; the wall-clock cap is not part of the compared configuration.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind](/adrs/0018-formal-vv-portfolio.md) - v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
* [ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC](/adrs/0027-tla-plus-specification-and-model-checking.md) - The v0.2 runtime matrix checks one step from each state.
* [ADR-0031: Property-based testing with Hypothesis, in two profiles](/adrs/0031-property-based-testing-with-hypothesis.md) - The kernel's guarantees are universally quantified: "every actor x state x action", "any order of definitions hashes the same", "any dependency graph closes to…

## Referenced by

* [ADR-0145: Per-kind admissibility: the kernel recomputes formal evidence from raw artifacts](/adrs/0145-per-kind-evidence-admissibility.md) - `domain.evidence.assess_receipt` recomputes admissibility for one claim only: the runtime matrix (`runtime_matrix` / `integration_test`).
* [Formal: Z3 policy soundness and bounded model checking](/lanes/0029-formal-z3-policy-soundness-and-bounded.md) - Capability lane with ADR numbers 0029–0030 reserved.
<!-- okf:generated:end links -->
