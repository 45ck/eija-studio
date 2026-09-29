# Gates defined in quality/sessions/smt_bmc.py

# Quality Gates

* [nox -s bmc_deep](bmc-deep.md) - Release-tier bounded model check: depth 8 over all three workflow variants (several minutes).
* [nox -s bmc](bmc.md) - Bounded model check of the real runtime to depth 6 (baseline + recommendation candidate), with seeded-fault self-test.
* [nox -s formal_smt_release](formal-smt-release.md) - Release tier: the same proof with a 4x larger differential sample; a missing z3-solver fails instead of skipping.
* [nox -s formal_smt](formal-smt.md) - Z3 proof that check_policy admits only authority-preserving candidates (+ sampled faithfulness + negative controls).
