# ADR-0018: Formal V&V portfolio: each technique is a distinct evidence kind

* Status: proposed (accepted per technique when its lane lands)
* Date: 2026-09-28

## Context and problem statement

v0.2 verifies one-step behaviour with a same-author 5×5×5 runtime matrix. Stronger assurance needs multi-step, symbolic and machine-checked techniques, and none of them may be relabelled as another.

## Considered options (all open source)

| Technique | Tool | What it can establish | Evidence kind |
|---|---|---|---|
| Machine-checked laws | [Bend 2](https://github.com/bendlang/bend) `LAWS.bend` / `PROOF.bend` | Laws hold for **all** action sequences of the model generated from code | `bend_proof` |
| Temporal model checking | [TLA+](https://github.com/tlaplus/tlaplus) with TLC | Safety invariants of the workflow and the commit protocol (replay, CAS, authority), up to declared bounds | `tlc_model_check` |
| SMT policy soundness | [Z3](https://github.com/Z3Prover/z3) | `check_policy` accepts only authority-preserving candidates across the whole transaction grammar | `smt_proof` |
| Bounded exhaustive runtime | explicit-state search over the real runtime | No reachable counterexample within depth *k* | `bounded_model_check` |
| Model-based differential tests | [Hypothesis](https://github.com/HypothesisWorks/hypothesis) stateful testing | The runtime and SQLite agree with an independent reference model on generated sequences | `property_test` |
| Mutation analysis | an OSS mutation tool | The suite detects seeded faults (fault-detection power, not correctness) | `mutation_score` |

## Decision outcome

Adopt all of them in stages. Every formal artefact is **generated from, or checked against, the executable Python model**, so the verified model cannot silently drift from the code. Every receipt states its assumptions and bounds. A proof about the model is not a proof about the Python runtime. Conformance between the two is a separate claim, covered by trace replay.
