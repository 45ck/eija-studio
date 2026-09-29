# Verification techniques and evidence kinds

# Verification Techniques

* [Machine-checked laws](bend-proof.md) - Planned (not implemented). Would establish: Laws hold for **all** action sequences of the model generated from code
* [Bounded exhaustive runtime](bounded-model-check.md) - Planned (not implemented). Would establish: No reachable counterexample within depth *k*
* [Bounded runtime matrix (integration_test)](integration-test.md) - Implemented: Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched a hand-written oracle that is partly derived from the model under test.
* [Mutation analysis](mutation-score.md) - Planned (not implemented). Would establish: The suite detects seeded faults (fault-detection power, not correctness)
* [Model-based differential tests](property-test.md) - Planned (not implemented). Would establish: The runtime and SQLite agree with an independent reference model on generated sequences
* [SMT policy soundness](smt-proof.md) - Planned (not implemented). Would establish: `check_policy` accepts only authority-preserving candidates across the whole transaction grammar
* [Temporal model checking](tlc-model-check.md) - Planned (not implemented). Would establish: Safety invariants of the workflow and the commit protocol (replay, CAS, authority), up to declared bounds
