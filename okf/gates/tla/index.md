# Gates defined in quality/sessions/tla.py

# Quality Gates

* [nox -s formal_tla_deep](formal-tla-deep.md) - formal_tla plus the candidate model checked with 5 operation ids (about 28k states).
* [nox -s formal_tla](formal-tla.md) - TLC model check of Excursion.tla, negative controls, and runtime-vs-spec conformance.
* [nox -s tla_drift](tla-drift.md) - The committed TLA+ model modules match the kernel's workflow, actor directory and bounds.
