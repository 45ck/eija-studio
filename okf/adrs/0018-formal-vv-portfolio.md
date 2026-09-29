---
type: Architecture Decision Record
title: 'ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind'
description: v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix.
resource: repo://docs/adr/0018-formal-vv-portfolio.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0018-formal-vv-portfolio.md
  title: 0018-formal-vv-portfolio.md
  hash_method: lf-sha256-v1
  sha256: a96d6e237cddf535f73b8998f9480355c7bdd38c5b2a90998337ab91f5e128b8
notes_baseline: 29b356474621e7a1b67e86067b684d4437549ffe8c557d19fdb7e0e2dd768c77
---

# ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed (accepted per technique when its lane lands) |
| Date | 2026-09-28 |
| Source | `repo://docs/adr/0018-formal-vv-portfolio.md` |

## Decision outcome (verbatim)

> Adopt all of them in stages. Every formal artefact is **generated from, or checked against, the executable Python model**, so the verified model cannot silently drift from the code. Every receipt states its assumptions and bounds. A proof about the model is not a proof about the Python runtime. Conformance between the two is a separate claim, covered by trace replay.

## Sections

* Context and problem statement
* Considered options (all open source)
* Decision outcome
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0025: Machine-check protected authority laws with Bend 2 in a pinned container](/adrs/0025-bend-machine-checked-laws.md) - The v0.2 runtime matrix observes one step of the runtime for 125 synthetic cells with a same-author oracle.
* [ADR-0027: TLA+ specification of the workflow and commit protocol, checked with TLC](/adrs/0027-tla-plus-specification-and-model-checking.md) - The v0.2 runtime matrix checks one step from each state.
* [ADR-0028: Model-to-code conformance by exhaustive graph comparison and TLC trace validation](/adrs/0028-runtime-conformance-by-graph-comparison-and-trace-validation.md) - A TLA+ proof about `Excursion.tla` is a proof about the model.
* [ADR-0029: Z3 proof that the protected policy admits only authority-preserving candidates](/adrs/0029-z3-policy-soundness-proof.md) - `domain.policy.check_policy` is the gate between an AI-proposed candidate workflow and the local owner.
* [ADR-0030: Bounded model checking by explicit-state search over the real runtime](/adrs/0030-bounded-model-checking-of-the-real-runtime.md) - The runtime matrix in `application/verifier.py` is one-step: five actors times five states times five actions, each cell from a fresh instance.
* [ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows](/adrs/0033-mutation-tool-selection.md) - The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role o…
* [ADR-0043: The README is verifiable: generated diagrams, dated status, MkDocs Material docs site](/adrs/0043-readme-truthfulness-and-docs-site.md) - EIJA's promise is that what you see matches the code.
* [HCI-ADR-0058: Screen layout model: five persistent regions, derived widths, no page scroll](/adrs/0058-hci-layout-model.md) - HCI-ADR-0058: Screen layout model: five persistent regions, derived widths, no page scroll
* [HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio](/adrs/0060-hci-typography.md) - HCI-ADR-0060: Typography: families, scale, weights and the monospace rule for the Studio
* [HCI-ADR-0063: Review an agent's change by meaning: operation list, ripple strip and an evidence rail with four-slot coverage](/adrs/0063-hci-evidence-change-review.md) - HCI-ADR-0063: Review an agent's change by meaning: operation list, ripple strip and an evidence rail with four-slot coverage
* [ADR-0102: Formal verification of the weave: a small trusted kernel, certificates, exhaustive small scope, Alloy for bounded statements, and drift guards](/adrs/0102-weave-formal-verification-of-weave.md) - The weave ties code, tests, requirements, UI, diagrams, the ubiquitous language, formal models and evidence into one typed, hash-anchored graph, and a rule set…
* [ADR-0145: Per-kind admissibility: the kernel recomputes formal evidence from raw artifacts](/adrs/0145-per-kind-evidence-admissibility.md) - `domain.evidence.assess_receipt` recomputes admissibility for one claim only: the runtime matrix (`runtime_matrix` / `integration_test`).
* [Machine-checked laws](/verification/bend-proof.md) - Planned (not implemented). Would establish: Laws hold for **all** action sequences of the model generated from code
* [Bounded exhaustive runtime](/verification/bounded-model-check.md) - Planned (not implemented). Would establish: No reachable counterexample within depth *k*
* [Mutation analysis](/verification/mutation-score.md) - Planned (not implemented). Would establish: The suite detects seeded faults (fault-detection power, not correctness)
* [Model-based differential tests](/verification/property-test.md) - Planned (not implemented). Would establish: The runtime and SQLite agree with an independent reference model on generated sequences
* [SMT policy soundness](/verification/smt-proof.md) - Planned (not implemented). Would establish: `check_policy` accepts only authority-preserving candidates across the whole transaction grammar
* [Temporal model checking](/verification/tlc-model-check.md) - Planned (not implemented). Would establish: Safety invariants of the workflow and the commit protocol (replay, CAS, authority), up to declared bounds
<!-- okf:generated:end links -->
