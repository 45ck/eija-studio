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

* [Machine-checked laws](/verification/bend-proof.md) - Establishes: Laws hold for **all** action sequences of the model generated from code
* [Bounded exhaustive runtime](/verification/bounded-model-check.md) - Establishes: No reachable counterexample within depth *k*
* [Mutation analysis](/verification/mutation-score.md) - Establishes: The suite detects seeded faults (fault-detection power, not correctness)
* [Model-based differential tests](/verification/property-test.md) - Establishes: The runtime and SQLite agree with an independent reference model on generated sequences
* [SMT policy soundness](/verification/smt-proof.md) - Establishes: `check_policy` accepts only authority-preserving candidates across the whole transaction grammar
* [Temporal model checking](/verification/tlc-model-check.md) - Establishes: Safety invariants of the workflow and the commit protocol (replay, CAS, authority), up to declared bounds
<!-- okf:generated:end links -->
