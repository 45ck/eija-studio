# Verification techniques and evidence kinds

# Verification Techniques

* [Machine-checked laws](bend-proof.md) - Establishes: Laws hold for **all** action sequences of the model generated from code
* [Bounded exhaustive runtime](bounded-model-check.md) - Establishes: No reachable counterexample within depth *k*
* [Bounded runtime matrix (integration_test)](integration-test.md) - Every cell of a declared actor x state x action matrix, run against the real runtime in a disposable sandbox, matched a separately written expected outcome; the receipt is recomputed from raw observations.
* [Mutation analysis](mutation-score.md) - Establishes: The suite detects seeded faults (fault-detection power, not correctness)
* [Model-based differential tests](property-test.md) - Establishes: The runtime and SQLite agree with an independent reference model on generated sequences
* [SMT policy soundness](smt-proof.md) - Establishes: `check_policy` accepts only authority-preserving candidates across the whole transaction grammar
* [Temporal model checking](tlc-model-check.md) - Establishes: Safety invariants of the workflow and the commit protocol (replay, CAS, authority), up to declared bounds
