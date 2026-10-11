# Installation proof

Run the installation scripts serially after building an explicit candidate wheel.
The scripts do not download packages: supply a local wheelhouse containing all of
that wheel's runtime dependencies. Preparing that wheelhouse is a separate network
operation; `pip download --only-binary=:all: --dest <wheelhouse> <candidate.whl>`
can populate it when downloads are authorised. Keep the wheelhouse to reproduce
the installation recorded by the pip report.

From the checkout, use absolute paths for the wheel, source snapshot, wheelhouse,
scratch parent and report. The scratch parent must already exist outside the source
snapshot. Both scripts deliberately create a new environment in a path with spaces.

```console
python scripts/candidate_wheel_smoke.py --wheel <candidate.whl> --source <source-snapshot> --wheelhouse <dependency-wheels> --scratch-root <outside-checkout> --out <outside-checkout>/candidate-install.json
```

The candidate probe expects `SOURCE_REVIEW_REQUIRED`. It checks installed packs,
pack-resolution failures, HTTP asset bytes, session protection, and a read-only
proposal/refusal. It does not approve or activate anything. A passing result proves
this local candidate installation and these bounded checks, not public package
publication, browser usability, production readiness or source approval.

For an owner-reviewed release, run `scripts/wheel_smoke.py` with the same arguments
and a **new** report filename. That probe keeps the strict trusted-source, eligible
demo, export-integrity and actual 125-cell compiler-receipt assertions. An unreviewed
candidate is expected to fail it; do not stamp the source merely to pass.

Each run retains the report and a sibling `<report-stem>-artifacts` directory:

- Source-to-wheel byte manifest, including generator templates and bundled packs.
- Venv creation, offline dependency installation and `pip check` logs.
- Pip installation report with dependency hashes and the installed package list.
- Isolated runtime identity, exact probe bytes/hash and application result logs.
- The explicit copied sample's provenance when the strict release probe uses it.

Runtime imports must come from the new venv, with neither system nor user
site-packages inherited. The runtime receives no checkout `PYTHONPATH` or inherited
EIJA provider settings. Direct URL dependency references are rejected before pip
installation because `--no-index` alone would not prevent that network path.
Old reports are never overwritten. Temporary installation directories are removed
after their logs and manifests have been retained.

The unit tests in `tests/test_wheel_smoke.py` check the runner's negative controls.
Their result alone is not an installation proof. Record the actual installation
run separately for each operating system and candidate revision.
