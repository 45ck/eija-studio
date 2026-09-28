# Formal V&V

Status as of 2026-09-29: **only the Bend 2 laws (merged PR #18) are on `main`; the other statuses below are pull-request states, not results.** The kernel today has one verification technique, the same-author 5 x 5 x 5 runtime matrix (125 one-step observations) described in [Verification](../verification/VERIFICATION.md). The techniques below are the plan in [ADR-0018](../adr/0018-formal-vv-portfolio.md), which is still `proposed`.

| Technique | Tool | Can establish | Evidence kind | ADRs | Status |
|---|---|---|---|---|---|
| Machine-checked laws | Bend 2 | Laws hold for all action sequences of the model generated from code | `bend_proof` | 0025-0026 | on main (merged PR #18); details in [Bend laws](../formal/bend.md) |
| Temporal model checking | TLA+ / TLC | Safety invariants of the workflow and commit protocol, up to declared bounds | `tlc_model_check` | 0027-0028 | branch pushed (`lane/tla`), no PR |
| SMT policy soundness | Z3 | `check_policy` accepts only authority-preserving candidates across the transaction grammar | `smt_proof` | 0029-0030 | open PR #11 |
| Bounded exhaustive runtime | explicit-state search over the real runtime | No reachable counterexample within depth *k* | `bounded_model_check` | 0029-0030 | open PR #11 |
| Model-based differential tests | Hypothesis | Runtime and SQLite agree with an independent reference model on generated sequences | `property_test` | 0031-0032 | branch pushed (`lane/property`), no PR |
| Mutation analysis | an OSS mutation tool | The suite detects seeded faults (detection power, not correctness) | `mutation_score` | 0033-0034 | planned |

## Rules that hold for every technique

* Each technique is a **distinct evidence kind**. None may be relabelled as another, and a receipt states its assumptions and bounds.
* Every formal artefact is generated from, or checked against, the executable Python model, so the verified model cannot silently drift from the code.
* A proof about the model is not a proof about the Python runtime. Conformance between the two is a separate claim, covered by trace replay.
* A missing prerequisite (Java for TLC, Docker or WSL for Bend) reports `NOT_RUN`, never `PASS`.
