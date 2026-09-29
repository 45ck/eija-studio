# Gates defined in quality/sessions/mutation.py

# Quality Gates

* [nox -s mutation_quick](mutation-quick.md) - Authority-core mutation run (policy.py, two workers, a few minutes) gated by the ratchet floor.
* [nox -s mutation](mutation.md) - Full mutation run over the domain and application authority/evidence modules, gated by the ratchet floor.
