# Gates defined in quality/sessions/tests.py

# Quality Gates

* [nox -s release_fixture](release-fixture.md) - Owner-only release gate: current bytes must match the owner-stamped fixture.
* [nox -s tests](tests.md) - Unit, integration, crash-recovery and concurrency tests of the kernel.
